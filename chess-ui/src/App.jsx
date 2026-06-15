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
import { useGames } from "./hooks/useGames";
import { useOpeningExplorer } from "./hooks/useOpeningExplorer";
import { useRecommendation } from "./hooks/useRecommendation";
import { buildRecommendationArrows } from "./utils/recommendationArrows";

function getSideToMove(fen) {
  return fen?.includes(" w ") ? "white" : "black";
}

export default function App() {
  const username = "chocoroku";
  const rating = 1858;

  const [hoveredRecommendationMove, setHoveredRecommendationMove] = useState(null);
  const [analysisFen, setAnalysisFen] = useState(null);

  const { games, loading, error } = useGames(username);

  const {
    currentNode,
    boardFen,
    children,
    parent,
    next,
    line,
    goToNode,
    goToParent,
    goToNext,
    goToStart,
  } = useOpeningExplorer(games);

  useEffect(() => {
    setAnalysisFen(null);
    setHoveredRecommendationMove(null);
  }, [boardFen]);

  const displayFen = analysisFen ?? boardFen;
  const sideToMove = getSideToMove(displayFen);
  const isFollowingRecommendation = Boolean(analysisFen);
  const hasKnownMoves = !isFollowingRecommendation && children.length > 0;
  const shouldShowRecommendation = isFollowingRecommendation || !hasKnownMoves;

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

  const arrows = shouldShowRecommendation
    ? hoveredRecommendationMove
      ? buildRecommendationArrows([hoveredRecommendationMove])
      : buildRecommendationArrows(recommendation?.candidates ?? [])
    : [];

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

    setHoveredRecommendationMove(null);
    setAnalysisFen(game.fen());
  }

  function returnToExplorerPosition() {
    setAnalysisFen(null);
    setHoveredRecommendationMove(null);
  }

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;
  if (!currentNode) return <ErrorState message="No opening tree available." />;

  return (
    <main className="app-shell">
      <Header username={username} gameCount={games.length} />

      <div className="app-grid">
        <section className="left-column">
          <ChessBoardPanel fen={displayFen} arrows={arrows} />

          <MoveControls
            canGoBack={Boolean(parent)}
            canGoForward={Boolean(next)}
            onBack={goToParent}
            onForward={goToNext}
            onStart={goToStart}
          />

          {isFollowingRecommendation && (
            <button type="button" onClick={returnToExplorerPosition}>
              Back to explored position
            </button>
          )}
        </section>

        <section className="right-column">
          <CurrentLine line={line} fen={displayFen} />

          {shouldShowRecommendation ? (
            <RecommendationPanel
              sideToMove={sideToMove}
              recommendation={recommendation}
              loading={recommendationLoading}
              error={recommendationError}
              onMoveHover={setHoveredRecommendationMove}
              onMoveLeave={() => setHoveredRecommendationMove(null)}
              onMoveSelect={playRecommendedMove}
            />
          ) : (
            <VariationList
              childrenNodes={children}
              sideToMove={sideToMove}
              onSelect={goToNode}
            />
          )}
        </section>
      </div>
    </main>
  );
}
