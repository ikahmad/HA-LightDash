# Release Notes for v0.10.12 (2026-06-03)

This release updates LightDash to improve reliability, fix bugs that could cause the addon to restart for no apparent reason, and adds privacy-first logging and diagnostic options to help with troubleshooting.

- **No more mysterious restarts.** We found that a development-mode file watcher was triggering restarts inside the addon — it's been removed, so LightDash will stay running.
- **Live state updates stay connected.** If the WebSocket to Home Assistant drops, the addon now automatically reconnects and keeps your dashboards in sync.
- **Faster recovery after network blips.** LightDash will now try to reconnect much more aggressively (up to 20 seconds instead of 2 minutes).
- **Clear shutdown logs.** You can see in the logs whether the addon shut down gracefully or was killed.
- **Log timestamps on every line.** Every log message now includes a timestamp, making it much easier to figure out what happened when.
- **Configurable log level.** A new dropdown in the addon config lets you choose how chatty the logs are — DEBUG, INFO, WARNING, or ERROR. It defaults to WARNING so logs are quiet day-to-day, but you can dial up when troubleshooting.
- **Optional crash reporting** — off by default. There's a new toggle in the addon config labelled "Send error logs back to developer for diagnostics". If you're asked to share diagnostics while troubleshooting, you can turn it on, reproduce the problem, and the crash details will be sent automatically.
