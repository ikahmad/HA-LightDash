# Release Notes

User-facing summary of changes since the last release. One section per actual
release to `main` — everything that changed, consolidated.

## v0.10.12 (2026-06-03)

Reliability, logging, and privacy improvements.

- **No more mysterious restarts.** Removed a development-mode file watcher that was triggering restarts in the addon.
- **Live state updates stay connected.** If the WebSocket to Home Assistant drops, the addon now automatically reconnects.
- **Faster recovery after network blips.** Max reconnect delay reduced from 2 minutes to 20 seconds.
- **Clear shutdown logs.** You can now see whether the addon shut down gracefully or was killed.
- **Log timestamps on every line.** All log messages include a timestamp, including uvicorn's own startup messages.
- **Configurable log level.** Choose DEBUG, INFO, WARNING, or ERROR in the addon config — defaults to WARNING.
- **Optional crash reporting.** New toggle in addon config labelled "Send error logs back to developer for diagnostics" — off by default. Turn it on if asked to share crash data while troubleshooting.
