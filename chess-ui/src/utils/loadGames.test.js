import { afterEach, describe, expect, it, vi } from "vitest";

import { loadGames } from "./loadGames";


describe("loadGames", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("encodes the username and returns games", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [{ id: "game-1", moves: "e4 e5" }],
    });
    vi.stubGlobal("fetch", fetchMock);

    await expect(loadGames("player name")).resolves.toHaveLength(1);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("player%20name")
    );
  });

  it("joins concurrent loads for the same account", async () => {
    let resolveFetch;
    const fetchMock = vi.fn(() => new Promise((resolve) => {
      resolveFetch = resolve;
    }));
    vi.stubGlobal("fetch", fetchMock);

    const first = loadGames("two-account-cache-test");
    const second = loadGames("TWO-ACCOUNT-CACHE-TEST");
    expect(fetchMock).toHaveBeenCalledTimes(1);

    resolveFetch({
      ok: true,
      json: async () => [{ id: "game-2", moves: "d4 d5" }],
    });

    const [firstResult, secondResult] = await Promise.all([first, second]);
    expect(firstResult).toBe(secondResult);
  });

  it("falls back cleanly when a player has no imported games", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      json: async () => ({ detail: "No imported rapid games were found." }),
    }));

    await expect(loadGames("missing-user")).resolves.toEqual([]);
  });

  it("accepts an empty successful response for the masters fallback", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [],
    }));

    await expect(loadGames("missing-user")).resolves.toEqual([]);
  });
});
