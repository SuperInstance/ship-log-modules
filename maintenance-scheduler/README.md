# 🔧 Maintenance Scheduler Module

Vessel maintenance tracking with engine-hour-based and calendar-based task scheduling. Never miss an oil change, zinc replacement, or haul-out again.

## Features

- **Engine hours tracker** — manually input or auto-updated from Signal K bridge
- **Task types** — oil change, zinc, engine, haul-out, inspection, safety, custom
- **Dual intervals** — track by engine hours AND/OR calendar days
- **Visual progress bars** — see how close each task is to needing service
- **Status badges** — OK / DUE SOON / OVERDUE at a glance
- **One-tap completion** — log a completed task with current engine hours
- **Maintenance history** — all completed tasks with dates and hours
- **Default tasks seeded** — oil change (100hrs/365d), zincs (365d), haul-out (730d), etc.
- **Offline-first** — all data in localStorage, works with no connection
- **Syncs with engine-hours module** — listens for engine hour updates

## Default Tasks (auto-seeded)

| Task | Interval | Type |
|------|----------|------|
| Engine Oil Change | 100 hrs / 365 days | 🛢️ Oil |
| Transmission Fluid | 250 hrs / 730 days | 🔧 Engine |
| Hull Zinc Replacement | 365 days | ⚙️ Zinc |
| Haul-out & Bottom Paint | 730 days | 🚢 Haul-out |
| Safety Equipment Check | 90 days | 🦺 Safety |
| Prop Shaft Inspection | 180 days | 🔍 Inspection |

## Installation

```bash
shiplog install maintenance-scheduler
```

## Integration

- **Signal K bridge** — set `maint_engine_hours` in localStorage to auto-update
- **Engine hours module** — shares the same localStorage key
- **Ship log API** — completed tasks can optionally POST to the logbook

## Data Storage

All data stored in browser localStorage:
- `maint_tasks` — task definitions and last-completed state
- `maint_engine_hours` — current engine hours
- `maint_history` — completion log (last 100 entries)
