# 📖 Crew Logbook Module

Shared crew log for multi-person vessel operations. Every crew member logs entries with their name, role, and watch. Built for watch handovers and situational awareness.

## Features

- **Crew roster** — add crew members with roles (captain, mate, deckhand, engineer, observer)
- **Role-coded entries** — each entry is color-coded by the author's role
- **Watch tracking** — entries tagged with day/night watch automatically
- **Watch handover alerts** — detects watch changes and summarizes the previous watch's important items
- **Important flagging** — mark critical entries (mayday, warnings, emergencies auto-flagged)
- **Filters** — by author, watch, today only, important only
- **Stats bar** — entry counts by watch, important count, crew size
- **Offline-first** — localStorage, no connection needed
- **Clean UI** — dark theme, role-coded left borders, badges, timestamps

## Roles & Colors

| Role | Color | Icon |
|------|-------|------|
| Captain | Amber | ⚓ |
| First Mate | Blue | 🧭 |
| Deckhand | Green | 🪝 |
| Engineer | Red | 🔧 |
| Observer | Purple | 🔍 |

## Installation

```bash
shiplog install crew-logbook
```

## Usage

1. Add crew members in the roster section
2. Select your name from the dropdown
3. Write your entry — press Cmd/Ctrl+Enter for quick submit
4. Entries are tagged with your watch (day/night) automatically
5. Watch handovers trigger a summary of the previous watch's important items

## Data

All data stored in browser localStorage:
- `crew_logbook` — all log entries
- `crew_roster` — crew member list
- `last_watch` — last detected watch (for handover detection)
