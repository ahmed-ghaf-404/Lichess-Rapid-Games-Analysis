export default function GameSummary({ currentNode, line }) {
  const moveText = line.map((node) => node.san).join(" ");

  return (
    <section className="panel">
      <h2>Current Line</h2>
      <p>{moveText || "Start position"}</p>
      <p className="fen-text">{currentNode?.fen}</p>
    </section>
  );
}