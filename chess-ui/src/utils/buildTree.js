import { Chess } from "chess.js";
import { createNode } from "./createNode";

export function buildTree(games) {
  const rootChess = new Chess();
  const rootId = "root";

  const nodesById = {
    [rootId]: createNode({
      id: rootId,
      fen: rootChess.fen(),
      moveNumber: 0,
      parentId: null,
    }),
  };

  let nextId = 1;

  for (const game of games) {
    if (!game?.moves) continue;

    const chess = new Chess();
    let currentNodeId = rootId;
    const moves = game.moves.split(/\s+/).filter(Boolean);

    for (const san of moves) {
      const move = chess.move(san);

      if (!move) {
        console.warn("Invalid move:", san, "in game:", game);
        break;
      }

      const fen = chess.fen();
      const currentNode = nodesById[currentNodeId];

      let existingChildId = currentNode.childIds.find((childId) => {
        const child = nodesById[childId];
        return child.san === san;
      });

      if (!existingChildId) {
        const nodeId = `node-${nextId++}`;

        nodesById[nodeId] = createNode({
          id: nodeId,
          san,
          fen,
          moveNumber: currentNode.moveNumber + 1,
          parentId: currentNodeId,
        });

        currentNode.childIds.push(nodeId);
        existingChildId = nodeId;
      }

      nodesById[existingChildId].visitCount += 1;
      currentNodeId = existingChildId;
    }
  }

  return {
    rootId,
    nodesById,
  };
}