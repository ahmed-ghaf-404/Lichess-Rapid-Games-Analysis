import { describe, expect, it } from "vitest";

import {
  DEFAULT_LICHESS_USERNAME,
  getPlayerRating,
  normalizeLichessUsername,
  validateLichessUsername,
} from "./lichessUser";


describe("Lichess username helpers", () => {
  it("uses ericrosen as the portfolio-friendly default", () => {
    expect(DEFAULT_LICHESS_USERNAME).toBe("ericrosen");
  });

  it("normalizes usernames before requesting games", () => {
    expect(normalizeLichessUsername("  EricRosen  ")).toBe("ericrosen");
  });

  it("rejects empty, short, and unsafe usernames", () => {
    expect(validateLichessUsername(" ")).toMatch(/enter/i);
    expect(validateLichessUsername("a")).toMatch(/2–30/);
    expect(validateLichessUsername("name<script>")).toMatch(/2–30/);
  });

  it("accepts Lichess-compatible usernames", () => {
    expect(validateLichessUsername("DrNykterstein")).toBe("");
    expect(validateLichessUsername("player_name-2")).toBe("");
  });

  it("takes the selected player's newest known rating", () => {
    const games = [
      {
        createdAt: 10,
        players: {
          white: { user: { id: "ericrosen" }, rating: 2500 },
          black: { user: { id: "opponent" }, rating: 2480 },
        },
      },
      {
        createdAt: 20,
        players: {
          white: { user: { id: "opponent" }, rating: 2510 },
          black: { user: { id: "EricRosen" }, rating: 2538 },
        },
      },
    ];

    expect(getPlayerRating(games, "ERICROSEN")).toBe(2538);
    expect(getPlayerRating(games, "missing", 1600)).toBe(1600);
  });
});
