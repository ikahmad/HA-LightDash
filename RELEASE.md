# Release Notes for v0.14.0 (2026-06-06)

Badges add compact context-aware controls to the top of any view — entity state at a glance, quick navigation, and conditional pills that appear and disappear based on what's happening in your home.

- **Entity badges:** Add `type: entity` badges to any view and see the entity icon, name, and live state in a compact pill. Tap a light, switch, or binary sensor badge to toggle it on or off — state updates arrive in real time.
- **Shortcut badges:** `type: shortcut` badges let you navigate to another view or open an external URL with a single tap. Perfect for quick links between dashboards or jumping to your Home Assistant frontend.
- **Entity-filter badges:** `type: entity-filter` badges only show when their conditions are met — for example, a "Roof open" badge that appears only when `cover.kitchen_roof` is in the `open` state. The badge re-evaluates via SSE so it appears and disappears dynamically.
- **Badges in example configs:** `living_room.yaml` now has entity badges for the porch and entryway lights plus a shortcut to "Other Rooms". `kitchen.yaml` has entity badges for kitchen lights and a filter badge for the roof.

---

# Release Notes for v0.13.4 (2026-06-06)

Favourite brightness shortcuts let you tap preset values in the dimmer and cover modals, so you don't always have to drag the slider.

- **Favourite values for light and cover:** You can now set `favourite_values` under `lightdash:` on any light tile, cover tile, or entity row — for example `[25, 50, 75, 100]`. Up to 4 values, each between 0 and 100. When you long-press to open the dimmer or cover modal, your presets appear as tap-able buttons on the left side. Tap one and the brightness or position is set immediately.
- **Browser JS syntax error fixed:** The generated JavaScript had a brace/paren ordering issue in the favourite-buttons code, causing `Uncaught SyntaxError: Unexpected token ')'` in the browser console and preventing the modals from working. Closing brackets are now in the correct order.

---

# Release Notes for v0.13.3 (2026-06-06)

Light and cover long-press modals now work with mouse clicks, making them testable on desktop browsers without touch emulation.

- **Mouse support for long-press modals:** The light dimmer and cover position modals now respond to `mousedown`/`mousemove`/`mouseup` events alongside the existing touch events. Hold-click on any light tile or cover tile to open the modal, then drag the slider with your mouse. This makes testing possible with browser automation tools like Playwright without enabling touch emulation.

---

# Release Notes for v0.13.2 (2026-06-06)

Clock auto-sizing gets more precise with percentage control and keeps text fitted as time ticks.

- **Fit-text with fine-tuning:** `clock_size: fit` and `date_fontsize: fit` now accept a percentage suffix like `"fit 75%"` — auto-sizes text to fill the card width, then scales down to the specified percentage. Perfect when full-width is too wide.
- **Text stays fitted as clock ticks:** The auto-sizing recalibrates every time the clock updates, so the time and date always fill the available width — even when the text length changes (e.g., seconds appearing).

---

# Release Notes for v0.13.1 (2026-06-06)

Clock cards are more flexible with resizable text and an optional date line.

- **Clock size control:** `clock_size` now accepts percentage strings like `"150%"` to scale the time text, or `"fit"` to auto-size text to fill the card width — alongside the existing `small`, `medium`, and `large`.
- **Date line on clock cards:** Set `date_show: true` under a `lightdash` subsection to show the current date below the time. Choose between `default` (long date), `iso` (YYYY-MM-DD), or `locale` (localised short date). The date has its own `date_fontsize` option, so the time and date can size independently.
- **Button cards for service calls:** The `button` card works without an `entity` field — perfect for triggering arbitrary HA services with `tap_action`, `target`, and `data`.

---

# Release Notes for v0.12.4 (2026-06-06)

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
