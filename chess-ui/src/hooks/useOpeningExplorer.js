import { useEffect, useMemo, useState } from "react";
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
  const [currentNodeId, setCurrentNodeId] = useState(tree.rootId);

  useEffect(() => {
    setCurrentNodeId(tree.rootId);
  }, [tree.rootId]);

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
    setCurrentNodeId(nodeId);
  }

  function goToParent() {
    if (parent) setCurrentNodeId(parent.id);
  }

  function goToNext() {
    if (next) setCurrentNodeId(next.id);
  }

  function goToStart() {
    setCurrentNodeId(tree.rootId);
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