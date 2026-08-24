import { afterEach, describe, expect, it, vi } from "vitest";

import {
  fetchRecommendation,
  getRecommendationCacheKey,
} from "./recommendationApi";


const START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const START_FEN_LATER = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 18 42";


afterEach(() => {
  vi.unstubAllGlobals();
});


describe("recommendation request cache", () => {
  it("keeps an unknown rating aligned with the backend bucket", () => {
    const key = getRecommendationCacheKey({
      fen: START_FEN,
      userId: "chocoroku",
      rating: null,
      color: "white",
    });

    expect(key).toContain('"ratingBucket":"unknown"');
  });

  it("reuses a key across move clocks and ratings in the same bucket", () => {
    const first = getRecommendationCacheKey({
      fen: START_FEN,
      userId: "ChocoRoku",
      rating: 1601,
      color: "white",
      maxCandidates: 6,
    });
    const equivalent = getRecommendationCacheKey({
      fen: START_FEN_LATER,
      userId: "chocoroku",
      rating: 1799,
      color: "white",
      maxCandidates: 6,
    });

    expect(equivalent).toBe(first);
  });

  it("joins concurrent requests for the same position", async () => {
    let resolveFetch;
    const responsePromise = new Promise((resolve) => {
      resolveFetch = resolve;
    });
    const fetchMock = vi.fn(() => responsePromise);
    vi.stubGlobal("fetch", fetchMock);

    const params = {
      fen: START_FEN,
      userId: "request-dedupe-test",
      rating: 1682,
      color: "white",
      maxCandidates: 6,
    };
    const first = fetchRecommendation(params);
    const second = fetchRecommendation({ ...params, fen: START_FEN_LATER });

    expect(fetchMock).toHaveBeenCalledTimes(1);

    resolveFetch({
      ok: true,
      status: 200,
      statusText: "OK",
      headers: { get: () => null },
      json: async () => ({ candidates: [], metadata: { cache: "miss" } }),
    });

    const [firstResult, secondResult] = await Promise.all([first, second]);
    expect(firstResult).toBe(secondResult);
  });
});
