import { useState } from "react";
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

export default function App() {
  const username = "chocoroku";
  const rating = 1858;

  const [hoveredRecommendationMove, setHoveredRecommendationMove] = useState(null);

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

  const sideToMove = boardFen?.includes(" w ") ? "white" : "black";

  const {
    data: recommendation,
    loading: recommendationLoading,
    error: recommendationError,
  } = useRecommendation({
    fen: boardFen,
    userId: username,
    rating,
    color: sideToMove,
    enabled: Boolean(boardFen),
  });

  const arrows = hoveredRecommendationMove
    ? buildRecommendationArrows([hoveredRecommendationMove])
    : buildRecommendationArrows(recommendation?.candidates ?? []);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;
  if (!currentNode) return <ErrorState message="No opening tree available." />;

  return (
    <main className="app-shell">
      <Header username={username} gameCount={games.length} />

      <div className="app-grid">
        <section className="left-column">
          <ChessBoardPanel fen={boardFen} arrows={arrows} />

          <MoveControls
            canGoBack={Boolean(parent)}
            canGoForward={Boolean(next)}
            onBack={goToParent}
            onForward={goToNext}
            onStart={goToStart}
          />
        </section>

        <section className="right-column">
          <CurrentLine line={line} fen={boardFen} />

          <RecommendationPanel
            recommendation={recommendation}
            loading={recommendationLoading}
            error={recommendationError}
            onMoveHover={setHoveredRecommendationMove}
            onMoveLeave={() => setHoveredRecommendationMove(null)}
          />

          <VariationList childrenNodes={children} onSelect={goToNode} />
        </section>
      </div>
    </main>
  );
}