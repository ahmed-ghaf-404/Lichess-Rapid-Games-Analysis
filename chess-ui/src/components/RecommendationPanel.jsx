export default function RecommendationPanel({
  sideToMove,
  recommendation,
  loading,
  error,
  onMoveHover,
  onMoveLeave,
  onMoveSelect,
}) {
  const title = `${sideToMove === "white" ? "White" : "Black"} to move`;

  if (loading) {
    return (
      <section className="panel recommendation-panel" aria-busy="true">
        <div className="panel-heading">
          <div>
            <span className="panel-kicker">Coach recommendation</span>
            <h2>{title}</h2>
          </div>
        </div>
        <div className="recommendation-skeleton" aria-label="Loading recommendation" />
      </section>
    );
  }

  if (error) {
    return (
      <section className="panel recommendation-panel">
        <div className="panel-heading">
          <div>
            <span className="panel-kicker">Coach recommendation</span>
            <h2>{title}</h2>
          </div>
        </div>
        <p className="error">{error}</p>
      </section>
    );
  }

  if (!recommendation || !recommendation.candidates?.length) {
    return (
      <section className="panel recommendation-panel">
        <div className="panel-heading">
          <div>
            <span className="panel-kicker">Coach recommendation</span>
            <h2>{title}</h2>
          </div>
        </div>
        <p className="empty-copy">No recommendation is available for this position.</p>
      </section>
    );
  }

  const [top, ...rest] = recommendation.candidates;

  return (
    <section className="panel recommendation-panel">
      <div className="panel-heading">
        <div>
          <span className="panel-kicker">Coach recommendation</span>
          <h2>{title}</h2>
        </div>
        <span className="coach-badge">Best practical move</span>
      </div>

      <button
        type="button"
        className="recommendation-hero"
        onMouseEnter={() => onMoveHover?.(top)}
        onMouseLeave={onMoveLeave}
        onClick={() => onMoveSelect?.(top)}
        title="Click to play this move"
      >
        <span className="recommendation-label">Recommended move</span>
        <span className="recommendation-move">{top.move_san}</span>
        <span className="recommendation-meta">
          Practical score {top.score} · {top.peer_games} peer games
        </span>
        <span className="play-hint" aria-hidden="true">
          Play move <span>→</span>
        </span>
      </button>

      <div className="reason-block">
        <span className="section-label">Why it works</span>

        {top.reasons?.length ? (
          <ul className="reason-list">
            {top.reasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        ) : (
          <p className="empty-copy">No explanation yet.</p>
        )}
      </div>

      {rest.length ? <div>
        <span className="section-label candidate-heading">Other candidates</span>

        <div className="variation-list">
          {rest.slice(0, 3).map((move) => {
            const evaluation = Number.isFinite(move.engine_eval_cp)
              ? (sideToMove === "white"
                ? move.engine_eval_cp / 100
                : move.engine_eval_cp / -100).toFixed(2)
              : "—";
            const winRate = Number.isFinite(move.peer_frequency)
              ? `${Math.round(move.peer_frequency * 100)}%`
              : "—";

            return (
              <button
                key={move.move_uci}
                type="button"
                className="variation-button candidate-button"
                onMouseEnter={() => onMoveHover?.(move)}
                onMouseLeave={onMoveLeave}
                onClick={() => onMoveSelect?.(move)}
                title="Click to play this move"
              >
                <span className="candidate-move">{move.move_san}</span>
                <span className="variation-count">
                  Eval {evaluation} · Frequency {winRate} · {move.peer_games} games
                </span>
              </button>
            );
          })}
        </div>
      </div> : null}
    </section>
  );
}
