import { useEffect, useRef, useState } from "react";
import { Chess } from "chess.js";
import { Chessboard } from "react-chessboard";

export default function Dashboard() {
  // ♟️ persistent game instance (IMPORTANT)
  const chessRef = useRef(new Chess());
  const game = chessRef.current;

  // 📌 UI state (ONLY fen)
  const [fen, setFen] = useState(game.fen());

  // 🔥 optional arrows (you can replace later with ML / engine)
  const [arrows, setArrows] = useState([]);

  // ♟️ handle piece drop (drag & drop on board)
  function onPieceDrop(sourceSquare, targetSquare) {
    if (!targetSquare) return false;

    const move = game.move({
      from: sourceSquare,
      to: targetSquare,
      promotion: "q",
    });

    if (!move) return false;

    // 🔥 update UI
    setFen(game.fen());

    // 🔥 simple demo arrow (last move)
    setArrows([
      {
        startSquare: sourceSquare,
        endSquare: targetSquare,
        color: "blue",
      },
    ]);

    return true;
  }

  return (
    <div style={{ padding: 20, display: "flex", flexDirection: "column", gap: 12 }}>
      <h2>Basic Chess Analysis Board</h2>

      <Chessboard
        position={fen}
        onPieceDrop={onPieceDrop}
        customArrows={arrows}
      />

      <div>
        <button onClick={() => console.log(game.fen())}>
          Log FEN
        </button>
      </div>
    </div>
  );
}