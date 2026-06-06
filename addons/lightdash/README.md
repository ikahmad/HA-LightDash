A lightweight, self-contained dashboard renderer for Home Assistant. Instead of running HA's full Lovelace frontend, which is a struggle for low-power devices such as NSPanels and older Android tablets, LightDash is a focused alternative: support for tiles and built-in entities, intelligent mapping of some common custom cards to lightweight alternatives, and plain HTML + CSS with much of the interactivity shifted to the addon itself.

I orignally built LightDash to run on the NSPanel Pro in-wall touchscreens I have around my house, which are getting increasingly slow as the HA team add more dashboard capabilities. Wonderful for iPads, desktop browsing and recent smartphones, but almost unusable on the devices that sit in the gap between ESPHome and modern browsers.

LightDash is designed to handle copy-and-pasted YAML from existing dashboards with _minimal_ (not quite zero) adjustment - there's an edit-and-preview web UI accessible from the addon control panel, where you can tweak the YAML and see the results immediately before saving.

**Caveat 1:** I've focused on the cards I use in my own small-screen dashboards. I'd love for contributors to add support for their own layouts!

**Caveat 2:** Yep, I used OpenCode to build a lot of this. I'm a 25+ year software architect and developer, but this is a one-day project. I'm pretty happy it's not filled with slop - I've reviewed it and it's passable - but I make no warranties about code quality this early in its life.

![LightDash](https://github.com/richkershaw/HA-LightDash/raw/main/example-images/example-lightdash.png)

---

## Badges

Badges are compact pills that sit above the cards in a view. They show entity state at a glance, navigate between views, or conditionally appear based on entity state.

Three badge types are supported:

### Entity badge

Shows an entity's icon, name, and live state. For binary entities (lights, switches, etc.), tapping the badge toggles the entity on/off. State updates arrive in real time via Server-Sent Events.

```yaml
badges:
  - type: entity
    entity: light.porch
    name: Porch
  - type: entity
    entity: sensor.temperature
```

### Shortcut badge

Shows an icon and label. Tapping navigates to another view or opens a URL.

```yaml
badges:
  - type: shortcut
    icon: mdi:arrow-right-bold
    label: Other Rooms
    tap_action:
      action: navigate
      navigation_path: other-rooms
  - type: shortcut
    label: HA
    tap_action:
      action: url
      url_path: http://ha.local:8123
```

### Entity-filter badge

Shows only when certain entity/state conditions are met (evaluated at render time). When an SSE event arrives for the badge's entity, HTMX re-fetches the badge HTML from the server so it can appear or disappear dynamically.

```yaml
badges:
  - type: entity-filter
    entity: cover.kitchen_roof
    name: Roof open
    conditions:
      - entity: cover.kitchen_roof
        state: open
```

Conditions use AND logic — all must match for the badge to show. Omit `conditions` to always show the badge (behaves like an entity badge but without the live state span).

![Badges](https://github.com/richkershaw/HA-LightDash/raw/main/example-images/example-badges.png)

## Feature Previews

![Clock](https://github.com/richkershaw/HA-LightDash/raw/main/example-images/example-clock.png)

![Weather card](https://github.com/richkershaw/HA-LightDash/raw/main/example-images/example-weather.png)

![Dimmer modal](https://github.com/richkershaw/HA-LightDash/raw/main/example-images/example-modal.png)

![Favourite values](https://github.com/richkershaw/HA-LightDash/raw/main/example-images/example-popup-favourites.png)

![Themes](https://github.com/richkershaw/HA-LightDash/raw/main/example-images/readme-themes.png)
