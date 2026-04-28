export function getNode(tree, nodeId) {
  return tree?.nodesById?.[nodeId] ?? null;
}

export function getChildren(tree, nodeId) {
  const node = getNode(tree, nodeId);
  if (!node) return [];

  return node.childIds
    .map((childId) => tree.nodesById[childId])
    .filter(Boolean)
    .sort((a, b) => b.visitCount - a.visitCount);
}

export function getParent(tree, nodeId) {
  const node = getNode(tree, nodeId);
  if (!node?.parentId) return null;
  return getNode(tree, node.parentId);
}

export function getMainlineChild(tree, nodeId) {
  const children = getChildren(tree, nodeId);
  return children[0] ?? null;
}

export function getLineToNode(tree, nodeId) {
  const line = [];
  let current = getNode(tree, nodeId);

  while (current && current.parentId) {
    line.unshift(current);
    current = getNode(tree, current.parentId);
  }

  return line;
}