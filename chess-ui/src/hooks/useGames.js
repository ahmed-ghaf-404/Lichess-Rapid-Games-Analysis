import { useEffect, useState } from "react";
import { loadGames } from "../utils/loadGames";
import { logger } from "../utils/logger";

export function useGames(username) {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!username) return;

    let cancelled = false;

    async function run() {
      try {
        setLoading(true);
        setError("");
        setGames([]);

        const data = await loadGames(username);

        if (!cancelled) {
          setGames(Array.isArray(data) ? data : []);
        }
      } catch (err) {
        logger.error("Loading player games failed", { username, error: err.message });
        if (!cancelled) {
          setError(err.message || "Failed to load games.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    run();

    return () => {
      cancelled = true;
    };
  }, [username]);

  return { games, loading, error };
}
