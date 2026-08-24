export default function VariationList({ childrenNodes, sideToMove, onSelect }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <span className="panel-kicker">Game history</span>
          <h2>Popular continuations</h2>
        </div>
        <span className="turn-badge">
          {sideToMove === "white" ? "White" : "Black"} to move
        </span>
      </div>

      {childrenNodes.length === 0 ? (
        <p>No moves from this position.</p>
      ) : (
        <div className="variation-list">
          {childrenNodes.map((node) => (
            <button
              key={node.id}
              type="button"
              className="variation-button"
              onClick={() => onSelect(node.id)}
            >
              <span className="candidate-move">{node.san}</span>
              <span className="variation-count">
                {node.visitCount} game{node.visitCount === 1 ? "" : "s"}
              </span>
            </button>
          ))}
        </div>
      )}
    </section>
  );
}
