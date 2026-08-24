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

  it("surfaces a useful not-found response", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      json: async () => ({ detail: "No imported rapid games were found." }),
    }));

    await expect(loadGames("missing-user")).rejects.toThrow(
      "No imported rapid games were found."
    );
  });

  it("rejects an empty successful response", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [],
    }));

    await expect(loadGames("missing-user")).rejects.toThrow(/no imported rapid games/i);
  });
});
