export const RECOMMENDATION_ARROW_COLOR = "rgba(217, 181, 95, 0.9)";
export const REPERTOIRE_ARROW_COLOR = "rgba(34, 197, 94, 0.9)";


export function buildMoveArrows(candidates = [], color = RECOMMENDATION_ARROW_COLOR) {
  return candidates
    .slice(0, 3)
    .filter((candidate) => candidate?.move_uci?.length >= 4)
    .map((candidate) => ({
      startSquare: candidate.move_uci.slice(0, 2),
      endSquare: candidate.move_uci.slice(2, 4),
      color,
    }));
}


export function buildRecommendationArrows(candidates = []) {
  return buildMoveArrows(candidates, RECOMMENDATION_ARROW_COLOR);
}
