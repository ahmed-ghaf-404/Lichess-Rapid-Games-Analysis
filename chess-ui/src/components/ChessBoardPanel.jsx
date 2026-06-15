import { Chessboard } from "react-chessboard";

export default function ChessBoardPanel({
  fen,
  arrows = [],
  sideToMove = "white",
  onMove,
}) {
  const sidePrefix = sideToMove === "white" ? "w" : "b";

  return (
    <section className="panel board-panel">
      <Chessboard
        options={{
          position: fen,
          arrows,
          allowDragging: true,
          canDragPiece: ({ piece }) => piece.pieceType.startsWith(sidePrefix),
          onPieceDrop: ({ sourceSquare, targetSquare }) =>
            onMove?.(sourceSquare, targetSquare) ?? false,
        }}
      />
    </section>
  );
}