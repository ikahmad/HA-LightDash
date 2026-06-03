# Release Notes

User-friendly summary of changes since the last release, written for end-users
(not developers). Use this to populate release notes.

## v0.10.12 (2026-06-03)

Privacy and configuration improvements.

- Added a toggle in the addon config labelled "Send error logs back to developer for diagnostics" — off by default. Turn it on if asked to share crash data while troubleshooting.
- Sentry crash reporting now reads the config before activating, so the toggle is respected immediately on restart.

---

## v0.10.11 (2026-06-03)

Logging improvements.

- Added a log level dropdown to the addon config (DEBUG / INFO / WARNING / ERROR). Defaults to WARNING so logs are quieter day-to-day, but you can dial up to INFO or DEBUG when troubleshooting.
- All log lines now consistently show timestamps, including uvicorn's own startup messages.

---

## v0.10.10 (2026-06-03)

Internal release infrastructure — no user-facing changes.

---

## v0.10.9 (2026-06-03)

Better log readability.

- All log messages now include a timestamp so it's clear when events happened when sharing logs.

---

## v0.10.8 (2026-06-03)

Reliability improvements and better recovery after network issues.

- Fixed mysterious app restarts — removed a development-mode file watcher that could trigger restarts for no apparent reason.
- Fixed WebSocket connection drops — the addon now automatically reconnects and keeps live state updates flowing, even after network blips.
- Added clear log messages when the addon shuts down gracefully vs. being killed.
- Faster reconnection after network issues (up to 20s max delay instead of 2 minutes).

---

## v0.10.5 – v0.10.7 (2026-06-03)

Behind-the-scenes error tracking.

- Added crash reporting so that if something goes wrong, error details are captured automatically to help diagnose issues.
