# Release Notes for v0.10.15 (2026-06-03)

This release adds better diagnostics for tracking down why the addon occasionally stops with no error logged.

- Added global exception handlers that catch crashes which previously went completely silent — if Python hits an unhandled exception anywhere, it will now be logged at CRITICAL level with full details.
- Added signal handlers for SIGTERM and SIGINT so the logs will show when the addon receives a shutdown signal from Home Assistant.
- The heartbeat now fires after 60 seconds (instead of 5 minutes) to capture an early memory and client-count snapshot before the potential death window.
