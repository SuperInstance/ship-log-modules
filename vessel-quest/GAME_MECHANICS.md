# 🎮 Vessel Quest — Deep Game Mechanics

> A design document for the systems that turn vessel operations into a living game world.
> 
> **Scope:** Quest chains, world events, crew roles & abilities, progression modifiers, leaderboard seasons, hidden mechanics.
>
> **Audience:** Engineers implementing the next iteration of `index.html` and supporting modules.
> 
> **Foundation (already built):** 10-rank ladder, 30+ achievements, 9 daily quests, seasonal multipliers (1.10–1.30), lore fragments, epithets. This document extends that foundation — it does not replace it.

---

## Table of Contents

1. [Quest Chain System](#1-quest-chain-system) — 6 multi-step storylines
2. [World Events](#2-world-events) — 8 limited-time global events
3. [Crew Roles & Abilities](#3-crew-roles--abilities) — 5 roles × 3 abilities = 15 abilities
4. [Progression Modifiers](#4-progression-modifiers) — Multiplier stacking rules
5. [Leaderboard Seasons](#5-leaderboard-seasons) — Weekly / Monthly / Seasonal / Yearly
6. [Hidden Mechanics](#6-hidden-mechanics) — 10 secret systems

---

# 1. Quest Chain System

## 1.1 Architecture

Quest chains are **multi-step storylines** that span days or weeks. Each chain has a narrative arc, a sequence of unlockable steps, and unique final rewards that go beyond XP (titles, badges, FishCoin currency, cosmetic effects).

### Data model

```js
// Stored in localStorage['vessel_quest_chains']
{
  activeChains: {
    ghost_gear: {
      chainId: 'ghost_gear',
      acceptedAt: 1721000000000,
      currentStep: 3,           // index of next uncompleted step
      completedSteps: [0, 1, 2],
      branchChoice: null,       // 'A' | 'B' once branch step is reached
      completedAt: null
    }
  },
  completedChains: {
    ghost_gear: { completedAt: 1722000000000, branch: 'A', reward: { fishcoin: 500, badge: 'ghost_warden' } }
  },
  abandonedChains: []          // chains the user explicitly abandoned
}
```

### Step structure

```js
{
  id: 'gg_step_3',                    // unique step id
  index: 3,                           // position in chain (0-based)
  name: 'Recovery Operation',
  narrative: 'You mark the GPS coordinates...',     // shown when unlocked
  objective: 'Bring the gear back aboard or arrange pickup',
  icon: '🎣',
  xp: 200,
  unlockCondition: (state) => state.completedSteps.includes(2),
  completionCheck: (stats, raw) => raw.recoveredGhostGear >= 1,
  timeLimit: null,                    // null = no limit, else ms
  isBranch: false,
  choices: null
}
```

### Branching

A step can declare `isBranch: true` with a `choices` array. When the user reaches that step, they pick A or B. The choice is stored in `branchChoice` and downstream steps reference it. Once a branch is chosen, the alternative steps become unavailable.

### Acceptance flow

1. Chain becomes **available** when its prerequisites are met (e.g., rank ≥ X, or stat ≥ Y).
2. User sees it on the quest board and clicks "Accept" → moves to `activeChains`.
3. Steps unlock sequentially as the previous step's `completionCheck` returns true.
4. The final step's completion marks the chain as complete and grants rewards.
5. Chains can be **abandoned** (right-click → abandon) with a 24-hour cooldown before re-acceptance.

### Acceptance limits

- **Max 3 active chains** at once per crew member.
- **1 chain offered per day** at random from the available pool (weighted by prerequisite satisfaction).
- Chains are **role-gated** when relevant (e.g., Mentor's Path requires Captain rank).

---

## 1.2 Chain Catalog

### Chain 1: 👻 The Ghost Gear

**Narrative Arc:** *Setup → Investigation → Climax → Resolution*
Ghost fishing gear — lost nets, lines, traps — kills marine life for decades. Your crew discovers one and decides to act.

| Step | Name | Objective | XP | Trigger |
|------|------|-----------|-----|---------|
| 0 | First Sight | Spot adrift gear at sea | 50 | Log entry tagged `ghost_gear` or containing "ghost gear" / "adrift net" |
| 1 | Mark the Spot | GPS-tag the location | 100 | Log entry with GPS coords within 0.01° of step-0 location, timestamp within 7 days |
| 2 | Report It | Notify maritime authority (or note in log) | 100 | Log entry with text matching "report.*ghost\|report.*adrift\|notified.*coast guard" |
| 3 | Recovery Operation | Recover the gear or arrange pickup | 250 | Maintenance task `ghost_gear_recovery` marked complete OR log entry confirming pickup |
| 4 | Document Impact | Photo + species impact notes | 200 | Log entry with photo attachment AND 100+ char text mentioning species |
| 5 | **BRANCH** | Choose path | 300 | See below |

**Branch A — Systemic Change:** Set up a reporting protocol with other boats in your fleet.
- Reward: Title `"Ghost Gear Warden"`, badge `"🌊 Warden of the Deep"`, 200 FishCoin.

**Branch B — Research Donation:** Donate recovered gear to a marine research institution.
- Reward: 1000 FishCoin, badge `"🔬 Citizen Scientist"`, cosmetic ship skin `ghost-net-blue`.

**Final completion bonus:** +500 XP if chain finished within 30 days of acceptance.

**Prerequisites:** Rank 2 (Boatswain) or higher.

---

### Chain 2: ⭐ Perfect Week

**Narrative Arc:** *Seven days of discipline. No skips. No slop. No shortcuts.*

| Step | Name | Objective | XP |
|------|------|-----------|-----|
| 0 | Day One Discipline | Full pre-departure checklist + 1 log + 1 maintenance tick | 150 |
| 1 | Day Two | Same as above | 175 |
| 2 | Day Three | Same | 200 |
| 3 | Day Four | Same | 225 |
| 4 | Day Five | Same | 250 |
| 5 | Day Six | Same | 275 |
| 6 | Day Seven | Same | 300 |

**Completion Conditions (per step):**
- Checklist completion = 100%
- At least 1 log entry that day
- At least 1 maintenance item completed or verified
- Zero overdue maintenance tasks at end of day

**Final rewards:**
- Title: `"The Flawless"`
- Badge: `"🌟 Perfect Week Pin"` (animated gold border)
- Bonus: 1000 XP if completed with **zero** maintenance task ever overdue during the 7 days
- Bonus: 500 FishCoin if completed in consecutive calendar days (no gaps)

**Prerequisites:** Rank 3 (Third Mate) or higher.

**Time limit:** 14 days from acceptance. If a day is missed, chain fails.

---

### Chain 3: 🐟 Species Master

**Narrative Arc:** *Become the boat's ichthyologist. Learn every fish you touch.*

| Step | Name | Objective | XP |
|------|------|-----------|-----|
| 0 | First Discovery | Log a new species (different from any logged before) | 75 |
| 1 | Three Down | 3 unique species logged | 125 |
| 2 | Halfway There | 5 unique species logged | 200 |
| 3 | Quick Study | 7 unique species logged | 275 |
| 4 | Veteran Observer | 10 unique species logged | 500 |
| 5 | **BRANCH** | Choose path | 300 |

**Unique species counter** tracks `species.*` tags in catch entries or species mentioned in log text (case-insensitive match against known species database).

**Branch A — The Teacher:** Write species field guide entries for the vessel's wiki.
- Reward: Title `"Ichthyologist"`, badge `"📖 Species Sage"`, 500 FishCoin.

**Branch B — The Scientist:** Submit structured species data to a research program.
- Reward: 1500 FishCoin, badge `"🧬 Data Contributor"`, unlocks `species_sightings` dashboard widget.

**Final completion bonus:** +300 XP for each species beyond 10 logged during the chain (uncapped).

**Prerequisites:** Rank 1 (Deckhand) — accessible to all.

---

### Chain 4: 🗺️ The Old Route

**Narrative Arc:** *A century ago, a fishing captain logged a route in this same water. Trace it. Compare it. Learn what changed.*

| Step | Name | Objective | XP |
|------|------|-----------|-----|
| 0 | The Discovery | Read the historical log entry (provided in quest modal) | 50 |
| 1 | Plan the Route | Create a trip with waypoints matching historical route | 200 |
| 2 | Sail the Path | Travel the route (GPS trail within 1 nm of each waypoint) | 400 |
| 3 | Note Differences | Log 3+ entries comparing current vs. historical conditions | 300 |
| 4 | Submit Report | Write a 500+ character retrospective entry | 250 |
| 5 | **BRANCH** | Choose path | 300 |

**Historical route data:** A bundled JSON file `historical_routes.json` ships with 6 pre-built routes from fictional (but realistic) historical captains (1920s–1970s). Routes have 4–8 waypoints and a flavor text entry from the original log.

**Branch A — Publish:** Submit your comparison report to a maritime archive.
- Reward: Title `"Historian of the Sea"`, badge `"📜 Maritime Scholar"`, 200 FishCoin.

**Branch B — Keep It:** Keep the route data private for the vessel's exclusive use.
- Reward: 1000 FishCoin, title `"Keeper of Routes"`, unlocks "Historical Overlay" map mode.

**Final completion bonus:** +1000 XP if the route was completed without deviating more than 5 nm from waypoints.

**Prerequisites:** Rank 4 (Second Mate) or higher. Trip Planner module required.

---

### Chain 5: ⛈️ Storm Season

**Narrative Arc:** *Weather builds. Pressure drops. You watch the barometer and decide when to run.*

| Step | Name | Objective | XP |
|------|------|-----------|-----|
| 0 | Barometer Falling | Log entry mentioning incoming weather | 75 |
| 1 | Secure the Deck | Complete storm-prep maintenance checklist (5+ items) | 200 |
| 2 | Weather the Storm | Log 3+ entries during storm window (weather: storm/gale) | 350 |
| 3 | Aftermath Report | Damage assessment log entry | 200 |
| 4 | Repair & Restore | Complete all storm-related maintenance tasks | 400 |
| 5 | Lessons Learned | Write 300+ char retrospective | 150 |
| 6 | **BRANCH** | Choose path | 300 |

**Storm window detection:** Triggered when the vessel's weather logs show sustained winds > 30 kt or sea state > 4 for ≥ 6 hours.

**Branch A — Crew Training:** Run a storm protocol drill with the crew.
- Reward: Title `"Storm Captain"`, badge `"🌪️ Eye of the Storm"`, 500 FishCoin.

**Branch B — Insurance Documentation:** Build a complete insurance claim dossier.
- Reward: 2000 FishCoin, badge `"📋 Meticulous Record Keeper"`, unlocks `insurance_report` PDF export.

**Final completion bonus:** +750 XP if all crew members logged at least once during the storm.

**Prerequisites:** Rank 3 (Third Mate) or higher. Cannot be started in winter (real storm season).

---

### Chain 6: 👨‍🏫 Mentor's Path

**Narrative Arc:** *A green hand steps aboard. Show them the ropes. Watch them become a mariner.*

| Step | Name | Objective | XP |
|------|------|-----------|-----|
| 0 | Welcome Aboard | Add new crew member to roster with role = "trainee" | 75 |
| 1 | Safety First Together | Complete safety checklist with trainee present (within 7 days) | 150 |
| 2 | First Solo Entry | Trainee logs their first entry without prompting | 200 |
| 3 | Week One Done | Trainee has 5+ entries | 250 |
| 4 | Finding Their Sea Legs | Trainee has 20+ entries | 350 |
| 5 | Solo Trip | Trainee completes their first trip as acting mate | 500 |
| 6 | **BRANCH** | Choose path | 400 |

**Trainee system:**
- A crew member is flagged `isTrainee: true` when added.
- Trainees get a "Mentor Active" indicator in the crew list.
- Steps check trainee's stats (entries, trips, checklists).
- Mentor (the player who accepted the chain) earns bonus XP for each trainee milestone.

**Branch A — The Mentor:** Continue developing the trainee as a long-term protégé.
- Reward: Title `"The Mentor"`, badge `"🧑‍🏫 Teacher of the Sea"`, 750 FishCoin. Trainee's `isTrainee` flag is cleared; they become a full crew member with bonus epithet candidate.

**Branch B — Send Them Off:** Graduate the trainee to another vessel.
- Reward: 1500 FishCoin, badge `"🌱 Nurturer"`, the trainee becomes a "graduate" in the alumni roster (persists as a record).

**Final completion bonus:** +500 XP per month the trainee remained active before graduation.

**Prerequisites:** Captain rank (level 6+). Crew size ≥ 2.

---

## 1.3 Implementation Notes

### Storage

```js
const CHAIN_STATE_KEY = 'vessel_quest_chains';
const CHAIN_DEFS_KEY = 'vessel_quest_chain_definitions'; // bundled JSON, not mutable
```

### Detection helpers

Most chain steps use **detection helpers** that scan recent logs/maintenance for keywords or stat thresholds:

```js
const CHAIN_HELPERS = {
  ghostGearMentioned: (log) => /ghost gear|adrift net|lost gear|derelict/i.test(log.text),
  gpsNearby: (logA, logB, thresholdDeg = 0.01) => {
    const dLat = Math.abs((logA.lat || 0) - (logB.lat || 0));
    const dLon = Math.abs((logA.lon || 0) - (logB.lon || 0));
    return dLat < thresholdDeg && dLon < thresholdDeg;
  },
  stormEntry: (log) => /storm|gale|squall|beaufort [7-9]|rough seas/i.test(log.text),
  crewAdded: (roster, days = 7) => roster.some(c => Date.now() - c.addedAt < days * 86400000),
  uniqueSpecies: (logs) => new Set(logs.flatMap(l => l.species || [])).size,
};
```

### Chain rendering

Each chain appears as a **collapsible card** in the quest panel:
- Header: chain icon + name + progress dots (●●●○○)
- Body: current step narrative + objective + "How to complete" hint
- Footer: XP reward, time remaining, abandon button
- Completed chains move to a "Trophy Case" tab

### Anti-abuse

- Chains check `state.acceptedAt` — no retroactive completion of past steps
- GPS proximity checks require actual logged coordinates (not fabricated)
- Photo requirements: must be image MIME type, ≥ 5 KB, captured within 1 hour of log timestamp
- Time limits prevent indefinite grinding on a single chain

---

# 2. World Events

## 2.1 Architecture

World events are **server-side (or scheduled) limited-time modifiers** that affect all crew members simultaneously. They layer on top of base XP, seasonal multipliers, role abilities, and progression modifiers.

### Data model

```js
// Stored in localStorage['vessel_quest_events']
{
  active: [
    {
      eventId: 'the_run_2026_summer',
      startedAt: 1721000000000,
      endsAt: 1721604000000,        // 7 days later
      state: {                       // event-specific state
        catchesLogged: 12,
        leaderboard: [{crewId, score}]
      }
    }
  ],
  history: [
    { eventId: '...', completedAt: 1722000000000, finalRank: 2, reward: {...} }
  ]
}
```

### Event lifecycle

1. **Triggered** by time (cron-style) or stat threshold (e.g., overdue maintenance count).
2. **Activated** with a system-wide notification banner.
3. **Tracked** via per-event state object.
4. **Ended** when duration expires.
5. **Rewarded** based on event-specific scoring.

### Modifier stacking order

When an event is active, modifiers are applied in this fixed order (bottom of stack → top):

```
base_xp
  × role_passive_multiplier
  × seasonal_multiplier
  × event_multiplier         ← world events layer here
  × modifier_multiplier      ← progression modifiers (rest, combo, etc.)
  + flat_modifier_bonus      ← first-of-day, milestone, etc.
  = final_xp
```

---

## 2.2 Event Catalog (8 events)

### Event 1: 🐟 The Run

> *"The fish are moving. The water's alive. Drop everything and log every catch."*

| Attribute | Value |
|-----------|-------|
| **Trigger** | Calendar-based: first Monday of each fishing-run season (Pacific salmon: May, Jun, Jul; tuna: Aug–Sep; cod: Oct–Nov). Configurable per region. |
| **Duration** | 7 days |
| **Modifier** | `2.0× XP` on catch reports |
| **Scoring** | Total weight of catches logged during event window |
| **Rewards (per crew)** | |
| — Top 1 | Badge `"🎣 Master of the Run"`, 2000 FishCoin, Title `"The Runner"` |
| — Top 10% | Badge `"🐟 Run Veteran"`, 500 FishCoin |
| — Participation | Badge `"🌊 Caught the Run"` + 100 FishCoin if ≥ 5 catches logged |
| **Catch-up Rule** | None — participation requires being active during the run |

**Implementation notes:**
- Run dates are stored in `runs.json` (regional, annually updated).
- Modifier applies to base XP of catch-category logs only.
- Anti-cheat: catches must have weight field; weight must be > 0; species must match a known fish.

---

### Event 2: 🏆 Deadliest Catch Week

> *"Seven days. Who logs the most? Honor and FishCoin on the line."*

| Attribute | Value |
|-----------|-------|
| **Trigger** | Random: ~1× per quarter, scheduled on a Wednesday to maximize mid-week activity |
| **Duration** | 7 days |
| **Modifier** | `1.5× XP` on all log entries |
| **Scoring** | Number of log entries during event window (catches weighted ×2) |
| **Rewards** | |
| — #1 | Badge `"👑 Captain of the Logs"`, 1000 FishCoin, Title `"Top Boat"` |
| — #2–3 | Badge `"🥈 First Mate of Logs"`, 500 FishCoin |
| — #4–10 | Badge `"🎖️ Crew of the Week"`, 250 FishCoin |
| **Tie-breaker** | Total distance traveled during event |

**Implementation notes:**
- Leaderboard shows real-time rank per crew.
- Only one event of this kind runs at a time per quarter.
- "Logs" excludes empty/test entries (must have ≥ 20 characters of text).

---

### Event 3: 🔧 Maintenance Marathon

> *"The boat doesn't fish if she doesn't float. Weekend of wrench-turning."*

| Attribute | Value |
|-----------|-------|
| **Trigger** | Last weekend of each month (Sat 00:00 → Mon 00:00 local time) |
| **Duration** | 48 hours |
| **Modifier** | `3.0× XP` on maintenance task completion |
| **Scoring** | Maintenance tasks completed (early completion ×1.5 bonus) |
| **Rewards** | |
| — 10+ tasks | Badge `"🏃 Marathoner"`, 200 FishCoin |
| — 25+ tasks | Badge `"🏃‍♂️ Ultra-Marathoner"`, 500 FishCoin, Title `"Wrencher"` |
| — Top of crew | Badge `"🥇 Top Wrench"` |

**Implementation notes:**
- "Early completion" = task completed > 7 days before due date.
- Stacks with Rest Bonus but not with Combo (one or the other).
- Doubles as anti-overdue mechanic — incentivizes catching up.

---

### Event 4: 📋 The Logjam

> *"Overdue tasks piling up. Break the jam."*

| Attribute | Value |
|-----------|-------|
| **Trigger** | Automatic: fires when vessel has ≥ 3 overdue maintenance tasks AND no event currently active |
| **Duration** | Until cleared + 7 days grace period |
| **Modifier** | `2.0× XP` per overdue task cleared (base), scaling `+0.5×` per task cleared beyond first |
| **Scoring** | Tasks cleared before deadline-equivalent (overdue → cleared) |
| **Rewards** | |
| — Cleared all overdue | Badge `"🌊 Logjam Breaker"`, 300 FishCoin, Title `"The Unclogger"` |
| — Cleared ≥ 5 | Badge `"🪓 Jam Buster"`, 150 FishCoin |
| — Cleared 1–4 | Badge `"🧹 Tidier"`, 50 FishCoin |

**Implementation notes:**
- Caps at `5.0×` to prevent runaway multipliers on huge backlogs.
- "Overdue" reset only counts tasks completed during event window.
- Event auto-ends if all overdue tasks are cleared.

---

### Event 5: 🌅 First Light

> *"The early bird gets the bonus."*

| Attribute | Value |
|-----------|-------|
| **Trigger** | Spring equinox week (Mar 17–23) + repeated during autumn equinox (Sep 22–28) |
| **Duration** | 7 days |
| **Modifier** | `1.5× XP` on logs timestamped before 06:00 local |
| **Scoring** | Number of early-bird logs |
| **Rewards** | |
| — 10+ early logs | Badge `"🌅 Dawn Master"`, 200 FishCoin |
| — 25+ early logs | Badge `"☀️ First Light Sage"`, 500 FishCoin, Title `"Dawn Patrol"` |
| — 50+ early logs | Badge `"🌄 Solstice Runner"`, 1000 FishCoin |

**Implementation notes:**
- "Early" = log timestamp hour < 6 in vessel's home port timezone.
- Stacks with seasonal spring multiplier (so spring = 1.5 × 1.15 = 1.725× XP base).
- No penalty for late logs — only bonuses for early.

---

### Event 6: 🔥 Iron Mariner Challenge

> *"Build the streak. Show no weakness."*

| Attribute | Value |
|-----------|-------|
| **Trigger** | Random: ~1× per 2 months, announced 48 hours in advance |
| **Duration** | 14 days |
| **Modifier** | Streak bonus is **doubled** during event (instead of 25 XP/day, +50 XP/day) |
| **Scoring** | Highest active streak achieved during event |
| **Rewards** | |
| — Streak 14 | Badge `"🔥 Iron Streak"`, 250 FishCoin |
| — Streak 21+ | Badge `"⚡ Iron Mariner"`, 500 FishCoin, Title `"The Constant"` |
| — Streak 30+ | Badge `"💎 Streak Master"` (legendary), 1500 FishCoin |

**Implementation notes:**
- Requires at least 1 log per calendar day to maintain streak.
- Streak continues after event ends (does not reset).
- "Highest active streak" = max of (current streak, longest streak during event).

---

### Event 7: 🐢 Ghost Net Cleanup

> *"Pull the past from the water. Free the future."*

| Attribute | Value |
|-----------|-------|
| **Trigger** | Random summer event (~1× between Jun 15 and Aug 31), requires maritime authority cooperation flag enabled |
| **Duration** | 3 days |
| **Modifier** | `5.0× XP` on ghost gear reports and `3.0× XP` on related maintenance |
| **Scoring** | Ghost gear items reported + recovered (weighted 1:3) |
| **Rewards** | |
| — 1+ report | Badge `"🌊 Ghost Gear Hunter"`, 100 FishCoin |
| — 5+ reports or 1+ recovered | Badge `"🐢 Marine Protector"`, 300 FishCoin, Title `"Warden of the Deep"` |
| — Top of crew | Badge `"🌟 Conservation Champion"`, 1000 FishCoin |

**Implementation notes:**
- Tied to Quest Chain 1 (The Ghost Gear) — completing the chain during the event grants chain rewards + event rewards.
- Ghost gear detection uses `CHAIN_HELPERS.ghostGearMentioned`.
- Recovered gear must have GPS + photo for full scoring.

---

### Event 8: 🎯 Highliner Tournament

> *"Compete across the season. The best fishers rise."*

| Attribute | Value |
|-----------|-------|
| **Trigger** | Quarterly at season changes (Mar 20, Jun 21, Sep 22, Dec 21) |
| **Duration** | 7 days |
| **Modifier** | `2.0× XP` on top-10% species (rarest catches by rarity score) |
| **Scoring** | Composite: 60% total catch weight, 25% species diversity, 15% log quality (avg entry length) |
| **Rewards** | |
| — #1 | Badge `"🏆 Tournament Champion"`, 5000 FishCoin, Title `"Highliner of the Quarter"` |
| — #2–3 | Badge `"🥈 Top Three"`, 2000 FishCoin |
| — #4–10 | Badge `"🎖️ Tournament Finalist"`, 500 FishCoin |

**Species rarity scoring:**
```js
const SPECIES_RARITY = {
  salmon: 1.0, cod: 1.0, tuna: 1.2, halibut: 1.5,
  shark: 2.5, swordfish: 3.0, whale: 5.0, 'sunfish': 4.0,
  // etc — bundled in species.json
};
function rarityScore(species, weight) {
  return (SPECIES_RARITY[species] || 1.0) * Math.log10(weight + 10);
}
```

**Implementation notes:**
- Log quality = average characters per entry (excluding test/empty entries).
- Composite score formula: `0.6 * weight_score + 0.25 * species_score + 0.15 * quality_score` (each normalized 0–100).
- Anti-cheat: catches must have valid species in known list.

---

## 2.3 Event Notification UX

When an event starts:
- Toast notification at top: `"🌊 THE RUN has begun! Catch reports earn 2× XP for 7 days."`
- Persistent banner with countdown timer
- Event-specific section in the quest panel showing:
  - Current event modifier (visible multiplier on XP gains)
  - Personal progress bar
  - Live leaderboard (if competitive)

---

# 3. Crew Roles & Abilities

## 3.1 Role Architecture

Each crew member has a **role** (captain, mate, deckhand, engineer, observer) that determines their **passive multipliers** and **active abilities**. Roles are assigned at crew creation and can be changed by the captain (with a 7-day cooldown).

### Role XP tracking

```js
// Each crew member accumulates role XP separately
crewMember: {
  id: 'cm_abc123',
  name: 'Hank',
  role: 'mate',
  roleXp: 1850,
  roleTier: 2,  // 1, 2, or 3 — unlocks abilities
  abilities: {
    trip_architect: true,    // tier 1
    efficiency_eye: true,    // tier 2
    route_master: false      // tier 3 — not yet unlocked
  }
}
```

### Tier thresholds

- **Tier 1** (abilities unlocked at role assignment): always available
- **Tier 2** (unlocked at 500 role XP): improved ability
- **Tier 3** (unlocked at 2000 role XP): full active ability

Role XP is earned the same way as vessel XP but **filtered by activity type** (e.g., engineer earns role XP from maintenance, deckhand from catch logs).

---

## 3.2 Role Catalog (15 abilities)

### ⚓ Captain

The captain runs the boat. Their abilities center on **leadership, economy, and morale.**

#### Ability 1: 🎯 Daily Bounty *(Tier 1, Passive + Active)*

**Description:** Captain designates one "bounty" action per day. Any crew member who completes that action earns +50 XP bonus.

**Activation:** Once per day, captain sets the bounty via UI ("Today's Bounty: Complete maintenance tasks").

**Effect:**
```js
if (bounty.active && actionMatches(action, bounty.actionType)) {
  xp += 50;
}
```

**Synergies:** Stacks with role multipliers. Captain earns +10% of all bounty XP claimed by crew (mentor bonus).

---

#### Ability 2: 🪙 Coin Mint *(Tier 2, Active)*

**Description:** Award 100 FishCoin to any crew member.

**Activation:** 1 use per day, manual button in crew panel.

**Effect:**
```js
function mintCoin(targetCrewId, amount = 100) {
  if (captain.coinMintsToday >= 1) return error('Cooldown');
  transferFishcoin(captain.id, targetCrewId, amount);
  captain.coinMintsToday += 1;
  logEvent('coin_minted', { from: captain.id, to: targetCrewId, amount });
}
```

**Limit:** Captain must have the FishCoin to give. Daily reset at 00:00 local.

---

#### Ability 3: 🎲 Double or Nothing *(Tier 3, Active)*

**Description:** Activate a 24-hour "high stakes" mode. Next log entry has 50% chance to earn 2× XP or 50% chance to earn 0× XP.

**Activation:** Once per week, manual button.

**Effect:**
```js
function activateDoubleOrNothing() {
  if (captain.doubleOrNothingWeek) return error('Used this week');
  captain.doubleOrNothingActive = true;
  captain.doubleOrNothingExpires = Date.now() + 86400000;
}

function applyDoubleOrNothing(baseXp) {
  if (!captain.doubleOrNothingActive) return baseXp;
  if (!captain.doubleOrNothingResolved) {
    // First entry triggers resolution
    const won = Math.random() < 0.5;
    captain.doubleOrNothingResolved = true;
    captain.doubleOrNothingWon = won;
    return won ? baseXp * 2 : 0;
  }
  // Subsequent entries during window get normal XP
  return baseXp;
}
```

**Visual cue:** Captain's avatar shows dice 🎲 icon during active window. After resolution, color codes gold (won) or red (lost).

---

### 🧭 Mate

The mate plans trips, manages logistics, and watches efficiency.

#### Ability 1: 📐 Trip Architect *(Tier 1, Passive)*

**Description:** Planning a trip grants +200 XP to the mate. All logs during that trip get +1.5× XP.

**Trigger:** Creating a trip with ≥ 3 waypoints.

**Effect:**
```js
if (action === 'trip_plan' && mate === planner && waypoints.length >= 3) {
  xp += 200;
  trip.architectBonus = 1.5;  // applies to all logs until trip end
}
```

---

#### Ability 2: 📊 Efficiency Eye *(Tier 2, Passive UI)*

**Description:** Unlocks the **Efficiency Dashboard** widget — a side panel showing per-trip stats:

- Catch-per-hour ratio
- Fuel-per-mile efficiency
- Time-to-first-catch
- Cost-per-pound
- Crew utilization hours

**Effect:** Information only — no XP modifier. But the mate sees patterns invisible to others.

**Display:** New panel in `index.html` accessible via tab toggle.

---

#### Ability 3: 🗺️ Route Master *(Tier 3, Active)*

**Description:** Once per trip, declare a "Master Route." Completing that trip grants +50% completion XP and unlocks a "Route Replay" visualization.

**Activation:** Set during trip planning.

**Effect:**
```js
if (trip.masterRoute && trip.completed) {
  completionXp = Math.round(completionXp * 1.5);
  trip.routeReplayUnlocked = true;  // shows GPS trail overlay
}
```

---

### 🪢 Deckhand

The deckhand is on the lines, sorting catch, working the deck.

#### Ability 1: 🐟 Catch Counter *(Tier 1, Passive)*

**Description:** All catch reports earn 2× XP.

**Effect:**
```js
if (action === 'catch_log' && author.role === 'deckhand') {
  xp *= 2;
}
```

---

#### Ability 2: 🏋️ Heavy Haul *(Tier 2, Passive)*

**Description:** Catch reports with weight > 100 lbs earn +50 bonus XP.

**Effect:**
```js
if (action === 'catch_log' && catch.weight > 100) {
  xp += 50;
  if (catch.weight > 500) xp += 100;  // escalating bonus
}
```

---

#### Ability 3: 👁️ Sea Eyes *(Tier 3, Passive)*

**Description:** The first log entry of any watch period earns +25 XP ("watch starter bonus").

**Effect:**
```js
function isFirstOfWatch(authorId, watch) {
  const key = `${authorId}:${watch}:${date}`;
  return !watchStartsLogged[key];
}
if (isFirstOfWatch(author.id, log.watch)) {
  xp += 25;
  watchStartsLogged[`${author.id}:${log.watch}:${date}`] = true;
}
```

**Synergy:** Watch = dawn (06:00–12:00), day (12:00–18:00), evening (18:00–24:00), night (00:00–06:00).

---

### 🔧 Engineer

The engineer keeps the boat running.

#### Ability 1: ⚙️ Wrench Master *(Tier 1, Passive)*

**Description:** All maintenance task completions earn 2× XP.

**Effect:**
```js
if (action === 'maint_complete' && author.role === 'engineer') {
  xp *= 2;
}
```

---

#### Ability 2: 🔬 Engine Sight *(Tier 2, Passive UI)*

**Description:** Unlocks the **Engine Health Dashboard** — shows:
- Engine hours (current, since last service)
- Oil pressure trend (last 30 days)
- Temperature anomalies (any reading > manufacturer spec)
- Fuel consumption rate vs. baseline
- Next-service countdown for each component

**Effect:** Information only. No XP modifier. Helps engineer prioritize.

---

#### Ability 3: ⏰ Predictive Maintenance *(Tier 3, Passive)*

**Description:** Maintenance tasks completed before due date earn +30 XP early-completion bonus.

**Effect:**
```js
if (action === 'maint_complete' && daysEarly(task) > 0) {
  xp += 30;
  if (daysEarly(task) > 7) xp += 20;  // very early bonus
}
```

**Synergy:** Stacks with Maintenance Marathon event modifier.

---

### 🔬 Observer

The observer is the data quality gatekeeper — science, compliance, precision.

#### Ability 1: 📍 Data Quality *(Tier 1, Passive)*

**Description:** Log entries with GPS + photo + ≥ 100 char text earn 1.5× XP.

**Effect:**
```js
const quality = (log.gps ? 1 : 0) + (log.photo ? 1 : 0) + (log.text.length >= 100 ? 1 : 0);
if (quality === 3 && author.role === 'observer') {
  xp *= 1.5;
}
```

---

#### Ability 2: 🏷️ Compliance Officer *(Tier 2, Passive)*

**Description:** Logs with proper tagging (species, weather, watch) earn +20 XP per correct tag.

**Effect:**
```js
const tags = ['species', 'weather', 'watch'];
const correctTags = tags.filter(t => log[t] && isValidTag(t, log[t])).length;
if (author.role === 'observer') {
  xp += correctTags * 20;
}
```

---

#### Ability 3: 📑 Audit Trail *(Tier 3, Active)*

**Description:** Submit a weekly compliance report. If ≥ 80% of the week's logs meet quality standards, earn 50 XP × (quality percentage).

**Activation:** Once per week, manual button in observer panel.

**Effect:**
```js
function submitAuditReport() {
  const weekLogs = getLogsFromLastWeek();
  const qualityRate = weekLogs.filter(meetsQualityStandard).length / weekLogs.length;
  if (qualityRate >= 0.8) {
    xp += Math.round(50 * qualityRate);
  }
}
```

---

## 3.3 Role Synergies

Some abilities interact to produce compound effects:

| Combo | Effect |
|-------|--------|
| Captain bounty = maintenance → Engineer completes it | Engineer gets 2× (role) × 1.5× (bounty) = 3× XP |
| Mate plans trip → Deckhand logs catches during trip | Deckhand gets 2× (role) × 1.5× (architect) = 3× XP |
| Observer audits while Engineer pre-completes maintenance | Both earn their bonuses + audit quality bonus |
| Captain mints coin to deckhand with catch streak | Visible recognition + retained multiplier |

---

## 3.4 Implementation Notes

### Role assignment

```js
function assignRole(crewId, role) {
  const crew = getCrew(crewId);
  crew.role = role;
  crew.roleXp = 0;
  crew.roleTier = 1;
  crew.abilities = ROLE_ABILITIES[role].tier1;
  crew.lastRoleChange = Date.now();
  // 7-day cooldown on re-assignment
}

const ROLE_COOLDOWN_MS = 7 * 86400000;
```

### Role XP calculation

```js
function calculateRoleXp(action, author) {
  const map = {
    catch_log: ['deckhand', 'observer'],
    maint_complete: ['engineer'],
    trip_plan: ['mate'],
    safety_check: ['observer', 'captain'],
    fuel_log: ['engineer', 'mate'],
    log_entry: ['captain', 'mate']  // general
  };
  return map[action]?.includes(author.role) ? baseXpForAction(action) : 0;
}
```

---

# 4. Progression Modifiers

## 4.1 The Modifier Stack

Every XP gain flows through this exact stack (applied bottom-up):

```
base_xp
  ─────────────────────────────────
  1. ROLE PASSIVE MULTIPLIER       (captain: 1.0, mate: 1.1, deckhand: 1.0, engineer: 1.0, observer: 1.05)
  2. SEASONAL MULTIPLIER           (spring 1.15, summer 1.25, fall 1.10, winter 1.30)
  3. EVENT MULTIPLIER              (when active, see World Events §2)
  4. PROGRESSION MODIFIERS:        
     a. Rest Bonus                 (×2.0 after 24h idle)
     b. Combo System               (×1.0 to ×3.0 based on combo count)
     c. Perfection Streak          (×1.0 to ×2.0 based on perfect days)
     d. Mentor Bonus               (Captain gets +10% of crew XP)
  ─────────────────────────────────
  5. FLAT BONUSES:                  
     a. First of Day               (+10 XP)
     b. Lucky Streak               (10× XP on 1-in-100 roll)
     c. Milestone                  (+50 XP on round-number unlocks)
     d. Quest Step                 (+quest.xp)
  ─────────────────────────────────
  = FINAL XP
```

### Stack formula

```js
function calculateFinalXp(action, author, ctx) {
  let xp = BASE_XP[action];
  
  // 1. Role passive
  xp *= ROLE_MULTIPLIERS[author.role];
  
  // 2. Seasonal
  xp *= getCurrentSeasonalMultiplier();
  
  // 3. Event
  if (ctx.activeEvent) xp *= ctx.activeEvent.modifier;
  
  // 4. Progression modifiers (these are MULTIPLICATIVE with each other)
  xp *= getRestMultiplier(author);
  xp *= getComboMultiplier(author);
  xp *= getPerfectionMultiplier(author);
  xp *= getMentorBonus(author, ctx);  // applied to captain separately
  
  // 5. Flat bonuses
  if (ctx.isFirstOfDay) xp += 10;
  if (ctx.luckyRoll) xp *= 10;
  if (ctx.milestone) xp += 50;
  if (ctx.questStep) xp += ctx.questStep.xp;
  
  return Math.round(xp);
}
```

---

## 4.2 Rest Bonus

**Design intent:** Anti-burnout. Reward crew who step away and come back fresh.

```js
function getRestMultiplier(author) {
  const lastLog = author.lastLogTimestamp || 0;
  const hoursSince = (Date.now() - lastLog) / 3600000;
  
  if (hoursSince >= 24) return 2.0;
  if (hoursSince >= 18) return 1.5;
  if (hoursSince >= 12) return 1.2;
  return 1.0;
}
```

**Visual feedback:** "Well-rested" badge appears next to crew name after 18h idle. "Rested" tag glows on next entry.

**Anti-abuse:** Only applies to the **first log entry** after the idle period. Subsequent entries use base multiplier.

---

## 4.3 Combo System

**Design intent:** Reward bursts of activity (e.g., a deckhand logging 5 catches during a hot bite).

```js
function getComboMultiplier(author) {
  const recentLogs = author.logsLast60Min || [];
  const count = recentLogs.length;
  
  if (count === 0) return 1.0;
  if (count === 1) return 1.1;   // 2nd log in window: +10%
  if (count === 2) return 1.3;   // 3rd: +30%
  if (count === 3) return 1.6;   // 4th: +60%
  if (count >= 4) return 2.0;    // 5+: ×2.0 (capped)
  
  return 1.0;
}
```

**Combo display:**
- Combo counter appears on entry: `"🔥 Combo x3 — next log +60% XP"`
- Counter increments per log within 60-minute window
- Counter resets after 60 minutes of inactivity
- Visible multiplier shown in real-time

**Edge case:** Combo resets at midnight (calendar day boundary), not just from inactivity. This prevents overnight combos from carrying into the next day.

---

## 4.4 First of Day

```js
function isFirstOfDay(authorId, date) {
  const key = `${authorId}:${date}`;
  return !firstOfDayTracker[key];
}

// On first log:
firstOfDayTracker[`${authorId}:${date}`] = true;
xp += 10;
```

**Visual:** "🌅 First light" badge appears next to the entry.

---

## 4.5 Perfection Streak

**Design intent:** Reward consistent, high-quality operations over time.

```js
function getPerfectionMultiplier(author) {
  const perfectDays = author.perfectDaysStreak || 0;
  
  if (perfectDays >= 30) return 2.0;
  if (perfectDays >= 14) return 1.5;
  if (perfectDays >= 7) return 1.3;
  if (perfectDays >= 3) return 1.1;
  return 1.0;
}
```

**"Perfect day" definition:**
- 100% checklist completion
- Zero overdue maintenance tasks at end of day
- At least 1 log entry
- All maintenance tasks completed within their due window

**Streak resets** if any day breaks the streak (missing log OR overdue task).

---

## 4.6 Mentor Bonus

```js
function getMentorBonus(author, ctx) {
  // Captain earns 10% of crew XP, but only from first 10 entries per day per mentee
  if (author.role !== 'captain') return 1.0;
  
  const crewXpToday = ctx.crewXpEarnedByMentees || 0;
  const cap = 10 * ctx.mentees.length * 100;  // soft cap
  
  return 1.0;  // Mentor bonus is APPLIED SEPARATELY, not as a multiplier
}

// Separate award:
function awardMentorBonus(captainId, menteeXp) {
  const menteeLogs = countLogsToday(menteeId);
  if (menteeLogs > 10) return;  // cap at 10 logs/day
  
  captain.bonusXp += Math.round(menteeXp * 0.10);
}
```

**Display:** Captain sees "Mentor Bonus" section in their XP breakdown: `"+47 XP from crew activity"`.

---

## 4.7 Modifier Interaction Examples

**Example 1:** Spring morning, deckhand logs first catch after 30h break during "The Run" event:

```
base_xp = 30 (catch)
× role (deckhand: 1.0)
× seasonal (spring: 1.15)
× event (the_run: 2.0)
× rest (24h+: 2.0)
× combo (first log: 1.0)
× perfection (3 perfect days: 1.1)
+ first of day (+10)
= 30 × 1.0 × 1.15 × 2.0 × 2.0 × 1.0 × 1.1 + 10
= 30 × 5.06 + 10
= 152 + 10
= 162 XP
```

**Example 2:** Engineer completes maintenance during Maintenance Marathon, 5th combo, 2 perfect weeks:

```
base_xp = 50 (maintenance)
× role (engineer: 1.0)
× seasonal (summer: 1.25)
× event (marathon: 3.0)
× rest (3h: 1.0)
× combo (5th: 2.0)
× perfection (14 perfect days: 1.5)
+ early completion (+30)
= 50 × 1.0 × 1.25 × 3.0 × 1.0 × 2.0 × 1.5 + 30
= 562.5 + 30
= 593 XP
```

---

# 5. Leaderboard Seasons

## 5.1 Ranking Architecture

Leaderboards operate on **rolling windows** — they score activity within a defined period, then reset. Four cadences run in parallel:

| Season | Duration | Reset | Aggregation |
|--------|----------|-------|-------------|
| Weekly | 7 days | Monday 00:00 UTC | Total XP earned |
| Monthly | ~30 days | 1st of month 00:00 UTC | Total XP earned |
| Seasonal | ~3 months | Real-world season start (Mar/Jun/Sep/Dec) | Composite score |
| Yearly | 365 days | Jan 1 00:00 UTC | Composite score |

### Composite score formula (seasonal & yearly)

```js
function compositeScore(crew, period) {
  const xp = crew.xpEarnedInPeriod;
  const catchWeight = crew.totalCatchWeightInPeriod;
  const diversity = crew.uniqueSpeciesInPeriod * 100;
  const quality = avgEntryLength(crew.entriesInPeriod);
  const distance = crew.distanceTraveledInPeriod;
  
  return (
    xp * 0.40 +
    catchWeight * 0.25 +
    diversity * 0.15 +
    quality * 0.10 +
    distance * 0.10
  );
}
```

This rewards both **volume** (XP) and **substance** (real catches, real distance).

---

## 5.2 Tier System

Each leaderboard uses 4 visible tiers based on percentile:

| Tier | Threshold | Visual |
|------|-----------|--------|
| 🥇 Platinum | Top 1% (min 1 crew) | Animated gold border + glow |
| 🥇 Gold | Top 3% (or next 2 below Platinum) | Gold border |
| 🥈 Silver | Top 10% | Silver border |
| 🥉 Bronze | Top 25% | Bronze border |
| — | Below 25% | No tier indicator |

**Min crew threshold:** Leaderboards with fewer than 4 crew members don't display tiers — they're too small to be meaningful.

---

## 5.3 Weekly: Crew Member of the Week

**Window:** Monday 00:00 UTC → Sunday 23:59 UTC

**Scoring:** Total XP earned

**Rewards:**
| Rank | FishCoin | Cosmetic | Title (1 week) |
|------|----------|----------|----------------|
| #1 | 500 | Gold crew border | "👑 Crew Member of the Week" |
| #2 | 250 | Silver crew border | "🥈 Runner-Up" |
| #3 | 100 | Bronze crew border | "🥉 Third Wheel" |
| Top 25% | 25 | — | — |

**Display:**
- Live leaderboard widget on main panel
- "Current Rank" badge on crew member profile
- Final results shown Monday morning as celebration modal

---

## 5.4 Monthly: Crew Member of the Month

**Window:** 1st 00:00 UTC → last day 23:59 UTC

**Scoring:** Total XP earned

**Rewards:**
| Rank | FishCoin | Cosmetic | Title (1 month) | Badge |
|------|----------|----------|-----------------|-------|
| #1 | 2000 | Animated avatar frame | "🏆 Crew Member of the Month" | "🌟 Monthly Champion" (permanent) |
| #2 | 1000 | Gold avatar frame | "🥈 Monthly Finalist" | — |
| #3 | 500 | Silver avatar frame | "🥉 Top Three" | — |
| Top 10% | 250 | — | — | — |

**Display:** Featured crew member spotlight — name + photo + stats in header for the following month.

---

## 5.5 Seasonal: Highliner of the Season

**Window:** Real-world fishing seasons
- Spring Salmon: Mar 20 – Jun 20
- Summer Solstice: Jun 21 – Sep 21
- Fall Harvest: Sep 22 – Dec 20
- Winter Off-season: Dec 21 – Mar 19 (special "Off-season Champion" rules apply)

**Scoring:** Composite (40% XP, 25% catch weight, 15% species diversity, 10% entry quality, 10% distance)

**Rewards:**
| Rank | FishCoin | Cosmetic | Title | Badge |
|------|----------|----------|-------|-------|
| #1 | 5000 | Legendary ship skin (unique) | "🎖️ Highliner of the Season" | "🐋 Highliner" (legendary) |
| #2 | 2500 | Epic ship skin | "🚢 Top Boat of [Season]" | "🥈 Season Runner-Up" (epic) |
| #3 | 1500 | Rare ship skin | "🛥️ Top Three" | "🥉 Top Three" (rare) |
| Top 10% | 500 | — | — | "🎖️ Season Finalist" (uncommon) |

**Special:** The seasonal champion's vessel name is engraved in the leaderboard hall of fame (persistent display across years).

---

## 5.6 Yearly: Legend of the Year

**Window:** Jan 1 00:00 UTC → Dec 31 23:59 UTC

**Scoring:** Composite (40% XP, 25% catch weight, 15% species diversity, 10% entry quality, 10% distance)

**Rewards:**
| Rank | FishCoin | Cosmetic | Title | Badge |
|------|----------|----------|-------|-------|
| #1 | 25000 | Animated legendary ship skin + unique avatar border | "👑 Legend of the Year" | "🌟 Hall of Fame" (legendary, permanent) |
| #2 | 10000 | Epic ship skin | "🏆 Runner-Up Legend" | "⭐ Hall of Fame" (epic) |
| #3 | 5000 | Rare ship skin | "🎖️ Top Three Legend" | "🎖️ Hall of Fame" (rare) |
| Top 10% | 1000 | — | — | "📜 Hall of Fame" (uncommon) |

**Display:** Year-end celebration ceremony (modal on Jan 1). Hall of Fame section persists permanently on the leaderboard page.

---

## 5.7 Anti-Cheat & Fairness

### Tiebreakers

When two crew members have identical scores, apply in order:
1. Total distance traveled (more = better)
2. Unique species count (more = better)
3. First-to-achieve timestamp (earlier = better)
4. Random (deterministic seed = combined crew ID hash)

### Anti-cheat measures

- **Log quality threshold:** Entries < 20 characters don't count toward scoring (prevents spam).
- **Catch verification:** Catches must have species + weight fields. Random 10% flagged for photo review.
- **Distance verification:** Distance is calculated from GPS deltas only — manual entry of distance is ignored for scoring.
- **Rate limits:** Maximum 50 logs/day count toward scoring (catches the edge case of compulsive loggers).
- **Bot detection:** Time between consecutive logs: if interval < 10 seconds, the second is flagged.

---

# 6. Hidden Mechanics

## 6.1 Discovery Philosophy

Hidden mechanics are **secret systems** that reward exploration and surprise the crew. They are:
- **Never advertised** — no hints in UI
- **Discoverable** — they happen visibly when triggered (small celebrations, badge animations)
- **Shareable** — players will tell each other, building community lore
- **Not required** — missing them doesn't block progression, but they add flavor

### Discovery UX

When a hidden mechanic triggers:
1. Subtle animation (e.g., screen flash, special sound, badge spawn)
2. Toast: `"🌟 You discovered: [Hidden Mechanic Name]"`
3. Hidden mechanics appear in a separate "Secrets" tab (only those discovered)
4. Each discovery adds a small XP bonus (75 XP for first discovery, 25 for repeats)

---

## 6.2 Hidden Mechanic Catalog (10 systems)

### Hidden 1: 🍀 Lucky Streak

**Trigger:** Every log entry has a 1% chance (1-in-100) of triggering a "Lucky Catch."

**Effect:**
```js
const lucky = Math.random() < 0.01;
if (lucky) {
  xp *= 10;
  showToast('🍀 LUCKY CATCH!', `Your entry earned 10× XP! +${xp} XP`);
  logEvent('lucky_streak', { entryId, xp });
}
```

**Visual:** Golden glow animation around the log entry. "Lucky!" particle effect.

**Discovery message:** `"🍀 Lucky Streak — A random roll gave you 10× XP. May the tide favor you again."`

---

### Hidden 2: 🎯 Milestone Celebrations

**Trigger:** Round-number cumulative achievements:
- 100th, 250th, 500th, 1000th, 2500th, 5000th, 10000th log entry
- 100th, 500th, 1000th, 5000th nautical mile traveled
- 50th, 100th, 500th, 1000th maintenance task completed
- 50th, 100th, 500th, 1000th catch logged
- 10th, 25th, 50th, 100th trip completed

**Effect:** Surprise celebration modal with confetti animation, special title grant, and bonus XP.

```js
const MILESTONES = {
  logs: [100, 250, 500, 1000, 2500, 5000, 10000],
  distance: [100, 500, 1000, 5000],
  maint: [50, 100, 500, 1000],
  catches: [50, 100, 500, 1000],
  trips: [10, 25, 50, 100]
};

function checkMilestone(stat, value) {
  if (MILESTONES[stat].includes(value) && !milestoneSeen[`${stat}_${value}`]) {
    milestoneSeen[`${stat}_${value}`] = true;
    return { type: stat, value };
  }
  return null;
}
```

**Rewards:** Special badge per milestone (`"💯 Century"`, `"📏 Long Haul"`, etc.) + 500 XP + 100 FishCoin.

---

### Hidden 3: 🥚 Easter Egg Phrases

**Trigger:** Specific keywords/phrases in log entry text:

| Phrase | Achievement | XP |
|--------|-------------|-----|
| "mayday" or "may day" | "📻 Voice in the Dark" | 100 |
| "ghost ship" | "👻 The Phantom" | 150 |
| "perfect haul" | "💎 Lucky Day" | 75 |
| "the big one" | "🎣 This One's for the Wall" | 200 |
| "calm seas" | "🌊 Mother Ocean's Smile" | 50 |
| "first mate" (referring to yourself) | "🎖️ Promotion" | 100 |
| "land ho" | "🏔️ Long Awaited Sight" | 75 |
| "shark" | "🦈 Tooth of the Sea" | 100 |
| "whale" | "🐋 The Larger World" | 150 |
| "moon" or "lunar" | "🌙 Tidal Wisdom" | 50 |
| "aurora" or "northern lights" | "✨ Sky Fire" | 200 |
| "rainbow" | "🌈 Pot of Gold" | 75 |
| "compass" | "🧭 True North" | 50 |

**Detection:** Case-insensitive substring match against log text.

**Anti-spam:** Each phrase can only trigger once per crew member.

---

### Hidden 4: 🌌 Constellation System

**Trigger:** Log entries at night hours (22:00, 23:00, 00:00, 01:00, 02:00, 03:00, 04:00 local) — across **at least 7 different calendar nights**, hitting **5+ different hour slots**.

**Effect:** Unlocks `"🌌 Star Navigator"` legendary hidden achievement.

```js
function checkConstellation(author) {
  const nightHours = [22, 23, 0, 1, 2, 3, 4];
  const recentNightLogs = author.logs.filter(log => 
    nightHours.includes(new Date(log.timestamp).getHours())
  );
  
  const uniqueNights = new Set(recentNightLogs.map(l => l.timestamp.split('T')[0])).size;
  const uniqueHours = new Set(recentNightLogs.map(l => 
    new Date(l.timestamp).getHours()
  )).size;
  
  return uniqueNights >= 7 && uniqueHours >= 5;
}
```

**Discovery message:** `"🌌 Star Navigator — You've logged across the night sky, hour by hour. The constellations know your name."`

**Reward:** +500 XP, badge `"🌌 Star Navigator"`, title `"The Navigator of Nights"`, special avatar border (animated starfield).

---

### Hidden 5: 🎂 Birthday Bonus

**Trigger:** Local date matches the crew member's birth date (set during crew creation, optional).

**Effect:** 5× XP on all log entries for that calendar day. Birthday banner on profile.

```js
function isBirthday(crewMember) {
  if (!crewMember.birthday) return false;
  const today = new Date();
  const bday = new Date(crewMember.birthday);
  return today.getMonth() === bday.getMonth() && today.getDate() === bday.getDate();
}

if (isBirthday(author)) {
  xp *= 5;
  showBanner(`🎂 Happy Birthday, ${author.name}! All XP ×5 today.`);
}
```

**Anti-abuse:** Birthday can be set once and locked. Changing it requires admin action.

---

### Hidden 6: ⚓ Vessel Birthday

**Trigger:** Anniversary of the vessel's first log entry.

**Effect:** 10× XP on that calendar day, special "vessel birthday" badge granted permanently to all crew.

**Discovery:** Auto-discovered on first anniversary. Pre-anniversary, no hint.

---

### Hidden 7: 🎰 Lucky Number 13

**Trigger:** Exactly the 13th log entry of a calendar day.

**Effect:** 13× XP on that entry (single entry only).

```js
function isLuckyThirteen(author, date) {
  const todaysLogs = author.logs.filter(l => l.timestamp.startsWith(date));
  return todaysLogs.length === 12;  // this is the 13th
}

if (isLuckyThirteen(author, today)) {
  xp *= 13;
  showToast('🎰 Lucky 13!', 'Your 13th entry earned 13× XP!');
}
```

**Visual:** Slot machine animation on the entry. Sound effect (optional, can be muted).

---

### Hidden 8: 📜 Echo of the Past

**Trigger:** Reading a log entry from exactly 1 year ago (to the day) — i.e., opening the log archive and viewing an entry whose date matches today's date one year prior.

**Effect:** Unlocks `"📜 Historian"` hidden achievement + 200 XP bonus on viewing.

```js
function isOneYearAgo(log, today) {
  const logDate = new Date(log.timestamp);
  const oneYearAgo = new Date(today);
  oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);
  return logDate.toDateString() === oneYearAgo.toDateString();
}
```

**Discovery message:** `"📜 Echo of the Past — A year ago today, you wrote this. History remembers."`

---

### Hidden 9: 🎭 Role Reversal

**Trigger:** A deckhand completes a maintenance task; an engineer logs a catch; an observer plans a trip — i.e., a crew member performs an action outside their primary role category.

**Effect:** +50 XP bonus + `"🎭 Role Reversal"` achievement.

```js
const ROLE_ACTIONS = {
  deckhand: ['catch_log'],
  engineer: ['maint_complete'],
  observer: ['data_quality_log'],
  mate: ['trip_plan'],
  captain: ['crew_award']
};

function isRoleReversal(action, author) {
  return !ROLE_ACTIONS[author.role]?.includes(action);
}
```

**Anti-abuse:** Only triggers once per (role, action) pair per crew member.

---

### Hidden 10: 🌊 Full Moon Tide

**Trigger:** Log entry during the full moon window (3 days: day before, day of, day after full moon).

**Effect:** +25 XP bonus + ephemeral "moonlit" badge (visible for 24 hours).

```js
function isFullMoon(date) {
  // Simplified: full moon is ~every 29.5 days
  // Use astronomical algorithm or a static lookup for the year
  const fullMoons = getFullMoonDates(date.getFullYear());
  return fullMoons.some(fm => {
    const start = new Date(fm); start.setDate(start.getDate() - 1);
    const end = new Date(fm); end.setDate(end.getDate() + 1);
    return date >= start && date <= end;
  });
}
```

**Discovery message:** `"🌊 Full Moon Tide — The moon pulls the tide, and your logs are stronger for it."`

---

## 6.3 Hidden Mechanics Storage

```js
const HIDDEN_STATE_KEY = 'vessel_quest_hidden';

// Per crew member:
{
  discoveredHidden: {
    lucky_streak: { firstTriggered: 1721000000000, count: 5 },
    easter_mayday: { firstTriggered: 1722000000000, count: 1 },
    constellation: { firstTriggered: 1723000000000, count: 1 },
    // ...
  },
  easterEggSeen: ['mayday', 'ghost_ship', 'perfect_haul'],
  constellationProgress: {
    nightsLogged: ['2026-07-15', '2026-07-16'],
    hoursLogged: [23, 1, 3]
  }
}
```

## 6.4 Anti-Abuse for Hidden Mechanics

- **Lucky Streak:** RNG-based, but capped at 1 trigger per hour per user.
- **Milestones:** Anti-farm — once seen, can't re-trigger by deleting data.
- **Easter Eggs:** Each phrase limited to once. Anti-spam: log entry must be ≥ 30 chars.
- **Constellation:** Requires logs across **distinct** nights (not same night with multiple entries).
- **Birthday:** Cannot be changed after initial setup.
- **Vessel Birthday:** Anchored to immutable first log timestamp.
- **Lucky 13:** Strict count — must be exactly the 13th entry (no padding entries).
- **Echo of the Past:** Triggers only on actual archive viewing, not arbitrary reads.
- **Role Reversal:** Tracks role at time of action, not retroactive role changes.
- **Full Moon:** Verified against astronomical calendar (no manual override).

---

# Appendix A: LocalStorage Schema Summary

| Key | Type | Purpose |
|-----|------|---------|
| `vessel_quest_state` | object | Existing: achievements, quests |
| `vessel_quest_chains` | object | New: active + completed chains |
| `vessel_quest_events` | object | New: active + historical events |
| `vessel_quest_seasons` | object | Existing: seasonal state |
| `vessel_quest_hidden` | object | New: hidden mechanic discoveries |
| `vessel_quest_chains_defs` | object (bundled, immutable) | New: chain definitions |
| `crew_members` | object | New: crew roster with role XP |
| `fishcoin_balance` | number | New: per-crew currency balance |
| `lucky_streak_tracker` | object | New: 1% RNG state per user |

---

# Appendix B: Cross-References to Existing Modules

| New System | Reads From | Writes To |
|------------|-----------|-----------|
| Quest Chains | crew_logbook, maint_history, trip_plan_data, photo_attachments | vessel_quest_chains |
| World Events | crew_logbook (catch logs), maint_tasks (overdue count), maint_history | vessel_quest_events, notifications |
| Crew Roles | crew_logbook (author filter), maint_history (author filter) | crew_members (roleXp) |
| Progression Modifiers | crew_logbook (timestamps), maint_tasks (overdue), trip_plan_data (checklist) | author.xpTotals |
| Leaderboard Seasons | all XP sources, GPS trail | leaderboard_season_data |
| Hidden Mechanics | crew_logbook (text, timestamps), crew_members (role) | vessel_quest_hidden |

---

# Appendix C: API Contract (for future server-side events)

When events go server-driven (future), expose:

```js
// GET /api/events/active
{
  events: [
    {
      id: 'the_run_2026_summer',
      name: 'The Run',
      startedAt: '2026-05-01T00:00:00Z',
      endsAt: '2026-05-08T00:00:00Z',
      modifier: 2.0,
      scope: 'catch_log'
    }
  ]
}

// GET /api/leaderboard/{season}/{period}
{
  season: 'summer',
  period: '2026-Q3',
  ranks: [
    { rank: 1, crewId: 'cm_abc', name: 'Hank', score: 12450 },
    // ...
  ]
}

// POST /api/hidden/trigger
{
  crewId: 'cm_abc',
  hiddenId: 'lucky_streak',
  context: { entryId: 'log_xyz' }
}
```

For now, all systems are **client-side deterministic** using localStorage. Server-driven events are a future enhancement.

---

# Appendix D: Performance Considerations

- **Quest chain checks** run on every log entry — keep check functions O(n) where n = relevant log count (use date-bounded queries).
- **Combo tracking** uses a sliding window — clear entries older than 60 minutes on every check.
- **Leaderboard recomputation** runs once per page load + on XP gain events. Cache intermediate results.
- **Hidden mechanic triggers** are checked in order of rarity (most common first, rarest last) to short-circuit quickly.
- **FishCoin transfers** must be atomic — use a single localStorage write with full state to avoid race conditions in multi-tab scenarios.

---

# Appendix E: Accessibility & Localization

- All hidden mechanics surface text in plain language — no reliance on color alone.
- Toast notifications auto-dismiss after 8 seconds, dismissible via click or Escape key.
- Easter egg phrases support a localized phrase list (`easter_phrases_en.json`, `easter_phrases_es.json`, etc.).
- Roles have localized titles: `"Captain"` (EN), `"Capitán"` (ES), `"船長"` (JA).
- All percentages and XP values displayed with thousands separators (`,` or `.` based on locale).

---

# Appendix F: Balance Testing Checklist

Before shipping, test these scenarios:

- [ ] New user joins mid-event — gets event modifier correctly applied.
- [ ] Crew member changes role mid-week — old role XP preserved, new role XP starts fresh.
- [ ] Combo counter resets correctly at midnight.
- [ ] Rest bonus only applies once per idle period (not every log after).
- [ ] Mentor bonus caps at 10 logs/day per mentee.
- [ ] Lucky streak RNG is uniform across 100+ test entries (~1% trigger rate).
- [ ] Constellation tracking requires 7 distinct calendar dates.
- [ ] Vessel birthday fires exactly 365 days after first log.
- [ ] World event overlap (multiple events active) — modifiers stack correctly.
- [ ] Leaderboard tiebreakers produce deterministic, reproducible results.

---

**End of document.**

*This file is the engineering spec. Implementation order is recommended as: Progression Modifiers (§4) → Leaderboard Seasons (§5) → Hidden Mechanics (§6) → Crew Roles (§3) → World Events (§2) → Quest Chains (§1). Earlier systems lay foundations later systems depend on.*
