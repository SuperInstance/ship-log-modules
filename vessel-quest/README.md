# 🏆 Vessel Quest — Gamified Vessel Operations

Turn your ship-log data into a game. Earn XP, level up, unlock achievements, complete daily quests, and climb the crew leaderboard — all from real vessel activity.

## How It Works

Vessel Quest reads data from **all other ship-log modules** and converts operations into XP:

| Action | XP |
|--------|-----|
| Log entry | +10 |
| Catch report | +30 |
| Maintenance completed | +50 |
| Fuel logged | +15 |
| Trip completed | +100 |
| Full checklist | +20 |
| Daily streak bonus | +25/day |
| Achievement unlock | +25 to +1000 |

## Rank Ladder

Progress through 10 ranks from Deckhand to Legend of the Sea:

1. 🪢 **Deckhand** (0 XP)
2. ⚓ **Boatswain** (100 XP)
3. 🧭 **Third Mate** (300 XP)
4. 📋 **Second Mate** (600 XP)
5. 🎖️ **First Mate** (1,000 XP)
6. 🚢 **Captain** (1,800 XP)
7. ⭐ **Master** (3,000 XP)
8. 🏆 **Commodore** (5,000 XP)
9. 👑 **Admiral** (8,000 XP)
10. 🐋 **Legend of the Sea** (12,000 XP)

## Achievements (28 total)

Across 5 rarity tiers:

- **Common** (gray): First Words, Journal Keeper, Getting Habitual...
- **Uncommon** (green): Storyteller, Week Warrior, Shipshape...
- **Rare** (purple): Chronicler, Old Salt, Navigator, Fully Equipped...
- **Epic** (pink): Unstoppable, Engine Whisperer, Four Seasons...
- **Legendary** (gold): Sea Bard, Iron Mariner, Ocean Crosser, Highliner...

## Daily Quests

3 random quests each day from a pool of 9:

- ✍️ Daily Entry — Log 1 entry (+15 XP)
- 💬 Chatterbox — Log 3+ entries (+30 XP)
- 🔧 Fix It — Complete maintenance (+40 XP)
- 🦺 Safety Check — Full checklist (+35 XP)
- 🐟 Daily Catch — Log a catch (+25 XP)
- ⛽ Fuel Up — Log fuel (+20 XP)
- 🧭 Plan Ahead — Review a trip (+25 XP)
- 🌙 Night Watch — Log at night (+20 XP)
- 🌅 Dawn Patrol — Log before 6 AM (+20 XP)

## Crew Leaderboard

When multiple crew members log entries, XP is distributed across the crew. The captain gets 40%, crew splits the rest. Competition drives engagement.

## Integration

Vessel Quest automatically reads from:
- `crew_logbook` (localStorage) — log entries, catch reports
- `maint_tasks` + `maint_history` — maintenance completion
- `shiplog.fuel.entries` — fuel logs
- `trip_plan_data` — waypoints, crew, checklists
- `maint_engine_hours` — engine hours

No configuration needed. Just use the other modules and watch your XP grow.

## Why Gamification?

Commercial fishing is hard, repetitive work. The data that makes the whole system valuable — consistent log entries, timely maintenance records, fuel tracking — is exactly the data that's tedious to enter. Vessel Quest makes data entry feel like progression, not paperwork.

A captain who checks their quest status each morning is a captain who logs consistently. That's worth more than any single feature.
