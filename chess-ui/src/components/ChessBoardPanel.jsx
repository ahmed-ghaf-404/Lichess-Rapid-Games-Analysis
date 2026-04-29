import { Chessboard } from "react-chessboard";

export default function ChessBoardPanel({ fen, arrows = [] }) {
  const arrowKey = JSON.stringify(arrows);

  return (
    <section className="panel board-panel">
        <Chessboard
        options={{
          position: fen,
          arrows,
          allowDragging: false,
        }}
      />
    </section>
  );
}