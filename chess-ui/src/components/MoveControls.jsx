export default function MoveControls({
  canGoBack,
  canGoForward,
  onBack,
  onForward,
  onStart,
}) {
  return (
    <div className="controls">
      <button type="button" onClick={onBack} disabled={!canGoBack}>
        ◀ Prev
      </button>

      <button type="button" onClick={onForward} disabled={!canGoForward}>
        Next ▶
      </button>

      <button type="button" onClick={onStart}>
        ⏮ Start
      </button>
    </div>
  );
}