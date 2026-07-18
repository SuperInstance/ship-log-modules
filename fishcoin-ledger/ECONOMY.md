# FishCoin Economic Design Document

> The science behind a fake economy that drives real behavior.

## Core Thesis

FishCoin is not a cryptocurrency. It is a **behavioral incentive system** disguised as a game currency. The goal is not to create a market — it is to make data entry feel rewarding instead of burdensome.

The problem we're solving: the data that makes a vessel system valuable (consistent logs, catch reports, maintenance records, fuel entries) is tedious to produce. Humans avoid tedium. FishCoin converts tedium into progression.

## Economy Architecture

### Faucets (Coin Sources)

| Source | Rate | Notes |
|--------|------|-------|
| Log entry | 5 🐟/entry | Base rate, unlimited |
| Catch report | 15 🐟/catch | Higher value — catch data is most useful |
| Maintenance complete | 25 🐟/task | Highest single-action reward |
| Fuel log | 10 🐟/entry | Moderate — less frequent, moderate value |
| Trip planned | 20 🐟/trip | Planning is rare but high-value |
| Safety checklist | 15 🐟/completion | Encourages safety culture |
| Night watch entry | 10 🐟/entry | Bonus on top of log entry |
| Dawn patrol | 10 🐟/entry | Bonus for early logging |
| Streak bonus | 50-300 🐟 | Exponential, resets on miss |
| Data quality bonus | 20 🐟/entry | GPS + photo = quality data |
| First-of-season | 100 🐟/species | Encourages biodiversity tracking |

**Estimated daily faucet:** 50-200 🐟 per active crew member (3-10 actions/day)

### Sinks (Coin Drains)

| Sink | Cost | Notes |
|------|------|-------|
| Pick dinner | 50 🐟 | Low-stakes, frequent |
| Pick music | 75 🐟 | Low-stakes, frequent |
| First shower | 100 🐟 | Moderate desire |
| Beer after shift | 150 🐟 | Popular, moderate |
| Coffee ashore | 200 🐟 | High desire, captain-funded |
| Bunk preference | 300 🐟 | High value on multi-day trips |
| Extra shore leave | 500 🐟 | Major perk |
| Legend title | 2,000 🐟 | Prestige, season goal |

**Design principle:** Sinks should be slightly more expensive than the daily faucet rate. A crew member who logs consistently should be able to afford one small perk every 2-3 days and one major perk per month.

### Target Balance

- **Daily earning rate:** ~100 🐟 (active crew member)
- **Weekly earning rate:** ~700 🐟
- **Monthly earning rate:** ~3,000 🐟
- **Season earning rate:** ~9,000 🐟

This means:
- Small perks (dinner, music): affordable every 1-2 days ✓
- Medium perks (shower, beer): affordable every 2-3 days ✓
- Large perks (coffee, bunk): weekly treat ✓
- Major perks (shore leave): monthly milestone ✓
- Legend title: season-long goal ✓

## Inflation Controls

### Season Reset
At the start of each new season (or calendar year), FishCoin balances reset to zero. The previous season's ledger is archived. This prevents hoarding and ensures each season is a fresh competition.

### Diminishing Returns (optional)
After 10 log entries in a single day, the reward per entry drops from 5 to 2 🐟. This prevents a crew member from gaming the system with low-quality spam entries while still rewarding genuine high-activity days.

### Quality Multipliers
Entries with GPS coordinates, photos, or species/weight data earn 2x FishCoin. This drives the specific data quality that makes the system valuable.

## The Coffee Principle

The most important perk in the catalog is **coffee ashore (200 🐟)**. Here's why:

1. **It's real.** A coffee costs $4-6. It's tangible.
2. **It's social.** The captain buying coffee for the crew is a bonding ritual.
3. **It's achievable.** 200 🐟 = ~2 days of consistent logging. Not trivial, not impossible.
4. **It's repeatable.** Unlike the Legend title, coffee can be earned weekly.
5. **It builds the habit.** A crew member who earns coffee this week will log harder next week to earn it again.

If the coffee perk works — if crew actually want it and earn it — the entire system works. Every other perk is a variation on the same principle: real-world reward for digital consistency.

## captain's Role

The captain is the **central bank**. They:
1. Set perk prices (can adjust based on budget)
2. Honor redemptions (actually buy the coffee)
3. Run `fishcoin distribute` at end of day
4. Can award bonus coins for exceptional work

The system only works if the captain honors the economy. If crew earn coins but can't spend them, the system collapses into a vanity metric. The captain's commitment is the backing currency.

## Why Not Real Money?

Real money creates:
- Tax implications
- Wage disputes
- Legal obligations
- Power dynamics

FishCoin creates:
- Game mechanics
- Social bonding
- Friendly competition
- No legal entanglement

The perk redemption IS real value, but it flows through the captain's discretion, not a contractual obligation. This keeps it fun.

## Metrics for Success

The economy is working if:
1. **Log entry frequency increases** after FishCoin launch
2. **Crew check balances** voluntarily (not just when reminded)
3. **Perks are redeemed** at least weekly
4. **Crew mention coins** in conversation ("I'm 50 away from a beer")
5. **Data quality improves** (more GPS-tagged entries, more catch details)

If none of these happen, the economy is too abstract. Lower perk prices, increase earn rates, or add more immediate perks.

## Future Extensions

- **Inter-vessel trading:** Boats in the same fleet trade FishCoin for shared resources
- **Market prices:** Fish prices in FishCoin, not just USD
- **Crew betting:** Wager coins on catch totals (high engagement, low stakes)
- **Achievement minting:** NFT-style badges for legendary achievements (purely cosmetic)
