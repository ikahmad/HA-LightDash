from __future__ import annotations

import asyncio
import html
import json
import logging
import sys
import atexit
import signal
import urllib.parse
from contextlib import asynccontextmanager
from pathlib import Path
from string import Template
from typing import Any, Dict

import httpx
import yaml
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

import sentry_sdk

from app.compat import collect_entities, scan_dashboard
from app.config import AppConfig
from app.constants import _SW_SCRIPT
from app.ha_client import HAClient
from app.parser import parse_dashboard
from app.renderer import _css_link, render_error, render_view, render_view_index
from app.sse_manager import SSEManager, run_ha_websocket_forever

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_fmt = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
for _log_name in ("", "uvicorn", "uvicorn.error", "uvicorn.access"):
    for _h in logging.getLogger(_log_name).handlers:
        _h.setFormatter(_fmt)

logger = logging.getLogger(__name__)


def _log_exit():
    try:
        logger.warning("LightDash process exiting")
    except Exception:
        sys.stderr.write("WARNING: LightDash process exiting (atexit, logger unavailable)\n")
        sys.stderr.flush()
atexit.register(_log_exit)


for _sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(
        _sig,
        lambda s, f: logger.warning("Received signal %d (%s)", s, signal.Signals(s).name),
    )


APP_DIR = Path(__file__).parent

_TPL_DIR = Path(__file__).resolve().parent / "templates"


def _load_tpl(name: str) -> Template:
    return Template((_TPL_DIR / name).read_text("utf-8"))


_TPL_DASHBOARD_LIST = _load_tpl("dashboard_list.html")
_TPL_CONFIG_PAGE = _load_tpl("config.html")
_TPL_PREVIEW = _load_tpl("preview.html")


async def _watch_dashboard_files(
    data_dir: Path, dashboards: dict, sse: SSEManager
) -> None:
    from app.parser import parse_dashboard_from_file

    if not data_dir.exists():
        return

    mtimes: dict = {p.stem: p.stat().st_mtime for p in data_dir.glob("*.yaml")}

    while True:
        await asyncio.sleep(10)
        try:
            current = {p.stem: p for p in data_dir.glob("*.yaml")}
            changed = False
            for name, path in current.items():
                mtime = path.stat().st_mtime
                if mtimes.get(name) != mtime:
                    try:
                        parsed = parse_dashboard_from_file(str(path))
                        scan_dashboard(parsed)
                        dashboards[name] = parsed
                        logger.info("Reloaded dashboard from disk: %s", name)
                        mtimes[name] = mtime
                        changed = True
                    except Exception as e:
                        logger.warning("Failed to reload %s: %s", name, e)
            for name in list(mtimes):
                if name not in current:
                    dashboards.pop(name, None)
                    del mtimes[name]
                    logger.info("Removed dashboard: %s", name)
                    changed = True
            if changed:
                _rebuild_entity_filter(dashboards, sse)
        except Exception as e:
            logger.warning("Dashboard watch error: %s", e)


def _rebuild_entity_filter(dashboards: dict, sse: SSEManager) -> None:
    entities: set = set()
    for d in dashboards.values():
        entities.update(collect_entities(d))
    sse.allowed_entities = entities
    logger.info(
        "Entity filter: %d entities across %d dashboard(s)",
        len(entities),
        len(dashboards),
    )


async def _heartbeat(sse: SSEManager) -> None:
    import os, time

    start = time.monotonic()
    first = True
    while True:
        await asyncio.sleep(60 if first else 300)
        first = False
        try:
            rss = int(Path(f"/proc/{os.getpid()}/status").read_text().split("VmRSS:")[1].split()[0])
        except Exception:
            rss = -1
        logger.info(
            "Heartbeat: uptime=%dm rss=%dKB sse_clients=%d",
            (time.monotonic() - start) / 60,
            rss,
            len(sse._clients),
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = AppConfig.from_env()

    sys.excepthook = lambda t, v, tb: logger.critical(
        "Unhandled exception", exc_info=(t, v, tb)
    )
    loop = asyncio.get_running_loop()
    loop.set_exception_handler(
        lambda l, ctx: logger.critical("asyncio exception: %s", ctx)
    )

    level = getattr(logging, config.log_level.upper(), logging.WARNING)
    logging.getLogger().setLevel(level)
    logger.info("Log level set to %s", config.log_level)

    if config.diagnostics:
        sentry_sdk.init(
            dsn="https://7dd83515f99eff25c8f24ebee7c4c9f5@o4511500507611136.ingest.de.sentry.io/4511500514492496",
            send_default_pii=True,
            enable_logs=True,
            traces_sample_rate=1.0,
            profile_session_sample_rate=1.0,
            profile_lifecycle="trace",
        )
        logger.info("Error diagnostics enabled — crash reports sent to developer")
    else:
        logger.info("Error diagnostics disabled")

    ha_client = HAClient(config.ha_url, config.ha_token)
    connected = await ha_client.connect()

    if not connected:
        logger.info("Running in offline mode — HA features disabled")

    logger.info("Starting HA WebSocket listener for %s", config.ha_url)
    sse = SSEManager()
    ws_task = asyncio.create_task(
        run_ha_websocket_forever(config.ha_url, config.ha_token, sse)
    )

    def _warn_ws_done(t: asyncio.Task):
        if not t.cancelled() and t.exception() is not None:
            logger.warning("WebSocket manager task failed: %s", t.exception())

    ws_task.add_done_callback(_warn_ws_done)

    dashboards = AppConfig.load_dashboards(config.config_dir, config.is_addon)
    logger.info("Loaded %d dashboard(s)", len(dashboards))
    for name, d in dashboards.items():
        scan_dashboard(d)
        url = f"{config.base_path}/d/{name}"
        logger.info('  "%s" → %s', d.title, url)

    app.state.config = config
    app.state.dashboards = dashboards
    app.state.ha_client = ha_client
    app.state.sse = sse
    app.state.base_path = config.base_path
    app.state.public_port = config.public_port

    logger.info("base_path=%r is_addon=%s", config.base_path, config.is_addon)

    import app.renderer as r
    r._base_path = config.base_path

    watch_task = asyncio.create_task(
        _watch_dashboard_files(Path(config.config_dir), dashboards, sse)
    )
    heartbeat_task = asyncio.create_task(_heartbeat(sse))

    _rebuild_entity_filter(dashboards, sse)

    yield

    logger.info("Shutdown initiated — cancelling background tasks")

    watch_task.cancel()
    try:
        await watch_task
    except asyncio.CancelledError:
        pass

    heartbeat_task.cancel()
    try:
        await heartbeat_task
    except asyncio.CancelledError:
        pass

    ws_task.cancel()
    try:
        await ws_task
    except asyncio.CancelledError:
        pass

    await ha_client.disconnect()
    logger.info("Shutdown complete")

app = FastAPI(lifespan=lifespan, title="LightDash", version="0.1.0")

static_dir = APP_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

_no_cache = {"Cache-Control": "no-cache, no-store, must-revalidate"}


def _bp() -> str:
    bp = getattr(app.state, "base_path", "")
    if bp:
        import app.renderer as r
        if not r._via_ingress.get():
            return ""
    return bp


@app.middleware("http")
async def detect_ingress(request: Request, call_next):
    import app.renderer as r
    public_port = getattr(app.state, "public_port", "")
    via_ingress = True
    if public_port:
        host = request.headers.get("host", "")
        via_ingress = not host.endswith(f":{public_port}")
    r._via_ingress.set(via_ingress)
    response = await call_next(request)
    return response


@app.get("/", response_class=HTMLResponse)
async def root():
    bp = _bp()
    dashboards = getattr(app.state, "dashboards", {})

    items = ""
    if dashboards:
        for name, d in sorted(dashboards.items()):
            title = html.escape(d.title or name)
            url = html.escape(f"{bp}/d/{name}")
            items += f'<li><a href="{url}">{title}</a></li>\n'
    else:
        items = '<li class="empty">No dashboards yet. <a href="' + html.escape(f"{bp}/_config") + '">Add one</a>.</li>'

    return HTMLResponse(
        _TPL_DASHBOARD_LIST.substitute(
            css_link=_css_link(),
            sw_script=_SW_SCRIPT,
            items=items,
            config_url=html.escape(f"{bp}/_config"),
        ),
        headers=_no_cache,
    )

@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0

@app.get("/d/{name}")
async def dashboard_index(name: str):
    dashboard = app.state.dashboards.get(name)
    if not dashboard:
        return HTMLResponse(
            render_error(f"Dashboard '{name}' not found."),
            status_code=404,
            headers=_no_cache,
        )
    if not dashboard.views:
        return HTMLResponse("No views", status_code=404)
    first = dashboard.views[0]
    bp = _bp()
    url = f"{bp}/d/{name}/view/{first.path}" if bp else f"/d/{name}/view/{first.path}"
    return RedirectResponse(url=url, status_code=302)


@app.get("/d/{name}/view/{view_path:path}", response_class=HTMLResponse)
async def dashboard_view(name: str, view_path: str):
    if name == "_preview":
        preview = getattr(app.state, "preview_data", None)
        if not preview:
            return HTMLResponse(render_error("No preview available"), status_code=404, headers=_no_cache)
        dashboard = preview["dashboard"]
        cfg = getattr(app.state, "config", None)
        ha_url = preview.get("ha_url") or (cfg.ha_url if cfg else "")
        entity_icons = preview.get("entity_icons", {})
        entity_states = preview.get("entity_states", {})
        for v in dashboard.views:
            if v.path == view_path:
                return HTMLResponse(
                    render_view(v, dashboard, ha_url=ha_url, entity_icons=entity_icons, entity_states=entity_states, dashboard_name="_preview"),
                    headers=_no_cache,
                )
        return HTMLResponse(render_error(f"View '{view_path}' not found"), status_code=404, headers=_no_cache)

    dashboard = app.state.dashboards.get(name)
    if not dashboard:
        return HTMLResponse(
            render_error(f"Dashboard '{name}' not found."),
            status_code=404,
            headers=_no_cache,
        )

    cfg = getattr(app.state, "config", None)
    ha_url = cfg.ha_url if cfg else ""

    ha = getattr(app.state, "ha_client", None)
    entity_icons = {}
    entity_states = {}
    if ha and ha.is_connected:
        states = await ha.get_states()
        if states:
            entity_icons = {
                s["entity_id"]: s["attributes"].get("icon", "")
                for s in states if s["attributes"].get("icon")
            }
            entity_states = {s["entity_id"]: s for s in states}

    for v in dashboard.views:
        if v.path == view_path:
            return HTMLResponse(
                render_view(v, dashboard, ha_url=ha_url, entity_icons=entity_icons, entity_states=entity_states, dashboard_name=name),
                headers=_no_cache,
            )

    return HTMLResponse(
        render_error(f"View '{view_path}' not found in dashboard '{name}'."),
        status_code=404,
        headers=_no_cache,
    )


@app.get("/health")
async def health():
    ha = getattr(app.state, "ha_client", None)
    ha_ok = ha and ha.is_connected
    sse = getattr(app.state, "sse", None)
    ws_ok = sse and sse.connected
    dashboards = getattr(app.state, "dashboards", {})
    bp = _bp()
    return {
        "status": "ok",
        "ha_connected": ha_ok,
        "ha_websocket": ws_ok,
        "sse_clients": len(sse._clients) if sse else 0,
        "dashboards_loaded": len(dashboards),
        "dashboards": {
            name: f"{bp}/d/{name}"
            for name in dashboards
        },
    }


@app.post("/action")
async def handle_action(request: Request):
    raw = await request.body()
    logger.debug("Raw POST body: %s", raw)
    raw_str = raw.decode("utf-8", errors="replace")
    if raw_str.startswith("{"):
        data: Dict[str, Any] = json.loads(raw_str) if raw_str else {}
    elif raw_str:
        data = dict(urllib.parse.parse_qsl(raw_str))
    else:
        data = {}

    entity_id = data.get("entity_id", "")
    action_type = data.get("action", "toggle")
    service = data.get("service", "")
    target = data.get("target", {})
    if isinstance(target, str):
        try:
            target = json.loads(target) if target.strip() else {}
        except (json.JSONDecodeError, ValueError):
            target = {}

    action_data = data.get("data", {})
    if isinstance(action_data, str):
        try:
            action_data = json.loads(action_data) if action_data.strip() else {}
        except (json.JSONDecodeError, ValueError):
            action_data = {}

    logger.info("Action: entity=%s action=%s service=%s", entity_id, action_type, service)

    ha = getattr(app.state, "ha_client", None)

    if ha and ha.is_connected:
        if action_type == "toggle":
            if service:
                parts = service.split(".")
                if len(parts) == 2:
                    payload: Dict[str, Any] = {"entity_id": entity_id}
                    result = await ha.call_service(parts[0], parts[1], payload)
                    logger.info("Toggle result: %s", "success" if result is not None else "failed")

        elif action_type == "call-service":
            if service:
                parts = service.split(".")
                if len(parts) == 2:
                    payload = dict(target)
                    if entity_id and "entity_id" not in payload:
                        payload["entity_id"] = entity_id
                    payload.update(action_data)
                    result = await ha.call_service(parts[0], parts[1], payload)
                    logger.info("Service call result: %s", "success" if result is not None else "failed")
    else:
        logger.warning("HA not connected — cannot forward action")

    return HTMLResponse("<!-- action received -->")


@app.get("/_sse")
async def sse_stream(request: Request):
    sse = getattr(app.state, "sse", None)
    if not sse:
        return PlainTextResponse("SSE not available", status_code=503)

    q = sse.subscribe()

    async def event_generator():
        try:
            while True:
                msg = await q.get()
                yield msg
        except Exception:
            pass
        finally:
            sse.unsubscribe(q)

    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/states")
async def api_states():
    ha = getattr(app.state, "ha_client", None)
    if not ha or not ha.is_connected:
        return {"error": "HA not connected"}
    states = await ha.get_states()
    return states or []


@app.get("/api/state/{entity_id:path}")
async def api_state(entity_id: str):
    ha = getattr(app.state, "ha_client", None)
    if not ha or not ha.is_connected:
        return {"error": "HA not connected"}
    state = await ha.get_state(entity_id)
    return state or {"error": "not found"}


@app.get("/api/value/{entity_id:path}")
async def api_entity_value(entity_id: str):
    ha = getattr(app.state, "ha_client", None)
    if not ha or not ha.is_connected:
        return PlainTextResponse("--")
    try:
        state = await ha.get_state(entity_id)
    except Exception:
        state = None
    if not state or "state" not in state:
        return PlainTextResponse("?")
    val = state["state"]
    unit = state.get("attributes", {}).get("unit_of_measurement", "")
    display = f"{val} {unit}" if unit else str(val)
    return PlainTextResponse(display)


@app.get("/api/history/{entity_id:path}")
async def api_history(entity_id: str, hours: int = 24):
    ha = getattr(app.state, "ha_client", None)
    if not ha or not ha.is_connected:
        return {"error": "HA not connected"}
    history = await ha.get_history(entity_id, hours)
    return history or []


@app.get("/api/view/{dashboard}/{view_path}/badge/{idx}")
async def view_badge(dashboard: str, view_path: str, idx: int):
    dashboards = getattr(app.state, "dashboards", {})
    d = dashboards.get(dashboard)
    if not d:
        return HTMLResponse("", status_code=404)

    ha = getattr(app.state, "ha_client", None)
    entity_states = {}
    if ha and ha.is_connected:
        states = await ha.get_states()
        if states:
            entity_states = {s["entity_id"]: s for s in states}

    for v in d.views:
        if v.path == view_path:
            if idx < 0 or idx >= len(v.badges):
                return HTMLResponse("", status_code=404)
            badge = v.badges[idx]
            if badge.get("type") != "entity-filter":
                return HTMLResponse("", status_code=400)

            import app.renderer as r
            r._entity_states = entity_states
            html = r._render_entity_filter_badge(badge, idx, view_path)
            return HTMLResponse(html, headers=_no_cache)

    return HTMLResponse("", status_code=404)


@app.get("/ha/image/serve/{path:path}")
async def proxy_ha_image(path: str):
    config = getattr(app.state, "config", None)
    if not config or not config.ha_url:
        return PlainTextResponse("HA not configured", status_code=502)
    url = f"{config.ha_url.rstrip('/')}/api/image/serve/{path}"
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(url, headers={"Authorization": f"Bearer {config.ha_token}"})
            return Response(content=resp.content, media_type=resp.headers.get("content-type", "image/png"))
        except Exception as e:
            logger.warning("Image proxy error: %s", e)
            return PlainTextResponse("Image fetch failed", status_code=502)


# ── Config editor ──────────────────────────────────────────────────────────

_NEW_DASHBOARD_TEMPLATE = """\
title: {name}
views:
  - title: Home
    path: home
    icon: mdi:home
    sections:
      - cards:
          - type: tile
            entity: ""
"""


@app.get("/_config", response_class=HTMLResponse)
async def config_page():
    bp = _bp()
    cfg = getattr(app.state, "config", None)
    public_base = cfg.public_base if cfg and cfg.public_base else ""
    css_link = _css_link()

    return HTMLResponse(
        _TPL_CONFIG_PAGE.substitute(
            css_link=css_link,
            sw_script=_SW_SCRIPT,
            bp=bp,
            public_base=public_base,
        ),
        headers=_no_cache,
    )


@app.get("/_config/dashboards")
async def config_list():
    bp = _bp()
    dashboards = getattr(app.state, "dashboards", {})
    return [
        {
            "name": name,
            "title": d.title,
            "url": f"{bp}/d/{name}",
        }
        for name, d in sorted(dashboards.items())
    ]


@app.get("/_config/dashboards/{name}.yaml")
async def config_yaml(name: str):
    config = getattr(app.state, "config", None)
    is_addon = config.is_addon if config else False
    config_dir = config.config_dir if config else "config"
    data_dir = AppConfig._get_data_dir(is_addon, config_dir)
    file_path = data_dir / f"{name}.yaml"
    if not file_path.exists():
        return JSONResponse({"error": "Not found"}, status_code=404)
    return PlainTextResponse(file_path.read_text())


@app.post("/_config/dashboards")
async def config_create(req: Request):
    data = await req.json()
    name = data.get("name", "").strip()
    if not name or not name.replace("-", "").replace("_", "").isalnum():
        return JSONResponse({"error": "Invalid name"}, status_code=400)

    config = getattr(app.state, "config", None)
    is_addon = config.is_addon if config else False
    config_dir = config.config_dir if config else "config"

    data_dir = AppConfig._get_data_dir(is_addon, config_dir)
    file_path = data_dir / f"{name}.yaml"
    if file_path.exists():
        return JSONResponse({"error": f"Dashboard '{name}' already exists"}, status_code=409)

    yaml_text = _NEW_DASHBOARD_TEMPLATE.format(name=name)
    try:
        AppConfig.flush_dashboard_to_disk(name, yaml_text, is_addon, config_dir)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

    dashboards = getattr(app.state, "dashboards", {})
    parsed = parse_dashboard(yaml.safe_load(yaml_text))
    dashboards[name] = parsed
    sse = getattr(app.state, "sse", None)
    if sse:
        _rebuild_entity_filter(dashboards, sse)

    bp = _bp()
    return {
        "name": name,
        "title": parsed.title,
        "url": f"{bp}/d/{name}",
    }


@app.put("/_config/dashboards/{name}")
async def config_save(name: str, req: Request):
    data = await req.json()
    yaml_text = data.get("yaml", "").strip()
    if not yaml_text:
        return JSONResponse({"error": "Empty YAML content"}, status_code=400)

    config = getattr(app.state, "config", None)
    is_addon = config.is_addon if config else False
    config_dir = config.config_dir if config else "config"

    data_dir = AppConfig._get_data_dir(is_addon, config_dir)
    file_path = data_dir / f"{name}.yaml"
    if not file_path.exists():
        return JSONResponse({"error": f"Dashboard '{name}' not found"}, status_code=404)

    try:
        AppConfig.flush_dashboard_to_disk(name, yaml_text, is_addon, config_dir)
    except yaml.YAMLError as e:
        return JSONResponse({"error": f"YAML parse error: {e}"}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

    dashboards = getattr(app.state, "dashboards", {})
    raw = yaml.safe_load(yaml_text)
    parsed = parse_dashboard(raw)
    dashboards[name] = parsed
    scan_dashboard(parsed)
    sse = getattr(app.state, "sse", None)
    if sse:
        _rebuild_entity_filter(dashboards, sse)

    return {"ok": True, "title": parsed.title}


@app.delete("/_config/dashboards/{name}")
async def config_delete(name: str):
    config = getattr(app.state, "config", None)
    is_addon = config.is_addon if config else False
    config_dir = config.config_dir if config else "config"

    AppConfig.delete_dashboard_from_disk(name, is_addon, config_dir)

    dashboards = getattr(app.state, "dashboards", {})
    dashboards.pop(name, None)

    return {"ok": True}


@app.put("/_config/dashboards/{name}/rename")
async def config_rename(name: str, req: Request):
    data = await req.json()
    new_name = data.get("new_name", "").strip()
    if not new_name or not new_name.replace("-", "").replace("_", "").isalnum():
        return JSONResponse({"error": "Invalid name"}, status_code=400)

    config = getattr(app.state, "config", None)
    is_addon = config.is_addon if config else False
    config_dir = config.config_dir if config else "config"

    data_dir = AppConfig._get_data_dir(is_addon, config_dir)
    old_path = data_dir / f"{name}.yaml"
    new_path = data_dir / f"{new_name}.yaml"

    if not old_path.exists():
        return JSONResponse({"error": f"Dashboard '{name}' not found"}, status_code=404)
    if new_path.exists():
        return JSONResponse({"error": f"Dashboard '{new_name}' already exists"}, status_code=409)

    old_path.rename(new_path)

    dashboards = getattr(app.state, "dashboards", {})
    if name in dashboards:
        dashboards[new_name] = dashboards.pop(name)

    return {"ok": True, "name": new_name}


@app.post("/_config/preview", response_class=HTMLResponse)
async def config_preview(req: Request):
    data = await req.json()
    yaml_text = data.get("yaml", "").strip()
    if not yaml_text:
        return JSONResponse({"error": "Empty YAML"}, status_code=400)

    try:
        raw = yaml.safe_load(yaml_text)
        if raw is None:
            return JSONResponse({"error": "Empty YAML content"}, status_code=400)
        dashboard = parse_dashboard(raw)
    except yaml.YAMLError as e:
        return JSONResponse({"error": f"YAML parse error: {e}"}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

    if not dashboard.views:
        return JSONResponse({"error": "No views in dashboard"}, status_code=400)

    ha = getattr(app.state, "ha_client", None)
    entity_states = {}
    entity_icons = {}
    if ha and ha.is_connected:
        try:
            states = await ha.get_states()
            if states:
                entity_icons = {
                    s["entity_id"]: s["attributes"].get("icon", "")
                    for s in states if s["attributes"].get("icon")
                }
                entity_states = {s["entity_id"]: s for s in states}
        except Exception:
            pass

    cfg = getattr(app.state, "config", None)
    ha_url = cfg.ha_url if cfg else ""
    bp = _bp()

    app.state.preview_data = {
        "dashboard": dashboard,
        "entity_icons": entity_icons,
        "entity_states": entity_states,
        "ha_url": ha_url,
    }

    view = dashboard.views[0]
    html_out = render_view(view, dashboard, ha_url=ha_url, entity_icons=entity_icons, entity_states=entity_states, dashboard_name="_preview")

    pages = ''.join(
        f'<a href="{bp}/d/_preview/view/{html.escape(v.path)}" class="{"active" if v is view else ""}">{html.escape(v.title or v.path)}</a>'
        for v in dashboard.views
    )
    top_bar = f'<div style="display:flex;gap:8px;padding:6px 12px;background:#1a1a1a;border-bottom:1px solid #2a2a2a;font-size:0.85rem">{pages}</div>'

    return HTMLResponse(
        _TPL_PREVIEW.substitute(
            css_link=_css_link(dashboard.lightdash.theme),
            sw_script=_SW_SCRIPT,
            top_bar=top_bar,
            html_out=html_out,
        ),
        headers=_no_cache,
    )
