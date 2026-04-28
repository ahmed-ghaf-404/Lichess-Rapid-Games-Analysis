export default function VariationList({ childrenNodes, onSelect }) {
  return (
    <section className="panel">
      <h2>Variations</h2>

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
              <span>{node.san}</span>
              <span className="variation-count">{node.visitCount}</span>
            </button>
          ))}
        </div>
      )}
    </section>
  );
}