# Release Notes for v0.10.15 (2026-06-03)

This release adds better diagnostics for tracking down why the addon occasionally stops with no error logged.

- Added global exception handlers that catch crashes which previously went completely silent — if Python hits an unhandled exception anywhere, it will now be logged at CRITICAL level with full details.
- Added signal handlers for SIGTERM and SIGINT so the logs will show when the addon receives a shutdown signal from Home Assistant.
- The heartbeat now fires after 60 seconds (instead of 5 minutes) to capture an early memory and client-count snapshot before the potential death window.

# Release Notes for v0.10.16 (2026-06-04)

This release adds a long-press dimmer modal for light entities and a CSS theme system so you can style your dashboard to match your mood.

- **Light dimmer:** Long-press any light tile or entity row to open a brightness slider. Drag your finger up and down to adjust brightness — the value is sent to Home Assistant when you let go. Tap the light icon to toggle on/off (turning on restores the last brightness).
- **Dashboard themes:** You can now pick a visual style for each dashboard. Add `theme: name` under the `lightdash:` key in your dashboard YAML, where `name` is one of: `ha-dark` (default), `daylight`, `glass`, `hearth`, `ink`, `sage`, `soft`, `bauhaus`, or `terminal`. Each theme is a complete redesign — colours, fonts, spacing, and control styles all change together.
