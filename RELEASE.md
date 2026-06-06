# Release Notes for v0.12.2 (2026-06-06)

Lots of new features have landed! Here's what's new:

- **Weather forecast card:** Add a `type: weather-forecast` card to any dashboard and see current conditions plus upcoming weather. Choose daily (shows weekday, icon, and high/low range), hourly (shows time, icon, and temperature), or twice-daily. You can pick what shows under the current temperature — high/low, precipitation, or humidity — and limit how many forecast items appear.
- **Forecast from a separate sensor:** Some weather integrations (like Pirate Weather) don't put forecast data in the entity itself. You can point `forecast_entity` at a template sensor that does have forecast data, while the main `entity` still drives current conditions.
- **Light dimmer on long-press:** Hold your finger on any light tile or light entity row and a brightness slider pops up. Drag up or down to set brightness — your finger lifts and it's sent to Home Assistant. Tap the light icon to switch on or off (turning back on remembers your last brightness).
- **Cover position on long-press:** Hold your finger on any cover tile or cover entity row and a position slider appears, alongside dedicated open, stop, and close buttons. Drag to any position, or tap the arrow buttons for full open or close.
- **Auto-revert to home screen:** Set `auto_revert_seconds` under the `lightdash:` section and your dashboard will automatically return to the first view after a period of inactivity — perfect for wall-mounted tablets that should always show the main screen.
- **Auto-close popups:** Set `auto_close_modal_seconds` and the dimmer and cover modals will dismiss themselves after a few seconds of inactivity, keeping your display clean.
- **Pick a theme:** Add `theme: name` under `lightdash:` to choose from 10 visual styles — `ha-dark`, `daylight`, `glass`, `hearth`, `ink`, `sage`, `soft`, `bauhaus`, `terminal`, or the base `style`. Everything changes together: colours, fonts, spacing, and control styles.
- **Hide entity icons:** Set `icon: none` on any entity row in an entities card and the icon disappears — the name and state shift left for a clean, compact, text-only look.
- **Accessibility improvements:** Weather condition names and cover control buttons now have proper `aria-label` attributes for screen readers.
