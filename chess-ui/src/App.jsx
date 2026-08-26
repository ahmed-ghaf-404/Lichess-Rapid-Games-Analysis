import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Chess } from "chess.js";
import "./styles/App.css";
import Header from "./components/Header";
import ChessBoardPanel from "./components/ChessBoardPanel";
import VariationList from "./components/VariationList";
import MoveControls from "./components/MoveControls";
import CurrentLine from "./components/CurrentLine";
import RecommendationPanel from "./components/RecommendationPanel";
import LoadingState from "./components/LoadingState";
import ErrorState from "./components/ErrorState";
import PreloadControls from "./components/PreloadControls";
import RepertoirePanel from "./components/RepertoirePanel";
import SiteFooter from "./components/SiteFooter";
import SiteNavigation from "./components/SiteNavigation";
import AboutPage from "./pages/AboutPage";
import ContactPage from "./pages/ContactPage";
import DevelopmentHistoryPage from "./pages/DevelopmentHistoryPage";
import { useGames } from "./hooks/useGames";
import { useOpeningExplorer } from "./hooks/useOpeningExplorer";
import { useRecommendation } from "./hooks/useRecommendation";
import { useRecommendationWarmup } from "./hooks/useRecommendationWarmup";
import { useRepertoire } from "./hooks/useRepertoire";
import {
  buildMoveArrows,
  RECOMMENDATION_ARROW_COLOR,
  REPERTOIRE_ARROW_COLOR,
} from "./utils/recommendationArrows";
import { getSideToMove } from "./utils/recommendationApi";
import { inferOpeningName } from "./utils/repertoire";
import {
  DEFAULT_LICHESS_USERNAME,
  getPlayerRating,
} from "./utils/lichessUser";
import {
  getAppMode,
  shouldShowCurrentLine,
  shouldShowDeveloperTools,
} from "./config/appMode";
import { logger } from "./utils/logger";
import { useLocalization } from "./i18n/useLocalization";


function useStableCallback(callback) {
  const callbackRef = useRef(callback);
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);
  return useCallback((...args) => callbackRef.current(...args), []);
}

export default function App() {
  const path = window.location.pathname.replace(/\/+$/, "") || "/";

  if (path === "/about") return <AboutPage />;
  if (path === "/contact") return <ContactPage />;
  if (path === "/history") return <DevelopmentHistoryPage />;
  return <ExplorerPage />;
}


function ExplorerPage() {
  const { formatNumber, t } = useLocalization();
  const [username, setUsername] = useState(DEFAULT_LICHESS_USERNAME);

  const [hoveredRecommendationMove, setHoveredRecommendationMove] = useState(null);
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [analysisIndex, setAnalysisIndex] = useState(-1);
  const [recommendationsEnabled, setRecommendationsEnabled] = useState(
    () => window.localStorage.getItem("ccc-recommendations-enabled") !== "false"
  );

  const analysisFen = analysisIndex >= 0 ? analysisHistory[analysisIndex] : null;

  const { games, loading, error } = useGames(username);
  const usingMasterFallback = !loading && !error && games.length === 0;
  const rating = useMemo(
    () => getPlayerRating(games, username),
    [games, username]
  );
  const appMode = getAppMode();
  const showCurrentLine = shouldShowCurrentLine();
  const showDeveloperTools = shouldShowDeveloperTools();

  const {
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
    tree,
  } = useOpeningExplorer(games);

  const displayFen = analysisFen ?? boardFen;
  const sideToMove = getSideToMove(displayFen);
  const isFollowingRecommendation = Boolean(analysisFen);
  const shouldShowRecommendation = Boolean(displayFen);
  const openingName = useMemo(
    () => inferOpeningName(games, line),
    [games, line]
  );
  const repertoire = useRepertoire(username, displayFen);


  const warmup = useRecommendationWarmup({
    tree,
    currentNodeId,
    displayFen,
    analysisPosition: isFollowingRecommendation,
    userId: username,
    rating,
    useMasterGames: usingMasterFallback,
    enabled:
      recommendationsEnabled &&
      !loading &&
      !error &&
      Boolean(currentNode),
  });

  const {
    data: recommendation,
    loading: recommendationLoading,
    error: recommendationError,
  } = useRecommendation({
    fen: displayFen,
    userId: username,
    rating,
    color: sideToMove,
    useMasterGames: usingMasterFallback,
    enabled:
      !loading &&
      !error &&
      Boolean(currentNode) &&
      Boolean(displayFen) &&
      shouldShowRecommendation &&
      recommendationsEnabled,
  });

  const recommendationMoves = useMemo(() => {
    if (!recommendationsEnabled) return [];
    const savedMoveUcis = new Set(
      repertoire.currentMoves.map((move) => move.move_uci)
    );
    return (recommendation?.candidates ?? []).filter(
      (move) => !savedMoveUcis.has(move.move_uci)
    );
  }, [recommendation, recommendationsEnabled, repertoire.currentMoves]);
  const arrows = useMemo(
    () => hoveredRecommendationMove
      ? buildMoveArrows(
          [hoveredRecommendationMove],
          hoveredRecommendationMove.visualSource === "repertoire"
            ? REPERTOIRE_ARROW_COLOR
            : RECOMMENDATION_ARROW_COLOR
        )
      : [
          ...buildMoveArrows(repertoire.currentMoves, REPERTOIRE_ARROW_COLOR),
          ...buildMoveArrows(recommendationMoves, RECOMMENDATION_ARROW_COLOR),
        ],
    [hoveredRecommendationMove, recommendationMoves, repertoire.currentMoves]
  );

  function updateRecommendationsEnabled(enabled) {
    setRecommendationsEnabled(enabled);
    window.localStorage.setItem("ccc-recommendations-enabled", String(enabled));
    if (!enabled) setHoveredRecommendationMove(null);
  }

  function clearAnalysisLine() {
    setAnalysisHistory([]);
    setAnalysisIndex(-1);
    setHoveredRecommendationMove(null);
  }

  function pushAnalysisPosition(nextFen) {
    setHoveredRecommendationMove(null);
    setAnalysisHistory((history) => [
      ...history.slice(0, analysisIndex + 1),
      nextFen,
    ]);
    setAnalysisIndex((index) => index + 1);
  }

  function playRecommendedMove(move) {
    const game = new Chess(displayFen);

    const result = game.move({
      from: move.move_uci.slice(0, 2),
      to: move.move_uci.slice(2, 4),
      promotion: move.move_uci[4] || "q",
    });

    if (!result) {
      logger.warn("Could not play recommended move", { move });
      return;
    }

    pushAnalysisPosition(game.fen());
  }

  function handleBoardMove(sourceSquare, targetSquare) {
    if (!targetSquare || sourceSquare === targetSquare) return false;

    const game = new Chess(displayFen);

    const result = game.move({
      from: sourceSquare,
      to: targetSquare,
      promotion: "q",
    });

    if (!result) return false;

    const nextFen = game.fen();

    if (!isFollowingRecommendation) {
      const matchingChild = children.find((child) => child.fen === nextFen);

      if (matchingChild) {
        selectOpeningNode(matchingChild.id);
        return true;
      }
    }

    pushAnalysisPosition(nextFen);
    return true;
  }

  function goToPreviousPosition() {
    setHoveredRecommendationMove(null);

    if (isFollowingRecommendation) {
      if (analysisIndex > 0) {
        setAnalysisIndex((index) => index - 1);
      } else {
        clearAnalysisLine();
      }
      return;
    }

    clearAnalysisLine();
    goToParent();
  }

  function goToNextPosition() {
    setHoveredRecommendationMove(null);

    if (isFollowingRecommendation) {
      if (analysisIndex < analysisHistory.length - 1) {
        setAnalysisIndex((index) => index + 1);
      }
      return;
    }

    clearAnalysisLine();
    goToNext();
  }

  function goToStartPosition() {
    clearAnalysisLine();
    goToStart();
  }

  function selectUsername(nextUsername) {
    clearAnalysisLine();
    setUsername(nextUsername);
  }

  function selectOpeningNode(nodeId) {
    clearAnalysisLine();
    goToNode(nodeId);
  }

  const stableBoardMove = useStableCallback(handleBoardMove);
  const stablePlayMove = useStableCallback(playRecommendedMove);
  const stableSelectOpeningNode = useStableCallback(selectOpeningNode);
  const stableRecommendationToggle = useStableCallback(updateRecommendationsEnabled);
  const hoverRecommendation = useStableCallback((move) =>
    setHoveredRecommendationMove({ ...move, visualSource: "recommendation" })
  );
  const hoverRepertoire = useStableCallback((move) =>
    setHoveredRecommendationMove({ ...move, visualSource: "repertoire" })
  );
  const clearHoveredMove = useStableCallback(() => setHoveredRecommendationMove(null));

  return (
    <main className="app-shell">
      <SiteNavigation activePath="/" />

      <Header
        username={username}
        gameCount={games.length}
        rating={rating}
        loading={loading}
        usingMasterFallback={usingMasterFallback}
        warmup={warmup}
        appMode={appMode}
        showDeveloperTools={showDeveloperTools}
        onUsernameChange={selectUsername}
      />

      {loading ? (
        <LoadingState message={t("app.loadingGames", { username })} />
      ) : null}

      {!loading && error ? (
        <ErrorState
          title={t("app.playerLoadError")}
          message={error}
          detail={t("app.playerLoadDetail")}
        />
      ) : null}

      {!loading && !error && !currentNode ? (
        <ErrorState
          title={t("app.treeUnavailable")}
          message={t("app.treeUnavailableMessage")}
        />
      ) : null}

      {!loading && !error && currentNode && warmup.loading ? (
        <LoadingState
          message={t("app.preparing")}
          detail={t("app.buffered", {
            completed: formatNumber(warmup.startup.completed),
            total: formatNumber(warmup.startup.total),
          })}
        >
          {showDeveloperTools ? <PreloadControls warmup={warmup} compact /> : null}
        </LoadingState>
      ) : null}

      {!loading && !error && currentNode && !warmup.loading ? (
        <div className="app-grid">
          <section className="left-column">
          <ChessBoardPanel
            fen={displayFen}
            arrows={arrows}
            sideToMove={sideToMove}
            onMove={stableBoardMove}
          />

          <MoveControls
            canGoBack={isFollowingRecommendation || Boolean(parent)}
            canGoForward={
              isFollowingRecommendation
                ? analysisIndex < analysisHistory.length - 1
                : Boolean(next)
            }
            onBack={goToPreviousPosition}
            onForward={goToNextPosition}
            onStart={goToStartPosition}
          />

          </section>

          <section className="right-column">
            {showCurrentLine ? (
              <CurrentLine line={line} fen={displayFen} showFen />
            ) : null}

          <RecommendationPanel
            sideToMove={sideToMove}
            recommendation={recommendation}
            recommendationsEnabled={recommendationsEnabled}
            loading={recommendationLoading}
            error={recommendationError}
            onRecommendationsEnabledChange={stableRecommendationToggle}
            onMoveHover={hoverRecommendation}
            onMoveLeave={clearHoveredMove}
            onMoveSelect={stablePlayMove}
          />

          {repertoire.enabled ? (
            <RepertoirePanel
              username={username}
              games={games}
              openingName={openingName}
              recommendation={recommendation}
              repertoire={repertoire}
              onMoveHover={hoverRepertoire}
              onMoveLeave={clearHoveredMove}
              onMoveSelect={stablePlayMove}
            />
          ) : null}

          {!isFollowingRecommendation && children.length > 0 && (
            <VariationList
              childrenNodes={children}
              sideToMove={sideToMove}
              onSelect={stableSelectOpeningNode}
            />
          )}

          {showDeveloperTools ? <PreloadControls warmup={warmup} /> : null}
          </section>
        </div>
      ) : null}

      <SiteFooter />
    </main>
  );
}
