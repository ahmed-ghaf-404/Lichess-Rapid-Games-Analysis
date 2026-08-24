import { Chess } from "chess.js";
import { createRequestId, logger } from "./logger";

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
  if (cached) {
    logger.debug("Recommendation cache hit", { userId, rating, color });
    return cached;
  }

  const requestId = createRequestId();
  logger.debug("Recommendation request started", {
    requestId,
    userId,
    rating,
    color,
    maxCandidates,
  });
  let res;
  try {
    res = await fetch(`${API_BASE}/recommend/position`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Request-ID": requestId,
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
  } catch (error) {
    if (error.name !== "AbortError") {
      logger.error("Recommendation network request failed", { requestId, error });
    }
    throw error;
  }

  if (!res.ok) {
    const errorText = await res.text();
    const level = res.status >= 500 ? "error" : "warn";
    logger[level]("Recommendation request rejected", {
      status: res.status,
      statusText: res.statusText,
      detail: errorText,
      requestId: res.headers.get("X-Request-ID") || requestId,
    });

      throw new Error(
        `Recommendation request failed: ${res.status} ${res.statusText} - ${errorText}`
      );
  }

  const json = await res.json();
  setCachedRecommendation(params, json);
  logger.info("Recommendation request completed", {
    status: res.status,
    requestId: res.headers.get("X-Request-ID") || requestId,
    candidateCount: json.candidates?.length ?? 0,
    cache: json.metadata?.cache,
  });
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
