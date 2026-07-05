export default function RecommendationPanel({
  sideToMove,
  recommendation,
  loading,
  error,
  onMoveHover,
  onMoveLeave,
  onMoveSelect,
}) {
  if (loading) {
    return (
      <section className="panel">
        <h2>Coach Recommendation · {sideToMove === "white" ? "White" : "Black"} to move</h2>
        <p>Loading recommendation...</p>
      </section>
    );
  }

  if (error) {
    return (
      <section className="panel">
        <h2>Coach Recommendation · {sideToMove === "white" ? "White" : "Black"} to move</h2>
        <p className="error">{error}</p>
      </section>
    );
  }

  if (!recommendation || !recommendation.candidates?.length) {
    return (
      <section className="panel">
        <h2>Coach Recommendation · {sideToMove === "white" ? "White" : "Black"} to move</h2>
        <p>No recommendation available for this position.</p>
      </section>
    );
  }

  const [top, ...rest] = recommendation.candidates;

  return (
    <section className="panel">
      <h2>Coach Recommendation · {sideToMove === "white" ? "White" : "Black"} to move</h2>

      <div
        style={{ marginBottom: "12px", cursor: "pointer" }}
        onMouseEnter={() => onMoveHover?.(top)}
        onMouseLeave={onMoveLeave}
        onClick={() => onMoveSelect?.(top)}
        title="Click to play this move"
      >
        <div style={{ fontSize: "0.9rem", opacity: 0.8 }}>Recommended move</div>
        <div style={{ fontSize: "1.25rem", fontWeight: 700 }}>{top.move_san}</div>
        <div style={{ fontSize: "0.9rem", opacity: 0.8 }}>
          Score: {top.score} · Peer games: {top.peer_games}
        </div>
      </div>

      <div style={{ marginBottom: "12px" }}>
        <div style={{ fontSize: "0.9rem", opacity: 0.8 }}>Why</div>

        {top.reasons?.length ? (
          <ul style={{ margin: "6px 0 0 18px" }}>
            {top.reasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        ) : (
          <p>No explanation yet.</p>
        )}
      </div>

      <div>
        <div style={{ fontSize: "0.9rem", opacity: 0.8, marginBottom: "8px" }}>
          Other candidates
        </div>

        <div className="variation-list">
          {[top, ...rest].slice(0, 3).map((move) => (
            <div
              key={move.move_uci}
              className="variation-button"
              style={{ cursor: "pointer" }}
              onMouseEnter={() => onMoveHover?.(move)}
              onMouseLeave={onMoveLeave}
              onClick={() => onMoveSelect?.(move)}
              title="Click to play this move"
            >
              <span>{move.move_san}</span>
              <span className="variation-count">
                Eval: {sideToMove === "white" ? move.engine_eval_cp/100 : move.engine_eval_cp/-100} · Win rate: {Math.round(move.peer_frequency * 100)}% · {move.peer_games} games
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}