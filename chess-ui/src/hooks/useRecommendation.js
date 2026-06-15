import { useEffect, useState } from "react";
import {
  fetchRecommendation,
  getCachedRecommendation,
} from "../utils/recommendationApi";

const MAX_CANDIDATES = Number(import.meta.env.VITE_RECOMMENDATION_MAX_CANDIDATES ?? 6);

export function useRecommendation({ fen, userId, rating, color, enabled = true }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!enabled || !fen || !userId) return;

    const params = {
      fen,
      userId,
      rating,
      color,
      maxCandidates: MAX_CANDIDATES,
    };

    const cached = getCachedRecommendation(params);
    if (cached) {
      setData(cached);
      setLoading(false);
      setError("");
      return;
    }

    const controller = new AbortController();
    let cancelled = false;

    async function run() {
      try {
        setLoading(true);
        setError("");

        const json = await fetchRecommendation({
          ...params,
          signal: controller.signal,
        });

        if (!cancelled) {
          setData(json);
        }
      } catch (err) {
        if (!cancelled && err.name !== "AbortError") {
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
      controller.abort();
    };
  }, [fen, userId, rating, color, enabled]);

  return { data, loading, error };
}
