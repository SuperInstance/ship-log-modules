# map-view — Ship Log Map Widget

Interactive Leaflet map showing ship-log-search entries as colored, clustered
pins on dark tiles. Mobile-first, designed for use at sea on a phone.

## Features

- Full-screen Leaflet map with **CartoDB DarkMatter** tiles
- Pins colored by category (catch, maintenance, weather, observation, navigation)
- Pin glyphs use category emoji for instant recognition
- Click a pin → popup with category, relative + absolute timestamp, full text,
  and metadata (coordinates, depth, speed, species when available)
- **Marker clustering** (Leaflet.markercluster) — spiderfies on max zoom
- **Filter sidebar** with:
  - Live text search
  - Category toggles with per-category counts
  - Date range (from / to)
- **"Use my position"** floating button — uses geolocation, drops a "you are
  here" marker with accuracy circle, and recenters the map
- **Auto-refresh every 60s** with a live countdown in the header
- **Offline cache** — falls back to the last-good localStorage snapshot when
  the network fails at sea
- **Auto-pause** polling when the tab is hidden (saves battery)

## Configuration

Override defaults before the script runs:

```html
<script>
  window.SHIPLOG_CONFIG = {
    apiBase:        "https://my-worker.example.workers.dev",
    refreshSeconds: 120,
    defaultZoom:    6,
  };
</script>
```

Or via query string: `?api=https://my-worker.example.workers.dev`.

## API contract

The widget talks to the same-origin (or `apiBase`) ship-log-search Worker:

| Endpoint                    | Used for                |
| --------------------------- | ----------------------- |
| `GET /api/timeline?k=N`     | Initial load + refresh  |
| `GET /api/nearby?lat&lon&r` | (reserved for v0.2)     |
| `GET /api/search?q`         | (reserved for v0.2)     |
| `GET /api/stats`            | (reserved for v0.2)     |

Entries can be a top-level JSON array **or** `{ entries: [...] }` /
`{ items: [...] }` / `{ results: [...] }`. Each entry should provide:

```json
{
  "category":  "catch | maintenance | weather | observation | navigation",
  "text":      "Tuna school at the rip, 6 keepers",
  "timestamp": "2026-07-18T01:23:00Z",
  "lat":       33.760,
  "lon":       -118.215,
  "species":   "yellowfin",
  "depth":     120,
  "speed":     4.5
}
```

`text`/`body`/`message` are all accepted for the body. `lon`/`lng` both work.
Entries without finite `lat`/`lon` are silently skipped.

## Sea-friendly UX details

- 48 px minimum tap targets throughout
- `touch-action: manipulation` to suppress 300 ms double-tap delay
- Dark UI with high-contrast accents — readable in sunlight, easy on night watch
- Viewport-fit cover with safe-area insets (notched phones, gesture bars)
- Big close button on popups (36 px)
- Reduced-motion respect
- Filters slide-in sidebar on desktop, full overlay on phones
- Floating locate-me button sits above the status bar, doesn't fight the map

## Install

Either:

```bash
shiplog install map-view
```

Or copy `index.html` and `module.json` into `modules/map-view/` of your
ship-log-search Worker.

## License

MIT