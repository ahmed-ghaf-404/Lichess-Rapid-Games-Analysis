export const DEFAULT_LICHESS_USERNAME = "ericrosen";

const LICHESS_USERNAME_PATTERN = /^[a-zA-Z0-9_-]{2,30}$/;

export function normalizeLichessUsername(username) {
  return username.trim().toLowerCase();
}

export function validateLichessUsername(username) {
  const normalized = normalizeLichessUsername(username);

  if (!normalized) {
    return "Enter a Lichess username.";
  }

  if (!LICHESS_USERNAME_PATTERN.test(normalized)) {
    return "Use 2–30 letters, numbers, underscores, or hyphens.";
  }

  return "";
}

export function getPlayerRating(games, username, fallback = 1500) {
  const normalizedUsername = normalizeLichessUsername(username);
  const newestGames = [...games].sort(
    (left, right) => Number(right.createdAt ?? 0) - Number(left.createdAt ?? 0)
  );

  for (const game of newestGames) {
    for (const color of ["white", "black"]) {
      const player = game?.players?.[color];
      const playerId = player?.user?.id?.toLowerCase();

      if (playerId === normalizedUsername && Number.isFinite(player.rating)) {
        return player.rating;
      }
    }
  }

  return fallback;
}
