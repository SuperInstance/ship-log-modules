# fuel-tracker — Ship Log Fuel Widget

A drop-in fuel tracking tab for the **ship-log-search** modular system. Logs
fuel-ups, calculates burn rate and nautical miles per gallon, projects range
from the current tank level, and visualizes cost trends — all from one
stand-alone HTML file.

## What it does

- **Log fill-ups** — date, gallons, price/gallon, location, engine hours, notes
- **Tank level gauge** — set capacity and current gallons; turns red below 20 %
- **Automatic efficiency calc** — uses delta of engine hours between fills to
  compute **GPH** (gallons / hour) and **NMPG** (nautical miles / gallon) when
  distance is recorded
- **Range estimate** — current gallons × NMPG; falls back to
  `gallons / GPH × avg speed` if no distance data yet
- **Cost tracking** — total spent, $/nm, $/hr, plus trend chart for
  price/gallon over time
- **Two charts** (Chart.js from CDN):
  - Fuel consumption (gallons per fill + GPH line)
  - Cost trend (price/gallon + trip cost)
- **Dark maritime theme** — amber accent, salt-spray-readable, sunlight-safe
- **Responsive** — works on nav-computer screens, iPads, phones at the helm
- **Offline-capable** — every save hits localStorage immediately and queues to
  ship-log-search when the network comes back
- **Stand-alone** — single `index.html`, no build step, no bundler

## Install

### Via the ship-log installer

```bash
shiplog install fuel-tracker
```

### Manual

Copy the directory into your ship-log-search Worker's `modules/` folder:

```bash
cp -r ship-log-modules/fuel-tracker /path/to/worker/modules/
```

Then add to your ship-log config (it shows up as a new **⛽ Fuel** tab).

### Stand-alone

The HTML file works by itself. Open `index.html` directly in a browser —
it runs in **local-only mode** until you point it at your ship-log-search API
in Settings.

## Configuration

Override the API base via:

**Query string** (handy for testing):

```
index.html?api=https://my-ship-log.workers.dev
```

**Or** before the script loads:

```html
<script>
  window.SHIPLOG_CONFIG = {
    apiBase: "https://my-ship-log.workers.dev"
  };
</script>
```

**Or** in the in-app **⚙ Settings** panel (persisted in localStorage).

### Settings panel

| Setting         | Default | What it does                                  |
| --------------- | ------- | --------------------------------------------- |
| Tank capacity   | 100 gal | Used for the gauge % and range estimate       |
| Current gallons | 0       | Manually update after each fill-up            |
| Units           | gallons | Display only — entries are stored in gallons  |
| Currency symbol | `$`     | Prefix for all money displays                 |
| API base URL    | —       | ship-log-search Worker root                   |
| Avg speed (kt)  | 6       | Fallback for range when NMPG is unknown       |

## API contract

The widget talks to the ship-log-search Worker. The entries it writes use
`category: "fuel"`, so they coexist cleanly with catches, weather, etc.

### Create

```
POST /api/log
Content-Type: application/json

{
  "category":         "fuel",
  "timestamp":        "2026-07-18T04:33:00.000Z",
  "gallons":           48.20,
  "unit":              "gallons",
  "price_per_gallon":  4.59,
  "total_cost":        221.24,
  "engine_hours":      1234.5,
  "trip_hours":        18.2,
  "distance_nm":       0,
  "location":          "Marina del Rey fuel dock",
  "lat":               33.9802,
  "lon":              -118.4514,
  "notes":             "Topped off, replaced fuel filter"
}
```

### List

```
GET /api/logs?category=fuel&limit=500
```

Returns an array (or `{ entries: [...] }` / `{ items: [...] }` /
`{ results: [...] }` — all are accepted).

### Delete (best-effort)

```
DELETE /api/log?id=<entry-id>
```

The widget gracefully tolerates servers that don't implement DELETE — the
local copy is removed either way.

## How calculations work

The widget assumes the only reliable signal between fill-ups is the engine
hours reading (read from the boat's hour meter, J1939 bus, Signal K, or read
off the gauge). For each new fill-up it computes:

```
trip_hours   = current.engineHours − previous.engineHours
gph          = gallons_added / trip_hours
nmpg         = distance_nm / gallons_added          (only if distance recorded)
```

- **Range** uses `current_gallons × nmpg` if you have NMPG, otherwise
  `current_gallons / gph × avg_speed_knots`.
- **Cost / nm** is `total_cost / total_distance_nm` across all entries.
- **Cost / hr** is `total_cost / total_trip_hours` across all entries.

If you want better distance tracking, log the start and end position of each
trip as separate `category: "navigation"` entries and the host app can
back-fill `distance_nm` into the fuel entry. (Or fill it in manually.)

## Offline behavior

Every save:

1. Writes to `localStorage` immediately and renders in the list (marked
   with a `queued` badge).
2. Attempts `POST /api/log`.
3. On failure → moves to the offline queue (`localStorage` key
   `shiplog.fuel.queue`).
4. On next page load, or whenever the browser comes back online, the queue is
   drained automatically.

A green dot in the header means synced; amber = queued; red = offline.

## Data export / import

Use **⚙ Settings → Export JSON** to download every entry + your settings as
a single file. **Import JSON** merges entries (de-duped by timestamp + gallons)
without overwriting existing data. Good for backup, migration, or sharing
efficiency stats with another vessel.

## Files

```
fuel-tracker/
├── module.json     Manifest consumed by ship-log installer / host UI
├── index.html      The widget (self-contained, ~50 KB)
└── README.md       This file
```

## Dependencies

- [Chart.js 4.4.1](https://www.chartjs.org/) — loaded from jsDelivr CDN, pinned
  for cacheability. Can be self-hosted by editing the `<script src>` tag.
- Nothing else. No bundler, no framework, no build step.

## Sea-friendly UX details

- 48 px minimum tap targets throughout
- `touch-action: manipulation` to suppress 300 ms double-tap delay
- Safe-area insets for notched phones and gesture bars
- Big numeric displays — readable in sunlight, easy on night watch
- Reduced-motion respect
- All numbers tabular-nums aligned
- Inputs use `inputmode="decimal"` so phones show the right keyboard

## License

MIT