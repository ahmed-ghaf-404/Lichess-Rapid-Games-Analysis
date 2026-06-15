const BASE_URL = import.meta.env.VITE_GAMES_API_URL || "http://127.0.0.1:8000";

export async function loadGames(username) {
  const res = await fetch(`${BASE_URL}/games/user/${username}`);

  if (!res.ok) {
    throw new Error(`Failed to load games for ${username}`);
  }

  return res.json();
}