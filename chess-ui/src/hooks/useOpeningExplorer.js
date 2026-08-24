import { useMemo, useState } from "react";
import { buildTree } from "../utils/buildTree";
import {
  getChildren,
  getMainlineChild,
  getNode,
  getParent,
  getLineToNode,
} from "../utils/treeSelectors";

export function useOpeningExplorer(games) {
  const tree = useMemo(() => buildTree(games), [games]);

  const [explorerState, setExplorerState] = useState({
    tree,
    currentNodeId: tree.rootId,
  });

  const currentNodeId =
    explorerState.tree === tree
      ? explorerState.currentNodeId
      : tree.rootId;

  const currentNode = useMemo(
    () => getNode(tree, currentNodeId),
    [tree, currentNodeId]
  );

  const children = useMemo(
    () => getChildren(tree, currentNodeId),
    [tree, currentNodeId]
  );

  const parent = useMemo(
    () => getParent(tree, currentNodeId),
    [tree, currentNodeId]
  );

  const next = useMemo(
    () => getMainlineChild(tree, currentNodeId),
    [tree, currentNodeId]
  );

  const line = useMemo(
    () => getLineToNode(tree, currentNodeId),
    [tree, currentNodeId]
  );

  const boardFen = currentNode?.fen ?? "start";

  function goToNode(nodeId) {
    if (!nodeId) return;

    setExplorerState({
      tree,
      currentNodeId: nodeId,
    });
  }

  function goToParent() {
    if (!parent) return;

    setExplorerState({
      tree,
      currentNodeId: parent.id,
    });
  }

  function goToNext() {
    if (!next) return;

    setExplorerState({
      tree,
      currentNodeId: next.id,
    });
  }

  function goToStart() {
    setExplorerState({
      tree,
      currentNodeId: tree.rootId,
    });
  }

  return {
    tree,
    currentNode,
    currentNodeId,
    boardFen,
    children,
    parent,
    next,
    line,
    goToNode,
    goToParent,
    goToNext,
    goToStart,
  };
}
