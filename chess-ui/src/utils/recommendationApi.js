import { Chess } from "chess.js";
import { createRequestId, logger } from "./logger";

const API_BASE = import.meta.env.VITE_COACH_AI_URL || "/api";
const MAX_RECOMMENDATION_CACHE_ENTRIES = 256;
const recommendationCache = new Map();
const inFlightRecommendations = new Map();

export function getSideToMove(fen) {
  return fen?.includes(" w ") ? "white" : "black";
}

export function getPositionCacheKey(fen) {
  return String(fen || "").trim().split(/\s+/).slice(0, 4).join(" ");
}

export function getRatingBucket(rating) {
  if (rating === null || rating === undefined || rating === "") return "unknown";
  if (!Number.isFinite(Number(rating))) return "unknown";
  const value = Number(rating);
  if (value < 1200) return "0-1199";
  if (value < 1400) return "1200-1399";
  if (value < 1600) return "1400-1599";
  if (value < 1800) return "1600-1799";
  if (value < 2000) return "1800-1999";
  if (value < 2200) return "2000-2199";
  return "2200+";
}

export function getRecommendationCacheKey({
  fen,
  userId,
  rating,
  color,
  maxCandidates = 6,
  useMasterGames = false,
}) {
  return JSON.stringify({
    position: getPositionCacheKey(fen),
    userId: String(userId || "").toLowerCase(),
    ratingBucket: getRatingBucket(rating),
    color,
    maxCandidates,
    statisticsSource: useMasterGames ? "masters" : "peer",
  });
}

export function getCachedRecommendation(params) {
  const key = getRecommendationCacheKey(params);
  const cached = recommendationCache.get(key);
  if (!cached) return null;

  recommendationCache.delete(key);
  recommendationCache.set(key, cached);
  return cached;
}

export function setCachedRecommendation(params, recommendation) {
  const key = getRecommendationCacheKey(params);
  recommendationCache.delete(key);
  recommendationCache.set(key, recommendation);

  while (recommendationCache.size > MAX_RECOMMENDATION_CACHE_ENTRIES) {
    recommendationCache.delete(recommendationCache.keys().next().value);
  }
}

function waitForSharedRequest(request, signal) {
  if (!signal) return request;
  if (signal.aborted) {
    return Promise.reject(new DOMException("The operation was aborted.", "AbortError"));
  }

  return new Promise((resolve, reject) => {
    const abort = () => reject(new DOMException("The operation was aborted.", "AbortError"));
    signal.addEventListener("abort", abort, { once: true });
    request.then(resolve, reject).finally(() => signal.removeEventListener("abort", abort));
  });
}

export async function fetchRecommendation({
  fen,
  userId,
  rating,
  color = getSideToMove(fen),
  maxCandidates = 6,
  useMasterGames = false,
  signal,
}) {
  if (!fen || !userId) {
    throw new Error("Missing FEN or user id for recommendation request.");
  }

  const params = { fen, userId, rating, color, maxCandidates, useMasterGames };
  const cached = getCachedRecommendation(params);
  if (cached) {
    logger.debug("Recommendation cache hit", { userId, rating, color });
    return cached;
  }

  const cacheKey = getRecommendationCacheKey(params);
  const existingRequest = inFlightRecommendations.get(cacheKey);
  if (existingRequest) {
    logger.debug("Recommendation request joined in-flight work", { userId, color });
    return waitForSharedRequest(existingRequest, signal);
  }

  const requestId = createRequestId();
  logger.debug("Recommendation request started", {
    requestId,
    userId,
    rating,
    color,
    maxCandidates,
    useMasterGames,
  });
  const request = (async () => {
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
          use_master_games: useMasterGames,
        }),
      });
    } catch (error) {
      logger.error("Recommendation network request failed", { requestId, error });
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
  })();

  inFlightRecommendations.set(cacheKey, request);
  const clearInFlight = () => {
    if (inFlightRecommendations.get(cacheKey) === request) {
      inFlightRecommendations.delete(cacheKey);
    }
  };
  request.then(clearInFlight, clearInFlight);

  return waitForSharedRequest(request, signal);
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
