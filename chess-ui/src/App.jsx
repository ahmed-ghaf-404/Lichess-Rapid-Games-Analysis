import { useMemo, useState } from "react";
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
import { useGames } from "./hooks/useGames";
import { useOpeningExplorer } from "./hooks/useOpeningExplorer";
import { useRecommendation } from "./hooks/useRecommendation";
import { useRecommendationWarmup } from "./hooks/useRecommendationWarmup";
import { buildRecommendationArrows } from "./utils/recommendationArrows";
import { getSideToMove } from "./utils/recommendationApi";
import {
  DEFAULT_LICHESS_USERNAME,
  getPlayerRating,
} from "./utils/lichessUser";
import { getAppMode, shouldShowDeveloperTools } from "./config/appMode";
import { logger } from "./utils/logger";

export default function App() {
  const [username, setUsername] = useState(DEFAULT_LICHESS_USERNAME);

  const [hoveredRecommendationMove, setHoveredRecommendationMove] = useState(null);
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [analysisIndex, setAnalysisIndex] = useState(-1);

  const analysisFen = analysisIndex >= 0 ? analysisHistory[analysisIndex] : null;

  const { games, loading, error } = useGames(username);
  const rating = useMemo(
    () => getPlayerRating(games, username),
    [games, username]
  );
  const appMode = getAppMode();
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


  const warmup = useRecommendationWarmup({
    tree,
    currentNodeId,
    displayFen,
    analysisPosition: isFollowingRecommendation,
    userId: username,
    rating,
    enabled: !loading && !error && Boolean(currentNode),
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
    enabled:
      !loading &&
      !error &&
      Boolean(currentNode) &&
      Boolean(displayFen) &&
      shouldShowRecommendation,
  });

  const arrows = hoveredRecommendationMove
      ? buildRecommendationArrows([hoveredRecommendationMove])
      : buildRecommendationArrows(recommendation?.candidates ?? []);

  function clearAnalysisLine() {
    setAnalysisHistory([]);
    setAnalysisIndex(-1);
    setHoveredRecommendationMove(null);
  }

  function pushAnalysisPosition(nextFen, preloadReason) {
    setHoveredRecommendationMove(null);
    setAnalysisHistory((history) => [
      ...history.slice(0, analysisIndex + 1),
      nextFen,
    ]);
    setAnalysisIndex((index) => index + 1);
    warmup.runBackgroundPreload([nextFen], preloadReason);
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

    pushAnalysisPosition(
      game.fen(),
      "Played recommendation; refilling next branches"
    );
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

    pushAnalysisPosition(nextFen, "Dragged move on board; refilling next branches");
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

  return (
    <main className="app-shell">
      <Header
        username={username}
        gameCount={games.length}
        rating={rating}
        loading={loading}
        warmup={warmup}
        appMode={appMode}
        showDeveloperTools={showDeveloperTools}
        onUsernameChange={selectUsername}
      />

      {loading ? <LoadingState message={`Loading @${username}'s rapid games…`} /> : null}

      {!loading && error ? (
        <ErrorState
          title="Player could not be loaded"
          message={error}
          detail="Check the spelling or try another Lichess username above."
        />
      ) : null}

      {!loading && !error && !currentNode ? (
        <ErrorState
          title="Opening tree unavailable"
          message="No opening tree could be built for this player."
        />
      ) : null}

      {!loading && !error && currentNode && warmup.loading ? (
        <LoadingState
          message="Preparing coach analysis…"
          detail={`Buffered ${warmup.startup.completed} of about ${warmup.startup.total} positions.`}
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
            onMove={handleBoardMove}
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
            <CurrentLine
              line={line}
              fen={displayFen}
              showFen={showDeveloperTools}
            />

          <RecommendationPanel
            sideToMove={sideToMove}
            recommendation={recommendation}
            loading={recommendationLoading}
            error={recommendationError}
            onMoveHover={setHoveredRecommendationMove}
            onMoveLeave={() => setHoveredRecommendationMove(null)}
            onMoveSelect={playRecommendedMove}
          />

          {!isFollowingRecommendation && children.length > 0 && (
            <VariationList
              childrenNodes={children}
              sideToMove={sideToMove}
              onSelect={selectOpeningNode}
            />
          )}

          {showDeveloperTools ? <PreloadControls warmup={warmup} /> : null}
          </section>
        </div>
      ) : null}

      <footer className="app-footer">
        Personal opening insights powered by Lichess game data and Stockfish.
      </footer>
    </main>
  );
}
