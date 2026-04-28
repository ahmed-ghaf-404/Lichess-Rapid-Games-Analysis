import { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:8001";

export function useRecommendation({ fen, userId, rating, color, enabled = true }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!enabled || !fen || !userId) return;

    let cancelled = false;

    async function run() {
      try {
        setLoading(true);
        setError("");

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
            max_candidates: 6,
          }),
        });

        if (!res.ok) {
          throw new Error(`Recommendation request failed: ${res.status}`);
        }

        const json = await res.json();
        if (!cancelled) {
          setData(json);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || "Failed to load recommendation.");
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
  }, [fen, userId, rating, color, enabled]);

  return { data, loading, error };
}