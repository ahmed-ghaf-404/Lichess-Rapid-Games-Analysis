export default function CurrentLine({ line, fen, showFen = false }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <span className="panel-kicker">Position</span>
          <h2>Current line</h2>
        </div>
        <span className="ply-count">{line.length} ply</span>
      </div>

      {line.length ? (
        <div className="move-sequence" aria-label="Current move sequence">
          {line.map((node, index) => (
            <span className="move-token" key={node.id}>
              {index % 2 === 0 ? `${Math.floor(index / 2) + 1}. ` : ""}
              {node.san}
            </span>
          ))}
        </div>
      ) : (
        <p className="empty-copy">Start position — choose a move to explore.</p>
      )}

      {showFen ? (
        <details className="developer-details">
          <summary>Developer: position FEN</summary>
          <code className="fen-text">{fen}</code>
        </details>
      ) : null}
    </section>
  );
}
