import { Chessboard } from "react-chessboard";

export default function ChessBoardPanel({ fen, arrows = [] }) {
  return (
    <div className="panel board-panel">
      <Chessboard
        key={`${fen}-${JSON.stringify(arrows)}`}
        options={{
          position: fen,
          arePiecesDraggable: false,
          customArrows: arrows,
          customBoardStyle: {
            borderRadius: "10px",
            boxShadow: "0 8px 24px rgba(0,0,0,0.35)",
          },
          customLightSquareStyle: {
            backgroundColor: "#f0d9b5",
          },
          customDarkSquareStyle: {
            backgroundColor: "#b58863",
          },
        }}
      />
    </div>
  );
}