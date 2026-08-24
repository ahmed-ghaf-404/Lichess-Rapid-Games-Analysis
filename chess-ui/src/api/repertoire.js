import { createRequestId, logger } from "../utils/logger";


const COACH_API_BASE = import.meta.env.VITE_COACH_AI_URL || "/api";
const REPERTOIRE_CACHE_TTL_MS = 30 * 1000;
const REPERTOIRE_CACHE_LIMIT = 2;
const repertoireCache = new Map();
const inFlightRepertoires = new Map();


function normalizeUserId(userId) {
  return String(userId || "").trim().toLowerCase();
}


function invalidateRepertoire(userId) {
  repertoireCache.delete(normalizeUserId(userId));
}


async function repertoireRequest(path, { method = "GET", body, writeKey } = {}) {
  const requestId = createRequestId();
  let response;

  try {
    response = await fetch(`${COACH_API_BASE}${path}`, {
      method,
      headers: {
        "Content-Type": "application/json",
        "X-Request-ID": requestId,
        ...(writeKey ? { "X-Repertoire-Key": writeKey } : {}),
      },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });
  } catch (error) {
    logger.error("Repertoire API network request failed", { requestId, error });
    throw new Error("The repertoire service is unavailable.");
  }

  if (response.status === 204) return null;
  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    logger.warn("Repertoire API request rejected", {
      requestId: response.headers.get("X-Request-ID") || requestId,
      status: response.status,
    });
    throw new Error(payload.detail || "The repertoire request failed.");
  }

  return payload;
}


export function fetchRepertoire(userId) {
  const cacheKey = normalizeUserId(userId);
  const cached = repertoireCache.get(cacheKey);
  if (cached && Date.now() - cached.storedAt < REPERTOIRE_CACHE_TTL_MS) {
    repertoireCache.delete(cacheKey);
    repertoireCache.set(cacheKey, cached);
    return Promise.resolve(cached.lines);
  }

  const existingRequest = inFlightRepertoires.get(cacheKey);
  if (existingRequest) return existingRequest;

  const request = repertoireRequest(
    `/repertoire/${encodeURIComponent(userId)}`
  ).then((lines) => {
    repertoireCache.delete(cacheKey);
    repertoireCache.set(cacheKey, { lines, storedAt: Date.now() });
    while (repertoireCache.size > REPERTOIRE_CACHE_LIMIT) {
      repertoireCache.delete(repertoireCache.keys().next().value);
    }
    return lines;
  });

  inFlightRepertoires.set(cacheKey, request);
  const clearInFlight = () => {
    if (inFlightRepertoires.get(cacheKey) === request) {
      inFlightRepertoires.delete(cacheKey);
    }
  };
  request.then(clearInFlight, clearInFlight);
  return request;
}

export async function createRepertoireLine(payload, writeKey) {
  const result = await repertoireRequest("/repertoire/lines", {
    method: "POST",
    body: payload,
    writeKey,
  });
  invalidateRepertoire(payload.user_id);
  return result;
}

export async function approveRepertoireMove(lineId, payload, writeKey) {
  const result = await repertoireRequest(`/repertoire/lines/${encodeURIComponent(lineId)}/moves`, {
    method: "POST",
    body: payload,
    writeKey,
  });
  invalidateRepertoire(payload.user_id);
  return result;
}

export async function removeRepertoireMove(lineId, moveId, userId, writeKey) {
  const result = await repertoireRequest(
    `/repertoire/lines/${encodeURIComponent(lineId)}/moves/${encodeURIComponent(moveId)}?user_id=${encodeURIComponent(userId)}`,
    { method: "DELETE", writeKey }
  );
  invalidateRepertoire(userId);
  return result;
}

export async function removeRepertoireLine(lineId, userId, writeKey) {
  const result = await repertoireRequest(
    `/repertoire/lines/${encodeURIComponent(lineId)}?user_id=${encodeURIComponent(userId)}`,
    { method: "DELETE", writeKey }
  );
  invalidateRepertoire(userId);
  return result;
}
