export function uciToArrow(moveUci, color) {
  if (!moveUci || moveUci.length < 4) return null;

  const from = moveUci.slice(0, 2);
  const to = moveUci.slice(2, 4);

  return [from, to, color];
}

export function buildRecommendationArrows(candidates = []) {
  const colors = [
    "rgba(34,197,94,0.9)",   // green - top move
    "rgba(59,130,246,0.8)",  // blue
    "rgba(245,158,11,0.8)",  // amber
  ];

  return candidates
    .slice(0, 3)
    .map((candidate, index) => uciToArrow(candidate.move_uci, colors[index]))
    .filter(Boolean);
}