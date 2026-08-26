import { memo, useCallback, useMemo } from "react";
import { Chessboard } from "react-chessboard";
import { useLocalization } from "../i18n/useLocalization";


const BOARD_ANIMATION_MS = Math.max(
  0,
  Number(import.meta.env.VITE_BOARD_ANIMATION_MS ?? 120)
);

function ChessBoardPanel({
  fen,
  arrows = [],
  sideToMove = "white",
  onMove,
}) {
  const { t } = useLocalization();
  const sidePrefix = sideToMove === "white" ? "w" : "b";
  const canDragPiece = useCallback(
    ({ piece }) => piece.pieceType.startsWith(sidePrefix),
    [sidePrefix]
  );
  const onPieceDrop = useCallback(
    ({ sourceSquare, targetSquare }) =>
      onMove?.(sourceSquare, targetSquare) ?? false,
    [onMove]
  );
  const options = useMemo(
    () => ({
      position: fen,
      arrows,
      allowDragging: true,
      animationDurationInMs: BOARD_ANIMATION_MS,
      canDragPiece,
      onPieceDrop,
    }),
    [fen, arrows, canDragPiece, onPieceDrop]
  );

  return (
    <section className="panel board-panel" aria-label={t("board.label")}>
      <div className="board-direction-lock" dir="ltr">
        <Chessboard options={options} />
      </div>
    </section>
  );
}

export default memo(ChessBoardPanel);
