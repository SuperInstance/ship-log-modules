# 🧭 Trip Planner Module

Plan fishing trips with waypoints, travel time estimates, fuel calculations, crew assignments, and pre-departure checklists.

## Features

- **Waypoint routing** — add waypoints with lat/lon, automatic distance calculation between them
- **Travel time estimation** — input cruising speed, get ETA for each leg and total trip
- **Fuel estimation** — approximate fuel needs based on distance (configurable MPG)
- **Crew management** — assign crew members for the trip
- **Pre-departure checklist** — 10-item default safety checklist, customizable
- **Export trip plan** — download as text file for filing a float plan
- **Distance calculations** — haversine formula, nautical miles
- **Offline-first** — all data in localStorage, no connection needed
- **Persist trips** — save and recall trip plans

## Default Checklist

1. Check weather forecast
2. File float plan
3. Test VHF radio
4. Check fuel level
5. Inspect hull and through-hulls
6. Test bilge pumps
7. Check life jackets and PFDs
8. Verify flares and emergency kit
9. Check engine oil and coolant
10. Test navigation lights

## Installation

```bash
shiplog install trip-planner
```

## Distance & Speed

- Uses the haversine formula for great-circle distance
- Results in nautical miles
- Per-waypoint speed adjustment (default 8 knots)
- Fuel estimate assumes 3 nm/gallon (adjustable in code)
