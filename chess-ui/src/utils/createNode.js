export function createNode({
  id,
  san = null,
  fen,
  moveNumber = 0,
  parentId = null,
}) {
  return {
    id,
    san,
    fen,
    moveNumber,
    parentId,
    childIds: [],
    visitCount: 0,
  };
}