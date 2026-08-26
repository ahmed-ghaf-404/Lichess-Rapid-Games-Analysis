const BASE_URL = import.meta.env.VITE_GAMES_API_URL || "/games";
const PLAYER_CACHE_LIMIT = 2;
const PLAYER_CACHE_TTL_MS = 5 * 60 * 1000;
const playerCache = new Map();
const inFlightPlayers = new Map();

export async function loadGames(username) {
  const cacheKey = String(username || "").trim().toLowerCase();
  const cached = playerCache.get(cacheKey);
  if (cached && Date.now() - cached.storedAt < PLAYER_CACHE_TTL_MS) {
    playerCache.delete(cacheKey);
    playerCache.set(cacheKey, cached);
    return cached.games;
  }

  const existingRequest = inFlightPlayers.get(cacheKey);
  if (existingRequest) return existingRequest;

  const request = (async () => {
    const res = await fetch(
      `${BASE_URL}/games/user/${encodeURIComponent(username)}`
    );

    if (!res.ok) {
      let detail = "";

      try {
        const body = await res.json();
        detail = typeof body?.detail === "string" ? body.detail : "";
      } catch {
        // Some proxies return an empty or non-JSON error response.
      }

      if (res.status === 404) {
        return [];
      }

      if (res.status === 422) {
        throw new Error(detail || "That is not a valid Lichess username.");
      }

      throw new Error(detail || "The games service is unavailable. Please try again.");
    }

    const games = await res.json();

    if (!Array.isArray(games)) {
      throw new Error("The games service returned an invalid response.");
    }

    playerCache.delete(cacheKey);
    playerCache.set(cacheKey, { games, storedAt: Date.now() });
    while (playerCache.size > PLAYER_CACHE_LIMIT) {
      playerCache.delete(playerCache.keys().next().value);
    }

    return games;
  })();

  inFlightPlayers.set(cacheKey, request);
  const clearInFlight = () => {
    if (inFlightPlayers.get(cacheKey) === request) {
      inFlightPlayers.delete(cacheKey);
    }
  };
  request.then(clearInFlight, clearInFlight);

  return request;
}
