/**
 * Vessel Quest — Epithets & Titles System
 * 
 * Earned titles displayed next to crew member names.
 * Each epithet has a check function against vessel stats.
 */

const EPITHETS = [
  // ── Logging Epithets ──────────────────────────────
  {
    id: 'the_steady',
    name: 'The Steady',
    icon: '📊',
    desc: '30-day logging streak',
    check: s => s.maxStreak >= 30,
    category: 'streak'
  },
  {
    id: 'the relentless',
    name: 'The Relentless',
    icon: '⚡',
    desc: '100-day logging streak',
    check: s => s.maxStreak >= 100,
    category: 'streak'
  },
  {
    id: 'night_owl',
    name: 'Night Owl',
    icon: '🦉',
    desc: '50 night-watch entries',
    check: s => s.nightEntries >= 50,
    category: 'time'
  },
  {
    id: 'early_bird',
    name: 'Early Bird',
    icon: '🐦',
    desc: 'Log before 5 AM twenty times',
    check: s => s.earlyBird >= 20,
    category: 'time'
  },
  {
    id: 'dawn_patrol',
    name: 'Dawn Patrol',
    icon: '🌅',
    desc: 'Log before 6 AM fifty times',
    check: s => s.earlyBird >= 50,
    category: 'time'
  },
  {
    id: 'the_chronicler',
    name: 'The Chronicler',
    icon: '📜',
    desc: '500 total log entries',
    check: s => s.totalLogs >= 500,
    category: 'volume'
  },
  {
    id: 'wordsmith',
    name: 'Wordsmith',
    icon: '✍️',
    desc: 'Average entry length > 100 characters',
    check: s => s.avgEntryLength >= 100,
    category: 'quality'
  },

  // ── Catch Epithets ────────────────────────────────
  {
    id: 'highliner',
    name: 'Highliner',
    icon: '🏆',
    desc: 'Log 1,000 catches',
    check: s => s.catches >= 1000,
    category: 'catch'
  },
  {
    id: 'fish_whisperer',
    name: 'Fish Whisperer',
    icon: '🐟',
    desc: 'Log 10 different species',
    check: s => s.uniqueSpecies >= 10,
    category: 'catch'
  },
  {
    id: 'big_game',
    name: 'Big Game Hunter',
    icon: '⚔️',
    desc: 'Log a single catch over 1,000 lbs',
    check: s => s.biggestCatch >= 1000,
    category: 'catch'
  },

  // ── Maintenance Epithets ──────────────────────────
  {
    id: 'wrench',
    name: 'Wrench',
    icon: '🔧',
    desc: 'Complete 25 maintenance tasks',
    check: s => s.maintCompleted >= 25,
    category: 'maintenance'
  },
  {
    id: 'engine_whisperer',
    name: 'Engine Whisperer',
    icon: '🧙',
    desc: 'Complete 50 maintenance tasks with zero overdue',
    check: s => s.maintCompleted >= 50 && s.overdueTasks === 0,
    category: 'maintenance'
  },
  {
    id: 'shipshape',
    name: 'Shipshape',
    icon: '✨',
    desc: 'Zero overdue maintenance for 90 days',
    check: s => s.daysWithoutOverdue >= 90,
    category: 'maintenance'
  },

  // ── Navigation Epithets ───────────────────────────
  {
    id: 'wayfinder',
    name: 'Wayfinder',
    icon: '🧭',
    desc: 'Plan 25 trips with waypoints',
    check: s => s.tripsPlanned >= 25,
    category: 'navigation'
  },
  {
    id: 'long_ranger',
    name: 'Long Ranger',
    icon: '🌊',
    desc: 'Travel 5,000 total nautical miles',
    check: s => s.totalDistance >= 5000,
    category: 'navigation'
  },
  {
    id: 'ocean_crosser',
    name: 'Ocean Crosser',
    icon: '🐬',
    desc: 'Travel 10,000 total nautical miles',
    check: s => s.totalDistance >= 10000,
    category: 'navigation'
  },

  // ── Safety Epithets ───────────────────────────────
  {
    id: 'storm_tested',
    name: 'Storm-Tested',
    icon: '⛈️',
    desc: 'Log during severe weather 5 times',
    check: s => s.stormEntries >= 5,
    category: 'safety'
  },
  {
    id: 'safety_first',
    name: 'Safety First',
    icon: '🦺',
    desc: 'Complete pre-departure checklist 25 times',
    check: s => s.fullChecklists >= 25,
    category: 'safety'
  },

  // ── Seasonal Epithets ─────────────────────────────
  {
    id: 'four_seasons',
    name: 'Four Seasons',
    icon: '🍂',
    desc: 'Log in all four seasons',
    check: s => s.uniqueSeasons >= 4,
    category: 'seasonal'
  },
  {
    id: 'year_round',
    name: 'Year-Round',
    icon: '📅',
    desc: 'Log in 12 different months',
    check: s => s.uniqueMonths >= 12,
    category: 'seasonal'
  },

  // ── Crew Epithets ─────────────────────────────────
  {
    id: 'the_mentor',
    name: 'The Mentor',
    icon: '👨‍🏫',
    desc: 'Crew of 5+ members',
    check: s => s.crewSize >= 5,
    category: 'crew'
  },
  {
    id: 'captain_blood',
    name: 'Old Salt',
    icon: '🧂',
    desc: '1,000 total entries + 100 maintenance + 100 catches',
    check: s => s.totalLogs >= 1000 && s.maintCompleted >= 100 && s.catches >= 100,
    category: 'special'
  },
  {
    id: 'renaissance',
    name: 'Renaissance Mariner',
    icon: '🎭',
    desc: 'Use all 5+ module types',
    check: s => s.modulesUsed >= 5,
    category: 'special'
  },
];

// ── Helper Functions ─────────────────────────────────

/**
 * Get all epithets a crew member has earned
 */
function getEarnedEpithets(stats) {
  return EPITHETS.filter(e => e.check(stats));
}

/**
 * Get the primary epithet (most recent/highest category)
 */
function getPrimaryEpithet(stats) {
  const earned = getEarnedEpithets(stats);
  if (earned.length === 0) return null;
  // Priority: special > seasonal > catch > navigation > maintenance > safety > streak > volume > time
  const priority = ['special', 'catch', 'navigation', 'maintenance', 'safety', 'seasonal', 'streak', 'volume', 'time', 'quality', 'crew'];
  for (const cat of priority) {
    const match = earned.find(e => e.category === cat);
    if (match) return match;
  }
  return earned[0];
}

/**
 * Format epithet for display
 */
function formatEpithet(epithet) {
  if (!epithet) return '';
  return `${epithet.icon} ${epithet.name}`;
}

// ── Export ────────────────────────────────────────────
if (typeof module !== 'undefined') {
  module.exports = { EPITHETS, getEarnedEpithets, getPrimaryEpithet, formatEpithet };
}
