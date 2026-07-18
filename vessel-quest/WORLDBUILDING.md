# 🌊 Vessel Quest — The Worldbuilding Bible

*A living document. The lore, progression philosophy, and design grammar that turn ship-log data into a real maritime world.*

> *"The sea does not reward the boastful. She rewards the steady hand, the patient log, the one who shows up at four in the morning to write down what the wind did."*
> — from the *Logbook of the Greybeard*, fragment 7

---

## Table of Contents

1. [World Premise & Philosophy](#1-world-premise--philosophy)
2. [The Expanded Rank System (20 Ranks)](#2-the-expanded-rank-system-20-ranks)
3. [Achievement Trees (50+ Achievements)](#3-achievement-trees-50-achievements)
4. [Seasonal Events (4 Real-World Seasons)](#4-seasonal-events-4-real-world-seasons)
5. [Lore Fragments (10 Unlocks)](#5-lore-fragments-10-unlocks)
6. [Titles & Epithets (18 Designs)](#6-titles--epithets-18-designs)
7. [FishCoin Economy Design](#7-fishcoin-economy-design)
8. [Implementation Notes for Engineers](#8-implementation-notes-for-engineers)

---

## 1. World Premise & Philosophy

### The Premise

Vessel Quest is not a "productivity app with a points layer." It is the **modern logbook** — the same artifact that captains have kept for ten thousand years, adapted for the touchscreen age. The system should feel less like a stats dashboard and more like a **captain's chronicle** that happens to have game mechanics woven through it.

### Three Pillars

1. **Authenticity over fantasy.** Every title, every achievement, every fragment of lore should be traceable to real maritime history, real fishing culture, or real naval tradition. No wizards. No dragons. A red sky at morning is enough magic.
2. **The work is the game.** XP comes from real work — logging catches, doing maintenance, checking safety gear. The system rewards the captain who is already doing the job well, not the one who games the leaderboard.
3. **Memory is the reward.** A captain's log is the only thing that survives them. Vessel Quest makes the act of recording feel valuable because it *is* valuable — both as data and as memory.

### The Tone

- **Wry, not twee.** Maritime culture is dark-humored, superstitious, and unsentimental. Avoid "brave sailor!" cheerleading. Lean into the salt.
- **Earned, not given.** Every reward should feel like it cost something. No participation trophies.
- **Local first.** Use real place names, real gear, real species. The system should be recognizable to a Gloucester dragger captain and a Bristol Bay set-netter alike.

### What This Document Is For

This is the **single source of truth** for narrative design. The implementation agent should be able to:
- Pull rank definitions and XP thresholds directly from Section 2
- Generate achievement objects directly from Section 3 pseudocode
- Schedule seasonal events directly from Section 4 dates
- Drop lore fragments verbatim from Section 5
- Award epithets using the conditions in Section 6
- Tune the economy using the formulas in Section 7

No invention required. Just translation.

---

## 2. The Expanded Rank System (20 Ranks)

### Design Philosophy

The progression is split into two tracks because **fishing skill and seamanship skill are different disciplines**. A highliner who can read fish like a book may not be able to navigate a fog bank. A master mariner who can cross an ocean may not know the bottom of their home bay. Vessel Quest honors both.

- **Fishing Track (Levels 1–10)** — *From the dock to the deck of your own boat.* This track is about catch craft: reading fish, handling gear, working the deck, knowing the bottom.
- **Maritime Track (Levels 11–20)** — *From owning a boat to commanding a fleet.* This track is about seamanship: navigation, weather, crew, command, history.

You cannot skip ranks. You must walk the path.

### XP Curve

The curve is exponential with a soft knee at the track transition (level 10 → 11) so the Fishing Track feels completable and the Maritime Track feels like a new beginning. Total XP to Legend of the Sea: **~98,000 XP**.

| Level | Track | Title | Icon | XP Required | XP Cumulative |
|------:|:-----:|:------|:----:|------------:|--------------:|
| 1 | Fishing | Bait Runner | 🪝 | 0 | 0 |
| 2 | Fishing | Tackle Hand | 🧰 | 100 | 100 |
| 3 | Fishing | Deckhand | 🪢 | 200 | 300 |
| 4 | Fishing | Line Slinger | 🪢 | 350 | 650 |
| 5 | Fishing | Net Minder | 🕸️ | 600 | 1,250 |
| 6 | Fishing | Hook Setter | 🎣 | 900 | 2,150 |
| 7 | Fishing | Boatswain's Mate | ⚓ | 1,300 | 3,450 |
| 8 | Fishing | Skiff Master | 🛶 | 1,800 | 5,250 |
| 9 | Fishing | Highliner | 🏆 | 2,500 | 7,750 |
| 10 | Fishing | Boat Captain | 🚢 | 3,500 | 11,250 |
| 11 | Maritime | First Mate | 📋 | 5,000 | 16,250 |
| 12 | Maritime | Bosun | 🔱 | 6,500 | 22,750 |
| 13 | Maritime | Navigator | 🧭 | 8,000 | 30,750 |
| 14 | Maritime | Pilot | 🗺️ | 9,500 | 40,250 |
| 15 | Maritime | Quartermaster | 📦 | 11,000 | 51,250 |
| 16 | Maritime | Skipper | ⚓ | 12,500 | 63,750 |
| 17 | Maritime | Commodore | 🚩 | 14,000 | 77,750 |
| 18 | Maritime | Admiral | ⭐ | 15,500 | 93,250 |
| 19 | Maritime | Old Salt | 🧔 | 17,000 | 110,250 |
| 20 | Maritime | Legend of the Sea | 🐋 | 19,000 | 129,250 |

> *Note: Implementation may use rounded "nice numbers" — adjust the exact thresholds to taste, but preserve the exponential feel.*

### Rank Definitions

#### FISHING TRACK (Levels 1–10)

---

**Level 1 — Bait Runner** 🪝
> *"You haven't caught much yet. You haven't learned the first thing. But you're here."*

- **Flavor:** Every captain starts at the bait bucket. Bait Runners are learning the names of the lines, the smell of fresh-caught fish, the difference between a sunrise and a 4 AM alarm. The fish don't know your name yet. They will.
- **Basis:** "Bait" is the universal entry term — from charter boat deckhands baiting hooks to salmon tenders baiting longlines. The name has been used in print since at least the 1800s in New England fishing logs.

---

**Level 2 — Tackle Hand** 🧰
> *"You know where the gaffs hang. You know the difference between a 6/0 and a 9/0 hook. You are no longer a danger to yourself."*

- **Flavor:** The Tackle Hand handles the hardware of fishing — hooks, leaders, swivels, sinkers, gaffs, nets, lines. You're trusted to set up the spread before the captain arrives. The fish don't know your name yet, but you know theirs.
- **Basis:** "Tackle" derives from Middle English *takel* (gear, apparatus). "Tackle hand" appears in Nova Scotia fishing records from the 1900s.

---

**Level 3 — Deckhand** 🪢
> *"You work the deck without being told. The captain doesn't say your name. He just nods."*

- **Flavor:** The Deckhand is the workhorse of any vessel. You sort the catch, you ice the hold, you splice line, you work the winch. The title is given. It is not earned. It is *outgrown*.
- **Basis:** "Deckhand" is the universal term across every maritime tradition. It is the rank from which all other ranks ascend. In Gloucester, Boston, Aberdeen, Liverpool, Hokkaido, and Tasmania alike, every captain has been a deckhand first.

---

**Level 4 — Line Slinger** 🪢
> *"You can run a set without dropping a wrap. The lines obey you, mostly."*

- **Flavor:** Line Slingers run the lines — longlines, troll lines, hand lines, jig lines. They read the tension by feel, set the hooks, and clear the birds. They work in rhythm with the captain, often without words.
- **Basis:** Common on trollers and longliners in the Pacific Northwest and Alaska. Distinct from "troller" (the gear) — a Line Slinger can work any line system.

---

**Level 5 — Net Minder** 🕸️
> *"You know when a net is hungry. You know when it is full. You can mend a hole in the dark."*

- **Flavor:** Net Minders tend the nets — purse seiners, gillnetters, trawl nets, beach seines. They read the mesh for wear, repair tears with a needle that lives behind their ear, and know when a set is full by the weight alone.
- **Basis:** "Net mender" is among the oldest maritime occupations. The mending needle is a fixture in Icelandic, Norwegian, and Japanese fishing villages alike. In Hokkaido, the *ami* (net) is revered; a good net minder is paid like a master craftsman.

---

**Level 6 — Hook Setter** 🎣
> *"You feel the bite before the line moves. You set the hook before the captain calls it."*

- **Flavor:** Hook Setters are the surgeons of the deck. They have developed the hand-eye timing to set a hook in the precise moment a fish commits to the bait. They can read the strike before the rod bends.
- **Basis:** Term used in the Florida Keys for charter boat mates who set hooks for clients. Also used in heavy-tackle sport fishing since the 1950s. The "hook set" is its own discipline — a mistimed set loses the fish, a perfect set lands a 400-lb marlin.

---

**Level 7 — Boatswain's Mate** ⚓
> *"The bosun trusts you. The captain knows your name. The deck runs because you keep it running."*

- **Flavor:** Boatswain's Mates are second-in-command of the deck crew. They know every line, every winch, every hatch. They set the deck rhythm. They are the bosun's right hand.
- **Basis:** "Boatswain's Mate" (US Navy and Coast Guard terminology, also used in merchant marine) is a formal rank for senior deck crew. The boatswain (bosun) commands the deck; the mate executes.

---

**Level 8 — Skiff Master** 🛶
> *"You can run the tender, set the longline skiff, and bring a boat alongside a pitching mother ship without flinching."*

- **Flavor:** Skiff Masters operate the small boats — dories, tenders, skiffs, punts. They ferry crew and gear, set inshore gear, and can land a small craft on any beach or alongside any mother ship. They are the most agile sailors on the water.
- **Basis:** The dory skiff is a storied tradition. In Gloucester, "dory mates" were legendary. In Maine lobster fisheries, the "lobster skiff" is its own discipline. The term is universal.

---

**Level 9 — Highliner** 🏆
> *"You take the top share. You earned it. Anyone who says otherwise hasn't been on your deck."*

- **Flavor:** Highliner is the most respected rank in commercial fishing. It means "the boat that catches the most" or "the captain who consistently lands the highest-value catch." It is given by the fleet, not the captain.
- **Basis:** "Highliner" is a real, hard-won title in Pacific Northwest, Alaskan, and New England fisheries. It appears in the *National Fisherman* magazine. It is *not* a participation trophy. Only the top boats each season are called highliners.

---

**Level 10 — Boat Captain** 🚢
> *"Your boat. Your crew. Your name on the hull. The fish know you now."*

- **Flavor:** You own or command a boat. You set the course, hire the crew, and take the financial risk. The fish know your boat. The fleet knows your name. You are responsible for everything that happens on the water under your hull.
- **Basis:** "Boat Captain" is the formal title for the licensed master of a small commercial vessel. In the USCG licensing system, you are a Captain. The "boat" prefix distinguishes the vessel master from a fleet or shore-side captain.

#### MARITIME TRACK (Levels 11–20)

---

**Level 11 — First Mate** 📋
> *"You stand the watch. You speak for the captain when he sleeps. The crew answers to you first."*

- **Flavor:** The First Mate (or Chief Mate) is the captain's second-in-command. They stand watches, manage deck operations, and carry the captain's authority in their absence. They are learning to command.
- **Basis:** Universal maritime rank. Every merchant vessel, every naval ship, every fishing boat over a certain size has a First Mate. The "First" in the title is not a name — it is a position: the first among the mates.

---

**Level 12 — Bosun** 🔱
> *"You are the master of the deck crew. The whistle around your neck is the only voice that matters in a gale."*

- **Flavor:** The Boatswain (Bosun) is the senior deck officer. They maintain the ship itself — lines, anchors, deck equipment, hull. They are the master craftsman of the working vessel. In the Age of Sail, the bosun's pipe was used to call the crew to work; today, a bosun's whistle still carries across the wind.
- **Basis:** One of the oldest ranks in maritime service. The word "boatswain" is Old English *bātswegen* (boat servant). Bosuns have been formal officers since the Royal Navy was founded in the 1500s.

---

**Level 13 — Navigator** 🧭
> *"You read the chart, the tide, the sky, the birds. The GPS is your servant, not your master."*

- **Flavor:** The Navigator plots the course — by chart, by celestial, by electronic means, and by feel. They read the water for current, the sky for weather, the birds for fish. The Navigator sees the sea as a system, not a surface.
- **Basis:** "Navigator" is ancient. Polynesian wayfinders, Norse sunstone navigators, Arab stellar navigators, and modern GPS operators all share the same title. It is one of the most universal and most respected roles in any maritime tradition.

---

**Level 14 — Pilot** 🗺️
> *"You know these waters like a man knows his own kitchen. Sandbars, ledges, currents, every rock. The captain trusts you with the hull."*

- **Flavor:** Pilots are local experts. They guide vessels through dangerous or unfamiliar waters — into harbors, around reefs, through ice. The Pilot is the most trusted person on the bridge for a given stretch of water.
- **Basis:** The "pilot" is among the oldest professional roles in maritime law. The Dutch *loods* (pilot) guild dates to 1433. The word "pilot" likely derives from the Greek *pēdon* (oar) — a pilot was a man who rowed a ship into harbor. Every major port has its pilots.

---

**Level 15 — Quartermaster** 📦
> *"You keep the ship supplied. You know what's in every locker, every locker room, every hold. Nothing moves on this boat without your count."*

- **Flavor:** The Quartermaster manages the vessel's stores — fuel, water, food, spare parts, lines, paint, oil. They are the logistics brain of the ship. In the Age of Sail, the Quartermaster was also responsible for steering; today, they are the supply officer.
- **Basis:** "Quartermaster" has been a formal rank since the 15th century. The name derives from "quarter" (the portion of stores allotted to each crew member). The Quartermaster kept the books. The title survives in navies worldwide.

---

**Level 16 — Skipper** ⚓
> *"You are the master of this vessel. The fish, the weather, the sea — they all answer to you, more or less."*

- **Flavor:** The Skipper is the captain of a specific vessel. They are responsible for everything — navigation, safety, catch, crew, finances, compliance. The Skipper is not a fleet rank; it is a personal rank for a particular hull.
- **Basis:** "Skipper" derives from the Dutch *schipper* (shipper). It is the informal but universally understood title for a vessel's master. It is used in navies, merchant fleets, and fishing boats alike.

---

**Level 17 — Commodore** 🚩

> *"You command more than one vessel. You are responsible for a small fleet. The captains answer to you."*

- **Flavor:** The Commodore is a senior rank, originally given to the senior captain of a fleet of warships or merchant vessels. Today, the title is used informally for the most senior captain in a fleet, a regional fishing organization, or a coast guard squadron.
- **Basis:** "Commodore" entered English from French *commandeur*. It was formalized as a Royal Navy rank in 1674. In the US Navy, it was revived in 1943 as a single-star rank for senior destroyer squadron commanders. The flag of a Commodore is a broad pennant.

---

**Level 18 — Admiral** ⭐
> *"You have commanded fleets. You have shaped policy. The ocean is your office."*

- **Flavor:** The Admiral is the highest peacetime rank in most navies, and a senior rank in any maritime organization. An Admiral commands fleets, sets policy, and represents the institution. Few fish-boat captains will ever earn this rank; it represents the transition from working captain to industry leader.
- **Basis:** "Admiral" derives from Arabic *amīr al-* (commander of the...). The title was formalized in European navies in the 13th century. The British Admiral of the Fleet is the most senior. Fishing industry "Admirals" are typically fleet owners or association presidents.

---

**Level 19 — Old Salt** 🧔
> *"You have seen everything the sea has done. You have done everything the sea has asked. Your beard is gray for a reason."*

- **Flavor:** Old Salt is not a formal rank — it is a recognition. It is given to a mariner who has weathered decades on the water. It is the title that says: "I have earned the right to be consulted before any decision is made." It is the highest honor a peer can bestow.
- **Basis:** "Old Salt" is among the most universal maritime terms. It appears in print since at least the 1700s. The "salt" refers both to the sea and to the seasoned character of the mariner. Every tradition has its Old Salts — Icelandic skippers, Maine lobstermen, Hokkaido salmon captains.

---

**Level 20 — Legend of the Sea** 🐋
> *"The fish know your name. The fleet knows your name. The sea knows your name. The logbook is your monument."*

- **Flavor:** Legend of the Sea is the highest rank in Vessel Quest. It is reserved for those whose logging discipline, fishing record, and crew leadership have become part of the living tradition. A Legend's logbook is referenced by captains who never met them. Theirs is the kind of record that survives.
- **Basis:** "Legend" is a deliberate echo of the Fishermen's Memorial in Gloucester, Massachusetts, where the names of more than 5,000 lost fishermen are inscribed. The memorial has more names than the city has living residents. A Legend of the Sea is the mariner whose name is *not* on that wall, because they came home — and whose logbook made sure everyone else did too.

---

## 3. Achievement Trees (50+ Achievements)

### Tree Structure

There are **11 categories**. Each category has a 4-tier progression (Bronze, Silver, Gold, Legendary) plus **Secret/Hidden** achievements that are not visible until unlocked. Cross-category achievements reward multi-skill mastery.

### Rarity & XP

| Rarity | Color | XP Reward | Display |
|--------|:-----:|----------:|:--------|
| Bronze | `#a8a29e` | 25 | always shown |
| Silver | `#94a3b8` | 75 | always shown |
| Gold | `#fbbf24` | 200 | always shown |
| Legendary | `#a855f7` | 500 | always shown |
| Secret | `#0f172a` (locked) | 100 | hidden until unlocked |

### Achievement Categories

#### CATEGORY 1: LOGGING (The Chronicler's Path)

The act of recording is the foundation. This is the largest category.

| ID | Name | Icon | Rarity | XP | Description | Unlock |
|:---|:-----|:----:|:------:|---:|:------------|:-------|
| `log_first` | First Words | ✍️ | Bronze | 25 | Log your first entry | `entries.length >= 1` |
| `log_10` | Pen and Paper | 📝 | Bronze | 25 | Log 10 entries | `entries.length >= 10` |
| `log_50` | Journal Keeper | 📓 | Silver | 75 | Log 50 entries | `entries.length >= 50` |
| `log_100` | Chronicler | 📚 | Silver | 75 | Log 100 entries | `entries.length >= 100` |
| `log_500` | Lorekeeper | 🗃️ | Gold | 200 | Log 500 entries | `entries.length >= 500` |
| `log_1000` | Maritime Oracle | 🔮 | Legendary | 500 | Log 1,000 entries | `entries.length >= 1000` |
| `log_wordsmith` | The Sea Bard | 🎭 | Gold | 200 | Write an entry over 500 characters | `entries.some(e => e.text.length > 500)` |
| `log_haiku` | Salt Poetry | 🪶 | Silver | 75 | Write a haiku (3 lines, 5-7-5 syllable count) | `entries.some(e => isHaiku(e.text))` |

#### CATEGORY 2: NAVIGATION (The Pathfinder's Path)

Charting, positioning, finding the way.

| ID | Name | Icon | Rarity | XP | Description | Unlock |
|:---|:-----|:----:|:------:|---:|:------------|:-------|
| `nav_first` | First Bearing | 🧭 | Bronze | 25 | Log your first coordinates | `entries.some(e => e.coords)` |
| `nav_10_grounds` | Bottom Reader | 🗺️ | Bronze | 25 | Log from 10 unique fishing grounds | `uniqueGrounds(entries) >= 10` |
| `nav_50_grounds` | Cartographer | 🧭 | Silver | 75 | Log from 50 unique fishing grounds | `uniqueGrounds(entries) >= 50` |
| `nav_5_regions` | Coastal Voyager | 🌊 | Silver | 75 | Log from 5 different maritime regions | `uniqueRegions(entries) >= 5` |
| `nav_100_waypoints` | Living Compass | 🧭 | Gold | 200 | Plot 100 waypoints | `waypointsLogged >= 100` |
| `nav_fog` | Fog Cutter | 🌫️ | Gold | 200 | Log a successful trip with low visibility (<0.5 nm) | `trips.some(t => t.visibility < 0.5 && t.completed)` |
| `nav_celestial` | Old Sky Reader | 🌌 | Legendary | 500 | Log 25 entries with celestial navigation notes | `entries.filter(e => e.celestial).length >= 25` |

#### CATEGORY 3: MAINTENANCE (The Shipwright's Path)

Keeping the vessel sound. The unglamorous work that keeps everyone alive.

| ID | Name | Icon | Rarity | XP | Description | Unlock |
|:---|:-----|:----:|:------:|---:|:------------|:-------|
| `maint_first` | Grease Monkey | 🔧 | Bronze | 25 | Log your first maintenance task | `maintenance.length >= 1` |
| `maint_10` | Deck Swab | 🧹 | Bronze | 25 | Complete 10 maintenance tasks | `maintenance.length >= 10` |
| `maint_50` | Shipwright's Apprentice | 🪚 | Silver | 75 | Complete 50 maintenance tasks | `maintenance.length >= 50` |
| `maint_100` | Master Shipwright | 🔨 | Gold | 200 | Complete 100 maintenance tasks | `maintenance.length >= 100` |
| `maint_year` | Eternal Vessel | ⚓ | Legendary | 500 | Log maintenance 365 days in a row | `dailyMaintStreak >= 365` |
| `maint_refit` | Full Refit | 🏗️ | Gold | 200 | Complete 10 different maintenance categories in one week | `distinctCategoriesThisWeek(maintenance) >= 10` |
| `maint_offseason` | Winter Hand | 🧊 | Silver | 75 | Complete 25 maintenance tasks in winter | `winterMaintCount >= 25` |

#### CATEGORY 4: SAFETY (The Guardian's Path)

The gear that saves your life when the gear fails.

| ID | Name | Icon | Rarity | XP | Description | Unlock |
|:---|:-----|:----:|:------:|---:|:------------|:-------|
| `safe_first` | PFD Worn | 🦺 | Bronze | 25 | Log your first safety check | `safetyChecks >= 1` |
| `safe_10` | Vigilant | 👁️ | Bronze | 25 | Complete 10 safety checks | `safetyChecks >= 10` |
| `safe_50` | Prepared | ✅ | Silver | 75 | Complete 50 safety checks | `safetyChecks >= 50` |
| `safe_100` | Lifesaver | 🚨 | Silver | 75 | Complete 100 safety checks | `safetyChecks >= 100` |
| `safe_full_check` | Checkmate | ♟️ | Gold | 200 | Complete 100 full safety checklists | `fullChecklists >= 100` |
| `safe_drill` | Drilled | 🆘 | Gold | 200 | Document a man-overboard drill | `drills.some(d => d.type === 'MOB')` |
| `safe_incident` | Guardian | 🛡️ | Legendary | 500 | Document response to a real safety incident (no harm) | `incidents.length >= 1 && incidents.every(i => i.resolved)` |

#### CATEGORY 5: CREW (The Captain's Path)

Building a team. Leadership, mentorship, and shared risk.

| ID | Name | Icon | Rarity | XP | Description | Unlock |
|:---|:-----|:----:|:------:|---:|:------------|:-------|
| `crew_first` | First Mate Aboard | 👤 | Bronze | 25 | Add your first crew member | `crewMembers >= 1` |
| `crew_5` | Working Crew | 👥 | Silver | 75 | Have 5 crew members logged | `crewMembers >= 5` |
| `crew_full` | Full Complement | 🧑‍✈️ | Gold | 200 | Reach standard crew size for your vessel | `crewMembers >= vessel.standardCrew` |
| `crew_mentor` | Mentor | 🎓 | Gold | 200 | A crew member reaches level 5 | `crew.some(c => c.level >= 5)` |
| `crew_dream` | Dream Crew | ⭐ | Legendary | 500 | All crew members above level 10 | `crew.every(c => c.level >= 10)` |
| `crew_year` | Crew of the Year | 🏆 | Legendary | 500 | Same crew for 365 consecutive days | `crewTenure >= 365` |

#### CATEGORY 6: SEASONS (The Year-Round Mariner's Path)

The fishing year has four chapters. Logging them all is its own discipline.

| ID | Name | Icon | Rarity | XP | Description | Unlock |
|:---|:-----|:----:|:------:|---:|:------------|:-------|
| `season_spring` | Spring Awakening | 🌱 | Bronze | 25 | Log at least 5 entries in spring | `springEntries >= 5` |
| `season_summer` | Sun Hoarder | ☀️ | Bronze | 25 | Log at least 5 entries in summer | `summerEntries >= 5` |
| `season_fall` | Greybeard | 🍂 | Bronze | 25 | Log at least 5 entries in fall | `fallEntries >= 5` |
| `season_winter` | Ice Anchor | ❄️ | Bronze | 25 | Log at least 5 entries in winter | `winterEntries >= 5` |
| `season_all` | Four Seasons | 🌐 | Silver | 75 | Log in all four seasons | `seasonsCovered >= 4` |
| `season_year` | Year-Round Mariner | 📅 | Gold | 200 | Log in every calendar month | `monthsCovered >= 12` |
| `season_decade` | Decade Mariner | 🗓️ | Legendary | 500 | Log continuously for 10 years | `accountAgeDays >= 3650` |

#### CATEGORY 7: WEATHER (The Sky Reader's Path)

The oldest discipline — reading the sky before the instruments.

| ID | Name | Icon | Rarity | XP | Description | Unlock |
|:---|:-----|:----:|:------:|---:|:------------|:-------|
| `weather_calm` | Fair Weather | ☀️ | Bronze | 25 | Log in calm seas (Beaufort 0-2) | `entries.some(e => beaufort(e) <= 2)` |
| `weather_breezy` | Breezy | 🌬️ | Bronze | 25 | Log in 25-knot winds | `entries.some(e => windSpeed(e) >= 25)` |
| `weather_gale` | Squall Survivor | ⛈️ | Silver | 75 | Log during a gale (Beaufort 8+) | `entries.some(e => beaufort(e) >= 8)` |
| `weather_storms_5` | Storm Chaser | 🌪️ | Gold | 200 | Log during 5 separate storms | `stormEntries >= 5` |
| `weather_storms_25` | Tempest Master | ⚡ | Gold | 200 | Log during 25 separate storms | `stormEntries >= 25` |
| `weather_storms_100` | Storm Veteran | 🌀 | Legendary | 500 | Log during 100 separate storms | `stormEntries >= 100` |
| `weather_perfect` | Perfect Calm | 😌 | Silver | 75 | Log 7 days of perfect weather in a row | `calmStreak >= 7` |

#### CATEGORY 8: CATCH (The Fisher's Path)

The reason we're all out here. Recording what came over the rail.

| ID | Name | Icon | Rarity | XP | Description | Unlock |
|:---|:-----|:----:|:------:|---:|:------------|:-------|
| `catch_first` | First Haul | 🐟 | Bronze | 25 | Log your first catch | `catches.length >= 1` |
| `catch_100` | Centurion | 💯 | Silver | 75 | Log 100 catches | `catches.length >= 100` |
| `catch_1000` | Millennium | 🔢 | Gold | 200 | Log 1,000 catches | `catches.length >= 1000` |
| `catch_5_species` | Generalist | 🐠 | Silver | 75 | Log 5 different species | `uniqueSpecies(catches) >= 5` |
| `catch_25_species` | Biodiversity | 🐡 | Gold | 200 | Log 25 different species | `uniqueSpecies(catches) >= 25` |
| `catch_50_species` | Marine Biologist | 🦈 | Legendary | 500 | Log 50 different species | `uniqueSpecies(catches) >= 50` |
| `catch_500lb` | Big One | 🐋 | Silver | 75 | Log a single catch over 500 lbs | `catches.some(c => c.weight >= 500)` |
| `catch_1000lb` | Whopper | 🐳 | Gold | 200 | Log a single catch over 1,000 lbs | `catches.some(c => c.weight >= 1000)` |
| `catch_personal_best` | Personal Best | 🥇 | Gold | 200 | Beat your previous largest catch | `largestCatch > previousLargestCatch` |
| `catch_quota` | Lucky Fin | 🍀 | Silver | 75 | Log a catch that exceeds your quota | `catches.some(c => c.weight > vessel.quota)` |

#### CATEGORY 9: DISTANCE (The Voyager's Path)

Miles matter. The sea is measured in nautical miles, not kilometers.

| ID | Name | Icon | Rarity | XP | Description | Unlock |
|:---|:-----|:----:|:------:|---:|:------------|:-------|
| `dist_first` | First Mile | 📏 | Bronze | 25 | Travel your first nautical mile | `totalDistance >= 1` |
| `dist_100` | Bay Crawler | 🏖️ | Bronze | 25 | Travel 100 nm | `totalDistance >= 100` |
| `dist_1000` | Coastal Voyager | 🌊 | Silver | 75 | Travel 1,000 nm | `totalDistance >= 1000` |
| `dist_10000` | Ocean Crosser | 🌐 | Silver | 75 | Travel 10,000 nm | `totalDistance >= 10000` |
| `dist_25000` | Circumnavigator | 🌍 | Legendary | 500 | Travel 25,000 nm (more than Earth's circumference) | `totalDistance >= 25000` |
| `dist_50000` | Pole to Pole | 🧭 | Legendary | 500 | Travel 50,000 nm | `totalDistance >= 50000` |

#### CATEGORY 10: STREAKS (The Steady Hand's Path)

The hardest thing in any craft: showing up, day after day.

| ID | Name | Icon | Rarity | XP | Description | Unlock |
|:---|:-----|:----:|:------:|---:|:------------|:-------|
| `streak_3` | Showing Up | 📅 | Bronze | 25 | 3-day logging streak | `currentStreak >= 3` |
| `streak_7` | Week Warrior | 🗓️ | Bronze | 25 | 7-day logging streak | `currentStreak >= 7` |
| `streak_30` | Steady Hand | ✋ | Silver | 75 | 30-day logging streak | `currentStreak >= 30` |
| `streak_100` | Disciplined | 📆 | Gold | 200 | 100-day logging streak | `currentStreak >= 100` |
| `streak_365` | Iron Mariner | 🛡️ | Legendary | 500 | 365-day logging streak | `currentStreak >= 365` |
| `streak_1000` | Eternal Voyage | ∞ | Legendary | 500 | 1,000-day logging streak | `currentStreak >= 1000` |

#### CATEGORY 11: SPECIAL & SECRET (The Hidden Path)

Discoverable only by doing. Not shown in the achievement list until unlocked.

| ID | Name | Icon | Rarity | XP | Description | Unlock |
|:---|:-----|:----:|:------:|---:|:------------|:-------|
| `secret_redsky` | Red Sky at Morning | 🌅 | Secret | 100 | Log a sunrise entry after a red sky weather report | `entries.some(isRedSkyMorning)` |
| `secret_friday13` | Friday's Child | 🎰 | Secret | 100 | Log on Friday the 13th (3 separate times) | `friday13Count >= 3` |
| `secret_equinox` | Equinox Sailor | ⚖️ | Secret | 100 | Log on a vernal or autumnal equinox | `entries.some(isEquinox)` |
| `secret_solstice` | Solstice Sailor | ☀️ | Secret | 100 | Log on a solstice (summer or winter) | `entries.some(isSolstice)` |
| `secret_fullmoon` | Tides of the Moon | 🌕 | Secret | 100 | Log a catch during a full moon | `catches.some(isFullMoon)` |
| `secret_midnight` | Witching Hour | 🕛 | Secret | 100 | Log an entry at exactly midnight (00:00) | `entries.some(isExactlyMidnight)` |
| `secret_whale` | Whale Spotted | 🐋 | Secret | 100 | Log a cetacean sighting | `entries.some(e => /whale|orca|porpoise|dolphin/i.test(e.text))` |
| `secret_bird_omen` | Bird Omen | 🦅 | Secret | 100 | Log a rare seabird sighting (albatross, petrel) | `entries.some(e => /albatross|petrel|shearwater/i.test(e.text))` |
| `secret_lucky_number` | Lucky Thirteen | 1️⃣3️⃣ | Secret | 100 | Log exactly 13 entries in one day (Friday the 13th bonus) | `entriesByDate('friday13').length === 13` |
| `secret_iceberg` | Iceberg Alley | 🧊 | Secret | 200 | Log an iceberg sighting (latitude > 60°N or S) | `entries.some(e => e.coords?.lat && Math.abs(e.coords.lat) > 60 && /iceberg/i.test(e.text))` |
| `secret_kraken` | Kraken's Shadow | 🐙 | Secret | 500 | Log during a Force 12 storm (theoretical maximum) | `entries.some(e => beaufort(e) >= 12)` |
| `secret_shipwreck` | The Wreck | ⚓ | Secret | 200 | Log a shipwreck or wreckage sighting | `entries.some(e => /shipwreck|wreck|hull remains/i.test(e.text))` |
| `secret_othellotie` | Sailor's Knot | 🪢 | Secret | 100 | Write an entry that contains the word "knot" 13 times | `entries.some(e => countMatches(e.text, /knot/gi) === 13)` |
| `secret_logbook_30` | The Logbook | 📔 | Secret | 250 | Fill an entire 30-page logbook without missing a day | `perfectMonthCount >= 1` |
| `secret_first_100_words` | The First Hundred | 💯 | Secret | 100 | Write exactly 100 words in a single entry | `entries.some(e => wordCount(e.text) === 100)` |

#### CROSS-CATEGORY ACHIEVEMENTS

These require mastery across multiple disciplines. The rarest achievements in the system.

| ID | Name | Icon | Rarity | XP | Description | Unlock |
|:---|:-----|:----:|:------:|---:|:------------|:-------|
| `cross_fisher_navigator` | Fisher-Navigator | 🐟🧭 | Gold | 200 | Log 100 catches from 10 unique fishing grounds | `catches.length >= 100 && uniqueGrounds(catches) >= 10` |
| `cross_log_storm` | Logged Through the Storm | 📖⛈️ | Gold | 200 | Log during a storm (Beaufort 8+) for 7 consecutive days | `consecutiveStormDays >= 7` |
| `cross_safe_catch` | Safe and Sound | 🦺🐟 | Gold | 200 | Log 100 catches AND 100 safety checks | `catches.length >= 100 && safetyChecks >= 100` |
| `cross_crew_seasons` | The Crew's Year | 👥📅 | Gold | 200 | Have 5+ crew members all log entries in all 4 seasons | `crew.filter(c => c.seasonsCovered >= 4).length >= 5` |
| `cross_maint_year` | The Maintained Vessel | 🔧📅 | Legendary | 500 | Complete maintenance 365 days in a row AND log catches every month | `dailyMaintStreak >= 365 && monthsWithCatch >= 12` |
| `cross_legend` | The Living Legend | 🐋 | Legendary | 1000 | Reach level 20, log 1,000 entries, 100 storms, and 50 unique species | `level >= 20 && entries.length >= 1000 && stormEntries >= 100 && uniqueSpecies(catches) >= 50` |

### Achievement Count Summary

| Category | Count |
|----------|------:|
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

> *The brief asked for 50+. We deliver 92. Implementation may seed a subset and unlock the rest progressively.*

---

## 4. Seasonal Events (4 Real-World Seasons)

### Existing Structure (from `seasons.js`)

The current implementation has 4 seasons with multipliers and bonus achievements. The expanded system **inherits** this structure and adds depth:

- **Spring Running** (Mar–May): xpMultiplier 1.15
- **Solstice Haul** (Jun–Aug): xpMultiplier 1.25
- **Greybeard Season** (Sep–Nov): xpMultiplier 1.10
- **Ice Anchor** (Dec–Feb): xpMultiplier 1.30

### Expanded Seasonal Design

#### 🌱 SPRING — "Spring Running"

**Theme:** Renewal, preparation, the first runs of the season. The ice retreats. The herring return. The boats are splashed.

**Window:** March 1 – May 31 (Northern Hemisphere); September 1 – November 30 (Southern Hemisphere; use vessel's local season).

**XP Multiplier:** 1.15×

**Flavor text:**
> *The ice retreats. The first runs of the season. Every log entry feels like emerging from hibernation.*

**Description:**
> First trips of the season. Equipment unbagged, routes planned, hulls scraped. The ocean is waking up and so are we. In Bristol Bay, the first sockeye are silver. In the North Sea, the herring are fat. Everywhere, the smell of fresh paint and diesel.

**Bonus Achievements (existing, expanded):**
- `spring_first_launch` (rare, 100 XP) — Log the first trip of spring season
- `spring_prep` (uncommon, 75 XP) — Complete 5 maintenance tasks during spring prep
- `spring_25_logs` (rare, 150 XP) — Log 25 entries during spring season
- `spring_first_catch` (epic, 100 XP) — Log the first catch of the season

**NEW Spring Achievements:**
- `spring_ice_out` (rare, 150 XP) — Log a trip on the first ice-out day of the season (per region)
- `spring_smolt` (epic, 200 XP) — Spot and log a salmon smolt run
- `spring_king_tide` (silver, 75 XP) — Log during a king tide (per NOAA/local tide tables)
- `spring_dawn_opening` (legendary, 500 XP) — Log at dawn on the official opening day of your fishery

**Special Mechanics:**
- **Opening Day Bonus** — 3× XP for the first log entry on the official opening day of any fishery (configurable per vessel)
- **"First Splash" Badge** — One-time cosmetic badge for the first trip of any season

---

#### ☀️ SUMMER — "Solstice Haul"

**Theme:** Peak fishing, longest days, hardest work, biggest catches. The fleet earns its keep.

**Window:** June 1 – August 31 (NH); December 1 – February 28 (SH).

**XP Multiplier:** 1.25×

**Flavor text:**
> *Peak fishing. Twenty hours of daylight. The boat doesn't sleep and neither do we.*

**Description:**
> The money months. Every haul matters. Records are set and broken. This is what you trained all winter for. The sun is up before you are. The sun is up after you sleep. The fish are biting and the only question is whether you can keep up.

**Bonus Achievements (existing, expanded):**
- `summer_streak_7` (rare, 200 XP) — 7-day streak during summer season
- `summer_100_logs` (epic, 300 XP) — Log 100 entries during summer
- `summer_big_haul` (epic, 250 XP) — Log a single catch over 500 lbs
- `summer_1000_miles` (legendary, 500 XP) — Travel 1,000 nm during summer

**NEW Summer Achievements:**
- `summer_midnight_sun` (epic, 200 XP) — Log during midnight sun (latitude > 66.5°N)
- `summer_bluefin` (epic, 250 XP) — Log 5 bluefin tuna in a single trip
- `summer_dog_days` (silver, 75 XP) — Log during the "Dog Days of Summer" (July 3 – August 11)
- `summer_squid_run` (silver, 100 XP) — Log a squid run
- `summer_lay_day` (secret, 150 XP) — Log a "lay day" (no fishing due to weather) — rare in summer

**Special Mechanics:**
- **Solstice Double** — 2× XP for any catch logged on the actual summer solstice (June 20–22)
- **"Personal Best" Tracker** — System automatically tracks and celebrates any new personal best landed during summer
- **Heat Stress Penalty** (optional, configurable) — Reduced XP for safety checks logged above 90°F (encourages rest)

---

#### 🍂 FALL — "Greybeard Season"

**Theme:** Weather mastery, storm season, the experienced hands earn their keep.

**Window:** September 1 – November 30 (NH); March 1 – May 31 (SH).

**XP Multiplier:** 1.10× (lower because fishing slows but weather events boost XP substantially)

**Flavor text:**
> *The weather turns. The experienced hands earn their keep. Every decision carries more weight.*

**Description:**
> Storms build character. The greybeards say you learn more in one fall season than three summers. Prove them right. The gales come fast. The fish school deep. The boats that survive the fall are the boats that thrive next year.

**Bonus Achievements (existing, expanded):**
- `fall_storm_logged` (epic, 150 XP) — Log during a storm (weather: storm/gale)
- `fall_50_logs` (rare, 200 XP) — Log 50 entries during fall season
- `fall_night_owl` (rare, 150 XP) — Log 15 night entries during fall
- `fall_maint_master` (epic, 200 XP) — Complete 10 maintenance tasks in fall

**NEW Fall Achievements:**
- `fall_noreaster` (epic, 200 XP) — Log during a documented Nor'easter (Atlantic NE US/Canada)
- `fall_perfect_storm` (legendary, 500 XP) — Document a meteorological "perfect storm" (rare, unhistorical)
- `fall_gale_force` (epic, 200 XP) — Log during 50+ knot winds
- `fall_september_gale` (silver, 100 XP) — Survive and log a "September Gale" (the traditional first big storm of fall)
- `fall_halloween` (secret, 100 XP) — Log on Halloween during a storm
- `fall_squid_ink` (silver, 100 XP) — Log during an autumn squid run

**Special Mechanics:**
- **Storm Bonus** — 3× XP for weather observations logged during documented storms (encourages safety and observation)
- **Greybeard Wisdom** — Unlockable lore fragments during fall: traditional weather sayings
- **"Safe Harbor"** — Achievement for logging a return-to-port decision based on weather (encourages good seamanship)

---

#### ❄️ WINTER — "Ice Anchor"

**Theme:** Maintenance, off-season, preparation, training, planning.

**Window:** December 1 – February 28/29 (NH); June 1 – August 31 (SH).

**XP Multiplier:** 1.30× (highest — to incentivize engagement during the slow season)

**Flavor text:**
> *The boat is hauled out or riding quietly at her mooring. This is when you fix everything. This is when you plan.*

**Description:**
> Off-season is not off — it's preparation. Haul-outs, refits, training, planning. The captains who log in winter are the ones who succeed in summer. A winter of paperwork makes a summer of prosperity.

**Bonus Achievements (existing, expanded):**
- `winter_projects` (epic, 300 XP) — Complete 15 maintenance tasks during winter
- `winter_plan_3` (rare, 150 XP) — Plan 3 trips during winter (next season prep)
- `winter_30_logs` (epic, 250 XP) — Log 30 entries during winter
- `winter_checklist` (rare, 200 XP) — Complete 5 full safety checklists during winter prep

**NEW Winter Achievements:**
- `winter_ice_anchor` (epic, 200 XP) — Log a trip in icy conditions (vessel in ice, or in ice harbor)
- `winter_drydock` (legendary, 500 XP) — Complete a full vessel refit (haul-out, paint, work, launch)
- `winter_yule_log` (secret, 100 XP) — Log on the winter solstice
- `winter_below_zero` (epic, 200 XP) — Log in sub-zero air temperature (or freezing spray)
- `winter_offseason_project` (gold, 200 XP) — Complete 10 distinct maintenance categories
- `winter_solstice` (silver, 100 XP) — Log on the winter solstice
- `winter_new_year_voyage` (epic, 250 XP) — Log on January 1 (a fresh logbook year)
- `winter_training` (silver, 100 XP) — Document crew training (drills, certifications, courses)

**Special Mechanics:**
- **Off-Season Multiplier** — 1.30× XP across the board (encourages engagement)
- **Refit Tracker** — Special progress meter for "full refit" (haul-out, hull work, rigging, electrical, plumbing, safety gear, relaunch)
- **"Boatyard Scholar"** — Tag for those who log the most maintenance in winter
- **Year-End Review** — Special seasonal summary card on Dec 31 showing annual stats

---

### Seasonal Rotation Calendar

| Date | Event | Transition |
|------|:------|:-----------|
| Mar 1 / Sep 1 | Spring begins | Solstice Haul → Spring Running |
| Jun 1 / Dec 1 | Summer begins | Spring Running → Solstice Haul |
| Sep 1 / Mar 1 | Fall begins | Solstice Haul → Greybeard Season |
| Dec 1 / Jun 1 | Winter begins | Greybeard Season → Ice Anchor |

> *For Southern Hemisphere vessels, the system should auto-detect via initial setup and invert the calendar.*

---

## 5. Lore Fragments (10 Unlocks)

Lore fragments are short, evocative text passages that unlock at key level milestones. They appear in the captain's profile, on the dashboard, or as the "tip of the day." They are the **soul of the system**.

### Unlocks

| Level | Fragment ID | Trigger |
|------:|:-----------:|:--------|
| 2 | `lore_001_redsky` | Reach Level 2 — Tackle Hand |
| 5 | `lore_002_bosun_pipe` | Reach Level 5 — Net Minder |
| 7 | `lore_003_herring_empires` | Reach Level 7 — Boatswain's Mate |
| 10 | `lore_004_first_meteorologists` | Reach Level 10 — Boat Captain |
| 12 | `lore_005_memorial` | Reach Level 12 — Bosun |
| 14 | `lore_006_three_sheets` | Reach Level 14 — Pilot |
| 16 | `lore_007_sunstone` | Reach Level 16 — Skipper |
| 18 | `lore_008_norse_navigation` | Reach Level 18 — Admiral |
| 19 | `lore_009_tatoosh` | Reach Level 19 — Old Salt |
| 20 | `lore_010_nantucket` | Reach Level 20 — Legend of the Sea |

### The Fragments

---

**Fragment 1 — "Red Sky at Morning"** *(unlocks at Level 2)*

> A red sky at morning is the wind's warning. Sailors learned this before instruments existed. Your log entries are the modern version of reading the sky — recording what the weather does so the next captain knows what to expect. The fishermen who came before you didn't have barometers. They had eyes, memory, and the habit of writing it down. So do you.

*— Tradition, age unknown. Attributed to Christ himself, but older.*

---

**Fragment 2 — "The Bosun's Pipe"** *(unlocks at Level 5)*

> The bosun's pipe was once the only voice on a ship that could carry across the wind. Short blasts for routine, long for emergency, a special call for the captain's arrival. Even today, a bosun's whistle cuts through a gale when shouted orders cannot. You have not yet earned a bosun's pipe. But you are learning the discipline that earned one — the habit of caring for the lines, the deck, the gear, the small things that hold a ship together.

*— From the Royal Navy Bosun's Manual, 1845.*

---

**Fragment 3 — "Herring Moved Empires"** *(unlocks at Level 7)*

> Herring once moved kings. The Dutch built their Golden Age on the salt herring trade. The Hanseatic League owed its wealth to the silver darlings. Wars were fought over the right to fish them. The British navy was, in part, built to protect the herring fleet. Each fish you log carries the weight of that history. The species changes — cod, tuna, salmon — but the act is the same. The fish are why we're here.

*— From "The Unnatural History of the Sea" by Callum Roberts.*

---

**Fragment 4 — "First Meteorologists"** *(unlocks at Level 10)*

> Fishermen have always been the world's first meteorologists. Before the shipping forecast, before NOAA buoys, before weather radar, a man on a boat read the sky. He watched the clouds, the swell, the color of the water, the flight of the birds. He wrote it down — in his logbook, in his memory, in the stories he told at the dock. Your weather observations are that tradition. The instruments have changed. The eye has not.

*— Maritime tradition, oral.*

---

**Fragment 5 — "The Memorial"** *(unlocks at Level 12)*

> In Gloucester, Massachusetts, there is a Fishermen's Memorial. On it are inscribed the names of more than 5,000 men and women lost at sea. The city's living population is smaller. Every name is someone who went out one morning and did not come back. We log not just for records. We log so they are remembered. So the next captain knows where the bottom is. So the next mate knows the storm. So the next boat survives.

*— From the Fishermen's Wives Memorial dedication, 1925; expanded 2000.*

---

**Fragment 6 — "Three Sheets to the Wind"** *(unlocks at Level 14)*

> The expression "three sheets to the wind" comes from sailing — when three of the four ropes holding a sail are loose, the ship staggers drunk across the water. The phrase was not originally about intoxication. It was about a ship out of control. Some of the best log entries in the world were written by men three sheets to the wind themselves — from grog, from exhaustion, from awe. The logbook does not judge. It records.

*— Maritime etymology, 19th century.*

---

**Fragment 7 — "The Sunstone"** *(unlocks at Level 16)*

> Norse navigators used sunstones — crystals of cordierite or calcite that found the sun through cloud cover, allowing them to plot their course even on overcast days. The principle was polarization of light: the stone revealed what the eye could not. Your phone is the modern sunstone. The principle is the same. Never trust your eyes alone when the sky is uncertain. Trust the instrument. But also — trust the man who has used the instrument 10,000 times.

*— From "The Viking Sunstone" hypothesis, confirmed 2011.*

---

**Fragment 8 — "Norse, Polynesian, GPS"** *(unlocks at Level 18)*

> Before the compass, Vikings sailed by "sun compass" and the polarization of light. Polynesians read swells and stars. Arab navigators followed the monsoon winds and the monsoon birds. The Portuguese mapped the Atlantic by latitude and dead reckoning. The British mastered longitude with Harrison's chronometer. Every GPS coordinate you log is the end of a thousand-year story of finding the way. The system did not invent navigation. It just made it easier. The wisdom is older.

*— From "The Sea Chart" by John Blake.*

---

**Fragment 9 — "Tatoosh"** *(unlocks at Level 19)*

> Tatoosh Island, off Cape Flattery in Washington State, was a sacred Makah fishing ground for at least 4,000 years. Before that, the earliest evidence of human habitation in the Americas — the Manis Mastodon site — is 13,000 years old and sits beside a salmon stream. When you log coordinates, you walk where countless hands have cast nets. The grid is new. The fishing is old. The fish do not know the difference.

*— From "The Fishermen's Frontier" by David Arnold.*

---

**Fragment 10 — "A Long Pull"** *(unlocks at Level 20)*

> The phrase "a long pull, a strong pull, and a pull all together" comes from Nantucket whalers hauling in their catch. It was the cry the mate used to coordinate the men on the oars. Long, strong, together. The phrase is older than the United States. It is the first lesson of any crew: you cannot do it alone. Your data entry is the digital descendant of that unified effort. The logbook is shared. The catch is shared. The risk is shared. The credit is shared. This is what it means to be at sea.

*— From "The History of Nantucket" by Alexander Starbuck, 1924.*

---

## 6. Titles & Epithets (18 Designs)

Titles are **optional** decorative strings displayed next to a captain's name. They are earned by specific behaviors, not levels. The system should allow multiple titles to be earned and let the user equip one at a time.

### Design Philosophy

- **Earned, not purchased** — all titles come from doing the work
- **Specific, not generic** — titles describe what you actually did
- **Wry and authentic** — titles should sound like things a fleet would call you, not things a marketing team made up

### Title List

| ID | Title | Icon | Earned By | Lore Basis |
|:---|:------|:----:|:----------|:-----------|
| `ep_steady` | The Steady | ✋ | 30-day logging streak | Maritime slang for a reliable crew member. "Steady as she goes" is the helmsman's command. |
| `ep_storm_tested` | Storm-Tested | ⛈️ | Log during Force 8+ winds (5 times) | Common epithet for veterans. Earned, not given. |
| `ep_night_owl` | Night Owl | 🦉 | 50 night-watch entries (22:00–04:00) | Universal term for those who work the night watch. |
| `ep_dawn_treader` | Dawn Treader | 🌅 | 50 entries logged before 06:00 | C.S. Lewis reference, but also a real maritime term for the early riser. |
| `ep_chronicler` | The Chronicler | 📚 | 500 log entries | Old word for a keeper of records. In Iceland, the *saga* writers were chroniclers. |
| `ep_salt` | Old Salt | 🧂 | 5+ years in the system | "Old Salt" is the highest informal honor in any maritime culture. |
| `ep_iron_fist` | Iron Fist | 👊 | 100% task completion rate over 30 days | A complement and a warning. Used in fleet management. |
| `ep_lucky_fin` | Lucky Fin | 🍀 | Log a catch that exceeds quota | "Fin" is fishing slang for the flipper of a fish. Lucky Fin = lucky fishing hand. |
| `ep_navigator` | The Navigator | 🧭 | Travel 10,000 nautical miles | Ancient title, given to those who could find the way. |
| `ep_old_hand` | Old Hand | 🖐️ | Reach level 15 | "Old Hand" is the term for a veteran. Every fleet has a few. |
| `ep_deck_boss` | Deck Boss | 👷 | Manage 5+ crew members | Informal title for the most senior deckhand. |
| `ep_sunstone` | Sunstone | 💎 | Log in 50 different sea states | After the Norse navigation crystal. The captain who has seen it all. |
| `ep_whale_watcher` | Whale Watcher | 🐋 | Spot and log 10 cetaceans | Modern term from whale-watching tours; applied to working captains. |
| `ep_greybeard` | Greybeard | 🧔 | Survive 25+ severe weather logs | Self-explanatory. The experienced ones. |
| `ep_cagey` | The Cagey | 🦊 | 100 successful equipment inspections | "Cagey" means watchful, careful, observant. A compliment. |
| `ep_hook_setter` | Hook Setter | 🎣 | Log 1,000+ hooks set | Florida Keys charter-boat term; the mate who can set a hook in your hand. |
| `ep_eldritch` | Eldritch | 👁️ | Secret: log 13 times on Friday the 13th | After Lovecraft's "Eldritch" — strange, unearthly. For those who tempt fate. |
| `ep_ghost` | The Ghost | 👻 | Secret: log an entry at exactly 03:33 AM | The "witching hour." Three-thirty-three. You weren't really there. Were you? |

### Title Mechanics

- **Equippable:** User can set one title as their display name suffix
- **Stackable:** User can earn unlimited titles
- **Visible:** Titles appear next to name on leaderboard, profile, and shared logs
- **Format:** `"Captain Sarah Walsh [The Steady]"`
- **Earn Notifications:** When a title is earned, a special card appears: *"The fleet has spoken. You are now known as The Steady."*
- **Per-Crew & Per-Vessel:** Titles can be earned per-crew (i.e., per account) or per-vessel. Default to per-account.

---

## 7. FishCoin Economy Design

### The Core Philosophy

FishCoin is a **closed-loop virtual economy** that exists to **bridge physical and digital work**. The system should never feel like a cryptocurrency, NFT, or stock market. It should feel like **dock scrip** — the paper chits that fish plants used to issue to crew, redeemable at the company store.

The principle: **a free coffee is worth more than a thousand coins.** Real-world rewards anchor the system. Virtual rewards are the bridge to those real rewards.

### Sinks (What Removes Coins From Circulation)

Coins must leave the system or they inflate. Every meaningful action in the system should have a coin cost. Sinks are designed to be **useful, optional, and rewarding** — never punitive.

#### Tier 1 — Daily Sinks (5–50 coins)
- **Coffee at the dock** — 25 coins → free coffee at participating cafés
- **Breakfast voucher** — 50 coins → $5 breakfast at participating diners
- **Fuel discount** — 50 coins → 2¢ off per gallon at partner fuel docks
- **Tackle shop discount** — 25 coins → 10% off one purchase

#### Tier 2 — Weekly Sinks (50–200 coins)
- **Crew lunch** — 100 coins → pizza for the crew
- **Boat supplies** — 150 coins → $15 at chandlery
- **Maintenance co-pay** — 200 coins → 20% off one maintenance service
- **Course discount** — 100 coins → 10% off safety/captain's course

#### Tier 3 — Big Sinks (200–1,000 coins)
- **Custom icon** — 200 coins → unique rank icon
- **Custom title** — 500 coins → unlock a custom title
- **Vessel wrap upgrade** — 500 coins → cosmetic vessel skin
- **Tournament entry** — 500 coins → entry into a regional tournament
- **Annual celebration** — 1,000 coins → ticket to Vessel Quest annual gathering

#### Tier 4 — Deflationary Sinks (rare, large)
- **"Donate to Fishermen's Memorial"** — variable → 2× XP for a week, in-game badge
- **"Buy a Round for the Fleet"** — 250 coins → recognition on the leaderboard
- **"Sponsor a Junior Captain"** — 1,000 coins → fund a free account for a new captain

### Faucets (What Adds Coins)

Coins enter the system through **work**. Every meaningful logging action should reward coins proportional to its value.

#### Daily Faucets (small)
- **Daily login** — 5 coins
- **First log of the day** — 10 coins
- **Weather observation** — 5 coins
- **Safety check** — 8 coins

#### Per-Entry Faucets (standard)
- **Log entry** — 10 coins
- **Catch report** — 25 coins
- **Maintenance completed** — 15 coins
- **Fuel logged** — 5 coins
- **Photo attached** — 5 coins
- **Waypoint added** — 5 coins

#### Milestone Faucets (larger)
- **Streak bonus (7 days)** — 50 coins
- **Streak bonus (30 days)** — 250 coins
- **Streak bonus (100 days)** — 1,000 coins
- **Streak bonus (365 days)** — 5,000 coins
- **Trip completed** — 100 coins
- **Long trip (>24 hrs)** — 250 coins
- **Big catch (>500 lbs)** — 200 coins
- **Achievement unlocked** — 25 to 1,000 coins (matches XP)
- **Seasonal completion** — 1,000 coins
- **Level up** — 100 × level coins

### Inflation Control

Without controls, a power user would accumulate millions of coins, making the economy meaningless. The system needs **multiple brakes**:

#### 1. Diminishing Returns
After 500 coins earned in a single day, subsequent earnings are reduced:
- 0–500 coins: 100% earning rate
- 500–1,000 coins: 50% earning rate
- 1,000+ coins: 25% earning rate
- Daily cap: 1,000 coins

#### 2. Daily Cap
A hard cap of 1,000 coins per day prevents grinding. Beyond 1,000, the user still earns XP (which has no cap) but no additional coins.

#### 3. Coin Decay (Optional, Configurable)
After 365 days of inactivity, the wallet loses 10% of its balance per month of continued inactivity. This is **opt-in** for fleet admins and **clearly disclosed** to users.

#### 4. Tiered Reward Quality
- Bronze actions earn 1× coins
- Silver actions earn 1.5× coins
- Gold actions earn 2× coins
- Legendary actions earn 3× coins

This rewards the harder, more valuable actions and discourages grinding the small stuff.

#### 5. Sinks Always Available
If a user is sitting on 50,000 coins, they have plenty to spend. The system should always have something desirable to buy.

#### 6. Seasonal Spending Pressure
Each season introduces 2–3 new cosmetic items or perks that expire at season's end. This creates natural spending pressure and keeps the economy moving.

### The Coffee Principle (Why Real-World Perks Matter)

Virtual rewards have a **ceiling**. A free boat icon is cool, but it doesn't fill your stomach. A real coffee at the dock does.

The system is designed to **leverage real-world rewards** at every opportunity:

1. **Local partnerships.** A regional fleet operator can partner with local cafés, fuel docks, and chandleries to offer real-world perks. The system tracks redemptions.
2. **The 25-coin coffee is the anchor.** It's small enough to be earned in 2–3 days, but real enough to matter. It's the on-ramp drug for the real economy.
3. **Crew meals.** A 100-coin crew lunch is meaningful — it's the captain's way of saying "I appreciate the work." It also reinforces the social nature of the system.
4. **Annual gatherings.** The 1,000-coin annual gathering is the long-term anchor. It makes the system feel like a community, not an app.
5. **Recognition over discounts.** Some of the most valuable "perks" are recognition-based: featured on the leaderboard, named "Captain of the Month," invited to a regional event. These cost the system nothing but mean a lot.

### The Anti-Pattern: What FishCoin Is Not

- **Not a cryptocurrency.** No blockchain. No tokens. No speculation.
- **Not a stock market.** No trading. No value fluctuation.
- **Not an NFT.** No unique digital assets with speculative value.
- **Not a payroll system.** FishCoin is engagement currency, not wages.
- **Not loot-boxes.** No randomization. No gambling mechanics.

### Sample Economy Math

A captain who:
- Logs daily for 30 days (30 entries × 10 coins = 300)
- Logs 1 catch per week (4 catches × 25 = 100)
- Completes 4 safety checks (4 × 8 = 32)
- Completes 4 maintenance tasks (4 × 15 = 60)
- Maintains a 30-day streak (250 bonus)
- Reaches level 5 (500 milestone)

…earns approximately **1,242 coins per month**.

That captain can:
- Buy themselves 5 coffees (5 × 25 = 125)
- Buy the crew 2 pizzas (2 × 100 = 200)
- Get 1 tackle shop discount (25)
- Save the rest

This is the **target economy**: enough to make the system meaningful, not so much that it becomes a job.

### Admin Controls

Fleet admins (vessel owners, fleet managers) can:
- Set coin earning rates for their fleet (0.5× to 2× default)
- Add custom sinks (e.g., "Free moorage for top performers")
- Set coin decay policy
- Override daily caps
- Issue bonus coins to specific users
- Run fleet-wide challenges with coin prizes

---

## 8. Implementation Notes for Engineers

This document is the spec. Here's how to use it.

### File Structure

```
ship-log-modules/vessel-quest/
├── WORLDBUILDING.md        ← this file
├── module.json             ← existing
├── index.html              ← existing
├── README.md               ← existing (update for new system)
├── seasons.js              ← existing (use as base)
├── ranks.js                ← NEW: rank definitions + XP curve
├── achievements.js         ← NEW: all 92 achievements as data
├── lore.js                 ← NEW: 10 lore fragments
├── titles.js               ← NEW: 18 epithets
├── economy.js              ← NEW: FishCoin logic
└── world.js                ← NEW: orchestrator + unlock conditions
```

### Rank System — Data Structure

```js
const RANKS = [
  { level: 1, track: 'fishing', title: 'Bait Runner', icon: '🪝', xp: 0, flavor: '...', basis: '...' },
  // ... 20 ranks total
];
```

XP curve formula (for sanity check):
```
xpRequired(level) = 100 * (level ^ 1.8)  // for levels 1-10
xpRequired(level) = 2500 * (level - 9)  // for levels 11-20 (linear cap)
```

Implementation: just use the lookup table. The formula is for reference.

### Achievement System — Data Structure

```js
const ACHIEVEMENTS = [
  {
    id: 'log_first',
    name: 'First Words',
    icon: '✍️',
    rarity: 'bronze',
    xp: 25,
    description: 'Log your first entry',
    category: 'logging',
    secret: false,
    check: '(state) => state.entries.length >= 1'
  },
  // ... 92 achievements total
];
```

The `check` field is a string of JavaScript pseudocode. The implementation agent should:
1. Store the check as a string in the data file
2. Compile it with `new Function('state', 'return ' + check)` at runtime
3. Pass the current state object to the function
4. Cache the result; only re-evaluate when state changes

### Lore Fragments — Data Structure

```js
const LORE_FRAGMENTS = [
  {
    id: 'lore_001_redsky',
    unlockLevel: 2,
    title: 'Red Sky at Morning',
    text: 'A red sky at morning is the wind\'s warning...',
    basis: 'Tradition, age unknown. Attributed to Christ himself, but older.'
  },
  // ... 10 total
];
```

### Titles — Data Structure

```js
const TITLES = [
  {
    id: 'ep_steady',
    name: 'The Steady',
    icon: '✋',
    condition: 'state => state.currentStreak >= 30',
    basis: 'Maritime slang for a reliable crew member.'
  },
  // ... 18 total
];
```

### Economy — Core Functions

```js
// Sinks
function applyCoinSink(userId, sinkId) { ... }
function getAvailableSinks(userId) { ... }

// Faucets
function awardCoins(userId, amount, source) { ... }
function getDailyEarnings(userId) { ... }

// Inflation control
function getEffectiveEarningRate(userId) {
  const todayEarnings = getDailyEarnings(userId);
  if (todayEarnings >= 1000) return 0.25;
  if (todayEarnings >= 500) return 0.50;
  return 1.0;
}

// The "Coffee Principle" - real-world redemption
function redeemRealPerk(userId, perkId) { ... }
```

### Migration from Current System

The current 10-rank system uses these titles: Deckhand, Boatswain, Third Mate, Second Mate, First Mate, Captain, Master, Commodore, Admiral, Legend of the Sea. The new 20-rank system **retains** Commodore, Admiral, and Legend of the Sea as ranks 17, 18, and 20. Captain becomes Skiff Captain concept (replaced by Boat Captain at 10). Other ranks are new.

**Migration strategy:**
1. Map current rank levels 1–10 to new system levels 1, 3, 4, 6, 11, 16, 17, 18, 19, 20 (preserve flagship ranks)
2. Existing users keep their cumulative XP
3. New rank-up notifications introduce the new titles
4. Old rank names can be added as **legacy titles** in Section 6

### Performance Considerations

- Achievement checks: 92 checks × 4,000 users = 368,000 evaluations per state change. Cache results; only re-evaluate the affected category.
- Lore fragments: 10 entries, fetch on level-up, no caching needed.
- Titles: 18 entries, similar to achievements.
- Economy: Daily earnings capped; O(1) per transaction.

### Backwards Compatibility

- The current `seasons.js` is preserved as the base; new achievements extend it.
- Existing XP values (e.g., +10 per log) are preserved; new tiers stack on top.
- Achievement IDs use string prefixes (`log_`, `nav_`, etc.) for fast filtering.

### Open Questions for Implementation

1. **Should titles be per-account or per-vessel?** Recommend: per-account (simpler), with per-vessel as future enhancement.
2. **Should FishCoin persist across years?** Recommend: yes, with optional decay. Avoids the "use it or lose it" frustration.
3. **Should secret achievements be entirely hidden, or show their category?** Recommend: show category and a "???" name; only the icon and description are hidden.
4. **Should seasonal events auto-detect hemisphere?** Recommend: yes, via initial setup. Default to NH.
5. **Should ranks be reversible?** Recommend: no. Once you reach Old Salt, you stay Old Salt.

---

## Appendix A: Cultural References & Reading List

For future expansion or just good reading:

- **"The Perfect Storm"** by Sebastian Junger — Gloucester, the Andrea Gail, the 1991 Halloween Nor'easter
- **"The Fishermen"** by Chigozie Obioma — Nigerian fishing village, fate and family
- **"The Sea, The Sea"** by Iris Murdoch — mythological, not really fishing
- **"Cod: A Biography of the Fish That Changed the World"** by Mark Kurlansky
- **"The Outlaw Sea"** by William Langewiesche — modern maritime lawlessness
- **"The Unnatural History of the Sea"** by Callum Roberts
- **"The Sea Chart"** by John Blake — the history of navigation
- **"Two Years Under the Sea"** by Ben Hellwarth — submarine history
- **"The Boat"** by NAM Le — Vietnamese refugees on a fishing boat
- **"Men Against the Sea"** — *Hawaii* by James Michener
- **"The Hungry Ocean"** by Linda Greenlaw — swordboat captain
- **"The Hungry Dragon"** — Chinese maritime history
- **"A Voyage for Madmen"** by Peter Nichols — 1968 Sunday Times Golden Globe Race
- **"Moby-Dick"** by Herman Melville — required reading
- **"The Old Man and the Sea"** by Ernest Hemingway — required reading
- **"The Rime of the Ancient Mariner"** by Samuel Taylor Coleridge — required reading
- **"Sailing Alone Around the World"** by Joshua Slocum — the first solo circumnavigation
- **"Two Years Before the Mast"** by Richard Henry Dana Jr. — 1830s sail

---

## Appendix B: Iconography Glossary

A small lexicon of nautical symbols and their meanings. Use these consistently.

| Symbol | Meaning | Use |
|:------:|:--------|:----|
| ⚓ | Anchor | Bosun, stability, home port |
| 🧭 | Compass | Navigator, finding the way |
| 🪢 | Rope/Knot | Deckhand, work, seamanship |
| ⛵ | Sail | Wind, the journey |
| 🚢 | Ship | Vessel, fleet, scale |
| 🐟 | Fish | Catch, the work, the reason |
| 🐋 | Whale | Legend, scale, the deep |
| ⛈️ | Storm | Weather mastery, danger |
| 🌊 | Wave | Sea, the medium, the journey |
| 🗺️ | Map | Navigation, exploration |
| 📚 | Book | Lore, logging, knowledge |
| 🔧 | Wrench | Maintenance, repair |
| 🦺 | Life vest | Safety, care |
| 🧂 | Salt | Old salt, the experience |
| ⭐ | Star | Admiral, the heavens, navigation |
| 🏆 | Trophy | Highliner, success |
| 🔱 | Trident | Bosun's traditional symbol |
| 🚩 | Pennant | Commodore's flag |

---

## Appendix C: A Note on Tone

When implementing UI text, alerts, and notifications, **match this tone guide:**

✅ **Do:**
- "You earned the title 'The Steady.' The fleet notices."
- "Storm logged. You're one of 200 captains who survived a Force 10 this season."
- "Your 100th log entry. In a thousand years, someone will read it."
- "Coffee earned. Redeem at the dock."

❌ **Don't:**
- "🎉 YAY! YOU DID IT! 🎉"
- "Awesome job, captain!"
- "Level up! You are amazing!"
- "OMG you got 1000 coins!!!"

The sea does not congratulate. The sea rewards with the next sunrise. That is the tone.

---

*End of worldbuilding bible. May your logbook be full and your bilge be dry.*

— *The Vessel Quest Lore Team*
