# Release Notes

This file contains a user-friendly summary of changes since the last release,
written for end-users (not developers). Use this to populate release notes.

## v0.10.12 (2026-06-03)

**Privacy-first error reporting.** You can now choose whether to send error logs to the developer for diagnostics. Head to the LightDash addon configuration page in Home Assistant — there's a new checkbox labelled *"Send error logs back to developer for diagnostics"*. It's off by default. If you're asked to share diagnostics while troubleshooting an issue, you can turn it on and reproduce the problem.

---

**You can now control log verbosity.** Head to the LightDash addon configuration page in Home Assistant to choose from DEBUG, INFO, WARNING, or ERROR. Defaults to WARNING — less noise in your addon logs, but you can dial up to INFO or DEBUG when troubleshooting.

**Better log consistency.** All log lines from LightDash now include timestamps, even uvicorn's own startup messages and access logs — no more guessing when something happened.

---

## v0.10.9 (2026-06-03)

**Better log readability.** All log messages now include a timestamp so if you need to share logs for troubleshooting, it's clear when events happened.

---

## v0.10.8 (2026-06-03)

**More stable, better recovery.** This release fixes two reliability issues:

- **No more mysterious restarts.** The app was using a development-mode file watcher that could trigger a restart for no apparent reason — this has been removed for the addon build, so it'll stay running.
- **Live updates keep working.** If the WebSocket connection to Home Assistant drops, the addon now automatically reconnects and restarts the event stream. Previously it could silently stop syncing state changes.
- **Better shutdown logging.** If the addon does stop, there are now clear log entries showing whether it shut down gracefully or was killed.
- **Faster reconnect.** After a network blip, the app will try to reconnect more aggressively (up to 20s max delay instead of 2 minutes).

---

## v0.10.5 – v0.10.7 (2026-06-03)

**Behind-the-scenes error tracking.** Added Sentry crash reporting so that if something goes wrong, the error details are captured automatically. This helps diagnose issues without needing to reproduce them.
