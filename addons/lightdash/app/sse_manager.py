from __future__ import annotations

import asyncio
import html
import json
import logging
import random
from typing import Any, Callable, Dict, Optional, Set

logger = logging.getLogger(__name__)


MAX_QUEUE = 256


class SSEManager:
    def __init__(self):
        self._clients: Set[asyncio.Queue] = set()
        self.allowed_entities: Set[str] = set()
        self.connected = False

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=MAX_QUEUE)
        self._clients.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        self._clients.discard(q)

    def broadcast(self, event: str, data: Any):
        payload = f"event: {event}\ndata: {json.dumps(data)}\n\n"
        dead: list[asyncio.Queue] = []
        for q in self._clients:
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                dead.append(q)
        for q in dead:
            self.unsubscribe(q)

    def notify_entity(self, entity_id: str, state: dict):
        value = state.get("state", "")
        unit = state.get("attributes", {}).get("unit_of_measurement", "")
        display = f"{value} {unit}" if unit else str(value)
        event_name = f"entity_{entity_id.replace('.', '_')}"
        payload = f"event: {event_name}\ndata: {html.escape(str(display))}\n\n"
        logger.info("SSE notify: event=%s data=%s", event_name, display)
        dead: list[asyncio.Queue] = []
        for q in self._clients:
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                dead.append(q)
        for q in dead:
            self.unsubscribe(q)


class HAWebSocket:
    def __init__(
        self,
        ha_url: str,
        ha_token: str,
        sse: SSEManager,
        on_weather_change: Optional[Callable[[str], None]] = None,
    ):
        self.ha_url = ha_url
        self.ha_token = ha_token
        self.sse = sse
        self.on_weather_change = on_weather_change
        self.connected = False
        self._ws: Any = None
        self._msg_id = 0
        self._pending: Dict[int, asyncio.Future] = {}
        self._run_task: Optional[asyncio.Task] = None

    async def call_service(
        self,
        domain: str,
        service: str,
        data: Dict[str, Any],
        *,
        return_response: bool = False,
        target: Optional[Dict[str, Any]] = None,
    ) -> Any:
        if not self.connected or self._ws is None:
            raise ConnectionError("WebSocket not connected")
        self._msg_id += 1
        msg_id = self._msg_id
        future: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending[msg_id] = future
        msg: Dict[str, Any] = {
            "id": msg_id,
            "type": "call_service",
            "domain": domain,
            "service": service,
            "service_data": data,
        }
        if return_response:
            msg["return_response"] = True
        if target:
            msg["target"] = target
        await self._ws.send(json.dumps(msg))
        try:
            return await asyncio.wait_for(future, timeout=30)
        except asyncio.TimeoutError:
            self._pending.pop(msg_id, None)
            raise TimeoutError(
                f"WebSocket call_service {domain}.{service} timed out"
            )

    def _dispatch(self, data: dict) -> None:
        if data.get("type") == "result":
            msg_id = data.get("id", 0)
            if not isinstance(msg_id, int):
                return
            future = self._pending.pop(msg_id, None)
            if future and not future.done():
                if data.get("success"):
                    future.set_result(data.get("result", {}))
                else:
                    err = data.get("error", {})
                    future.set_exception(
                        Exception(err.get("message", "Unknown error"))
                    )
            return

        if data.get("type") != "event":
            return

        event = data.get("event", {})
        if event.get("event_type") != "state_changed":
            return

        event_data = event.get("data", {})
        entity_id = event_data.get("entity_id", "")
        new_state = event_data.get("new_state", {})
        if not entity_id or not new_state:
            return

        if self.sse.allowed_entities and entity_id not in self.sse.allowed_entities:
            return

        self.sse.notify_entity(entity_id, new_state)

        if entity_id.startswith("weather.") and self.on_weather_change:
            try:
                self.on_weather_change(entity_id)
            except Exception:
                logger.exception("Weather change callback failed for %s", entity_id)

    async def _fail_pending(self, exc: Exception) -> None:
        pending = self._pending
        self._pending = {}
        for future in pending.values():
            if not future.done():
                future.set_exception(exc)

    async def run(self) -> None:
        if not self.ha_url or not self.ha_token:
            logger.info("HA not configured — skipping WebSocket listener")
            return

        import ssl
        import time

        import websockets

        logger.info("HA WebSocket listener started")

        ws_url = (
            self.ha_url.replace("http://", "ws://")
            .replace("https://", "wss://")
            .strip("/")
        )
        ws_url = f"{ws_url}/api/websocket"
        logger.info("WebSocket target: %s", ws_url)

        use_ssl = self.ha_url.startswith("https://")
        ctx = None
        if use_ssl:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        delay = 5.0
        max_delay = 20.0

        while True:
            try:
                async with websockets.connect(
                    ws_url, ssl=ctx if use_ssl else None
                ) as ws:
                    msg = json.loads(await ws.recv())
                    auth_msg = {"type": "auth", "access_token": self.ha_token}
                    await ws.send(json.dumps(auth_msg))
                    auth_resp = json.loads(await ws.recv())
                    if auth_resp.get("type") != "auth_ok":
                        logger.error(
                            "HA WebSocket auth failed: %s — giving up", auth_resp
                        )
                        return

                    logger.info("HA WebSocket connected")
                    self.connected = True
                    self._ws = ws
                    delay = 5.0

                    self._msg_id += 1
                    await ws.send(
                        json.dumps(
                            {
                                "id": self._msg_id,
                                "type": "subscribe_events",
                                "event_type": "state_changed",
                            }
                        )
                    )
                    sub_resp = json.loads(await ws.recv())
                    if sub_resp.get("success"):
                        logger.info("Subscribed to HA state changes")
                    else:
                        logger.warning(
                            "HA state subscription failed: %s", sub_resp
                        )
                        return

                    last_msg = time.monotonic()
                    async for message in ws:
                        last_msg = time.monotonic()
                        data = json.loads(message)
                        self._dispatch(data)

            except asyncio.CancelledError:
                logger.info("HA WebSocket listener cancelled")
                self.connected = False
                self._ws = None
                await self._fail_pending(
                    Exception("WebSocket cancelled")
                )
                return
            except websockets.exceptions.InvalidStatus as e:
                logger.warning(
                    "HA WebSocket rejected: %s (reconnecting in %ds)",
                    e,
                    round(delay),
                )
            except Exception as e:
                logger.warning(
                    "HA WebSocket error: %s (reconnecting in %ds)",
                    e,
                    round(delay),
                )
            finally:
                self.connected = False
                self._ws = None
                await self._fail_pending(
                    ConnectionError("WebSocket disconnected")
                )

            await asyncio.sleep(delay)
            delay = min(delay * 1.5 + random.uniform(0, delay * 0.25), max_delay)

    def start(self) -> asyncio.Task:
        self._run_task = asyncio.create_task(self._run_forever())
        return self._run_task

    async def _run_forever(self) -> None:
        delay = 1.0
        while True:
            try:
                await self.run()
            except asyncio.CancelledError:
                logger.info("WebSocket manager cancelled — exiting")
                raise
            except Exception:
                logger.exception("WebSocket listener crashed unexpectedly")
            else:
                logger.warning("WebSocket listener stopped unexpectedly")
            logger.info("Restarting WebSocket listener in %.1fs", delay)
            await asyncio.sleep(delay)
            delay = min(delay * 2, 30.0)

    async def stop(self) -> None:
        if self._run_task:
            self._run_task.cancel()
            try:
                await self._run_task
            except asyncio.CancelledError:
                pass
            self._run_task = None
