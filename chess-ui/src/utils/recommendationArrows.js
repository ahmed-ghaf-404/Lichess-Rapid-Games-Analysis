export function buildRecommendationArrows(candidates = []) {
  return candidates
    .slice(0, 3)
    .filter((candidate) => candidate?.move_uci?.length >= 4)
    .map((candidate) => ({
      startSquare: candidate.move_uci.slice(0, 2),
      endSquare: candidate.move_uci.slice(2, 4),
      color: "rgba(34, 197, 94, 0.85)",
    }));
}