/**
 * Vessel Quest — Lore Fragments
 * 
 * Maritime wisdom unlocked as you level up.
 * Each fragment is tied to a rank threshold.
 * These are the soul of the progression system.
 */

const LORE_FRAGMENTS = [
  {
    unlockRank: 1,
    title: 'The First Lesson',
    text: 'A boat is a hole in the water that you pour money into. You knew this before you started. You still went anyway. That\'s not stubbornness — that\'s calling.'
  },
  {
    unlockRank: 2,
    title: 'Reading the Water',
    text: 'Color changes mean temperature breaks. Temperature breaks mean fish. Birds working means bait below. Bait means everything. You can learn this from a book, but your eyes learn it faster.'
  },
  {
    unlockRank: 3,
    title: 'The Clock and the Tide',
    text: 'The tide waits for no one, and it doesn\'t check your schedule. Slack water is a twenty-minute window, not a suggestion. The ocean runs on geological time. You run on watch time. The gap between them is where experience lives.'
  },
  {
    unlockRank: 4,
    title: 'Why We Log',
    text: 'A logbook is not a diary. It is evidence. Evidence of where you were, what you saw, what you decided. When the same conditions come next season — and they will — the log tells you what worked. Memory lies. Ink doesn\'t.'
  },
  {
    unlockRank: 5,
    title: 'The Mate\'s Job',
    text: 'The captain decides where. The mate decides how. The deck decides when. If any one of these fails, the whole operation fails. A good mate is worth their weight in gold — literally, by the pound of fish they put on deck.'
  },
  {
    unlockRank: 6,
    title: 'Weather Wisdom',
    text: 'Red sky at morning: sailors take warning. This is not superstition — it\'s meteorology. A red sunrise means dust in the atmosphere to the east, which means high pressure has passed and a low is coming. Your log entries are the modern version of reading the sky.'
  },
  {
    unlockRank: 7,
    title: 'On Maintenance',
    text: 'There are two kinds of maintenance: the kind you do on schedule, and the kind you do at sea in a storm. The first costs time. The second costs fingers. Choose wisely.'
  },
  {
    unlockRank: 8,
    title: 'The Highliner',
    text: 'In every fleet, there is one boat that consistently outfishes the others. They don\'t have better gear or a bigger hold. They have better data. They know where the fish were last year, last week, at this tide, at this temperature. Their logbook is their secret weapon.'
  },
  {
    unlockRank: 9,
    title: 'The Old Salts',
    text: 'The old salts don\'t talk about the big catches. They talk about the ones that got away. Not because they\'re bitter — because the near-misses teach more than the successes. Every entry in your log that says "slow day, no catch" is worth as much as the one that says "full hold." Maybe more.'
  },
  {
    unlockRank: 10,
    title: 'Legend of the Sea',
    text: 'You have done what most people only romanticize. You have lived with the ocean, worked her waters, read her moods, and come back to tell about it. Your logbook is a chronicle of a life most people only dream about. The sea remembers everyone who sails her. Now she remembers you.'
  },
  // Extended lore for prestige ranks
  {
    unlockRank: 11,
    title: 'The Return',
    text: 'You\'ve come back to the basics — but with new eyes. The deckhand\'s work is the same work you did at level one. But now you see the connections: how the bait choice affects the catch, how the catch affects the market, how the market affects the next trip. The circle closes.'
  },
  {
    unlockRank: 12,
    title: 'The Ledger',
    text: 'A captain once told me: "I\'ve never met a rich fisherman who didn\'t keep good books." The logbook, the maintenance schedule, the fuel tracker — these aren\'t bureaucracy. They\'re the bones of a operation that survives the years.'
  },
  {
    unlockRank: 13,
    title: 'Teaching the Trade',
    text: 'The highest form of mastery is teaching. Your crew watches you. Your log entries teach them what to notice. Your maintenance schedule teaches them what to value. You are not just running a boat — you are training the next generation of mariners.'
  },
  {
    unlockRank: 14,
    title: 'The Storm That Taught Everything',
    text: 'Every experienced mariner has one storm that changed them. The one where they thought "this might be it." The one where they had to make decisions that mattered. That storm is in your logbook now. The entry from that day is the most important thing you\'ve ever written.'
  },
  {
    unlockRank: 15,
    title: 'What the Data Shows',
    text: 'You\'ve been logging long enough now that the patterns are visible. You can see the seasons in your entry counts. You can see the catches trending up or down. You can see the maintenance becoming routine or falling behind. The data doesn\'t lie — and neither does the ocean.'
  },
  {
    unlockRank: 16,
    title: 'The Boat Knows',
    text: 'You\'ve maintained this vessel so long that you hear changes in the engine note. You feel differences in the helm. You smell problems before they\'re visible. This is not mysticism — it\'s thousands of hours of data processed by the most sophisticated pattern-matching system ever built: the human brain.'
  },
  {
    unlockRank: 17,
    title: 'Leaving a Wake',
    text: 'Every log entry you write is a ripple. It affects your crew\'s bonuses, your buyer\'s planning, the harbor master\'s records, the next generation\'s understanding of what fishing was like in your era. You are writing primary source history.'
  },
  {
    unlockRank: 18,
    title: 'The Ocean\'s Ledger',
    text: 'The ocean keeps its own books. Every fish taken is recorded in the ecosystem. Every gallon burned is recorded in the atmosphere. Every log entry you make is your acknowledgment that you are part of this ledger — not separate from it.'
  },
  {
    unlockRank: 19,
    title: 'Commodore\'s Wisdom',
    text: 'A fleet is only as good as its weakest boat. A harbor is only as good as its least-prepared captain. Your consistent logging, your diligent maintenance, your careful planning — these raise the standard for everyone around you. You\'ve become infrastructure.'
  },
  {
    unlockRank: 20,
    title: 'The Legend Complete',
    text: 'There is nothing left to prove. Your logbook spans seasons. Your maintenance is flawless. Your crew is trained. Your catches are consistent. You have become what the old salts talk about when they talk about the good ones. The sea is in your bones. Welcome home.'
  },
];

// ── Helpers ────────────────────────────────────────────

/**
 * Get all lore fragments unlocked at or below a given rank
 */
function getUnlockedLore(rank) {
  return LORE_FRAGMENTS.filter(f => f.unlockRank <= rank);
}

/**
 * Get the lore fragment for a specific rank (for rank-up reveal)
 */
function getLoreForRank(rank) {
  return LORE_FRAGMENTS.find(f => f.unlockRank === rank);
}

/**
 * Get the most recently unlocked lore (for "new unlock" display)
 */
function getLatestLore(rank, previousRank) {
  return LORE_FRAGMENTS.filter(f => f.unlockRank > previousRank && f.unlockRank <= rank);
}

// ── Export ────────────────────────────────────────────
if (typeof module !== 'undefined') {
  module.exports = { LORE_FRAGMENTS, getUnlockedLore, getLoreForRank, getLatestLore };
}
