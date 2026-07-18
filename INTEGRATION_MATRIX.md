# 🔌 Vessel Ecosystem Integration Matrix

> *A technical document showing how every module connects to every other module — data flows, shared localStorage keys, API endpoints, dependencies, and the integration points for the gamification layer.*

> **Audience:** Engineers implementing or auditing the ship-log-modules ecosystem.
> **Goal:** Make it possible to verify that every module is wired correctly, every shared key is honored, and every gamification hook fires.

---

## Table of Contents

1. [Module Inventory](#1-module-inventory)
2. [Dependency Graph](#2-dependency-graph)
3. [Data Flow Diagrams](#3-data-flow-diagrams)
4. [Shared localStorage Schema](#4-shared-localstorage-schema)
5. [API Endpoint Map](#5-api-endpoint-map)
6. [The Gamification Layer (vessel-quest + fishcoin-ledger)](#6-the-gamification-layer)
7. [Category & Event Taxonomy](#7-category--event-taxonomy)
8. [Event Bus Contract](#8-event-bus-contract)
9. [Integration Verification Checklist](#9-integration-verification-checklist)
10. [Known Integration Tensions](#10-known-integration-tensions)

---

## 1. Module Inventory

The vessel ecosystem currently consists of **twelve modules**, grouped by type per `MODULE_SPEC.md`.

### 1.1 Core / Widget Modules (6)

| Module | Status | Entry | Purpose |
|--------|:------:|-------|---------|
| `crew-logbook` | ✅ built | `index.html` | Shared crew log with role + watch tagging |
| `map-view` | ✅ built | `index.html` | Leaflet map with categorized pins + clustering |
| `fuel-tracker` | ✅ built | `index.html` | Fuel fill-up log, NMPG, range, cost charts |
| `maintenance-scheduler` | ✅ built | `index.html` | Task scheduling by engine-hours + calendar |
| `trip-planner` | ✅ built | `index.html` | Waypoint routing, fuel estimate, checklist |
| `tide-predictor` | ✅ built | `index.html` | NOAA tide forecasts + station search |

### 1.2 Data Source Modules (3)

| Module | Status | Entry | Purpose |
|--------|:------:|-------|---------|
| `weather-feed` | ✅ built | `weather-feed.py` | NOAA weather forecast ingestion (6-hour cadence) |
| `ais-tracker` | ✅ built | `ais-tracker.py` + `ais-simulator.py` | Signal K WebSocket → AIS contact/departure events |
| `engine-hours` | ✅ built | `engine-hours.py` | Engine-hour reading source (Signal K or manual) |

### 1.3 Export Modules (1)

| Module | Status | Entry | Purpose |
|--------|:------:|-------|---------|
| `export-csv` | ✅ built | `export.py` | Filtered entry export to CSV |

### 1.4 Integration Modules (1)

| Module | Status | Entry | Purpose |
|--------|:------:|-------|---------|
| `fishcoin-ledger` | ✅ built | `fishcoin.py` | Tokenized crew economy (FishCoin earn/spend/redemption) |

### 1.5 Gamification Widget (1)

| Module | Status | Entry | Purpose |
|--------|:------:|-------|---------|
| `vessel-quest` | ✅ built | `index.html` | XP, ranks, achievements, streaks, leaderboards, chains, events, hidden mechanics |

### 1.6 Planned Modules (per `MODULE_SPEC.md`)

- `photo-log` (widget) — R2 photo attachments on entries
- `noaa-logbook` (export) — NOAA compliance format export
- `multi-vessel` (integration) — Shared index with `vessel_id`
- `opencpn-sync` (integration) — Two-way sync with OpenCPN waypoints
- `catch-analytics` (widget) — Charts: catch by species/date/ground (referenced in `VESSEL_EXPERIENCE.md` as a daily-use tab; treat as **planned or already partially implemented** — engineer should verify)

> **Integration caveat:** The `VESSEL_EXPERIENCE.md` narrative references `catch-analytics` heavily. If it is not yet implemented in the same shape, either build it as a thin pass-through over `crew-logbook` (filter by `category === 'catch'`, group by species/date/ground, render charts) or defer the catch-analytics references in the experience doc until it ships.

---

## 2. Dependency Graph

The arrows below mean "reads from" or "depends on the data shape of." Every widget ultimately reads from the same shared log API (`/api/log`, `/api/logs`).

```
                         ┌────────────────────────┐
                         │   ship-log-search      │
                         │   (core Worker)        │
                         │   SQLite (logs table)  │
                         └──────────┬─────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
            ▼                       ▼                       ▼
    ┌──────────────┐        ┌──────────────┐       ┌────────────────┐
    │ crew-logbook │        │  map-view    │       │  export-csv    │
    │  (widget)    │        │  (widget)    │       │  (export)      │
    └──────┬───────┘        └──────────────┘       └────────────────┘
           │                       ▲
           │ writes log entries    │ reads all categories
           │ to localStorage       │
           ▼                       │
    ┌──────────────────────────────┴────────┐
    │           gamification loop          │
    │   ┌──────────────┐   ┌────────────┐  │
    │   │ vessel-quest │◀──│  shared    │  │
    │   │  (widget)    │   │  events    │  │
    │   └──────┬───────┘   └────────────┘  │
    │          │                            │
    │          │ triggers coin earn/spend   │
    │          ▼                            │
    │   ┌──────────────────┐               │
    │   │ fishcoin-ledger  │               │
    │   │  (integration)   │               │
    │   └──────────────────┘               │
    └───────────────────────────────────────┘
                ▲                       ▲
                │ reads category        │ reads fuel
                │ "maintenance"         │ entries for
                │                       │ range estimates
        ┌───────┴────────┐      ┌───────┴────────┐
        │ maintenance-   │      │  fuel-tracker  │
        │ scheduler      │      │  (widget)      │
        └────────┬───────┘      └────────────────┘
                 │
                 │ writes/reads
                 │ maint_engine_hours
                 │
                 ▼
         ┌──────────────┐
         │ engine-hours │
         │  (data src)  │
         └──────────────┘


        ┌─────────────────┐        ┌──────────────────┐
        │   trip-planner  │◀──────▶│   tide-predictor │
        │   (widget)      │ tide   │   (widget)       │
        │                 │ windows│                  │
        └─────────────────┘        └──────────────────┘

        ┌─────────────────┐        ┌──────────────────┐
        │  weather-feed   │        │   ais-tracker    │
        │  (data src)     │        │   (data src)     │
        │  POST /api/log  │        │  POST /api/log   │
        └─────────────────┘        └──────────────────┘
                  │                        │
                  └────────┬───────────────┘
                           ▼
                    ship-log-search
```

### 2.1 Module Dependency Matrix

A module in row **R** depends on a module in column **C** if R needs C's data shape, key, or endpoint.

| ↓ Reader / Source → | crew-logbook | map-view | fuel-tracker | maintenance | trip-planner | tide-predictor | engine-hours | weather-feed | ais-tracker | export-csv | vessel-quest | fishcoin-ledger |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **crew-logbook** | — | | | | | | | | | | ✓ (reads `vessel_quest_state`) | ✓ (logs earns) |
| **map-view** | | — | | | | | | | | | | |
| **fuel-tracker** | | | — | ✓ (range uses engine hours) | | | ✓ | | | | | |
| **maintenance-scheduler** | | | | — | | | ✓ (writes `maint_engine_hours`) | | | | | | |
| **trip-planner** | | | ✓ (range check) | | — | ✓ (tide windows) | | | | | | |
| **tide-predictor** | | | | | | — | | | | | | |
| **engine-hours** | | | | ✓ (`maint_engine_hours`) | | | — | | | | | |
| **weather-feed** | | | | | | | | — | | | | |
| **ais-tracker** | | | | | | | | | — | | | |
| **export-csv** | ✓ | ✓ | ✓ | ✓ | ✓ | | | ✓ | ✓ | — | | |
| **vessel-quest** | ✓ (primary) | | ✓ | ✓ | ✓ | | ✓ | ✓ | ✓ | | — | ✓ (reads ledger for leaderboard) |
| **fishcoin-ledger** | ✓ (reads for `distribute`) | | ✓ | ✓ | ✓ | | | | | | ✓ (inverse — quest may trigger ledger write) | — |

### 2.2 Hard Dependencies (blockers if missing)

| Consumer | Required Source | Reason |
|---|---|---|
| `vessel-quest` | `crew-logbook` | Primary log feed for XP and achievements |
| `vessel-quest` | `maintenance-scheduler` | Maintenance completion XP |
| `fishcoin-ledger` | `crew-logbook` (or API equivalent) | `distribute` reads today's logs |
| `maintenance-scheduler` | `engine-hours` | Hours feed "due" calculation |
| `trip-planner` (range warning) | `fuel-tracker` | Tank level + NMPG for range check |
| `map-view` | any log-producing module | All pins come from `category` field |

### 2.3 Soft Dependencies (graceful degradation)

| Consumer | Optional Source | Degradation |
|---|---|---|
| `map-view` | `crew-logbook` (live refresh) | Falls back to `localStorage["shiplog.map.entries"]` cache |
| `fuel-tracker` | network → API | Queues to `shiplog.fuel.queue` and retries |
| `vessel-quest` | `weather-feed`, `ais-tracker` | Achievements for storms/AIS contacts never fire |
| `fishcoin-ledger` | `crew-logbook` | `distribute` returns "no entries" — captain can still award manually |

---

## 3. Data Flow Diagrams

The diagrams below show **data flow**, not call flow. Arrows indicate where data ends up, not necessarily where the request originates.

### 3.1 Master Data Flow

```
┌─────────────────────────── VESSEL DATA SOURCES ───────────────────────────┐
│                                                                          │
│   captain/mate/engineer      weather-feed       ais-tracker    engine-hrs│
│         │                         │                  │              │   │
│         │ POST /api/log           │ POST /api/log    │ POST /api/log│   │
│         │ (category=…)            │ (weather)        │ (ais-…)      │   │
│         ▼                         ▼                  ▼              │   │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    ship-log-search Worker                       │   │
│   │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │   │
│   │  │ /api/log POST  │  │ SQLite         │  │ /api/logs GET  │    │   │
│   │  │ + /api/timeline│  │ logs table     │  │ + /api/search  │    │   │
│   │  │ + /api/nearby  │  │ (id, ts, cat,  │  │ + /api/stats   │    │   │
│   │  │ + /api/stats   │  │  text, lat,lon,│  │ + /api/nearby  │    │   │
│   │  └────────────────┘  │  meta(json),…) │  └────────────────┘    │   │
│   │          │            └────────┬───────┘          │             │   │
│   │          │                     │                  │             │   │
│   │          │    write-through to localStorage        │             │   │
│   │          │     (per-module cacheKey)               │             │   │
│   └──────────┼─────────────────────┼──────────────────┼─────────────┘   │
│              │                     │                  │                 │
└──────────────┼─────────────────────┼──────────────────┼─────────────────┘
               │                     │                  │
               ▼                     ▼                  ▼
       ┌──────────────────┐  ┌───────────────┐  ┌────────────────────┐
       │ crew-logbook UI  │  │   map-view    │  │ fuel-tracker /     │
       │ (offline-first   │  │ (pins from    │  │ maintenance /       │
       │  localStorage    │  │  category     │  │ vessel-quest /     │
       │  `crew_logbook`) │  │  filter)      │  │ fishcoin-ledger     │
       └────────┬─────────┘  └───────────────┘  └─────────┬──────────┘
                │                                          │
                │     every entry passes through:         │
                │     ┌──────────────────────────┐         │
                └────▶│   EVENT BUS              │◀────────┘
                      │   (window.dispatchEvent) │
                      └─────────────┬────────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                ▼                   ▼                   ▼
       ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐
       │  vessel-quest   │  │  fishcoin-ledger│  │   catch-analytics│
       │  (XP, lvl, achv)│  │  (coin ledger)  │  │   (rollups,      │
       │                 │  │                 │  │    charts)       │
       └────────┬────────┘  └────────┬────────┘  └──────────────────┘
                │                    │
                │ quest unlocks     │ perk redemption
                │ → coin earn       │ (manual / captain)
                ▼                    ▼
       ┌────────────────────────────────────────────┐
       │  crew_profile_card, leaderboard, dashboard │
       └────────────────────────────────────────────┘
```

### 3.2 Per-Action Data Flow

For each category of log entry, what flows where:

```
CATEGORY: "catch"
─────────────────
src:    crew-logbook (form)
post:   POST /api/log { category: "catch", species, weight, lat, lon, text }
        ↓
store:  SQLite logs table
        ↓ (cache)
        localStorage["crew_logbook"] (entry appended)
        ↓
        localStorage["shiplog.map.entries"] (pin added)
        ↓
fanout: vessel-quest → +30 XP, achievement checks (catch_*, species_*)
        fishcoin-ledger → +15 🐟 (catch_report reward)
        catch-analytics → species diversity, ground heatmap update
        map-view → green catch pin at lat/lon

CATEGORY: "maintenance"
──────────────────────
src:    maintenance-scheduler (task complete button)
post:   POST /api/log { category: "maintenance", task_id, hours_at_completion }
        ↓
store:  SQLite logs table
        ↓
        localStorage["maint_history"] (append)
        localStorage["maint_tasks"] (mark complete, reset due-date)
        ↓
fanout: vessel-quest → +50 XP, +30 XP if early-completion, role multipliers
        fishcoin-ledger → +25 🐟 (maintenance reward)
        engine-hours → reads "hours_at_completion"

CATEGORY: "weather"
───────────────────
src:    weather-feed.py (cron, 6-hour) OR captain manual
post:   POST /api/log { category: "weather", beaufort, wind, pressure, text }
        ↓
store:  SQLite logs table
        ↓
fanout: vessel-quest → +10 XP, storm achievement checks (weather_*)
        map-view → blue weather pin
        seasonal events → storm bonus triggers

CATEGORY: "fuel"
────────────────
src:    fuel-tracker (form)
post:   POST /api/log { category: "fuel", gallons, price_per_gallon, … }
        ↓
store:  SQLite logs table
        ↓
        localStorage["shiplog.fuel.entries"] (append, triggers NMPG compute)
        localStorage["shiplog.fuel.queue"] (if offline, until drain)
        ↓
fanout: vessel-quest → +15 XP
        fishcoin-ledger → +10 🐟
        trip-planner → reads `shiplog.fuel.entries` for range estimate

CATEGORY: "navigation" / "observation"
──────────────────────────────────────
src:    crew-logbook (free-text or waypoint form)
post:   POST /api/log { category: "navigation"|"observation", text, lat, lon }
        ↓
store:  SQLite logs table
        ↓
fanout: vessel-quest → +10 XP base, hidden mechanic checks (easter eggs)
        map-view → purple navigation pin / grey observation pin

CATEGORY: "ais-contact" / "ais-departure"
─────────────────────────────────────────
src:    ais-tracker.py (Signal K WebSocket)
post:   POST /api/log { category: "ais-contact", vessel_name, mmsi, … }
        ↓
store:  SQLite logs table
        ↓
fanout: vessel-quest → +10 XP, AIS-related achievements
        map-view → grey AIS pin
        oracle-relay → WebSocket broadcast

CATEGORY: "trip_complete"
─────────────────────────
src:    trip-planner (post-trip submit)
post:   POST /api/log { category: "trip_complete", trip_id, waypoints, … }
        ↓
store:  SQLite logs table
        ↓
fanout: vessel-quest → +100 XP, distance achievement checks (dist_*)
        fishcoin-ledger → +20 🐟 (trip_plan reward) + +100 🐟 bonus
        catch-analytics → trip-level rollup
        map-view → trip trail overlay
```

### 3.3 Cross-Module Read Patterns

Which modules read from which others' state:

| Reading Module | Reads From | Key / Endpoint | Purpose |
|---|---|---|---|
| `vessel-quest` | `crew-logbook` | `localStorage["crew_logbook"]` | Entry count, species, streaks, text for easter eggs |
| `vessel-quest` | `maintenance-scheduler` | `localStorage["maint_tasks"]`, `maint_history` | Maintenance XP |
| `vessel-quest` | `fuel-tracker` | `localStorage["shiplog.fuel.entries"]` | Fuel XP |
| `vessel-quest` | `trip-planner` | `localStorage["trip_plan_data"]` | Trip XP, waypoint count |
| `vessel-quest` | `engine-hours` | `localStorage["maint_engine_hours"]` | Engine-hour maintenance triggers |
| `vessel-quest` | `weather-feed` | (via `/api/logs?category=weather`) | Storm events |
| `vessel-quest` | `ais-tracker` | (via `/api/logs?category=ais-contact`) | AIS achievements |
| `vessel-quest` | `fishcoin-ledger` | `fishcoin.json` | Reads balances for leaderboard; writes when chain/achievement grants coins |
| `fishcoin-ledger` | `crew-logbook` | SQLite (logs table) | `distribute` reads today's entries |
| `fuel-tracker` | `maintenance-scheduler` | `localStorage["maint_engine_hours"]` | Trip hours delta for GPH calc |
| `trip-planner` | `fuel-tracker` | `localStorage["shiplog.fuel.entries"]` | Range check |
| `trip-planner` | `tide-predictor` | (read-only reference) | User opens tide tab manually; planner can suggest |
| `maintenance-scheduler` | `engine-hours` | `localStorage["maint_engine_hours"]` | Recalculates "due" on every write |
| `map-view` | (all) | `/api/timeline?k=N` + cache | Pins from any category |
| `export-csv` | (all) | `/api/logs` (filterable) | Bulk export |
| `catch-analytics` | `crew-logbook` | SQLite `category='catch'` | Species, ground, season charts |

---

## 4. Shared localStorage Schema

Every localStorage key used by the ecosystem. Keys are **namespaced** to prevent collision with other apps on the same origin.

### 4.1 Master Key List

| Key | Owner Module | Type | Lifetime | Purpose |
|---|---|---|---|---|
| `crew_logbook` | crew-logbook | `Entry[]` | persistent | All log entries |
| `crew_roster` | crew-logbook | `CrewMember[]` | persistent | Captain + crew (name, role, color) |
| `last_watch` | crew-logbook | `string` ("day"\|"night") | session | Watch handover detection |
| `maint_tasks` | maintenance-scheduler | `Task[]` | persistent | Task definitions + last-completed state |
| `maint_engine_hours` | engine-hours / maintenance | `number` | persistent | Current engine hours |
| `maint_history` | maintenance-scheduler | `HistoryEntry[]` (cap 100) | persistent (rolling) | Completion log |
| `shiplog.fuel.entries` | fuel-tracker | `FuelEntry[]` | persistent | Fill-ups |
| `shiplog.fuel.queue` | fuel-tracker | `Entry[]` | until drained | Offline POST queue |
| `shiplog.fuel.settings` | fuel-tracker | `Settings` | persistent | Tank capacity, units, currency |
| `shiplog.map.entries` | map-view | `Entry[]` | persistent (rolling) | Pin cache for offline map |
| `shiplog.map.filter` | map-view | `Filter` | session | Active sidebar filter |
| `trip_plan_data` | trip-planner | `TripPlan[]` | persistent | Saved trips |
| `trip_active` | trip-planner | `TripPlan` | session | Current in-progress trip |
| `tide_station` | tide-predictor | `string` (station id) | persistent | Last-selected NOAA station |
| `ais_vessel_cache` | ais-tracker | `Record[]` (file, not localStorage) | persistent | AIS vessel state (file-based) |
| `vessel_quest_state` | vessel-quest | `QuestState` | persistent | XP, level, achievements, streaks, titles |
| `vessel_quest_chains` | vessel-quest | `ChainState` | persistent | Active + completed + abandoned chains |
| `vessel_quest_chain_definitions` | vessel-quest | `ChainDef[]` (immutable) | bundled | Static chain definitions |
| `vessel_quest_events` | vessel-quest | `EventState` | persistent | Active + historical world events |
| `vessel_quest_seasons` | vessel-quest | `SeasonState` | persistent | Seasonal multipliers + state |
| `vessel_quest_hidden` | vessel-quest | `HiddenState` | persistent | Hidden mechanic discoveries + RNG state |
| `crew_members` | vessel-quest | `CrewMember[]` (enriched) | persistent | Roster with role XP + abilities |
| `lucky_streak_tracker` | vessel-quest | `Record<crewId, lastTriggerTs>` | persistent | 1% RNG cooldown per user |
| `fishcoin_balance` | vessel-quest → fishcoin | `Record<name, number>` | mirrored | Mirror of fishcoin.json balances (for UI) |
| `fishcoin_history` | fishcoin-ledger | (file, not localStorage) | persistent | Transaction history (file-based) |

### 4.2 Schema Examples

#### `crew_logbook` entry

```js
{
  id: "cl_1721000000000_a1b2",
  author: "Sarah Walsh",
  role: "captain",
  watch: "dawn",            // "dawn" | "day" | "evening" | "night" | computed from hour
  text: "Light SW wind, barometer steady…",
  category: "observation",  // primary category for vessel-quest routing
  species: null,            // ["coho"] if catch
  weight: null,             // lbs if catch
  lat: 57.0531,             // optional
  lon: -135.3348,           // optional
  timestamp: 1721000000000,
  important: false,         // auto-flagged for mayday / storm / emergency text
  meta: {}                  // freeform metadata for downstream consumers
}
```

#### `maint_tasks` task

```js
{
  id: "mt_oil_change",
  name: "Engine Oil Change",
  type: "oil",
  intervalHours: 100,
  intervalDays: 365,
  lastCompletedHours: 124.3,
  lastCompletedDate: "2026-07-12",
  nextDueHours: 224.3,
  nextDueDate: "2027-07-12",
  status: "ok"              // "ok" | "due_soon" | "overdue"
}
```

#### `vessel_quest_state` (summary)

```js
{
  level: 11,
  rank: "First Mate",
  track: "maritime",
  xp: 16250,
  xpToNext: 22500,
  achievements: { /* 62 of 92 unlocked */ },
  titles: ["The Steady", "Old Salt", "Storm-Tested"],
  activeTitle: "The Steady",
  currentStreak: 178,
  longestStreak: 178,
  firstLogTimestamp: 1721000000000,
  loreFragmentsSeen: ["lore_001_redsky", …],
  fishcoinBalance: 6840,
  rankUpNotificationsSeen: { 11: true }
}
```

### 4.3 Cross-Module LocalStorage Contracts

These are the contracts that must hold for the ecosystem to function. **If any are broken, the gamification layer will misbehave.**

| Contract | Owner | Reader(s) | Failure mode if broken |
|---|---|---|---|
| Every `crew_logbook` entry has a unique `id` | crew-logbook | vessel-quest, fishcoin-ledger | Duplicate XP / coin on retry |
| `crew_logbook` entries have `category` ∈ enum | crew-logbook | vessel-quest (routing), map-view (color) | Default category, missed XP |
| `crew_logbook` entries have valid `timestamp` (ms) | crew-logbook | vessel-quest (streaks, season) | Streak breaks, wrong season |
| `maint_engine_hours` is a monotonically-increasing `number` | engine-hours | maintenance-scheduler, fuel-tracker | Recalculation errors |
| `maint_history` entries reference valid `task.id` | maintenance-scheduler | vessel-quest | Maintenance XP lost |
| `shiplog.fuel.entries` entries have `engine_hours` and `timestamp` | fuel-tracker | vessel-quest, fuel-tracker self | NMPG cannot compute |
| `trip_plan_data` entries have `waypoints[]` and `completedAt` | trip-planner | vessel-quest | Trip XP not awarded |
| `vessel_quest_state.xp` is monotonically increasing per crew member | vessel-quest | vessel-quest (level check), UI | "Rank went down" display glitch |
| `vessel_quest_state.currentStreak` decrements on missed day | vessel-quest | vessel-quest (display) | Streak inflation |
| `fishcoin_balance` mirror matches `fishcoin.json` | fishcoin-ledger ↔ vessel-quest | leaderboard UI | UI shows wrong balances |

### 4.4 Cache Invalidation Rules

| Cache Key | Invalidated When | Strategy |
|---|---|---|
| `shiplog.map.entries` | New POST `/api/log` succeeds OR fails-when-queued | TTL (5 min) + manual refresh + live polling (60s) |
| `shiplog.fuel.entries` | New fill-up submitted | Append + recompute NMPG on next view |
| `maint_history` | Task completion | Append-only, capped at 100 entries |
| `vessel_quest_state.achievements` | Check returns true | Set membership; idempotent |

---

## 5. API Endpoint Map

All API endpoints are served by the central `ship-log-search` Worker. Modules call these via `fetch()` from the browser or via `requests` from Python.

### 5.1 HTTP Endpoints (core Worker)

| Method | Path | Used By | Request Body / Params | Response |
|---|---|---|---|---|
| `POST` | `/api/log` | crew-logbook, maintenance-scheduler, fuel-tracker, trip-planner, weather-feed, ais-tracker | `{ category, timestamp, text, lat?, lon?, meta?, …category-specific fields }` | `{ ok: true, id: "log_…" }` |
| `GET` | `/api/logs` | all widgets | `?category=&from=&to=&limit=&offset=&q=` | `Entry[]` or `{ entries: Entry[] }` |
| `DELETE` | `/api/log?id=…` | fuel-tracker (best-effort) | — | `{ ok: true }` |
| `GET` | `/api/timeline` | map-view | `?k={limit}` | `{ entries: Entry[] }` |
| `GET` | `/api/nearby` | map-view (reserved) | `?lat=&lon=&radius=` | `Entry[]` |
| `GET` | `/api/search` | map-view, vessel-quest (planned) | `?q={query}` | `Entry[]` |
| `GET` | `/api/stats` | catch-analytics, vessel-quest | — | `{ countsByCategory, totalEntries, … }` |

### 5.2 Per-Category POST Body Shape

```js
// category: "catch"
{
  category: "catch",
  timestamp: 1721000000000,
  species: "coho",          // string or [string]
  weight: 14.5,             // lbs
  count: 1,                 // optional, for multi-fish catches
  lat: 57.0531,
  lon: -135.3348,
  text: "Coho on the troll, bright silver",
  meta: { ground: "southcape", gear: "troll", author: "Hank" }
}

// category: "maintenance"
{
  category: "maintenance",
  timestamp: 1721000000000,
  task_id: "mt_oil_change",
  hours_at_completion: 312.4,
  text: "Oil + filter change at 312.4 hrs",
  meta: { author: "Mo", early_completion_days: 12 }
}

// category: "fuel"
{
  category: "fuel",
  timestamp: 1721000000000,
  gallons: 48.20,
  price_per_gallon: 4.59,
  total_cost: 221.24,
  engine_hours: 312.4,
  trip_hours: 18.2,
  distance_nm: 0,
  location: "Marina del Rey fuel dock",
  lat: 33.9802, lon: -118.4514,
  notes: "Topped off, replaced fuel filter"
}

// category: "weather"
{
  category: "weather",
  timestamp: 1721000000000,
  beaufort: 5,             // 0-12
  wind_speed_kt: 21,
  wind_direction: "SW",
  pressure_mb: 1006.3,
  sea_state: 4,
  text: "Wind fresh, swell building",
  lat: 57.0531, lon: -135.3348
}

// category: "navigation"
{
  category: "navigation",
  timestamp: 1721000000000,
  waypoint_name: "South Rip",
  lat: 57.0531, lon: -135.3348,
  bearing: 215,
  speed_kt: 6.2,
  text: "Waypoint set, running for the rip"
}

// category: "observation"
{
  category: "observation",
  timestamp: 1721000000000,
  text: "Whales sighted, two adults, heading west",
  lat: 57.0531, lon: -135.3348
}

// category: "ais-contact"
{
  category: "ais-contact",
  timestamp: 1721000000000,
  vessel_name: "F/V Stormy Petrel",
  mmsi: 368020000,
  distance_m: 312,
  bearing: 87,
  speed_kt: 4.2,
  course: 178
}

// category: "ais-departure"
{
  category: "ais-departure",
  timestamp: 1721000000000,
  vessel_name: "F/V Stormy Petrel",
  mmsi: 368020000,
  distance_m: 1100,
  last_bearing: 88
}

// category: "trip_complete"
{
  category: "trip_complete",
  timestamp: 1721000000000,
  trip_id: "tp_2026_07_18",
  waypoints: [ { name, lat, lon, eta, arrivedAt } ],
  distance_nm: 87,
  duration_hours: 14.2,
  crew: ["Sarah Walsh", "Hank", "Mo"],
  checklist_complete: true
}

// category: "safety_check"
{
  category: "safety_check",
  timestamp: 1721000000000,
  checklist_id: "pre_departure_v1",
  items_total: 10,
  items_passed: 10,
  text: "Pre-departure checklist complete, all pass"
}
```

### 5.3 Python Module Endpoints (CLI tools)

| Module | CLI / Script | Default DB / Source |
|---|---|---|
| `fishcoin-ledger` | `python3 fishcoin.py {earn,spend,balance,leaderboard,history,rewards,perks,distribute,reset}` | `~/.local/share/shiplog/fishcoin.json` |
| `fishcoin-ledger` | `python3 fishcoin.py distribute` | Reads `~/.local/share/shiplog/local.db` (ship-log-sync SQLite) |
| `weather-feed` | `python3 weather-feed.py` | NOAA API → POST `/api/log` |
| `ais-tracker` | `python3 ais-tracker.py` | Signal K WebSocket → POST `/api/log` + Oracle Relay |
| `ais-simulator` | `python3 ais-simulator.py --port 9099 --vessels 5` | Local TCP port (dev) |
| `engine-hours` | `python3 engine-hours.py` | Reads from Signal K → `localStorage["maint_engine_hours"]` (via Worker sync) |
| `installer` | `python3 shiplog-installer.py` | — |
| `export-csv` | `python3 export.py` | Reads `/api/logs` (or local SQLite) |

### 5.4 External APIs Consumed

| Source | Used By | Endpoint | Auth |
|---|---|---|---|
| NOAA CO-OPS (tides) | tide-predictor | `api.tidesandcurrents.noaa.gov/api/prod/datagetter` | none |
| NOAA weather | weather-feed | `api.weather.gov` (or equivalent) | none |
| Signal K | ais-tracker, engine-hours | `ws://localhost:3000/signalk/v1/stream` | none (LAN) |
| Oracle Relay | ais-tracker | `wss://oracle-relay.casey-digennaro.workers.dev/room/casey-fishing` | bearer token (in config) |
| Leaflet tiles | map-view | `https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png` | none |
| Chart.js CDN | fuel-tracker, tide-predictor | `cdn.jsdelivr.net/npm/chart.js@4.4.1` | none |

---

## 6. The Gamification Layer

The gamification layer consists of two cooperating modules: `vessel-quest` (XP, ranks, achievements, chains, events, hidden mechanics) and `fishcoin-ledger` (tokenized economy). They are tightly integrated but functionally independent.

### 6.1 XP → FishCoin Flow

Every meaningful action triggers an XP award and a FishCoin earn. The two systems **must stay in sync** to maintain player trust.

```
[ACTION]
   │
   ▼
[event bus: action.completed]
   │
   ├──▶ vessel-quest.handleAction()
   │      │
   │      ├─ apply XP formula (base × role × season × event × progression + flat)
   │      ├─ check achievement unlocks
   │      ├─ check quest chain step completion
   │      ├─ check hidden mechanic triggers
   │      ├─ update streak counter
   │      └─ update leaderboard
   │
   └──▶ fishcoin-ledger.recordEarn()
          │
          ├─ apply quality multiplier (2× if GPS + photo + ≥100 char text)
          ├─ apply diminishing returns (>10 entries/day → 2 🐟 instead of 5)
          └─ update ledger file + mirror to localStorage["fishcoin_balance"]
```

### 6.2 XP Award Table (canonical)

The numbers below are the **canonical source** for the gamification layer. Other docs (`WORLDBUILDING.md`, `GAME_MECHANICS.md`) reference these as authoritative. If they disagree, **this table wins** until reconciled.

| Action | Base XP | FishCoin | Source Module |
|---|---:|---:|---|
| Log entry (any category) | 10 | 5 🐟 | crew-logbook |
| Catch report (species + weight) | 30 | 15 🐟 | crew-logbook |
| Maintenance completed | 50 | 25 🐟 | maintenance-scheduler |
| Fuel logged | 15 | 10 🐟 | fuel-tracker |
| Trip completed | 100 | 20 🐟 | trip-planner |
| Full safety checklist | 20 | 15 🐟 | crew-logbook (safety_check category) |
| Daily streak bonus (per day) | 25/day | varies | vessel-quest |
| Achievement unlock | 25–1000 (per achievement) | 25–1000 🐟 | vessel-quest |
| Hidden mechanic triggered | 50–500 | 0–200 🐟 | vessel-quest |
| Night-watch entry | 10 (bonus on top of base) | 10 🐟 bonus | crew-logbook (computed) |
| Dawn-patrol entry | 10 (bonus on top of base) | 10 🐟 bonus | crew-logbook (computed) |
| Data-quality bonus (GPS + photo) | +5 | +20 🐟 | crew-logbook (computed) |
| First catch of new species (per season) | +50 | +100 🐟 | vessel-quest (detected) |
| AIS contact logged | 10 | 5 🐟 | ais-tracker |
| Weather observation | 10 | 5 🐟 | weather-feed |

### 6.3 XP Multiplier Stack (canonical)

From `GAME_MECHANICS.md §4.1`. Applied bottom-up:

```
base_xp
  × role_passive_multiplier    (captain: 1.0, mate: 1.1, deckhand: 1.0, engineer: 1.0, observer: 1.05)
  × seasonal_multiplier        (spring 1.15, summer 1.25, fall 1.10, winter 1.30)
  × event_multiplier           (when active, see World Events §2)
  × rest_multiplier            (×2.0 after 24h idle, ×1.5 after 18h, ×1.2 after 12h)
  × combo_multiplier           (×1.0 to ×2.0 based on combo count)
  × perfection_multiplier      (×1.0 to ×2.0 based on perfect-day streak)
  + flat bonuses               (first of day +10, milestone +50, quest step xp, lucky 10×, lucky 13×13)
  = final_xp
```

### 6.4 Rank Table (canonical — 20 ranks from `WORLDBUILDING.md §2`)

| Lvl | Title | Track | XP Required | XP Cumulative |
|---:|---|---|---:|---:|
| 1 | Bait Runner 🪝 | Fishing | 0 | 0 |
| 2 | Tackle Hand 🧰 | Fishing | 100 | 100 |
| 3 | Deckhand 🪢 | Fishing | 200 | 300 |
| 4 | Line Slinger 🪢 | Fishing | 350 | 650 |
| 5 | Net Minder 🕸️ | Fishing | 600 | 1,250 |
| 6 | Hook Setter 🎣 | Fishing | 900 | 2,150 |
| 7 | Boatswain's Mate ⚓ | Fishing | 1,300 | 3,450 |
| 8 | Skiff Master 🛶 | Fishing | 1,800 | 5,250 |
| 9 | Highliner 🏆 | Fishing | 2,500 | 7,750 |
| 10 | Boat Captain 🚢 | Fishing | 3,500 | 11,250 |
| 11 | First Mate 📋 | Maritime | 5,000 | 16,250 |
| 12 | Bosun 🔱 | Maritime | 6,500 | 22,750 |
| 13 | Navigator 🧭 | Maritime | 8,000 | 30,750 |
| 14 | Pilot 🗺️ | Maritime | 9,500 | 40,250 |
| 15 | Quartermaster 📦 | Maritime | 11,000 | 51,250 |
| 16 | Skipper ⚓ | Maritime | 12,500 | 63,750 |
| 17 | Commodore 🚩 | Maritime | 14,000 | 77,750 |
| 18 | Admiral ⭐ | Maritime | 15,500 | 93,250 |
| 19 | Old Salt 🧔 | Maritime | 17,000 | 110,250 |
| 20 | Legend of the Sea 🐋 | Maritime | 19,000 | 129,250 |

> **Migration note:** The 10-rank system in `vessel-quest/README.md` maps to the new 20-rank system as: rank 1→1, rank 2→3, rank 3→4, rank 4→6, rank 5→11, rank 6→16, rank 7→17, rank 8→18, rank 9→19, rank 10→20. Cumulative XP is preserved.

### 6.5 FishCoin Sink Catalog (canonical — from `fishcoin-ledger/README.md` + `ECONOMY.md`)

| Perk | Cost | Source |
|---|---:|---|
| Pick tonight's dinner | 50 🐟 | fishcoin-ledger |
| Pick wheelhouse music | 75 🐟 | fishcoin-ledger |
| First shower at port | 100 🐟 | fishcoin-ledger |
| Beer after shift | 150 🐟 | fishcoin-ledger |
| Coffee ashore (the **anchor perk**) | 200 🐟 | fishcoin-ledger |
| Pick your bunk next trip | 300 🐟 | fishcoin-ledger |
| Extra hour shore leave | 500 🐟 | fishcoin-ledger |
| Crew Legend title (season) | 2,000 🐟 | fishcoin-ledger |
| Custom icon | 200 🐟 | WORLDBUILDING.md |
| Custom title | 500 🐟 | WORLDBUILDING.md |
| Vessel wrap upgrade | 500 🐟 | WORLDBUILDING.md |
| Tournament entry | 500 🐟 | WORLDBUILDING.md |
| Annual celebration ticket | 1,000 🐟 | WORLDBUILDING.md |
| Donate to Fishermen's Memorial | variable | WORLDBUILDING.md |
| Buy a round for the fleet | 250 🐟 | WORLDBUILDING.md |
| Sponsor a Junior Captain | 1,000 🐟 | WORLDBUILDING.md |

> **Reconciliation note:** The `WORLDBUILDING.md` economy (the "expanded" design) and the `fishcoin-ledger/README.md` + `ECONOMY.md` economy (the "current" implementation) have overlapping but not identical perk lists and reward rates. See §10 for the integration tensions.

### 6.6 World Event Catalog (canonical — from `GAME_MECHANICS.md §2`)

8 events with the following trigger / duration / modifier / scoring / reward structure:

| # | Event | Trigger | Duration | Modifier |
|---|---|---|---:|---:|
| 1 | 🐟 The Run | Calendar (first Mon of fishing-run season) | 7 days | 2.0× catch XP |
| 2 | 🏆 Deadliest Catch Week | Random, ~1× per quarter | 7 days | 1.5× all log XP |
| 3 | 🔧 Maintenance Marathon | Last weekend of month | 48 hrs | 3.0× maintenance XP |
| 4 | 📋 The Logjam | Auto (≥3 overdue + no event) | until cleared + 7d | 2.0× +0.5× per task |
| 5 | 🌅 First Light | Equinox week (Mar/Sep) | 7 days | 1.5× for logs <06:00 |
| 6 | 🔥 Iron Mariner Challenge | Random, ~1× per 2 months | 14 days | Streak bonus ×2 |
| 7 | 🐢 Ghost Net Cleanup | Random summer, Jun 15 – Aug 31 | 3 days | 5.0× ghost-gear XP |
| 8 | 🎯 Highliner Tournament | Quarterly at season change | 7 days | 2.0× top-10% species |

### 6.7 Quest Chain Catalog (canonical — from `GAME_MECHANICS.md §1.2`)

6 chains, all branching:

| Chain | Prereq Rank | Steps | Branch Reward A | Branch Reward B |
|---|:---:|:---:|---|---|
| 👻 Ghost Gear | 2 | 6 | Ghost Gear Warden title + 200 🐟 | Citizen Scientist badge + 1000 🐟 |
| ⭐ Perfect Week | 3 | 7 | The Flawless title + bonus | 500 🐟 + bonus |
| 🐟 Species Master | 1 | 6 | Ichthyologist title + 500 🐟 | Data Contributor badge + 1500 🐟 |
| 🗺️ The Old Route | 4 | 6 | Historian title + 200 🐟 | Keeper of Routes title + 1000 🐟 |
| ⛈️ Storm Season | 3 | 7 | Storm Captain title + 500 🐟 | Insurance dossier + 2000 🐟 |
| 👨‍🏫 Mentor's Path | 6 (Captain) | 7 | The Mentor title + 750 🐟 | Nurturer badge + 1500 🐟 |

### 6.8 Hidden Mechanic Catalog (canonical — from `GAME_MECHANICS.md §6.2`)

10 systems, all client-side deterministic:

| # | Mechanic | Trigger | Effect |
|---|---|---|---|
| 1 | 🍀 Lucky Streak | 1% per log entry | 10× XP, gold animation |
| 2 | 🎯 Milestone Celebrations | Round-number achievements | Confetti + 500 XP + badge |
| 3 | 🥚 Easter Egg Phrases | Keyword match in log text | 50–200 XP, achievement |
| 4 | 🌌 Constellation | 7+ distinct nights × 5+ hour slots | Star Navigator legendary |
| 5 | 🎂 Birthday Bonus | Crew member birthday (set once) | 5× XP that day |
| 6 | ⚓ Vessel Birthday | First log anniversary | 10× XP that day, permanent badge |
| 7 | 🎰 Lucky Number 13 | Exactly 13th entry of day | 13× XP |
| 8 | 📜 Echo of the Past | Read entry from exactly 1 year ago | Historian achievement |
| 9 | 🎭 Role Reversal | Out-of-role action | 50 XP + achievement |
| 10 | 🌊 Full Moon Tide | Log during ±1 day of full moon | +25 XP, ephemeral badge |

### 6.9 Title / Epithet Catalog (canonical — from `WORLDBUILDING.md §6`)

18 titles, all earned by behavior (not purchasable, except custom titles via FishCoin):

`ep_steady`, `ep_storm_tested`, `ep_night_owl`, `ep_dawn_treader`, `ep_chronicler`, `ep_salt`, `ep_iron_fist`, `ep_lucky_fin`, `ep_navigator`, `ep_old_hand`, `ep_deck_boss`, `ep_sunstone`, `ep_whale_watcher`, `ep_greybeard`, `ep_cagey`, `ep_hook_setter`, `ep_eldritch`, `ep_ghost`

### 6.10 Achievement Catalog (canonical — from `WORLDBUILDING.md §3` + `vessel-quest/ACHIEVEMENTS.json`)

92 total achievements across 11 categories + cross-category + secret.

| Category | Count |
|---|---:|
| Logging | 8 |
| Navigation | 7 |
| Maintenance | 7 |
| Safety | 7 |
| Crew | 6 |
| Seasons | 7 |
| Weather | 7 |
| Catch | 10 |
| Distance | 6 |
| Streaks | 6 |
| Special & Secret | 15 |
| Cross-Category | 6 |
| **Total** | **92** |

The on-disk `vessel-quest/ACHIEVEMENTS.json` should be the binding source — engineers should reconcile any drift between `WORLDBUILDING.md` tables and the JSON file.

### 6.11 Leaderboard Cadences (canonical — from `GAME_MECHANICS.md §5`)

| Season | Window | Aggregation |
|---|---|---|
| Weekly | Mon 00:00 UTC → Sun 23:59 UTC | Total XP |
| Monthly | 1st → last day of month UTC | Total XP |
| Seasonal | Real-world season (Mar/Jun/Sep/Dec starts) | Composite (40/25/15/10/10) |
| Yearly | Jan 1 → Dec 31 UTC | Composite (40/25/15/10/10) |

### 6.12 The Gamification Event Bus

`vessel-quest` listens for these events from other modules:

```js
window.addEventListener('shiplog:log:created',   onLogCreated);
window.addEventListener('shiplog:log:maintenance-complete', onMaintComplete);
window.addEventListener('shiplog:log:trip-complete', onTripComplete);
window.addEventListener('shiplog:log:safety-check', onSafetyCheck);
window.addEventListener('shiplog:streak:tick',  onStreakTick);     // daily timer
window.addEventListener('shiplog:season:change', onSeasonChange);  // quarterly
window.addEventListener('shiplog:event:start',  onEventStart);
window.addEventListener('shiplog:event:end',    onEventEnd);
```

And emits:

```js
window.dispatchEvent(new CustomEvent('shiplog:xp:gained',         { detail: { crewId, amount, source, multiplier } }));
window.dispatchEvent(new CustomEvent('shiplog:achievement:unlock',{ detail: { id, rarity } }));
window.dispatchEvent(new CustomEvent('shiplog:rank:up',           { detail: { level, rank, track } }));
window.dispatchEvent(new CustomEvent('shiplog:chain:step',        { detail: { chainId, step, branch } }));
window.dispatchEvent(new CustomEvent('shiplog:chain:complete',    { detail: { chainId, branch, reward } }));
window.dispatchEvent(new CustomEvent('shiplog:hidden:discovered', { detail: { id, name } }));
window.dispatchEvent(new CustomEvent('shiplog:title:earned',      { detail: { id, name } }));
window.dispatchEvent(new CustomEvent('shiplog:coin:earned',       { detail: { name, amount, reason } }));
window.dispatchEvent(new CustomEvent('shiplog:streak:milestone',  { detail: { crewId, days } }));
```

`fishcoin-ledger` listens for:

```js
window.addEventListener('shiplog:log:created',   onCoinEarn);     // call distribute-equivalent
window.addEventListener('shiplog:achievement:unlock', onAchievementCoinAward);
window.addEventListener('shiplog:chain:complete', onChainCoinAward);
window.addEventListener('shiplog:coin:spent',    onCoinSpend);
```

And emits:

```js
window.dispatchEvent(new CustomEvent('shiplog:coin:earned', { detail }));
window.dispatchEvent(new CustomEvent('shiplog:coin:spent',  { detail }));
window.dispatchEvent(new CustomEvent('shiplog:coin:redeemed', { detail: { name, perk, cost } }));
```

### 6.13 Anti-Abuse Invariants

The gamification layer enforces these invariants. **Engineers must not violate them.**

- Chains check `state.acceptedAt` — no retroactive step completion.
- GPS proximity checks require **actual logged coordinates** (`lat`/`lon` are finite numbers from device GPS, not manual entry).
- Photo requirements: must be image MIME, ≥5 KB, captured within 1 hour of log timestamp.
- Lucky Streak: 1% per log, **capped at 1 trigger per hour per user**.
- Easter Egg phrases: each limited to once per crew member; log must be ≥30 chars.
- Constellation: requires logs across **distinct** calendar dates.
- Birthday: cannot be changed after initial setup.
- Vessel Birthday: anchored to immutable first-log timestamp.
- Lucky 13: must be exactly the 13th entry of the day.
- Log quality threshold: entries <20 chars don't count toward scoring.
- Rate limit: max 50 logs/day count toward leaderboard scoring.
- Bot detection: time-between-consecutive-logs <10s flags the second entry.

---

## 7. Category & Event Taxonomy

### 7.1 Canonical Log Categories

| Category | Owner Module | Map Pin Color | Pin Icon | Drives |
|---|---|:---:|:---:|---|
| `catch` | crew-logbook | green `#10b981` | 🎣 | vessel-quest (catch XP, species), fishcoin-ledger (catch_report), catch-analytics |
| `maintenance` | maintenance-scheduler | amber `#f59e0b` | 🔧 | vessel-quest (maintenance XP), fishcoin-ledger (maintenance) |
| `weather` | weather-feed / crew-logbook | blue `#3b82f6` | 🌊 | vessel-quest (weather XP, storm achievements), seasonal events |
| `observation` | crew-logbook | grey `#9ca3af` | 👁 | vessel-quest (base XP), hidden mechanics (easter eggs) |
| `navigation` | trip-planner / crew-logbook | purple `#a855f7` | 🧭 | vessel-quest (base XP), distance achievements, map pins |
| `fuel` | fuel-tracker | (no pin by default) | — | vessel-quest (fuel XP), NMPG calc |
| `safety_check` | crew-logbook | (no pin by default) | — | vessel-quest (checklist XP) |
| `trip_complete` | trip-planner | (no pin) | — | vessel-quest (trip XP), fishcoin-ledger |
| `ais-contact` | ais-tracker | grey | ⚓ | vessel-quest (AIS XP) |
| `ais-departure` | ais-tracker | grey | ⚓ | vessel-quest (AIS XP) |

### 7.2 Source Attribution

Every entry should carry an `author` in its `meta` field. This drives crew attribution for:

- vessel-quest XP (per-crew leaderboards)
- fishcoin-ledger earn (per-crew balance)
- streak tracking (per-crew)
- role multiplier (per-crew role)

If `meta.author` is missing, default to `"Captain"` (the historical default).

### 7.3 Importance Flagging

`crew-logbook` auto-flags entries containing:

- `mayday` / `may day`
- `emergency`
- `man overboard` / `MOB`
- `ghost ship`
- (Future) storm keywords when wind > 50 kt

Flagged entries appear with an amber border and a 🚨 badge in the UI. They are **not** excluded from XP — in fact, important entries may earn small XP bonuses in future iterations.

---

## 8. Event Bus Contract

### 8.1 Event Naming Convention

All events use the `shiplog:` prefix, lowercase, colon-separated, past-tense for facts:

```
shiplog:log:created
shiplog:log:updated
shiplog:log:deleted
shiplog:log:maintenance-complete
shiplog:log:trip-complete
shiplog:log:safety-check
shiplog:log:catch-reported
shiplog:log:fuel-logged
shiplog:log:weather-observed
shiplog:log:ais-contact
shiplog:log:ais-departure
shiplog:streak:tick
shiplog:streak:milestone
shiplog:streak:broken
shiplog:season:change
shiplog:season:started
shiplog:season:ended
shiplog:event:start
shiplog:event:end
shiplog:event:milestone
shiplog:xp:gained
shiplog:xp:lost            // for corrections
shiplog:achievement:unlock
shiplog:rank:up
shiplog:chain:step
shiplog:chain:branch
shiplog:chain:complete
shiplog:chain:abandon
shiplog:chain:available
shiplog:hidden:discovered
shiplog:title:earned
shiplog:title:equipped
shiplog:coin:earned
shiplog:coin:spent
shiplog:coin:redeemed
shiplog:leaderboard:tick
shiplog:leaderboard:changed
shiplog:engine-hours:updated
shiplog:trip:started
shiplog:trip:waypoint-added
shiplog:trip:completed
shiplog:fuel:fillup
shiplog:maintenance:task-due
shiplog:maintenance:task-overdue
shiplog:maintenance:task-complete
shiplog:weather:storm-detected
shiplog:ais:contact
shiplog:ais:departure
shiplog:app:ready
shiplog:app:online
shiplog:app:offline
shiplog:app:error
```

### 8.2 Event Detail Shapes

```js
// shiplog:log:created
{ id: "cl_…", category: "catch", author: "Hank", timestamp: 1721000000000, text: "…", lat: 57.05, lon: -135.33, meta: {…} }

// shiplog:xp:gained
{ crewId: "cm_…", amount: 47, source: "catch_log", multiplier: 2.1, flatBonus: 10, finalXp: 47 }

// shiplog:rank:up
{ crewId: "cm_…", fromLevel: 4, toLevel: 5, fromRank: "Line Slinger", toRank: "Net Minder", track: "fishing" }

// shiplog:achievement:unlock
{ id: "catch_100", name: "Centurion", rarity: "silver", xp: 75, coin: 75, category: "catch" }

// shiplog:chain:complete
{ chainId: "species_master", branch: "A", reward: { xp: 300, coin: 500, badge: "species_sage", title: "Ichthyologist" } }

// shiplog:coin:earned
{ name: "Hank", amount: 15, reason: "Catch logged: coho 14.5 lbs", source: "catch_report" }

// shiplog:coin:redeemed
{ name: "Hank", perk: "coffee", cost: 200 }

// shiplog:season:change
{ from: "spring", to: "summer", fromMultiplier: 1.15, toMultiplier: 1.25 }
```

### 8.3 Cross-Tab / Cross-Tab Sync

The event bus fires in one tab. Other tabs need to hear about it. Two strategies:

1. **`storage` event** — every localStorage write fires a `storage` event in other tabs. Wrap critical writes to emit custom events when `localStorage` changes.
2. **`BroadcastChannel`** — modern, clean, supported in all major browsers. Recommended for ecosystem-wide events:

```js
const channel = new BroadcastChannel('shiplog');
channel.postMessage({ type: 'shiplog:log:created', detail: {...} });
channel.onmessage = (ev) => dispatchEvent(new CustomEvent(ev.data.type, { detail: ev.data.detail }));
```

Use `BroadcastChannel` as the primary sync mechanism. Fall back to `storage` events for browsers that lack `BroadcastChannel` (rare in 2026 but possible on old marine tablets).

---

## 9. Integration Verification Checklist

Use this checklist to verify that every integration in the ecosystem is wired correctly. Each item is testable.

### 9.1 Data Flow Tests

- [ ] **D1:** Creating a log entry in crew-logbook → triggers `shiplog:log:created` event.
- [ ] **D2:** `shiplog:log:created` → vessel-quest awards XP.
- [ ] **D3:** `shiplog:log:created` → fishcoin-ledger awards coins (after debounce).
- [ ] **D4:** `shiplog:log:created` with `category: 'catch'` → map-view shows green pin.
- [ ] **D5:** `shiplog:log:created` with `category: 'weather'` → storm achievement check fires.
- [ ] **D6:** Completing a maintenance task → `shiplog:maintenance:task-complete` event.
- [ ] **D7:** Maintenance completion → vessel-quest awards maintenance XP.
- [ ] **D8:** Maintenance completion → maintenance-scheduler updates `maint_tasks` last-completed state.
- [ ] **D9:** Trip completion → `shiplog:trip:completed` event → vessel-quest awards trip XP.
- [ ] **D10:** Fuel fill-up → NMPG computed within 2 seconds.
- [ ] **D11:** Engine-hours update → maintenance-scheduler recalculates "due" status on all tasks.
- [ ] **D12:** AIS contact event → map-view shows grey pin.
- [ ] **D13:** Weather-feed cron → POST /api/log succeeds → vessel-quest awards weather XP.

### 9.2 localStorage Contract Tests

- [ ] **L1:** `crew_logbook` is an array.
- [ ] **L2:** Every `crew_logbook` entry has `id`, `author`, `category`, `timestamp`, `text`.
- [ ] **L3:** `maint_engine_hours` is a number that increases monotonically.
- [ ] **L4:** `vessel_quest_state.xp` matches the sum of all `shiplog:xp:gained` events for that crew member.
- [ ] **L5:** `fishcoin_balance` mirror matches the captain's `fishcoin.json` ledger.
- [ ] **L6:** `shiplog.fuel.entries` entries have `gallons`, `price_per_gallon`, `engine_hours`, `timestamp`.
- [ ] **L7:** `shiplog.map.entries` is invalidated when offline > 6 hours.

### 9.3 Gamification Tests

- [ ] **G1:** Streak increments on consecutive-day log.
- [ ] **G2:** Streak resets on missed day (verified by `date.now()` > `lastLogTimestamp + 36h`).
- [ ] **G3:** Lucky Streak RNG fires ~1% of the time over 1000 trials (within 0.5%–1.5% tolerance).
- [ ] **G4:** Lucky Streak is capped at 1 trigger per hour per user.
- [ ] **G5:** Easter egg "calm seas" triggers only once per crew member.
- [ ] **G6:** Vessel Birthday grants 10× XP exactly 365 days after first log timestamp.
- [ ] **G7:** Lucky 13 grants 13× XP only on exactly the 13th entry of a day.
- [ ] **G8:** Perfect Week chain requires 7 consecutive days with checklist + log + maintenance.
- [ ] **G9:** Species Master chain counts unique species from `meta.species` AND text scan.
- [ ] **G10:** Ghost Gear chain regex matches `ghost gear`, `adrift net`, `lost gear`, `derelict` (case-insensitive).
- [ ] **G11:** Storm Season chain triggers only when wind >30 kt for ≥6 hours.
- [ ] **G12:** Iron Mariner Challenge streak bonus doubles correctly (instead of +25/day, +50/day).
- [ ] **G13:** Mentor Bonus caps at 10 logs/day per mentee.
- [ ] **G14:** Combo counter resets at midnight (calendar day boundary).
- [ ] **G15:** Rest Bonus applies only to first log after idle (not every subsequent log).
- [ ] **G16:** First of Day awards +10 XP only once per calendar day per crew member.
- [ ] **G17:** Title equipping persists across reloads.
- [ ] **Lore Fragment 1 unlocks at Level 2; Fragment 10 at Level 20.**

### 9.4 Economy Tests

- [ ] **E1:** `fishcoin distribute` awards coins based on today's logs.
- [ ] **E2:** Coin earn matches REWARDS table for each action type.
- [ ] **E3:** Quality multiplier (2× for GPS + photo + ≥100 chars) applies correctly.
- [ ] **E4:** Diminishing returns after 10 entries/day reduce earn to 2 🐟 instead of 5.
- [ ] **E5:** Daily cap of 1,000 🐟 enforced.
- [ ] **E6:** Coin spend decrements balance, increments spent_total.
- [ ] **E7:** Coin spend below balance fails with clear error.
- [ ] **E8:** Season reset archives old ledger, starts new one.
- [ ] **E9:** Leaderboard sorts by earned_total descending.
- [ ] **E10:** Coin redemption broadcasts `shiplog:coin:redeemed` event.

### 9.5 Leaderboard Tests

- [ ] **LB1:** Weekly leaderboard resets on Monday 00:00 UTC.
- [ ] **LB2:** Monthly leaderboard resets on 1st of month UTC.
- [ ] **LB3:** Composite score = 0.4×xp + 0.25×catch_weight + 0.15×diversity + 0.10×quality + 0.10×distance.
- [ ] **LB4:** Tier badges (Platinum/Gold/Silver/Bronze) assign correctly by percentile.
- [ ] **LB5:** Leaderboards with <4 crew members don't display tiers.

### 9.6 Cross-Module Tests

- [ ] **C1:** Captain changes role mid-week → old role XP preserved, new role XP starts fresh.
- [ ] **C2:** World event overlap (2 events active) → modifiers stack correctly.
- [ ] **C3:** Multi-tab: log entry in tab A → tab B's leaderboard updates within 5 seconds (BroadcastChannel).
- [ ] **C4:** Offline → log entries queued → online → queue drains in order.
- [ ] **C5:** Multiple browser types (mobile + desktop) → leaderboard shows combined data correctly.
- [ ] **C6:** Export-csv produces CSV with all categories filterable.
- [ ] **C7:** Map-view refresh (60s polling) picks up new pins within 90 seconds.

### 9.7 UI / UX Tests

- [ ] **U1:** First entry on Day 1 shows "First Words" achievement within 2 seconds.
- [ ] **U2:** Rank-up animation appears once (not on every page load).
- [ ] **U3:** Hidden mechanic toasts are dismissible by click or Escape.
- [ ] **U4:** All notifications honor `prefers-reduced-motion`.
- [ ] **U5:** Tabs render correctly at 320px width (mobile-first).
- [ ] **U6:** Dark theme readable in direct sunlight (WCAG AA contrast on text).
- [ ] **U7:** Numbers use thousands separators (`,` or `.` based on locale).

---

## 10. Known Integration Tensions

The vessel ecosystem has been designed by **multiple authors across multiple sessions**. There are real tensions between the design documents that engineers must resolve before shipping. This section names them explicitly.

### 10.1 Two FishCoin Economies

The `WORLDBUILDING.md` (the "expanded" design, written for the gamification layer) defines a FishCoin economy with one set of rates. The `fishcoin-ledger/README.md` and `fishcoin-ledger/ECONOMY.md` (the "current" implementation, written for the Python CLI) define a different economy. They differ in:

| Item | `WORLDBUILDING.md` | `fishcoin-ledger/README.md` |
|---|---|---|
| Log entry earn | 10 🐟 | 5 🐟 |
| Catch earn | 25 🐟 | 15 🐟 |
| Maintenance earn | 15 🐟 | 25 🐟 |
| Fuel earn | 5 🐟 | 10 🐟 |
| Photo bonus | 5 🐟 | (rolled into data_quality 20 🐟) |
| Quality multiplier | 2× for GPS+photo+text | (separate data_quality bonus) |
| Daily cap | 1,000 🐟 (with diminishing returns) | (season reset instead of daily cap) |
| Coffee ashore | (implied, not in cost table) | 200 🐟 |

**Resolution options:**

1. **Pick WORLDBUILDING and update `fishcoin.py`.** The expanded design has better balancing and aligns with the gamification layer's XP table.
2. **Pick `fishcoin.py` and update `WORLDBUILDING.md`.** The CLI is already shipped; align the design doc to match.
3. **Adopt a single canonical table** (see §6.2 above) and update both docs to match.

**Recommendation:** Option 3. The §6.2 table in this document is **proposed canonical**. Engineers should adopt it and update both source documents.

### 10.2 Two Rank Systems

`vessel-quest/README.md` defines a **10-rank** system (Deckhand → Legend of the Sea). `WORLDBUILDING.md §2` defines a **20-rank** system (Bait Runner → Legend of the Sea). The 10-rank system is shipped in `index.html`; the 20-rank system is the design.

**Resolution:** Migrate to the 20-rank system. The mapping in §6.4 above preserves flagship ranks (Commodore, Admiral, Legend) and cumulative XP. The `vessel-quest/ranks.js` file (referenced in `WORLDBUILDING.md §8`) should be created to hold the 20-rank data.

### 10.3 `catch-analytics` Reference

`VESSEL_EXPERIENCE.md` references `catch-analytics` as a daily-use tab. The `MODULE_SPEC.md` lists it as "✅ built" but the `ship-log-modules/catch-analytics/` directory contains only an empty placeholder.

**Resolution:** Either (a) build `catch-analytics` as a thin pass-through widget over `crew-logbook` (filter `category === 'catch'`, group by species/date/ground, render charts), or (b) update `VESSEL_EXPERIENCE.md` to defer catch-analytics mentions until the widget is built.

**Recommendation:** Option (a). It's a high-value tab and the data is already there.

### 10.4 Quest Chain Trigger Reliability

The `GAME_MECHANICS.md` describes 6 quest chains with detection helpers. Some are highly dependent on text content (regex matches for "ghost gear", "calm seas", etc.) which means the user must **write the right words** in their log entries. This is a **discovery tax** — the chain is invisible unless you happen to write the magic word.

**Resolution options:**

1. **Add a "Quest hints" panel** that surfaces available chains + their detection criteria (spoiling the discovery but ensuring activation).
2. **Add a "Suggest this log completes…" nudge** that detects when a log matches a chain step and offers to mark it.
3. **Make chain steps auto-detect from structured fields** where possible (e.g., GPS proximity for Ghost Gear can use `lat`/`lon` directly).

**Recommendation:** A combination of (1) and (3). Show chains + criteria in the Quest tab (visible but not spoiler-y — the criteria are general, the magic words are not). Use structured fields wherever possible. Reserve regex matching for truly ambiguous chains (Species Master, where the text is the only signal).

### 10.5 Season Detection Hemisphere

`WORLDBUILDING.md §4` notes that seasons should auto-detect hemisphere. The implementation must capture this at vessel setup and invert the calendar for Southern Hemisphere users.

**Resolution:** Add a `vessel.hemisphere` setting (default: `NH`) at first-run. The seasonal engine reads this. `crew-logbook` already needs a timezone setting for First Light event detection — these can be the same field.

### 10.6 Offline / Online State Sync

`fuel-tracker` has a robust offline queue (`shiplog.fuel.queue`). Other widgets (crew-logbook, maintenance-scheduler) do not. If a vessel loses connectivity at sea (common), data entered offline is at risk of being lost or duplicated on reconnect.

**Resolution:** Add a shared `shiplog.outbox.queue` for all write operations. The crew-logbook, maintenance-scheduler, and trip-planner should all write to this queue when offline and drain it on reconnect. The `ship-log-search` Worker should support idempotent POSTs (idempotency-key header) to prevent duplicates.

### 10.7 Privacy / Multi-Crew Data

A single `crew_logbook` is shared by all crew members. Every entry is visible to every crew member. This is intentional (the logbook is shared) but raises privacy questions for personal logs (e.g., "I'm seasick", "I'm thinking about quitting").

**Resolution:** Add a `visibility` field on entries. Default: `crew`. Allow `private` (only the author sees) and `public` (exported, shared with fleet). The vessel-quest XP for a private entry still counts for the author but the entry text is hidden from the crew log view.

---

## Appendix A: Glossary of Keys, Endpoints, and Categories

For grep-friendly reference.

### Keys (alphabetical)

```
ais_vessel_cache              (file, ais-tracker)
crew_logbook                  (crew-logbook, primary)
crew_members                  (vessel-quest, enriched roster)
crew_roster                   (crew-logbook, basic roster)
fishcoin_balance              (mirror)
fishcoin_history              (file)
last_watch                    (crew-logbook, session)
lucky_streak_tracker          (vessel-quest)
maint_engine_hours            (engine-hours / maintenance)
maint_history                 (maintenance-scheduler)
maint_tasks                   (maintenance-scheduler)
shiplog.fuel.entries          (fuel-tracker)
shiplog.fuel.queue            (fuel-tracker, offline)
shiplog.fuel.settings         (fuel-tracker)
shiplog.map.entries           (map-view, cache)
shiplog.map.filter            (map-view, session)
tide_station                  (tide-predictor)
trip_active                   (trip-planner, session)
trip_plan_data                (trip-planner)
vessel_quest_chain_definitions (vessel-quest, bundled immutable)
vessel_quest_chains           (vessel-quest)
vessel_quest_events           (vessel-quest)
vessel_quest_hidden           (vessel-quest)
vessel_quest_seasons          (vessel-quest)
vessel_quest_state            (vessel-quest, primary)
```

### Endpoints (alphabetical)

```
DELETE /api/log?id=…
GET    /api/logs?category=&from=&to=&limit=&offset=&q=
GET    /api/nearby?lat=&lon=&radius=
GET    /api/search?q=
GET    /api/stats
GET    /api/timeline?k=
POST   /api/log
```

### Categories (alphabetical)

```
ais-contact
ais-departure
catch
fuel
maintenance
navigation
observation
safety_check
trip_complete
weather
```

### Event Names (alphabetical)

See §8.1 above.

---

## Appendix B: Module Manifest Audit

Every module has a `module.json`. This matrix confirms the manifest claims match the integration reality.

| Module | Manifest Type | Manifest Permissions | Reality | Pass? |
|---|---|---|---|:---:|
| crew-logbook | widget | read:logs, write:logs | Writes `crew_logbook`, reads own | ✅ |
| map-view | widget | read:logs | Reads `/api/timeline` | ✅ |
| fuel-tracker | widget | read:logs, write:logs | Writes `category=fuel` entries | ✅ |
| maintenance-scheduler | widget | read:logs, write:logs | Writes `category=maintenance` entries | ✅ |
| trip-planner | widget | read:logs, write:logs | Writes `category=trip_complete` | ✅ |
| tide-predictor | widget | read:logs | Reads only | ✅ |
| weather-feed | (data source, no manifest yet) | — | Writes `category=weather` | ⚠️ **needs manifest** |
| ais-tracker | (data source, no manifest yet) | — | Writes `category=ais-contact/departure` | ⚠️ **needs manifest** |
| engine-hours | (data source, no manifest yet) | — | Writes `maint_engine_hours` | ⚠️ **needs manifest** |
| export-csv | (export, no manifest yet) | — | Reads `/api/logs` | ⚠️ **needs manifest** |
| vessel-quest | widget | read:logs | Reads logs; should also request write permission for state writes | ⚠️ **needs write permission** |
| fishcoin-ledger | integration | read:logs, write:logs | Reads logs for distribute; writes ledger file | ✅ |

**Recommendation:** Add `module.json` to weather-feed, ais-tracker, engine-hours, and export-csv. Add `write:vessel-quest-state` permission to vessel-quest manifest.

---

## Appendix C: Performance Budget

| Operation | Budget | Notes |
|---|---|---|
| Log entry submission (click → stored → XP awarded → coin earned → UI updated) | < 500 ms | Includes localStorage write + achievement check |
| Map-view render of 5,000 pins | < 2 s | Marker clustering handles this |
| Achievement check on every log entry | < 50 ms | 92 checks × 5,000 logs = 460k ops, but most short-circuit |
| Streak tick (daily timer) | < 100 ms | Once per day |
| Seasonal event check | < 50 ms | On every entry, fast |
| Quest chain step completion check | < 100 ms | O(n) on relevant logs |
| Combo counter update | < 10 ms | O(1) sliding window |
| `fishcoin distribute` | < 2 s for 50 entries/day | Single SQLite read |
| Leaderboard recomputation | < 200 ms | Cache intermediate results |
| Annual review generation | < 1 s | Pure rollups, deterministic |

If any operation exceeds budget, **measure first, optimize second**. The ecosystem is small enough that premature optimization is the wrong move.

---

## Appendix D: References

- `MODULE_SPEC.md` — module types, manifest schema, install/discovery
- `vessel-quest/WORLDBUILDING.md` — world premise, 20 ranks, 92 achievements, lore, titles, economy (expanded)
- `vessel-quest/GAME_MECHANICS.md` — quest chains, world events, crew roles, progression modifiers, leaderboard seasons, hidden mechanics
- `vessel-quest/ACHIEVEMENTS.json` — on-disk achievement data
- `vessel-quest/seasons.js` — base seasonal logic
- `vessel-quest/epithets.js` — title definitions
- `vessel-quest/lore.js` — lore fragment definitions
- `fishcoin-ledger/ECONOMY.md` — FishCoin economy (current implementation)
- `fishcoin-ledger/README.md` — FishCoin reward + perk tables (current)
- `fishcoin-ledger/fishcoin.py` — Python CLI implementation
- `VESSEL_EXPERIENCE.md` — the user journey narrative (this document's companion)

---

**End of document.**

*This is the wiring. The experience is the story. The wiring exists to make the story real.*