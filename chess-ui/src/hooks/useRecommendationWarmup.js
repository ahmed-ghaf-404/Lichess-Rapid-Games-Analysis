import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  fetchRecommendation,
  fenAfterUciMove,
  getSideToMove,
} from "../utils/recommendationApi";

const envNumber = (name, fallback) => {
  const value = Number(import.meta.env[name]);
  return Number.isFinite(value) ? value : fallback;
};

const clampNumber = (value, min, max, fallback) => {
  const number = Number(value);
  if (!Number.isFinite(number)) return fallback;
  return Math.min(max, Math.max(min, Math.round(number)));
};

export const DEFAULT_PRELOAD_SETTINGS = {
  startupEnabled: import.meta.env.VITE_WARMUP_ENABLED !== "false",
  blockStartup: import.meta.env.VITE_WARMUP_BLOCKING !== "false",
  maxLeafPositions: envNumber("VITE_WARMUP_MAX_POSITIONS", 12),
  startupDepth: envNumber("VITE_WARMUP_DEPTH", 2),
  startupBranching: envNumber("VITE_WARMUP_BRANCHING", 2),
  nearLeafThreshold: envNumber("VITE_NEAR_LEAF_THRESHOLD", 1),
  backgroundDepth: envNumber("VITE_BACKGROUND_WARMUP_DEPTH", 2),
  backgroundBranching: envNumber("VITE_BACKGROUND_WARMUP_BRANCHING", 3),
  maxCandidates: envNumber("VITE_RECOMMENDATION_MAX_CANDIDATES", 6),
};

function normalizeSettings(settings) {
  return {
    startupEnabled: Boolean(settings.startupEnabled),
    blockStartup: Boolean(settings.blockStartup),
    maxLeafPositions: clampNumber(settings.maxLeafPositions, 1, 200, 12),
    startupDepth: clampNumber(settings.startupDepth, 1, 5, 2),
    startupBranching: clampNumber(settings.startupBranching, 1, 8, 2),
    nearLeafThreshold: clampNumber(settings.nearLeafThreshold, 0, 10, 1),
    backgroundDepth: clampNumber(settings.backgroundDepth, 1, 5, 2),
    backgroundBranching: clampNumber(settings.backgroundBranching, 1, 8, 3),
    maxCandidates: clampNumber(settings.maxCandidates, 1, 12, 6),
  };
}

function estimateTreeSize(seedCount, depth, branching) {
  if (!seedCount || depth <= 0) return 0;

  let levels = 0;
  let levelSize = 1;

  for (let level = 0; level < depth; level += 1) {
    levels += levelSize;
    levelSize *= Math.max(1, branching);
  }

  return seedCount * levels;
}

function getNode(tree, nodeId) {
  return tree?.nodesById?.[nodeId] ?? null;
}

function getChildren(tree, nodeId) {
  const node = getNode(tree, nodeId);
  if (!node) return [];

  return node.childIds
    .map((childId) => tree.nodesById[childId])
    .filter(Boolean)
    .sort((a, b) => b.visitCount - a.visitCount);
}

function collectLeafFens(tree, maxPositions) {
  if (!tree?.nodesById) return [];

  return Object.values(tree.nodesById)
    .filter((node) => node?.fen && node.childIds.length === 0)
    .sort((a, b) => b.visitCount - a.visitCount)
    .slice(0, maxPositions)
    .map((node) => node.fen);
}

function getNearestLeafDistance(tree, nodeId, maxDepth = 10) {
  const start = getNode(tree, nodeId);
  if (!start) return null;
  if (start.childIds.length === 0) return 0;

  const queue = [{ node: start, distance: 0 }];
  const seen = new Set([start.id]);

  while (queue.length) {
    const { node, distance } = queue.shift();
    if (node.childIds.length === 0) return distance;
    if (distance >= maxDepth) continue;

    for (const childId of node.childIds) {
      if (seen.has(childId)) continue;
      const child = getNode(tree, childId);
      if (!child) continue;
      seen.add(childId);
      queue.push({ node: child, distance: distance + 1 });
    }
  }

  return null;
}

function collectNearLeafFens(tree, nodeId, threshold, maxSeeds) {
  const start = getNode(tree, nodeId);
  if (!start) return [];

  const leaves = [];
  const queue = [{ node: start, distance: 0 }];
  const seen = new Set([start.id]);

  while (queue.length && leaves.length < maxSeeds) {
    const { node, distance } = queue.shift();

    if (node.childIds.length === 0) {
      leaves.push(node.fen);
      continue;
    }

    if (distance >= threshold) continue;

    for (const child of getChildren(tree, node.id)) {
      if (seen.has(child.id)) continue;
      seen.add(child.id);
      queue.push({ node: child, distance: distance + 1 });
    }
  }

  return leaves;
}

function uniqueFens(fens) {
  return [...new Set(fens.filter(Boolean))];
}

async function preloadRecommendationTree({
  seedFens,
  depth,
  branching,
  maxCandidates,
  userId,
  rating,
  signal,
  seen,
  onProgress,
}) {
  const queue = uniqueFens(seedFens).map((fen) => ({ fen, depth: 0 }));
  const estimatedTotal = estimateTreeSize(queue.length, depth, branching);
  let completed = 0;

  onProgress?.({
    completed,
    total: estimatedTotal,
    queued: queue.length,
    currentFen: "",
  });

  while (queue.length && !signal?.aborted) {
    const item = queue.shift();
    if (!item?.fen) continue;

    const seenKey = `${item.fen}|d:${item.depth}|b:${branching}|m:${maxCandidates}`;
    if (seen?.has(seenKey)) continue;
    seen?.add(seenKey);

    const recommendation = await fetchRecommendation({
      fen: item.fen,
      userId,
      rating,
      color: getSideToMove(item.fen),
      maxCandidates,
      signal,
    });

    completed += 1;
    onProgress?.({
      completed,
      total: Math.max(estimatedTotal, completed),
      queued: queue.length,
      currentFen: item.fen,
    });

    if (item.depth + 1 < depth) {
      for (const candidate of recommendation?.candidates?.slice(0, branching) ?? []) {
        const nextFen = fenAfterUciMove(item.fen, candidate.move_uci);
        if (!nextFen) continue;
        queue.push({ fen: nextFen, depth: item.depth + 1 });
      }
    }
  }

  return completed;
}

export function useRecommendationWarmup({
  tree,
  currentNodeId,
  displayFen,
  analysisPosition = false,
  userId,
  rating,
  enabled = true,
}) {
  const [settings, setSettingsState] = useState(() =>
    normalizeSettings(DEFAULT_PRELOAD_SETTINGS)
  );
  const [startupRunId, setStartupRunId] = useState(0);
  const [startupSkipped, setStartupSkipped] = useState(false);
  const startupSeenRef = useRef(new Set());
  const backgroundSeenRef = useRef(new Set());
  const backgroundRunningRef = useRef(false);

  const [startup, setStartup] = useState({
    loading: false,
    done: false,
    completed: 0,
    total: 0,
    queued: 0,
    currentFen: "",
    error: "",
  });

  const [background, setBackground] = useState({
    loading: false,
    completed: 0,
    total: 0,
    queued: 0,
    currentFen: "",
    reason: "",
    error: "",
  });

  const seedFens = useMemo(
    () => collectLeafFens(tree, settings.maxLeafPositions),
    [tree, settings.maxLeafPositions]
  );

  const nearestLeafDistance = useMemo(
    () => getNearestLeafDistance(tree, currentNodeId, settings.nearLeafThreshold + 6),
    [tree, currentNodeId, settings.nearLeafThreshold]
  );

  const nearLeafFens = useMemo(
    () =>
      collectNearLeafFens(
        tree,
        currentNodeId,
        settings.nearLeafThreshold,
        settings.backgroundBranching
      ),
    [tree, currentNodeId, settings.nearLeafThreshold, settings.backgroundBranching]
  );

  const setSettings = useCallback((patch) => {
    setSettingsState((current) => normalizeSettings({ ...current, ...patch }));
  }, []);

  const restartStartup = useCallback(() => {
    startupSeenRef.current = new Set();
    setStartupSkipped(false);
    setStartupRunId((value) => value + 1);
  }, []);

  const skipStartup = useCallback(() => {
    setStartupSkipped(true);
    setStartup({
      loading: false,
      done: true,
      completed: 0,
      total: 0,
      queued: 0,
      currentFen: "",
      error: "Startup preload skipped.",
    });
  }, []);

  const runBackgroundPreload = useCallback(
    async (fens, reason = "Manual background preload") => {
      const seeds = uniqueFens(fens);
      if (!enabled || !userId || seeds.length === 0 || backgroundRunningRef.current) {
        return;
      }

      backgroundRunningRef.current = true;
      const controller = new AbortController();

      try {
        setBackground({
          loading: true,
          completed: 0,
          total: estimateTreeSize(
            seeds.length,
            settings.backgroundDepth,
            settings.backgroundBranching
          ),
          queued: seeds.length,
          currentFen: "",
          reason,
          error: "",
        });

        const completed = await preloadRecommendationTree({
          seedFens: seeds,
          depth: settings.backgroundDepth,
          branching: settings.backgroundBranching,
          maxCandidates: settings.maxCandidates,
          userId,
          rating,
          signal: controller.signal,
          seen: backgroundSeenRef.current,
          onProgress: (progress) => {
            setBackground((current) => ({ ...current, ...progress, loading: true }));
          },
        });

        setBackground((current) => ({
          ...current,
          loading: false,
          completed,
          total: Math.max(current.total, completed),
          queued: 0,
          currentFen: "",
        }));
      } catch (err) {
        if (err.name !== "AbortError") {
          setBackground((current) => ({
            ...current,
            loading: false,
            error: err.message || "Background preload failed.",
          }));
        }
      } finally {
        backgroundRunningRef.current = false;
      }
    },
    [
      enabled,
      userId,
      rating,
      settings.backgroundDepth,
      settings.backgroundBranching,
      settings.maxCandidates,
    ]
  );

  useEffect(() => {
    if (!enabled || !settings.startupEnabled || startupSkipped || !userId || seedFens.length === 0) {
      setStartup((current) => ({ ...current, loading: false, done: true }));
      return;
    }

    const controller = new AbortController();

    setStartup({
      loading: true,
      done: false,
      completed: 0,
      total: estimateTreeSize(seedFens.length, settings.startupDepth, settings.startupBranching),
      queued: seedFens.length,
      currentFen: "",
      error: "",
    });

    async function run() {
      try {
        const completed = await preloadRecommendationTree({
          seedFens,
          depth: settings.startupDepth,
          branching: settings.startupBranching,
          maxCandidates: settings.maxCandidates,
          userId,
          rating,
          signal: controller.signal,
          seen: startupSeenRef.current,
          onProgress: (progress) => {
            setStartup((current) => ({ ...current, ...progress, loading: true }));
          },
        });

        if (!controller.signal.aborted) {
          setStartup((current) => ({
            ...current,
            loading: false,
            done: true,
            completed,
            total: Math.max(current.total, completed),
            queued: 0,
            currentFen: "",
          }));
        }
      } catch (err) {
        if (!controller.signal.aborted) {
          setStartup((current) => ({
            ...current,
            loading: false,
            done: true,
            error: err.message || "Warmup failed.",
          }));
        }
      }
    }

    run();

    return () => controller.abort();
  }, [
    enabled,
    settings.startupEnabled,
    settings.startupDepth,
    settings.startupBranching,
    settings.maxCandidates,
    startupSkipped,
    startupRunId,
    seedFens,
    userId,
    rating,
  ]);

  useEffect(() => {
    if (!enabled || startup.loading || !displayFen) return;

    if (analysisPosition) {
      runBackgroundPreload([displayFen], "Following recommendation line");
      return;
    }

    if (nearLeafFens.length) {
      runBackgroundPreload(
        nearLeafFens,
        `Near opening-tree leaf: ${nearestLeafDistance} move${nearestLeafDistance === 1 ? "" : "s"} away`
      );
      return;
    }

    if (nearestLeafDistance === 0) {
      runBackgroundPreload([displayFen], "At opening-tree leaf");
    }
  }, [
    enabled,
    startup.loading,
    displayFen,
    analysisPosition,
    nearLeafFens,
    nearestLeafDistance,
    runBackgroundPreload,
  ]);

  return {
    loading: startup.loading && settings.blockStartup,
    done: startup.done,
    completed: startup.completed,
    total: startup.total,
    error: startup.error,
    settings,
    setSettings,
    restartStartup,
    skipStartup,
    startup,
    background,
    nearestLeafDistance,
    nearLeafFens,
    estimatedStartupTotal: estimateTreeSize(
      seedFens.length,
      settings.startupDepth,
      settings.startupBranching
    ),
    estimatedBackgroundTotal: estimateTreeSize(
      Math.max(1, nearLeafFens.length || 1),
      settings.backgroundDepth,
      settings.backgroundBranching
    ),
    runBackgroundPreload: (fens = [displayFen], reason = "Manual background preload") =>
      runBackgroundPreload(fens, reason),
  };
}
