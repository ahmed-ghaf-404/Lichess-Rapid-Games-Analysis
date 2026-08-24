const BASE_URL = import.meta.env.VITE_GAMES_API_URL || "/games";

export async function loadGames(username) {
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
      throw new Error(
        detail || `No imported rapid games were found for @${username}.`
      );
    }

    if (res.status === 422) {
      throw new Error(detail || "That is not a valid Lichess username.");
    }

    throw new Error(detail || "The games service is unavailable. Please try again.");
  }

  const games = await res.json();

  if (!Array.isArray(games) || games.length === 0) {
    throw new Error(`No imported rapid games were found for @${username}.`);
  }

  return games;
}
