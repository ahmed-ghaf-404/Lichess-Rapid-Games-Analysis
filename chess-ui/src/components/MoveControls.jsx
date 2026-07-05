export default function MoveControls({
  canGoBack,
  canGoForward,
  onBack,
  onForward,
  onStart,
}) {
  return (
    <div className="controls">
      <button type="button" onClick={onStart}>
        ⏮ Start
      </button>

      <button type="button" onClick={onBack} disabled={!canGoBack}>
        ◀ Previous
      </button>

      <button type="button" onClick={onForward} disabled={!canGoForward}>
        Next ▶
      </button>
    </div>
  );
}