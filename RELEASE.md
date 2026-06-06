# Release Notes for v0.12.2 (2026-06-06)

This release fixes a layout regression where all card content was top-aligned instead of centered.

- **Fixed card alignment:** An overly broad CSS change in v0.12.0 accidentally switched every `align-items: center` rule to `flex-start`, causing entity rows, tiles, glance items, buttons, headings, toggles, dimmer modals, and clock cards to all shift their content to the top. Everything is back to centered now. The only rule that correctly stays at `flex-start` is `.weather-current` (the condition text needs top-alignment with the icon).

# Release Notes for v0.12.1 (2026-06-06)

This release adds comprehensive documentation for all features including the weather forecast card, long-press modals, and auto-timeout settings.

- **Full README docs:** The README now covers every supported card type including `weather-forecast`, all `lightdash` config options (theme, auto_revert_seconds, auto_close_modal_seconds), and detailed walkthroughs of the long-press dimmer and cover position modals.

# Release Notes for v0.12.0 (2026-06-06)

This release adds a long-press cover control modal and two auto-timeout settings for a more polished interactive experience.

- **Cover position modal:** Long-press any cover tile or entity row to open a position slider with dedicated open, stop, and close buttons. Drag the slider to set a precise position, or tap the arrow buttons for full open/close.
- **Auto-revert to home:** Set `auto_revert_seconds` under the `lightdash:` section to automatically return to the first dashboard view after a period of inactivity — perfect for wall-mounted tablets.
- **Auto-close modals:** Set `auto_close_modal_seconds` to automatically dismiss popup modals (dimmer, cover) after inactivity, keeping your dashboard clean.

# Release Notes for v0.11.0 (2026-06-05)

This release adds a weather forecast card so you can see current conditions and upcoming weather right on your dashboard.

- **Weather forecast card:** Add `type: weather-forecast` to any dashboard with a weather entity. Shows the current temperature, condition icon, and your choice of secondary info (high/low, precipitation, or humidity) alongside a scrollable forecast list.
- **Daily, hourly, or twice-daily:** Set `forecast_type` to control the forecast granularity. Daily shows weekday names and high/low ranges; hourly shows times and single temperatures.
- **Configurable forecast count:** Use `forecast_count` to limit how many forecast items appear — default is 5 for daily/twice-daily and 12 for hourly.
- **Temperature rounding:** Set `round_temperature: true` to round all displayed temperatures to whole numbers.
- **Auto-refresh:** Views with a weather card automatically refresh every 30 minutes so the forecast stays current without manual reloads.

# Release Notes for v0.10.17 (2026-06-04)

This release adds the ability to hide entity icons in entities cards for a cleaner, more compact look.

- **Hide entity icons:** Set `icon: none` on any entity item in an entities card and the icon disappears. The entity name and state naturally shift to the left edge for a compact, text-only row.

# Release Notes for v0.10.15 (2026-06-03)

This release adds better diagnostics for tracking down why the addon occasionally stops with no error logged.

- Added global exception handlers that catch crashes which previously went completely silent — if Python hits an unhandled exception anywhere, it will now be logged at CRITICAL level with full details.
- Added signal handlers for SIGTERM and SIGINT so the logs will show when the addon receives a shutdown signal from Home Assistant.
- The heartbeat now fires after 60 seconds (instead of 5 minutes) to capture an early memory and client-count snapshot before the potential death window.

# Release Notes for v0.10.16 (2026-06-04)

This release adds a long-press dimmer modal for light entities and a CSS theme system so you can style your dashboard to match your mood.

- **Light dimmer:** Long-press any light tile or entity row to open a brightness slider. Drag your finger up and down to adjust brightness — the value is sent to Home Assistant when you let go. Tap the light icon to toggle on/off (turning on restores the last brightness).
- **Dashboard themes:** You can now pick a visual style for each dashboard. Add `theme: name` under the `lightdash:` key in your dashboard YAML, where `name` is one of: `ha-dark` (default), `daylight`, `glass`, `hearth`, `ink`, `sage`, `soft`, `bauhaus`, or `terminal`. Each theme is a complete redesign — colours, fonts, spacing, and control styles all change together.
