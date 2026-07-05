import { useEffect, useState } from "react";
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

export default function App() {
  const username = "chocoroku";
  const rating = 1858;

  const [hoveredRecommendationMove, setHoveredRecommendationMove] = useState(null);
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [analysisIndex, setAnalysisIndex] = useState(-1);

  const analysisFen = analysisIndex >= 0 ? analysisHistory[analysisIndex] : null;

  const { games, loading, error } = useGames(username);

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
    enabled: Boolean(displayFen) && shouldShowRecommendation,
  });

  const arrows = hoveredRecommendationMove
      ? buildRecommendationArrows([hoveredRecommendationMove])
      : buildRecommendationArrows(recommendation?.candidates ?? []);

  function clearAnalysisLine() {
    setAnalysisHistory([]);
    setAnalysisIndex(-1);
    setHoveredRecommendationMove(null);
  }

  useEffect(() => {
    clearAnalysisLine();
  }, [boardFen]);

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
      console.warn("Could not play recommended move:", move);
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
        setHoveredRecommendationMove(null);
        goToNode(matchingChild.id);
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

    goToNext();
  }

  function goToStartPosition() {
    clearAnalysisLine();
    goToStart();
  }

  if (loading) return <LoadingState message="Loading games..." />;
  if (error) return <ErrorState message={error} />;
  if (!currentNode) return <ErrorState message="No opening tree available." />;
  if (warmup.loading) {
    return (
      <LoadingState
        message="Precomputing coach analysis..."
        detail={`Buffered ${warmup.startup.completed} of about ${warmup.startup.total} positions. You can change the preload shape below.`}
      >
        <PreloadControls warmup={warmup} compact />
      </LoadingState>
    );
  }

  return (
    <main className="app-shell">
      <Header username={username} gameCount={games.length} warmup={warmup} />

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
          <CurrentLine line={line} fen={displayFen} />

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
              onSelect={goToNode}
            />
          )}

          <PreloadControls warmup={warmup} />
        </section>
      </div>
    </main>
  );
}