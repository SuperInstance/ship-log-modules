# 🐟 FishCoin — Vessel Crew Economy

Tokenized incentive system for crew engagement. Crew earn FishCoin (🐟) for data-entry tasks that benefit the vessel. Coins can be redeemed for real-world perks.

## The Problem

The data that makes your vessel system valuable — consistent log entries, catch reports, maintenance records — is exactly the data that's most tedious to enter. FishCoin makes data entry rewarding.

## How It Works

```
Crew logs a catch → fishcoin earn automatically → balance grows → redeem for coffee ashore
```

It's half game, half incentive. The captain funds the economy. The crew competes for perks. The vessel gets better data.

## Reward Table

| Action | Reward |
|--------|--------|
| Log entry | 5 🐟 |
| Catch report (species + weight) | 15 🐟 |
| Maintenance task completed | 25 🐟 |
| Fuel entry logged | 10 🐟 |
| Trip planned | 20 🐟 |
| Safety checklist completed | 15 🐟 |
| Night watch entry | 10 🐟 |
| Dawn patrol (before 6 AM) | 10 🐟 |
| 3-day streak bonus | 50 🐟 |
| 7-day streak bonus | 100 🐟 |
| 30-day streak bonus | 300 🐟 |
| Data quality (GPS + photo) | 20 🐟 |
| First catch of season | 100 🐟 |

## Perk Catalog

| Perk | Cost |
|------|------|
| Pick tonight's dinner | 50 🐟 |
| Pick wheelhouse music | 75 🐟 |
| Beer after shift | 150 🐟 |
| First shower at port | 100 🐟 |
| Coffee ashore | 200 🐟 |
| Pick your bunk next trip | 300 🐟 |
| Extra hour shore leave | 500 🐟 |
| Crew Legend title (season) | 2,000 🐟 |

## Usage

```bash
# Manual
python3 fishcoin.py earn Casey "Caught first sockeye" 15
python3 fishcoin.py spend Casey "Coffee ashore" 200
python3 fishcoin.py balance Casey

# Auto-distribute based on today's log entries
python3 fishcoin.py distribute

# View standings
python3 fishcoin.py leaderboard
python3 fishcoin.py history Casey

# View reward/perk tables
python3 fishcoin.py rewards
python3 fishcoin.py perks

# New season (archives old one)
python3 fishcoin.py reset --confirm
```

## Auto-Distribution

The `distribute` command reads the local ship-log SQLite database, counts today's entries per crew member, and automatically awards FishCoin based on the reward table. Run it at the end of each day via cron:

```bash
# End of day auto-distribution
0 20 * * * python3 /path/to/fishcoin.py distribute
```

## Integration

- Reads from `ship-log-sync` SQLite database
- Pairs with `vessel-quest` widget for visual leaderboard
- Crew names match `crew-logbook` roster
- Season archive at `~/.local/share/shiplog/fishcoin_season_YYYY.json`
