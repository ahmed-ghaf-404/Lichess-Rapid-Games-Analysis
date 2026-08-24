import { describe, expect, it } from "vitest";

import {
  analyzeRepertoireDivergence,
  buildRepertoireTree,
  getPositionKey,
  suggestRepertoireLineName,
} from "./repertoire";


describe("repertoire utilities", () => {
  it("normalizes position keys without move clocks", () => {
    expect(getPositionKey("8/8/8/8/8/8/8/K6k w - - 12 34")).toBe(
      "8/8/8/8/8/8/8/K6k w - -"
    );
  });

  it("nests prerequisite repertoire lines", () => {
    const tree = buildRepertoireTree([
      { id: "italian", parent_line_id: null, name: "My Italian Lines" },
      { id: "traxler", parent_line_id: "italian", name: "My Traxler Lines" },
    ]);

    expect(tree[0].children[0].name).toBe("My Traxler Lines");
  });

  it("suggests familiar opening-family names", () => {
    expect(suggestRepertoireLineName("Sicilian Defense: Najdorf Variation")).toBe(
      "My Sicilian Lines"
    );
    expect(suggestRepertoireLineName("London System")).toBe("My London Lines");
  });

  it("finds the player's first divergence from an approved move", () => {
    const startKey = getPositionKey(
      "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    );
    const result = analyzeRepertoireDivergence(
      [{
        id: "game-1",
        moves: "d4 d5",
        opening: { name: "Queen's Pawn Game" },
        players: { white: { user: { id: "chocoroku" } }, black: { user: { id: "other" } } },
      }],
      [{
        name: "My King Pawn Lines",
        moves: [{ position_key: startKey, move_uci: "e2e4", move_san: "e4" }],
      }],
      "chocoroku"
    );

    expect(result.divergenceCount).toBe(1);
    expect(result.divergences[0].playedSan).toBe("d4");
  });
});
