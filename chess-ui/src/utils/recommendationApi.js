import { Chess } from "chess.js";

const API_BASE = import.meta.env.VITE_COACH_AI_URL || "/api";
const recommendationCache = new Map();

export function getSideToMove(fen) {
  return fen?.includes(" w ") ? "white" : "black";
}

export function getRecommendationCacheKey({ fen, userId, rating, color, maxCandidates = 6 }) {
  return JSON.stringify({ fen, userId, rating, color, maxCandidates });
}

export function getCachedRecommendation(params) {
  return recommendationCache.get(getRecommendationCacheKey(params)) ?? null;
}

export function setCachedRecommendation(params, recommendation) {
  recommendationCache.set(getRecommendationCacheKey(params), recommendation);
}

export async function fetchRecommendation({
  fen,
  userId,
  rating,
  color = getSideToMove(fen),
  maxCandidates = 6,
  signal,
}) {
  if (!fen || !userId) {
    throw new Error("Missing FEN or user id for recommendation request.");
  }

  const params = { fen, userId, rating, color, maxCandidates };
  const cached = getCachedRecommendation(params);
  if (cached) return cached;

  const res = await fetch(`${API_BASE}/recommend/position`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      fen,
      user_id: userId,
      rating,
      color,
      max_candidates: maxCandidates,
    }),
    signal,
  });

  if (!res.ok) {
      const errorText = await res.text();

      throw new Error(
        `Recommendation request failed: ${res.status} ${res.statusText} - ${errorText}`
      );
  }

  const json = await res.json();
  setCachedRecommendation(params, json);
  return json;
}

export function fenAfterUciMove(fen, moveUci) {
  if (!fen || !moveUci || moveUci.length < 4) return null;

  const game = new Chess(fen);
  const result = game.move({
    from: moveUci.slice(0, 2),
    to: moveUci.slice(2, 4),
    promotion: moveUci[4] || "q",
  });

  return result ? game.fen() : null;
}
