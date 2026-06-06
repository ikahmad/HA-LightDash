# Changelog

## v0.13.0 (2026-06-06)
- **Added:** `fontsize` clock card option — accepts a percentage string (`"150%"`, `"80%"`) to scale the time text, or `"fit"` to auto-size text to fill the card width
- **Added:** `date_show` clock card option — shows the current date below the time
- **Added:** `date_format` clock card option — `default` (toDateString), `iso` (toISOString date-only), or `locale` (toLocaleDateString)
- **Added:** `date_fontsize` clock card option — same behaviour as `fontsize`, applied to the date line
- **Added:** Automatic `scripts.js` inclusion and `icey_textFit()` initialisation when any clock card uses `fontsize: fit` or `date_fontsize: fit`

## v0.12.4 (2026-06-06)
- **Fixed:** YAML editor inserted tab characters for indentation instead of spaces, causing parsing errors. Editor now uses 4-space indentation with `indentWithTabs: false`, and pasted content has tabs automatically converted to spaces.

## v0.12.2 (2026-06-06)
- **Fixed:** Broad `align-items: flex-start` replacement in v0.12.0 accidentally changed all CSS flex containers from `center` to `flex-start` — entities, tiles, glance, button, heading, dimmer, and clock cards all had their content top-aligned instead of centered. Reverted all to `center` except the intended `.weather-current` rule.

## v0.12.1 (2026-06-06)
- **Added:** `README.md` documentation for weather-forecast card, cover/light long-press modals, auto-revert and auto-close modal config options, theme support, and architecture notes

## v0.12.0 (2026-06-06)
- **Added:** `auto_revert_seconds` lightdash config option — automatically returns to the first dashboard view after a period of inactivity
- **Added:** `auto_close_modal_seconds` lightdash config option — automatically closes popup modals (dimmer and cover) after a period of inactivity
- **Added:** Long-press cover modal — long-press any cover tile or entity row to open a position slider with open/stop/close buttons alongside
- **Added:** `data-cover-entity` attribute on cover tile cards and entity rows for long-press targeting
- **Added:** `_view_needs_cover_modal()` helper for conditional cover modal injection
- **Added:** Cover modal CSS across all 10 theme files
- **Changed:** Dimmer modal now also respects `auto_close_modal_seconds` — resets the auto-close timer on slider drag, close button, and backdrop tap
- **Changed:** Cover inline control buttons (`cover-btn`) class no longer conflicts with modal buttons — test assertion tightened

## v0.11.0 (2026-06-05)
- **Added:** `weather-forecast` card type — displays current weather conditions (condition icon, temperature, extrema/precipitation/humidity) and forecast list (daily/hourly/twice_daily) from any HA `weather` entity
- **Added:** `forecast_count` config option — limits how many forecast items appear (default 5 daily / 12 hourly)
- **Added:** `round_temperature` config option — rounds all displayed temperatures to integers
- **Added:** `secondary_info_attribute` config option — controls what shows under the current temp (extrema / precipitation / humidity)
- **Added:** Views containing a weather card auto-refresh every 30 minutes via `<meta http-equiv="refresh">` to pick up updated forecast data
- **Added:** Weather condition icon mapping (15 HA condition strings → MDI icons) across all 10 theme CSS files
- **Added:** `_view_needs_weather_refresh()` helper for conditional meta refresh injection
- **Changed:** Version bump to 0.11.0 (minor feature release)

## v0.10.17 (2026-06-04)
- **Added:** `icon: none` support on entity items in entities cards — hides the icon, name/state align left naturally (no -offset needed)
- **Added:** `.entity-row.no-icon` CSS class across all 10 theme files for theme-level styling hooks

## v0.10.16 (2026-06-04)
- **Added:** Long-press dimmer modal on light entity tiles and entity rows — vertical brightness slider, icon tap toggles on/off, shows entity name and current brightness percent
- **Added:** CSS theme system — new `lightdash.theme` key in dashboard YAML selects a theme CSS file (default `ha-dark`); themes are drop-in replacements sharing identical class structure
- **Added:** 9 built-in themes: ha-dark, daylight, glass, hearth, ink, sage, soft, bauhaus, terminal
- **Changed:** `render_view_index()` signature updated to accept `Dashboard` object for theme-aware rendering
- **Changed:** Default CSS file is now `ha-dark.css` (was `style.css`)
- **Changed:** Dimmer modal — on/off button removed, icon click toggles instead (reduces modal height)
- **Changed:** Dimmer modal — spacing tightened (12px padding, 10px gap), track widened to 88px
- **Fixed:** `_url()` HTML escaping in dimmer JS — Python string concatenation no longer produces raw `_url(` literal in output
- **Fixed:** Dimmer JS runs inside `DOMContentLoaded` to avoid null element references from head-early execution

## v0.10.15 (2026-06-03)
- **Added:** Global exception handlers – `sys.excepthook` and asyncio loop exception handler (log at CRITICAL, catches crashes that would otherwise go silent)
- **Added:** Signal handlers for SIGTERM/SIGINT/SIGHUP — log signal receipt at WARNING
- **Changed:** Heartbeat first interval decreased from 300s to 60s for early memory capture

## v0.10.14 (2026-06-03)
- **Fixed:** OOM crash from unbounded SSE queues — each client queue capped at 256 messages, slow/disconnected clients dropped automatically
- **Added:** Periodic heartbeat log (every 5 min) with RSS, uptime, and SSE client count to detect memory growth before OOM

## v0.10.13 (2026-06-03)
- **Changed:** `RELEASE.md` consolidated — single section per release, no per-commit-version grouping; user-facing only

## v0.10.12 (2026-06-03)
- **Added:** Configurable error diagnostics toggle ("Send error logs back to developer for diagnostics") — addon config checkbox, defaults to off
- **Changed:** Sentry SDK init moved into `lifespan` so it reads configuration before activating
- **Added:** Translations entry for `diagnostics` config key

## v0.10.11 (2026-06-03)
- **Added:** Configurable log level via addon config dropdown (`log_level` — `DEBUG|INFO|WARNING|ERROR`, default `WARNING`)
- **Fixed:** Timestamp format now consistently applied to all loggers including uvicorn's own output
- **Fixed:** `app.sse_manager` no longer pinned to INFO — respects root log level

## v0.10.10 (2026-06-03)
- **Added:** `RELEASE.md` — user-friendly summary of changes since last release for populating release notes
- **Changed:** `AGENTS.md` updated to require `RELEASE.md` maintenance with each version bump

## v0.10.9 (2026-06-03)
- **Added:** Timestamps to all console log output — lines now prefixed with `2026-06-03 12:34:56` for easier chrono-debugging

## v0.10.8 (2026-06-03)
- **Fixed:** App crash/stop with no error in logs — removed uvicorn `--reload` flag (was silently restarting when Python wrote `__pycache__` files)
- **Fixed:** WebSocket events silently stop syncing — background listener now restarts on any unexpected exit
- **Added:** Process-exit logging and shutdown lifecycle logs to distinguish graceful shutdown from hard kill
- **Changed:** Max WebSocket reconnect delay reduced from 120s to 20s — faster recovery after network blips
- **Changed:** Health check grace period increased (20s start, 5 retries) for slower HA hardware

## v0.10.5 – v0.10.7 (2026-06-03)
- **Added:** Sentry error tracking — unhandled exceptions and crashes now capture stack traces automatically for both local dev and addon deployments

## v0.10.4 (2026-05-31)
- **Fixed:** External state changes (HA toggles) not updating the UI — SSE
  extension's `swap()` was silently a no-op because the entity-state span
  inherited `hx-swap="none"` from its parent `.entity-row` (needed for toggle
  actions). Fixed by always setting `hx-swap="innerHTML"` on every entity-state
  span, overriding ancestor inheritance.

## v0.10.3 (2026-05-31)
- **Fixed:** External state changes (e.g. toggling a light from HA directly) not
  reflected in frontend — `htmx:sseMessage` handler was reading
  `e.detail.elt` (always `undefined` because the detail is a raw SSE
  `MessageEvent`, not an HTMX event with an `elt` property). Changed to
  `e.target`, which is the element the event was dispatched on (the entity-state
  span).
- **Fixed:** `st()` moved before the guard in `htmx:sseMessage` handler so
  toggle sync runs even if the event target isn't an entity-state span.
- **Fixed:** Same `e.detail.elt` → `e.target` fix in the slider sync
  `htmx:sseMessage` handler (`ss()` function).

## v0.10.2 (2026-05-31)
- **Fixed:** Tile cards with `hide_state: true` (e.g. Porch, Entryway) showing no
  visual state change when toggled — always render hidden entity-state span for
  binary entities so SSE events have a DOM target for icon recoloring.
- **Fixed:** Click handler no longer returns early when toggle switch is absent
  (guard relaxed from `if(!t||!s)return` to `if(!s)return`).
- **Fixed:** `st()` function now toggles `entity-on`/`entity-off` classes even
  when no toggle switch is present, via `if(s)` guard.

## v0.10.1 (2026-05-31)
- **Fixed:** Clock function renamed from `uc()` to `uclk()` to avoid overwriting
  the icon color interpolation function `uc(s)` at global scope.

## v0.10.0 (2026-05-31)
- **Added:** Icon color interpolation — entity card icons now show an amber glow
  when on and dim grey when off, with smooth brightness-aware transitions.
- **Added:** `_icon_color_for_state()` server-side helper and `uc(s)` client-side
  function for real-time color updates via SSE.

## v0.9.2 (2026-05-31)
- **Added:** Diagnostic startup logs in `main.py` and `sse_manager.py`.
- **Changed:** SSE notify log promoted from DEBUG to INFO for operational
  observability.
- **Changed:** File-watcher poll interval increased from 2s to 10s.

## v0.9.1 (2026-05-31)
- **Fixed:** Toggle switches not syncing with entity state on initial page load
  after inline rendering change — `st()` now also runs on `DOMContentLoaded`.

## v0.9.0 (2026-05-31)
- **Optimization:** Removed `pydantic` and `python-dotenv` dependencies — smaller
  container, faster pip install, less memory at runtime.
- **Optimization:** Entity state values now rendered inline during page generation
  instead of 1 HTTP request per entity on page load — eliminates N round-trips
  per dashboard render.
- **Optimization:** Icon SVG cache capped at 200 entries — prevents unbounded
  memory growth across many dashboards.
- **Optimization:** Dashboard file watcher reduced from 2s to 10s polling —
  fewer filesystem hits on SD card storage.
- **Resilience:** HA WebSocket reconnection uses exponential backoff (5s → 120s)
  with random jitter — avoids thundering-herd on supervisor recovery.
- **Resilience:** HA WebSocket auth failures stop retrying instead of spinning
  forever against a hopeless connection.
- **Resilience:** Health endpoint now exposes WebSocket status and active SSE
  client count for easier monitoring.

## v0.8.1 (2026-05-29)
- **Fixed:** Clock cards displaying `--:--` after switching views — the update
  function now runs on every HTMX content swap, not just on page load.

## v0.8.0 (2026-05-29)
- **Experiment:** Tested moving inline HTML/JS into Jinja2 templates, but found it was
  far too slow for lower-CPU Home Assistant devices like the HA Yellow, and reverted to
  the less-clean but much higher performing approach retained, albeit with some flow improvements.

## v0.7.2 (2026-05-29)
- **Optimistic toggle updates** — switches now flip instantly when clicked, no
  waiting for confirmation from Home Assistant. The server confirms silently in
  the background and corrects if needed.
- **Loading pulse animation** — tiles, toggles, sliders, and buttons glow with a
  subtle blue pulse while the command is being sent to Home Assistant if the request takes 
  more than a second or so. Provides visual feedback during the round-trip.

## v0.7.1 (2026-05-29)
- **Fixed:** Inline feature layout for number entities — the up/value/down
  controls now sit flush to the right of the tile name as intended, rather than
  floating in the middle with extra padding.

## v0.7.0 (2026-05-29)
- **Fixed:** Dashboard file watching during startup (the `watch_task` coroutine
  was referenced but never created, preventing clean shutdown).
- **Fixed:** Route handlers no longer crash when escaping HTML output.
- **Added:** `markupsafe` to dependencies.
