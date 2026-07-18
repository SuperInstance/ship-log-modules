# 🌊 Tide Predictor Module

NOAA tide predictions widget for ship-log-search. Real-time tide levels, 7-day forecasts, high/low predictions, and interactive tide curves for any NOAA tide station.

## Features

- **Live tide level** — current water height with rising/falling indicator
- **Next event countdown** — "Next High in 3h 24m" at a glance
- **Interactive tide curve** — Chart.js visualization, 1-day / 3-day / week views
- **High & Low predictions table** — all tide events for the selected date range
- **Station search** — find any NOAA tide station worldwide (6,000+ stations)
- **Quick stations** — Alaska, Pacific Northwest shortcuts (Sitka, Juneau, Kodiak, Seattle, etc.)
- **Offline cache** — 6-hour local cache for intermittent connectivity (critical for vessels)
- **Units** — Feet (primary) + meters (secondary), MLLW datum
- **Zero dependencies** — just an HTML file + Chart.js from CDN

## Installation

```bash
shiplog install tide-predictor
```

Or manual: copy `index.html` and `module.json` to your ship-log modules directory.

## Data Source

NOAA CO-OPS API (`api.tidesandcurrents.noaa.gov`). Official NOAA harmonic constant predictions. No API key required.

## Configuration

The widget works standalone. Default station is Sitka, AK (`9451600`).

Customize quick stations by editing the `QUICK_STATIONS` array in `index.html`:

```javascript
const QUICK_STATIONS = [
  { id: '9451600', name: 'Sitka, AK' },
  { id: '8454000', name: 'Providence, RI' },
  // ... add your local stations
];
```

Station selection persists in localStorage.

## Navigation Use

⚠️ **This widget is for supplemental planning only.** Always verify with official NOAA tide tables for navigation-critical decisions. The predictions use harmonic constants and don't account for real-time weather effects (storm surge, atmospheric pressure).

## API Reference

The widget calls two NOAA endpoints:

1. **Predictions (6-min intervals):** Smooth tide curve data
   ```
   api/prod/datagetter?product=predictions&interval=6&datum=MLLW
   ```

2. **High/Low predictions:** Tide event times
   ```
   api/prod/datagetter?product=predictions&interval=hilo&datum=MLLW
   ```

No authentication required. Rate limit: ~1 request/second ( NOAA public API).
