# Ship Log Module System

## What This Is

Ship-log-search is built as a core Worker with a pluggable module system. Modules are optional add-ons that extend functionality. Anyone can write one. Install only what you need.

## Module Types

### 1. Widget Modules (frontend)
Drop-in HTML+JS snippets that add tabs, panels, or overlays to the ship-log UI.
Examples: Map view, catch analytics, weather overlay, photo gallery.

### 2. Data Source Modules (backend)
Scripts or Workers that feed data INTO ship-log-search via the API.
Examples: Signal K bridge, AIS receiver, weather station, engine monitor.

### 3. Export Modules
Convert ship-log data to other formats.
Examples: CSV export, PDF report, NOAA logbook format, Excel.

### 4. Integration Modules
Connect ship-log-search to external systems.
Examples: Multi-vessel sync, OpenCPN plugin, Home Assistant, email reports.

## Module Manifest

Every module ships a `module.json`:

```json
{
  "name": "map-view",
  "version": "0.1.0",
  "type": "widget",
  "description": "Interactive Leaflet map showing log entries as pins",
  "author": "SuperInstance",
  "homepage": "https://github.com/SuperInstance/ship-log-map",
  "config": {
    "tab": { "label": "🗺️ Map", "icon": "🗺️" },
    "scripts": ["leaflet.js"],
    "styles": ["leaflet.css"]
  },
  "requires": {
    "ship-log-search": ">=0.2.0"
  },
  "permissions": ["read:logs"]
}
```

## Installation

```bash
# Install a module
shiplog install map-view

# List installed modules
shiplog modules

# Remove a module
shiplog remove map-view
```

Or manual: copy module files to `/modules/<name>/` and add to config.

## Module Discovery

Browse available modules at the Module Registry Worker:
`https://module-registry.casey-digennaro.workers.dev/`

## Writing Your Own Module

1. Create a directory: `modules/my-module/`
2. Add `module.json` manifest
3. Add your code (HTML/JS for widgets, Python/JS for data sources)
4. Test locally: `wrangler dev`
5. Publish: push to GitHub, submit to registry

### Widget Module Example

```javascript
// modules/weather-overlay/widget.js
export function init(api) {
  // api provides: query(), onLog(), getPosition()
  const panel = api.addTab('Weather', '🌦️');

  api.onLog((entry) => {
    if (entry.category === 'weather') {
      panel.appendChild(renderWeather(entry));
    }
  });
}
```

## Available Modules

| Module | Type | Status | Description |
|--------|------|--------|-------------|
| map-view | widget | ✅ built | Leaflet map with entry pins |
| catch-analytics | widget | ✅ built | Charts: catch by species/date/ground |
| export-csv | export | ✅ built | Export filtered entries to CSV |
| ais-tracker | data source | ✅ built | Auto-log nearby AIS contacts |
| weather-feed | data source | ✅ built | NOAA weather forecast ingestion |
| engine-hours | widget | ✅ built | Track engine hours and maintenance intervals |
| photo-log | widget | planned | R2 photo attachments on entries |
| noaa-logbook | export | planned | Export to NOAA compliance format |
| multi-vessel | integration | planned | Shared index with vessel_id |
| opencpn-sync | integration | planned | Two-way sync with OpenCPN waypoints |
