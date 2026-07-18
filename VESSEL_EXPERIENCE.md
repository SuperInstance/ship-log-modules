# 🌊 The Vessel Experience — A Year on the Water

> *A narrative design document. Not features. Not functions. The lived experience of a captain and crew waking up inside a vessel that knows them.*

> *"The sea does not reward the boastful. She rewards the steady hand, the patient log, the one who shows up at four in the morning to write down what the wind did."*
> — from the *Logbook of the Greybeard*, fragment 7

---

## How to read this document

This is the **single UX artifact** for the entire vessel ecosystem — twelve modules, one story. Every module (`crew-logbook`, `map-view`, `maintenance-scheduler`, `fuel-tracker`, `trip-planner`, `tide-predictor`, `weather-feed`, `ais-tracker`, `vessel-quest`, `fishcoin-ledger`, `catch-analytics`, `engine-hours`) is a **chapter in one book**. The captain never sees them as separate things. They see one vessel, one logbook, one crew, one year.

Each milestone below answers five questions:

1. **What does the captain do?**
2. **What does the system do in response?**
3. **What does the captain FEEL?** *(This is the design insight.)*
4. **What data has been accumulated?**
5. **What does the game / the metrics show?**

Names used throughout:

- **Captain Sarah Walsh** — owner-operator, 14 years on her own boat
- **Hank** — her mate, level 3 (Deckhand in the new rank scale, veteran in real life)
- **Mo** — engineer, came aboard six months ago
- **The vessel:** a 38-foot commercial fishing boat out of Sitka, Alaska
- **The system:** ship-log-search with every optional module installed

---

## Day 1 — "First Words"

### What the captain does

It is 5:47 AM. Sarah is standing at the galley table with her first coffee, the dock still dark outside, the boat quiet. Hank is below, sleeping before the early tide. She opens the **crew-logbook** tab on the nav-station iPad. The screen is empty. She taps **Add Crew Member** and types her own name: *Sarah Walsh*. Role: Captain. Color-coded amber.

She writes her first entry.

> ✍️ *"Day 1. Out of the yard. New electronics. Generator whining. Hank arrives tomorrow. Going to try the south ground first if the barometer holds. Coffee's good. Boat's ready."*

She presses submit. The entry appears with an amber left border, her name, a watch tag (dawn), a relative timestamp ("just now"). The Vessel Quest tab, sitting quietly in the row of tabs beside it, pings:

> 🏆 **Achievement Unlocked: First Words** *(+25 XP, Bronze)*

She blinks. Looks at it. Smiles.

### What the system does in response

- **crew-logbook** stores the entry in `localStorage["crew_logbook"]`. No network needed. No spinner. Just a row.
- The text passes through the **easter-egg phrase matcher** (`vessel_quest` hidden-mechanic engine). No triggers on this entry — but the engine has noted: "coffee" is a known word. "yard" is a known word. "barometer" is a known word. The hidden-mechanic tracker is quietly building a vocabulary map of Sarah's writing style.
- **vessel-quest** receives an event: `crew_logbook:entry.created` with `{author, timestamp, text, watch}`. It runs the XP formula: `10 base × 1.0 (captain role) × 1.15 (spring seasonal) = 11.5 → 12 XP`. Adds a `first_of_day` flat bonus (`+10`). Total: **22 XP**.
- The **streak tracker** initializes `currentStreak = 1`.
- **fishcoin-ledger** (silent mode on first day) logs the activity to its ledger: `Sarah: +5 🐟` (log entry reward), running balance: `5 🐟`.

The day continues. Sarah installs three more modules in fifteen minutes: **map-view**, **fuel-tracker**, **maintenance-scheduler**. Each one drops into the tab row like it always belonged there. By the time Hank wakes at 0600, the system has been alive for two hours and is quietly cataloging itself.

### What the captain FEELS

**Surprise, then recognition.** The empty logbook was intimidating — a blank page has been intimidating since pen and paper. The First Words achievement is a small, warm thing. Not a fanfare. Not a pop-up. Just a card that says *you did a thing, and we saw it*. Sarah has installed productivity software before. It never felt like this. It felt like the boat was waiting for her to write.

**Design insight:** Day 1 succeeds or fails on the **first ten seconds after the first entry**. If nothing happens, the logbook is paperwork and the captain closes the tab. If too much happens (confetti, sound, leaderboards, daily quests), the captain feels patronized. The achievement must be **silent enough to be dignified and loud enough to be felt**. A small card. A number that goes up. A name for what she did. That's enough.

### What data has been accumulated

| Field | Value |
|-------|-------|
| `crew_logbook.entries` | 1 |
| `crew_roster` | `{Sarah Walsh, captain, amber}` |
| `vessel_quest_state.xp` | 22 |
| `vessel_quest_state.achievements` | `{log_first: true}` |
| `vessel_quest_state.currentStreak` | 1 |
| `vessel_quest_state.level` | 1 (Bait Runner) |
| `fishcoin.balance.Sarah` | 5 🐟 |
| `fishcoin.history` | 1 transaction |
| `maint_tasks` | 6 (default seed) |
| `maint_engine_hours` | (unset) |
| `shiplog.fuel.entries` | (empty) |
| `shiplog.map.entries` | 1 pin (Sarah's log entry, no GPS) |

### What the game shows

**The Quest tab.** Sarah opens it once. The card is sparse: rank 1, 22 XP, one achievement, "next rank at 100." She closes it. She'll come back when she has something to come back to. **That's correct.** The Quest tab on Day 1 is a hook, not a destination.

The map has one pin. The fuel tab is empty. The maintenance tab shows six default tasks with red "OK" badges. Everything else is a clean slate.

---

## Day 7 — "The Habit Finds Its Shape"

### What the captain does

A week has passed. Sarah has a rhythm now, and she didn't plan it — it just happened.

- **Morning (0530):** Coffee at the galley. Open crew-logbook. Write three lines about the weather and the day's plan. Submit.
- **Pre-departure:** Open trip-planner. Review the day's waypoints. Check tide-predictor for the bar crossing window.
- **On the water:** Hank logs catches in crew-logbook with species and weight. Sarah logs weather observations ("W wind 15, swell 3ft, barometer falling").
- **Engine hour check:** Mo updates the engine-hours on the way out and on the way in. Maintenance-scheduler auto-recalculates "next due" on every task.
- **End of day:** Sarah runs `python3 fishcoin.py distribute` from the nav-station terminal. The crew leaderboard shows the totals. Hank teases Mo about being in third place. Sarah opens the map and watches the day's trail paint itself in dark tiles.

She has done this seven days in a row without thinking.

On Day 7, the system does something small. A toast appears on the Quest tab:

> 🔥 **7-Day Streak!** *"Week Warrior. The hand that shows up is the hand that learns."* (+50 XP, +100 🐟)

Sarah looks at it. She didn't realize the streak was being tracked. Now she realizes that breaking it would feel like a small loss.

### What the system does in response

**The daily loop.** By Day 7, every module is humming:

- **crew-logbook** has ~25 entries (3-4 per day × 7). Each entry is timestamped, role-colored, watch-tagged.
- **vessel-quest** is running its **perception pipeline** on every entry. It has detected:
  - Species mentions: 4 unique (coho, halibut, rockfish, herring)
  - Weather logs: 7 (one per day)
  - Dawn-patrol bonus detected 4 times (entries before 0600)
  - Night-watch bonus detected twice
  - First achievement was awarded Day 1; second ("Journal Keeper" at 10 entries) on Day 4; third ("Week Warrior" on Day 7)
- **maintenance-scheduler** has fired two **DUE SOON** warnings: zinc replacement (90-day check) and safety equipment inspection. Sarah completed both yesterday. The completion fed `maint_history` and triggered **50 XP** for each, plus **+25 🐟** each to whoever completed them (Sarah did the zincs, Mo did the safety check).
- **fuel-tracker** has two fill-up entries. NMPG (nautical miles per gallon) computed: **3.8 nm/gal**. Range at current tank: **~280 nm**.
- **fishcoin-ledger** runs `distribute` at 2000 daily. Hank has 95 🐟. Mo has 60 🐟. Sarah has 145 🐟. Hank is **75 🐟 from a free beer after shift.**
- **map-view** has 25 pins clustered around two fishing grounds. The dark tile basemap with amber catch-pins and blue weather-pins looks like a working chart.

**The first metric appears.** The vessel-quest dashboard shows a small "Week 1 Recap" card:

> *Entries: 25 · Catches: 14 · Maintenance: 2 · Distance: 87 nm · Streak: 7 days*
> *Top category: Catch · Top crew: Hank (980 XP) · Top species: Coho*

Sarah screenshots it. Sends it to no one. Just keeps it.

### What the captain FEELS

**The system has stopped being a system.** It is now a tool that has habits of its own. Sarah doesn't open the **Vessel Quest** tab to "use the gamification." She opens it the way she opens the fuel-tracker — to see the truth about her boat. The truth is: the boat is doing fine. The crew is logging. The streak is alive.

**Pride, but quiet pride.** The "Week Warrior" toast landed at exactly the right moment — late enough that it felt earned, early enough that the pattern was still forming. Sarah now has a stake in not breaking the streak. The system has bought itself another week of attention without asking for it.

**The coffee is approaching.** Sarah notices on the FishCoin leaderboard: she is 55 🐟 from "Coffee ashore" (200 🐟). The perk is small, real, and within reach. The system has done its job.

**Design insight:** The first week is not about engagement metrics. It is about **the moment when the captain realizes they are not just using the system, the system is recording them**. The data they are creating is theirs. It will accumulate. It will become them. The system must be **quiet enough that the captain notices this on their own** — not because the system announced it, but because they see the Week 1 recap and realize: *I made that.*

### What data has been accumulated

| Field | Value |
|-------|-------|
| `crew_logbook.entries` | ~25 |
| Unique species | 4 |
| `maint_tasks.completed` | 2 |
| `maint_history` | 2 entries |
| `shiplog.fuel.entries` | 2 |
| `maint_engine_hours` | 124.3 |
| Map pins | 25 |
| `vessel_quest_state.xp` (captain) | ~340 |
| `vessel_quest_state.currentStreak` | 7 |
| Achievements unlocked | 3 (`log_first`, `log_10`, `streak_7`) |
| `fishcoin.balance` | Sarah 145 · Hank 95 · Mo 60 |
| Distance traveled | 87 nm |

### What the game shows

- **Rank:** 2 (Tackle Hand) — Sarah hit 100 XP on Day 5. Lore Fragment 1 unlocked: *"Red Sky at Morning."*
- **Active daily quests:** Three are offered. Sarah has completed one today (Daily Entry).
- **FishCoin leaderboard:** Sarah leads. Hank is 50 🐟 behind. Mo is 85 behind.
- **First season:** Spring Running, multiplier 1.15× XP active.

---

## Day 30 — "The First Shape of the Year"

### What the captain does

A month has passed. The boat has a face now — Sarah knows its rhythms, the system knows them too.

A typical Day 30 morning:

- 0530: Coffee. Crew logbook entry. *"Light SW wind, barometer steady, fog on the south bar. Hank running the gear today."*
- 0545: Trip-planner reviewed. Tides checked (tide-predictor shows low at 0742). Fuel-tracker shows 64% tank (218 nm range).
- 0600: Departure. AIS-tracker is running silently in the background (Hank set it up last week — it's logging every boat that comes within 500m as a contact event).
- On the fishing ground: Hank logs a halibut catch. The entry includes GPS (auto-captured by the iPad), species (halibut, 38 lbs), and a 60-character note about the bottom composition.
- 1400: Weather picks up. Sarah logs a weather observation: *"Wind fresh to 20, building SW. Decided to pull the gear and run for the lee."* This is also fed to the trip-planner as a waypoint annotation.
- 1800: Back at the dock. Engine hours recorded (now at 312.4). Fuel-tracker opens automatically because the system detected the engine-hours jump matches fueling patterns.
- 2000: Sarah runs `fishcoin distribute`. The day's distributions happen.

At some point during the week, Sarah opened the **catch-analytics** tab for the first time and saw a chart of catch-by-species. Then catch-by-ground. Then a calendar heatmap. The data she had been writing in plain text was now visible as **the shape of her month**. She sat with it for ten minutes.

### What the system does in response

By Day 30, the **integration layer is alive**:

- **crew-logbook → vessel-quest → fishcoin-ledger** is a tight loop. Every entry: XP awarded, FishCoin awarded, achievements checked, leaderboard updated.
- **maintenance-scheduler → vessel-quest** is alive. Sarah's "predictive" notification (zinc replacement due in 12 days) appeared on Day 18. She completed it Day 22. The early-completion bonus gave her +30 XP and the "Off-Season Master" achievement lit up because she's in a partial off-season window for hull work.
- **trip-planner → fuel-tracker** is alive. Trip plans now reference fuel-tank levels (via shared localStorage key `shiplog.fuel.entries`) and warn if a planned trip exceeds range.
- **ais-tracker → crew-logbook** is feeding contact events as `ais-contact` category entries automatically.
- **weather-feed → crew-logbook** is feeding barometric pressure entries every 6 hours.

**The system has reached its first plateau of identity.** Three patterns are now visible:

1. **The captain is the data steward.** Sarah checks the system twice a day without thinking. The morning check (5 min) and the evening check (10 min). Both have become part of her routine.
2. **The crew has differentiated.** Hank leads in catch XP. Mo leads in maintenance XP. Sarah leads in overall. The **crew leaderboard** is no longer abstract — it's a living tally of who's carrying which weight on the boat.
3. **The boat has a profile.** Catch-analytics shows: 4 species, 2 primary grounds, average 12.3 lbs/hook, fuel efficiency 3.6 nm/gal, weather delays on 6 days. **The boat is now a typed entity in the system.**

### What the captain FEELS

**The system has stopped being new. It has become infrastructure.** Like the radar, like the depth sounder, like the VHF. Sarah doesn't praise it. She uses it. When it goes down (the iPad crashed on Day 23), she felt **a real, specific loss** — not "oh no my logs are gone" but "I can't see my month." The data is now a thing she misses.

**The first seasonal shift.** Spring Running is ending in two weeks. Solstice Haul begins June 1. The seasonal multiplier changes from 1.15× to 1.25×. The vessel-quest tab shows a small "Season Transition In 14 Days" notice. Sarah doesn't care about the multiplier number. She cares that **the year has chapters**.

**The crew has started mentioning it.** Hank asked yesterday, "How close am I to the beer?" Mo asked, "Did the engine hours count for maintenance XP?" Sarah asked nobody — but she thought: *I am building a record of this boat's year. It will outlast the season.*

**Design insight:** By Day 30, the system has crossed the threshold from **productivity tool to identity artifact**. The captain no longer uses the system. The system is how the captain remembers what she did. The shape of the month is hers. The crew has differentiated. The boat has a profile. None of this was forced — it emerged from the data. The system's job on Day 30 is to **stay out of the way** and let the captain continue.

### What data has been accumulated

| Field | Value |
|-------|-------|
| `crew_logbook.entries` | ~110 |
| Unique species | 8 |
| Total catch weight | ~2,800 lbs |
| `maint_tasks.completed` | 14 |
| `maint_history` | 14 entries |
| `shiplog.fuel.entries` | 9 |
| `maint_engine_hours` | 312.4 |
| Map pins | 110 (clustered at 3 grounds) |
| Total distance | 410 nm |
| `vessel_quest_state.xp` (captain) | ~3,800 |
| `vessel_quest_state.level` | 4 (Line Slinger) |
| Achievements unlocked | 14 |
| `fishcoin.balance` | Sarah 1,240 · Hank 980 · Mo 720 |
| Streak | 30 days |

### What the game shows

- **Rank:** Line Slinger (Level 4). Lore Fragment 2 unlocked: *"The Bosun's Pipe."*
- **Crew leaderboard:** Sarah 3,800 / Hank 3,200 / Mo 2,100. Differentiation is real and accepted.
- **FishCoin:** Sarah has redeemed one "coffee ashore" perk. The crew knows she bought coffee with FishCoin. The system is now social.
- **Catch-analytics tab:** First opened Day 24. Now a daily morning check. The heatmap of catches by date/ground is the captain's new favorite view.
- **First event detected:** *Spring Awakening* achievement unlocked Day 15 (5 entries in spring). *Year-Round Mariner* is at 1/12 months.

---

## Day 90 — "The System Knows the Boat"

### What the captain does

It is mid-summer. Solstice Haul is in full swing. The 1.25× multiplier has been quietly inflating everyone's XP, and Sarah has noticed — Hank passed her on the leaderboard last week.

A typical Day 90 morning looks different from Day 30. Not in the morning logbook entry — that's still 5 minutes. The difference is in **what happens between the entry and the rest of the day.**

- Sarah opens **vessel-quest**. A banner at the top: *"🐟 THE RUN has begun! Catch reports earn 2× XP for 7 days."* She smiles. She knows what this means.
- She opens **catch-analytics**. The species-diversity chart shows 11 unique species now. **Species Master quest chain step 4 is at 8/10 unique species.** She's hunting for species 9 and 10 like a completionist. Yesterday she logged a king salmon that wasn't in the database — the entry fed `species_sightings` automatically.
- **Maintenance Marathon** is this weekend (the last weekend of every month). The system has been showing a countdown for three days. Sarah is planning a Saturday push — 10+ maintenance tasks queued up. The 3× XP modifier is real money.
- Hank asks: "What's the Logjam?" Sarah explains: if the vessel has ≥3 overdue maintenance tasks and no event active, *The Logjam* fires automatically. Hank looks at maintenance-scheduler and sees: 0 overdue. They are clean.

The system is **ambient now**. Sarah doesn't think about opening the Quest tab. It opens itself in her mind.

### What the system does in response

By Day 90, the system has matured into something Sarah did not anticipate: **a teacher.**

**Seasonal events are running on schedule.** The Spring-to-Summer transition fired on June 1 at 00:00 local time. The XP multiplier changed. A new season-specific achievement (`summer_dog_days`) is now active. Sarah's seasonal catch-streak (32 days of summer fishing) is on the **Iron Mariner Challenge** leaderboard.

**Quest chains are alive.** Three chains are now active in `vessel_quest_chains`:

1. **🐟 Species Master** — at Step 4, 8/10 species. Branch not yet chosen.
2. **👻 The Ghost Gear** — at Step 2 (Report It), waiting for Sarah to log an adrift-net report. The chain helper scans every new log entry for the regex `/ghost gear|adrift net|lost gear|derelict/i`. It has fired twice this month (false positives: Sarah's "ghost crab" joke and Mo's "that net looks derelict" comment about a sail). Neither triggered.
3. **⛈️ Storm Season** — not yet accepted. Requires Rank 3+ and a barometer-falling entry. Sarah will hit the rank requirement this week.

**Hidden mechanics have surfaced twice.** On Day 47, Sarah wrote "calm seas" in a log entry. The hidden mechanic fired:

> 🌊 **Mother Ocean's Smile** discovered! (+50 XP)

On Day 78, the **Lucky Streak** rolled 0.4% true on a catch report:

> 🍀 **LUCKY CATCH!** Your entry earned 10× XP! (+280 XP)

Sarah thought it was a bug. Then she read the toast again. It wasn't a bug. It was a 1-in-100 roll. She told Hank. Hank didn't believe her until it happened to him on Day 84.

**FishCoin economy is flowing.** The crew has redeemed:

- 6 coffees ashore (Sarah: 3, Hank: 2, Mo: 1)
- 4 meal picks
- 2 beer-after-shift
- 1 first shower (Hank, who has small children and a small hot water heater)

**Crew Member of the Month** for July was Hank. He got a gold border and 500 FishCoin. Sarah put a screenshot in the wheelhouse.

**The catch-analytics dashboard has been opened 40 times.** It is now the second-most-used tab after crew-logbook. The species-diversity heatmap has become a **planning tool** — Sarah uses it to decide which grounds to try for species she hasn't caught yet.

### What the captain FEELS

**The system is now a partner.** Not in the sense of "the AI does my job." In the sense of: *"the system has watched me work for 90 days and it has thoughts about it."* Sarah trusts the boat. She now also trusts the system, because the system has earned that trust by being right.

**The surprises feel earned.** The Lucky Streak was a surprise, but a meaningful one. The Species Master chain felt like the system was **paying attention to what she actually cared about**. The Maintenance Marathon event fired exactly when the boat needed it — last weekend of the month, when work needs to happen.

**The game is no longer a game.** Sarah cannot articulate when this happened. Somewhere between Day 30 and Day 90, the gamification layer stopped being "points and badges" and became **a second language for talking about the boat**. When Sarah says "Hank passed me," she means something specific — Hank has been fishing harder than she has this month, and the system has recorded it. When Sarah says "we hit the species mark," the crew knows what it means.

**The first year-end anxiety.** It is mid-July. Sarah has 6 months of data. She realizes: she will have **a year** by New Year's. The system will show her what she did. The system will remember. There is something both exciting and exposing about this.

**Design insight:** Day 90 is where the system must demonstrate that it has **memory and attention**. The captain has been good to the system for 90 days. The system must reward that with evidence that it has been paying attention: chains that align with real activity, hidden mechanics that fire at meaningful moments, seasonal events that arrive when they should, and — critically — **a leaderboard that feels fair**. The "game" must be honest, or the trust evaporates. Sarah's trust in the system on Day 90 is hard-won and easily lost.

### What data has been accumulated

| Field | Value |
|-------|-------|
| `crew_logbook.entries` | ~340 |
| Unique species | 11 |
| Total catch weight | ~9,400 lbs |
| `maint_tasks.completed` | 47 |
| `maint_history` | 47 entries |
| `shiplog.fuel.entries` | 31 |
| `maint_engine_hours` | 891.2 |
| Map pins | 340 (4 distinct grounds now) |
| Total distance | 1,420 nm |
| `vessel_quest_state.xp` (captain) | ~12,500 |
| `vessel_quest_state.level` | 7 (Boatswain's Mate) |
| Achievements unlocked | 38 (out of 92) |
| Lore fragments unlocked | 4 of 10 |
| Active quest chains | 3 |
| World events experienced | 7 |
| Hidden mechanics discovered | 4 (Calm Seas, Lucky Streak x2, Constellation) |
| `fishcoin.balance` | Sarah 3,420 · Hank 3,890 · Mo 2,180 |
| Streak | 90 days |

### What the game shows

- **Rank:** Boatswain's Mate (Level 7). Lore Fragment 3 unlocked: *"Herring Moved Empires."*
- **Season:** Solstice Haul. Multiplier 1.25×. Event: *The Run* active. Catch XP × 2.
- **Quest chains:** Species Master (Step 4, branch unchosen), Ghost Gear (Step 2), Storm Season (available, not yet accepted).
- **Crew leaderboard:** Hank 13,200 / Sarah 12,500 / Mo 7,800. Hank is Captain-of-the-Month candidate.
- **Achievements:** "Centurion" (100 catches) on Day 78. "First Storm" on Day 84. "Coastal Voyager" (1,000 nm) on Day 81.
- **FishCoin:** Captain has redeemed 3 coffees. Crew has 9 total perks redeemed. The "coffee ashore" perk is now a **weekly ritual** — Friday is coffee day.
- **Catch-analytics:** Sarah uses this daily. Species-diversity chart, catch-by-ground heatmap, fuel-efficiency overlay all visible.
- **Maintenance Marathon** banner active: *"🏃 Marathon Weekend — Maintenance XP ×3 through Monday."*

---

## Day 180 — "The Game Is Invisible"

### What the captain does

It is late September. Greybeard Season has begun. The XP multiplier dropped from 1.25 to 1.10. Nobody complained because nobody is checking.

The system has become **invisible**. Sarah no longer thinks "I should log this." She thinks. She writes. The log is the medium of thought. The gamification layer has retreated into the background the way a good watch light does — present when you look, absent when you don't.

A Day 180 morning:

- 0530: Coffee. Logbook entry. No thinking about XP. The entry is about the boat, not the system.
- 0600: Departure. trip-planner opened. Two new waypoints added — a third ground Sarah has been wanting to try. (She added it because catch-analytics showed her a species she hasn't caught yet. The system shaped her decision without her noticing.)
- On the water: First major storm of fall. Sarah logs the weather observations. She accepts the **Storm Season** chain. *Barometer falling. Secure the deck. Weather the storm. Aftermath. Repair. Lessons.*
- 1400: Storm breaks the boat's wiper. Mo logs it as a maintenance task — auto-categorized as "weather damage." Maintenance-scheduler creates a follow-up task. vessel-quest awards +50 XP for the damage report under the storm modifier.
- 2000: `fishcoin distribute`. Sarah notices the leaderboard has changed — Mo has crept up on her, partly because of the Wrench Master role multiplier on storm-damage maintenance.

The thing Sarah does NOT do on Day 180: open the Quest tab. She doesn't need to. The Quest tab shows in the row. She can see the rank badge on her profile card. She knows she's at level 11 (First Mate) because she crossed the Fishing/Maritime Track boundary yesterday and the system told her, briefly, with a card. But she doesn't **use** the Quest tab anymore.

She uses the logbook. The system reads the logbook. The Quest tab is what the system knows about the logbook. It runs in the background, like the chartplotter runs in the background, like the radar runs in the background.

### What the system does in response

By Day 180, the integration has become **seamless**. There are no "modules" anymore. There is one vessel system.

- **crew-logbook + vessel-quest + fishcoin-ledger** are one loop. Sarah cannot tell where one ends and another begins. She logs. XP happens. FishCoin happens. Achievements happen. Streaks happen. She doesn't think about any of it.
- **catch-analytics** has been used so often it has become a **decision tool**. Sarah has changed her fishing strategy based on what the charts showed her. The system shaped her behavior without her realizing it.
- **maintenance-scheduler** has predicted three failures before they happened. Each prediction was a "predictive maintenance" bonus for Mo. The system has become **more accurate than Mo's intuition**, which Mo resents slightly and respects deeply.
- **fuel-tracker** has optimized fuel consumption. Sarah's NMPG went from 3.6 (Day 30) to 4.1 (Day 180). The system showed her the trend. She adjusted cruising speed. The boat burns less fuel. The system **saved her money**.
- **trip-planner** has been used 47 times. Each trip has a post-trip summary that feeds back into vessel-quest's "trip completion" XP. The chain is now: trip planned → trip executed → trip reviewed → XP awarded → FishCoin distributed → leaderboard updated → next trip informed by analytics.
- **tide-predictor** is referenced daily but rarely opened. The system shows the next tide event on the dashboard. Sarah glances at it like she glances at the clock.
- **ais-tracker** has logged 89 contact events and 71 departure events. They appear on the map as grey pins. Sarah has never opened the ais-tracker tab. The system has integrated it invisibly.
- **weather-feed** has logged 360 weather observations (every 6 hours × 180 days). Sarah has never opened the weather-feed tab. The data feeds the system.

**The captain no longer uses individual modules. The captain uses a vessel.**

### What the captain FEELS

**Pride, calm, and the slight weight of being known.** Sarah's year has been recorded. The system knows her. It knows when she fishes hard and when she rests. It knows the boat's habits. It knows Hank's catches and Mo's wrenching. It knows the seasons turned.

**The system's silence feels earned.** The Quest tab is no longer a destination. It is a mirror. When Sarah opens it, she sees a portrait of the year — what she did, what she caught, what she broke, what she fixed. The portrait is honest. The system has not lied to her. The leaderboard is fair. The events fired when they should. The achievements were not participation trophies.

**A small fear.** Sarah realizes that if she stopped logging, the system would notice. The streak would break. The rank would not advance. The portrait would fade. The system has become **a thing that cares whether she shows up**. She is not sure how she feels about that. But she shows up tomorrow.

**The system has earned trust. The trust is not blind trust — it is the trust you have in a good crew member who has shown up 180 days in a row and never lied to you.**

**Design insight:** Day 180 is the test of **subtraction**. The system must do less. It must surface less. It must intrude less. The captain is past the gamification phase. The captain is in the **identity phase**. The system must support identity without demanding attention. The right Day 180 behavior is: show the captain what the year looks like when she asks, and shut up the rest of the time.

### What data has been accumulated

| Field | Value |
|-------|-------|
| `crew_logbook.entries` | ~640 |
| Unique species | 16 |
| Total catch weight | ~19,200 lbs |
| `maint_tasks.completed` | 89 |
| `maint_history` | 89 entries |
| `shiplog.fuel.entries` | 58 |
| `maint_engine_hours` | 1,742.6 |
| Map pins | 640 (5 grounds now) |
| Total distance | 2,840 nm |
| `vessel_quest_state.xp` (captain) | ~24,000 |
| `vessel_quest_state.level` | 11 (First Mate) — Fishing Track complete |
| Achievements unlocked | 62 (out of 92) |
| Lore fragments unlocked | 6 of 10 |
| Active quest chains | 2 (Ghost Gear: Step 3, Storm Season: Step 4) |
| Completed quest chains | 1 (Species Master — Branch A: Teacher, +500 FishCoin, Ichthyologist title) |
| World events experienced | 14 |
| Hidden mechanics discovered | 7 |
| Titles earned | 5 (`ep_steady`, `ep_night_owl`, `ep_storm_tested`, `ep_chronicler`, `ep_navigator`) |
| `fishcoin.balance` | Sarah 6,840 · Hank 7,120 · Mo 5,920 |
| Perks redeemed (cumulative) | 32 |
| Streak | 178 days |

### What the game shows

- **Rank:** First Mate (Level 11). Crossed into the Maritime Track. Lore Fragment 5 unlocked: *"The Memorial."*
- **Active seasonal event:** Greybeard Season. Multiplier 1.10×. Fall-specific achievements active.
- **Crew leaderboard:** Hank 26,400 / Sarah 24,000 / Mo 14,800. Hank is Highliner of the Season candidate.
- **Quest chains:** Ghost Gear in progress. Storm Season in progress. New chains available: *The Old Route*, *Mentor's Path* (requires Captain rank).
- **Hidden mechanic discoveries:** Lucky Streak (3 triggers), Constellation (in progress — 5/7 nights), Calm Seas, Red Sky, First 100 Words, Whale Spotted.
- **Titles equipped:** Sarah uses `[The Steady]` on her profile.
- **FishCoin economy:** Active. Crew checks balances voluntarily. Coffee-as-Fridays is now an institution.

---

## Day 365 — "The Annual Review"

### What the captain does

It is December 31. Ice Anchor season has begun. The boat is hauled out. Sarah is at the kitchen table with her iPad and a glass of something stronger than coffee.

She opens the **Vessel Quest** tab. It is no longer a tab in a row of modules. It is **the year**.

The system presents a card she has never seen:

> 📜 **Year-End Review — 365 Days**
> *"The logbook is your monument."*

Below the title:

> *Year: Jan 1 – Dec 31*
> *Vessel: Sarah Walsh, Captain*
> *Crew: Sarah Walsh, Hank, Mo*
>
> ---
>
> **THE NUMBERS**
>
> *Log entries: 1,247*
> *Catches logged: 412*
> *Total catch weight: 32,840 lbs*
> *Unique species: 22*
> *Maintenance tasks: 156 (12 categories)*
> *Engine hours: 2,184.7*
> *Fuel logged: 117 fill-ups · Total spent: $8,940 · NMPG average: 3.95*
> *Distance traveled: 4,820 nm*
> *Days at sea: 271*
> *Storms logged: 8 (3 Force 8+, 1 Force 10)*
>
> **THE PEOPLE**
>
> *Sarah Walsh · Captain · Level 14 (Pilot) · 41,200 XP · Streak 365*
> *Hank · First Mate · Level 13 (Navigator) · 38,900 XP · Streak 358*
> *Mo · Engineer · Level 9 (Highliner) · 18,400 XP · Streak 178*
>
> **THE BOAT**
>
> *Fishing grounds used: 7*
> *Primary species: Coho salmon (38% of catch by weight)*
> *Best month: July (8,400 lbs)*
> *Worst month: February (haul-out, 412 lbs)*
> *Maintenance Marathon completions: 12*
> *Predictive maintenance wins: 7*
>
> **THE HONORS**
>
> *Achievements unlocked: 78 of 92 (85%)*
> *Lore fragments: 9 of 10*
> *Quest chains completed: 4 of 6*
> *World events experienced: 21*
> *Hidden mechanics discovered: 9 of 10 (Constellation: ⏳)*
> *Titles earned: 11 · Currently equipped: [The Chronicler]*
>
> **THE MONEY**
>
> *FishCoin earned (lifetime): 38,420*
> *FishCoin spent (lifetime): 31,640*
> *Most-redeemed perk: Coffee ashore (47 times)*

Below the numbers is a **map of the year**. Every pin she logged, every ground she tried, every storm she rode out, painted on the dark tiles. The map is dense in summer, sparse in February, dense again in fall, present but quiet in winter.

Below the map is a **lore fragment she has never seen**:

> *"A long pull, a strong pull, and a pull all together."*
> *— Nantucket whalers, calling the crew to the oars.*
>
> *You did it. The logbook is yours.*

Sarah screenshots it. She does not send it to anyone. She sits with it for a long time.

Then she closes the iPad and goes to bed.

Tomorrow is January 1. The system will detect that the year rolled over. It will archive the season. It will start a new ledger. It will keep the cumulative XP. It will keep the achievements. It will keep the lore. It will keep the streaks — except the streak counter, which resets, because streaks are for living years, not archived ones.

The system will be there in the morning.

### What the system does in response

**The annual review is generated automatically** by a combination of three systems:

- **vessel-quest** rolls up `vessel_quest_state`, `vessel_quest_chains`, `vessel_quest_events`, `vessel_quest_hidden` into a yearly summary.
- **crew-logbook + map-view** generate the map of the year (pin cluster by month).
- **catch-analytics + fuel-tracker + maintenance-scheduler** generate the "people" and "boat" sections.

The review is **not generated by an LLM.** It is generated by **deterministic rollups** of the same data the captain has been creating all year. The review is honest because the data is honest. Sarah could audit every number by scrolling her own logs.

**Season transition.** On January 1, the system:
- Archives the current season's FishCoin ledger to `~/.local/share/shiplog/fishcoin_season_2026.json`.
- Starts fresh FishCoin balances for the new year.
- Resets the streak counter (cumulative streak history preserved separately).
- Awards the **Vessel Birthday** bonus (×10 XP) to all crew on the anniversary of the first log entry.
- Surfaces a new "Year Ahead" card on the dashboard with the year's projected XP curve based on last year's pace.

### What the captain FEELS

**Recognition.** For one year, Sarah showed up. The system showed up too. The review is not a leaderboard. It is **a witness**. It says: *you did this. Here is the shape of it.* Sarah's relationship with the system on Day 365 is not transactional. It is **commemorative**.

**The system is now part of the boat's history.** Sarah's logbook is no longer just a record. It is **a chapter in the vessel's life**. The next captain who buys this boat, if Sarah ever sells it, will inherit a year of her work. The data is portable. The patterns are portable. The lessons are portable.

**The streak breaks.** Sarah's 365-day streak ends on January 1 (streak counters reset at the year boundary by design — see `vessel_quest_state.streakResetPolicy`). On January 2, the streak counter shows `1`. Sarah logs. The streak is alive again. The system is forgiving. The system does not punish her for the year rolling over. The system rewards her for showing up again.

**Design insight:** Day 365 is **the day the system becomes the artifact.** Up to now, the system has been a tool. On Day 365, the system becomes **the logbook itself** — the same artifact that captains have kept for ten thousand years, now digitized, now gamified, now personalized. The annual review is the moment the captain realizes: *this is what I built this year. This is what I will look back on.* The system must surface this clearly, once, and then **quiet down for January 2**, because the next year is starting and the system has work to do.

### What data has been accumulated

| Field | Value |
|-------|-------|
| `crew_logbook.entries` | 1,247 |
| Unique species | 22 |
| Total catch weight | 32,840 lbs |
| `maint_tasks.completed` | 156 |
| `maint_history` | 156 entries |
| `shiplog.fuel.entries` | 117 |
| `maint_engine_hours` | 2,184.7 |
| Map pins | 1,247 (7 grounds, ~12 storm cells, ~89 AIS contacts, 360 weather observations) |
| Total distance | 4,820 nm |
| `vessel_quest_state.xp` (captain) | 41,200 |
| `vessel_quest_state.level` | 14 (Pilot) |
| Achievements unlocked | 78 of 92 (85%) |
| Lore fragments unlocked | 9 of 10 (Constellation in progress) |
| Quest chains completed | 4 of 6 (Old Route and Mentor's Path partial) |
| World events experienced | 21 |
| Hidden mechanics discovered | 9 of 10 |
| Titles earned | 11 |
| FishCoin earned (lifetime) | 38,420 |
| FishCoin spent (lifetime) | 31,640 |
| Streak | reset to 1 (Jan 2) — 365 cumulative archived |

### What the game shows

**The Annual Review.** A single card. Numbers. People. Map. Lore.

Below it: **the new year is empty.** Same system. Same modules. Same tabs. The Quest tab still has a rank ladder (16 more ranks to Legend). There are still 14 achievements to find. The lore has one fragment left to unlock. There are two quest chains still in progress. The hidden mechanics have one left.

The game has not ended. The game has **continued**. Sarah has been playing it for a year. She will play it for another. Not because it is a game. Because it is the boat.

---

## Appendix: The Emotional Arc

The captain's emotional relationship with the system over a year:

```
Day 1      Curious → Surprised → "This is for me"
Day 7      Routine → Slight investment → "I want to keep the streak"
Day 30     Identity → "This is my data" → "I trust this"
Day 90     Partner → "It knows me" → "It has thoughts about my work"
Day 180    Infrastructure → Invisible → "It is the boat"
Day 365    Witness → "This is what I built" → "I will keep building"
```

## Appendix: What the System Does NOT Do

This is as important as what it does:

- **It does not judge bad days.** A day with one entry is recorded as faithfully as a day with twenty.
- **It does not require daily use.** The streak is incentive, not obligation. Missing a day is a small loss, not a catastrophe.
- **It does not pretend to be alive.** It is a system. It records. It rewards. It does not pretend to be a person.
- **It does not lock the captain in.** The data is exportable. The accounts are transferable. The captain owns the logbook, not the other way around.
- **It does not get louder over time.** It gets quieter. The Day 365 system is more restrained than the Day 7 system. The data is the noise; the system is the silence around it.
- **It does not surprise the captain with bad surprises.** Every event, every notification, every perk has been designed to be predictable. The only surprises are the hidden mechanics, which are delightful because they are rare.

## Appendix: The Three Promises the System Makes

1. **The data is yours.** Everything you enter is yours. You can export it. You can delete it. You can take it to another vessel. You can show it to your family. You can pass it to the next captain. The system does not own your record.

2. **The work is the reward.** Every point, every coin, every badge comes from real work — real logs, real maintenance, real catches. There is no shortcut. There is no purchase. There is no shortcut around the boat.

3. **The system will be here tomorrow.** The streak continues. The data accumulates. The seasons turn. The system does not go away. It is not a fad. It is not a campaign. It is the logbook. It will be there when the captain wakes up. It will be there when she goes to bed. It will be there next year, and the year after that, until the boat is sold or the captain retires or the system itself retires with the dignity of an Old Salt.

---

**End of document.**

*This is the UX. The features exist to serve this. If a feature does not appear in this story, it does not need to exist. If a moment in this story has no feature to support it, the feature is missing.*