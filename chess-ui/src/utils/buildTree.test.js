import { describe, expect, it } from "vitest";

import { buildTree } from "./buildTree";
import {
  getChildren,
  getLineToNode,
  getMainlineChild,
  getParent,
} from "./treeSelectors";


describe("opening tree", () => {
  const tree = buildTree([
    { moves: "e4 e5 Nf3" },
    { moves: "e4 c5 Nf3" },
    { moves: "e4 e5 Nc3" },
  ]);

  it("merges shared moves and counts visits", () => {
    const [e4] = getChildren(tree, tree.rootId);
    const [e5, c5] = getChildren(tree, e4.id);

    expect(e4.san).toBe("e4");
    expect(e4.visitCount).toBe(3);
    expect(e5.san).toBe("e5");
    expect(e5.visitCount).toBe(2);
    expect(c5.san).toBe("c5");
    expect(c5.visitCount).toBe(1);
  });

  it("selects the most visited continuation as the main line", () => {
    const e4 = getMainlineChild(tree, tree.rootId);
    expect(getMainlineChild(tree, e4.id).san).toBe("e5");
  });

  it("returns parent and line navigation data", () => {
    const e4 = getMainlineChild(tree, tree.rootId);
    const e5 = getMainlineChild(tree, e4.id);
    const nf3 = getMainlineChild(tree, e5.id);

    expect(getParent(tree, nf3.id).id).toBe(e5.id);
    expect(getLineToNode(tree, nf3.id).map((node) => node.san)).toEqual([
      "e4",
      "e5",
      "Nf3",
    ]);
  });
});
