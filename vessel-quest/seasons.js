/**
 * Vessel Quest — Seasonal Events Engine
 * 
 * Real-world seasons drive in-game events with bonus XP,
 * limited-time achievements, and thematic modifiers.
 */

const SEASONS = {
  spring: {
    id: 'spring',
    name: 'Spring Running',
    icon: '🌱',
    months: [3, 4, 5], // March-May
    color: '#10b981',
    bgTint: 'rgba(16,185,129,0.04)',
    xpMultiplier: 1.15,
    flavor: 'The ice retreats. The first runs of the season. Every log entry feels like emerging from hibernation.',
    description: 'First trips of the season. Equipment unbagged, routes planned, hulls scraped. The ocean is waking up and so are we.',
    bonusAchievements: [
      {
        id: 'spring_first_launch',
        name: 'First Splash',
        desc: 'Log the first trip of spring season',
        icon: '🚢',
        xp: 100,
        rarity: 'rare',
        check: (s) => s.seasonTrips >= 1
      },
      {
        id: 'spring_prep',
        name: 'Winter Readiness',
        desc: 'Complete 5 maintenance tasks during spring prep',
        icon: '🔧',
        xp: 75,
        rarity: 'uncommon',
        check: (s) => s.seasonMaint >= 5
      },
      {
        id: 'spring_25_logs',
        name: 'Spring Awakening',
        desc: 'Log 25 entries during spring season',
        icon: '🌸',
        xp: 150,
        rarity: 'rare',
        check: (s) => s.seasonLogs >= 25
      },
      {
        id: 'spring_first_catch',
        name: 'Ice Breaker',
        desc: 'Log the first catch of the season',
        icon: '🐟',
        xp: 100,
        rarity: 'epic',
        check: (s) => s.seasonCatches >= 1
      },
    ]
  },

  summer: {
    id: 'summer',
    name: 'Solstice Haul',
    icon: '☀️',
    months: [6, 7, 8],
    color: '#f59e0b',
    bgTint: 'rgba(245,158,11,0.04)',
    xpMultiplier: 1.25,
    flavor: 'Peak fishing. Twenty hours of daylight. The boat doesn\'t sleep and neither do we.',
    description: 'The money months. Every haul matters. Records are set and broken. This is what you trained all winter for.',
    bonusAchievements: [
      {
        id: 'summer_streak_7',
        name: 'Sun Never Sets',
        desc: '7-day streak during summer season',
        icon: '🔆',
        xp: 200,
        rarity: 'rare',
        check: (s) => s.summerStreak >= 7
      },
      {
        id: 'summer_100_logs',
        name: 'Sunlight Hoarder',
        desc: 'Log 100 entries during summer',
        icon: '📰',
        xp: 300,
        rarity: 'epic',
        check: (s) => s.seasonLogs >= 100
      },
      {
        id: 'summer_big_haul',
        name: 'Personal Best',
        desc: 'Log a single catch over 500 lbs',
        icon: '💪',
        xp: 250,
        rarity: 'epic',
        check: (s) => s.biggestCatch >= 500
      },
      {
        id: 'summer_1000_miles',
        name: 'Endless Horizon',
        desc: 'Travel 1,000 nm during summer',
        icon: '🌊',
        xp: 500,
        rarity: 'legendary',
        check: (s) => s.seasonDistance >= 1000
      },
    ]
  },

  fall: {
    id: 'fall',
    name: 'Greybeard Season',
    icon: '🍂',
    months: [9, 10, 11],
    color: '#dc2626',
    bgTint: 'rgba(220,38,38,0.04)',
    xpMultiplier: 1.10,
    flavor: 'The weather turns. The experienced hands earn their keep. Every decision carries more weight.',
    description: 'Storms build character. The greybeards say you learn more in one fall season than three summers. Prove them right.',
    bonusAchievements: [
      {
        id: 'fall_storm_logged',
        name: 'Storm Witness',
        desc: 'Log during a storm (weather: storm/gale)',
        icon: '⛈️',
        xp: 150,
        rarity: 'epic',
        check: (s) => s.stormEntries >= 1
      },
      {
        id: 'fall_50_logs',
        name: 'Greybeard',
        desc: 'Log 50 entries during fall season',
        icon: '🧔',
        xp: 200,
        rarity: 'rare',
        check: (s) => s.seasonLogs >= 50
      },
      {
        id: 'fall_night_owl',
        name: 'Dark Watch',
        desc: 'Log 15 night entries during fall',
        icon: '🌑',
        xp: 150,
        rarity: 'rare',
        check: (s) => s.seasonNight >= 15
      },
      {
        id: 'fall_maint_master',
        name: 'Winterization',
        desc: 'Complete 10 maintenance tasks in fall',
        icon: '🛠️',
        xp: 200,
        rarity: 'epic',
        check: (s) => s.seasonMaint >= 10
      },
    ]
  },

  winter: {
    id: 'winter',
    name: 'Ice Anchor',
    icon: '❄️',
    months: [12, 1, 2],
    color: '#0ea5e9',
    bgTint: 'rgba(14,165,233,0.04)',
    xpMultiplier: 1.30, // Higher multiplier to reward offseason engagement
    flavor: 'The boat is hauled out or riding quietly at her mooring. This is when you fix everything. This is when you plan.',
    description: 'Offseason is not off — it\'s preparation. Haul-outs, refits, training, planning. The captains who log in winter are the ones who succeed in summer.',
    bonusAchievements: [
      {
        id: 'winter_projects',
        name: 'Boatyard Scholar',
        desc: 'Complete 15 maintenance tasks during winter',
        icon: '📚',
        xp: 300,
        rarity: 'epic',
        check: (s) => s.seasonMaint >= 15
      },
      {
        id: 'winter_plan_3',
        name: 'Strategist',
        desc: 'Plan 3 trips during winter (next season prep)',
        icon: '🗺️',
        xp: 150,
        rarity: 'rare',
        check: (s) => s.seasonTrips >= 3
      },
      {
        id: 'winter_30_logs',
        name: 'Year-Round Mariner',
        desc: 'Log 30 entries during winter',
        icon: '🗓️',
        xp: 250,
        rarity: 'epic',
        check: (s) => s.seasonLogs >= 30
      },
      {
        id: 'winter_checklist',
        name: 'Ready for Sea',
        desc: 'Complete 5 full safety checklists during winter prep',
        icon: '✅',
        xp: 200,
        rarity: 'rare',
        check: (s) => s.winterChecklists >= 5
      },
    ]
  },
};

// ── Helper Functions ─────────────────────────────────

/**
 * Get the current season based on month
 */
function getCurrentSeason(date = new Date()) {
  const month = date.getMonth() + 1; // 1-12
  for (const [key, season] of Object.entries(SEASONS)) {
    if (season.months.includes(month)) {
      return { key, ...season };
    }
  }
  return { key: 'summer', ...SEASONS.summer }; // fallback
}

/**
 * Get the XP multiplier for the current season
 */
function getCurrentXpMultiplier(date = new Date()) {
  return getCurrentSeason(date).xpMultiplier;
}

/**
 * Apply seasonal XP multiplier to base XP
 */
function applySeasonalMultiplier(baseXp, date = new Date()) {
  return Math.round(baseXp * getCurrentXpMultiplier(date));
}

/**
 * Get seasonal achievements for current season
 */
function getSeasonalAchievements(date = new Date()) {
  return getCurrentSeason(date).bonusAchievements;
}

/**
 * Check if a date falls within a specific season
 */
function isDateInSeason(dateStr, seasonKey) {
  const month = parseInt(dateStr.substring(5, 7));
  return SEASONS[seasonKey].months.includes(month);
}

/**
 * Calculate seasonal stats from raw log data
 */
function calculateSeasonalStats(entries, maintenanceHistory, trips, date = new Date()) {
  const season = getCurrentSeason(date);
  const seasonMonths = season.months;
  const year = date.getFullYear();
  
  // Filter entries to current season
  const seasonEntries = entries.filter(e => {
    if (!e.timestamp) return false;
    const d = new Date(e.timestamp);
    return seasonMonths.includes(d.getMonth() + 1) && 
           d.getFullYear() === (season.months.includes(12) && d.getMonth() === 11 ? year : year);
  });

  const seasonLogs = seasonEntries.length;
  const seasonCatches = seasonEntries.filter(e => 
    e.category === 'catch' || (e.text && /catch|caught|salmon|halibut|tuna|cod|sockeye/i.test(e.text))
  ).length;
  const seasonNight = seasonEntries.filter(e => e.watch === 'night').length;
  const seasonMaint = maintenanceHistory.filter(h => {
    if (!h.ts) return false;
    const d = new Date(h.ts);
    return seasonMonths.includes(d.getMonth() + 1);
  }).length;
  const seasonTrips = trips.filter(t => {
    if (!t.date) return false;
    return seasonMonths.includes(parseInt(t.date.split('-')[1]));
  }).length;
  const stormEntries = seasonEntries.filter(e => 
    e.text && /storm|gale|squall|rough|beaufort/i.test(e.text)
  ).length;

  return {
    seasonName: season.name,
    seasonIcon: season.icon,
    seasonColor: season.color,
    seasonLogs,
    seasonCatches,
    seasonNight,
    seasonMaint,
    seasonTrips,
    stormEntries,
    xpMultiplier: season.xpMultiplier,
  };
}

// ── Export for module use ────────────────────────────
if (typeof module !== 'undefined') {
  module.exports = {
    SEASONS,
    getCurrentSeason,
    getCurrentXpMultiplier,
    applySeasonalMultiplier,
    getSeasonalAchievements,
    isDateInSeason,
    calculateSeasonalStats,
  };
}
