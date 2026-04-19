// Shared level palette + helpers used by multiple components.

export const LEVELS = [
  { key: "Highly Atypical", short: "Hi. Atypical", tw: "level-highly-atypical", rank: 0 },
  { key: "Atypical", short: "Atypical", tw: "level-atypical", rank: 1 },
  { key: "Mixed", short: "Mixed", tw: "level-mixed", rank: 2 },
  { key: "Standard", short: "Standard", tw: "level-standard", rank: 3 },
  { key: "Highly Standard", short: "Hi. Standard", tw: "level-highly-standard", rank: 4 },
];

export const LEVEL_BY_KEY = Object.fromEntries(LEVELS.map((l) => [l.key, l]));

export function levelColor(levelKey) {
  return LEVEL_BY_KEY[levelKey]?.tw ?? "ink-500";
}

// For a tiny ordinal bar (e.g. the sidebar level pills): a 5-cell track
// with the ranked cells highlighted. Mirrors the Law Insider "spectrum".
export function levelCells(levelKey) {
  const rank = LEVEL_BY_KEY[levelKey]?.rank ?? 0;
  return [0, 1, 2, 3, 4].map((i) => i <= rank);
}
