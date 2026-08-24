export default function MoveControls({
  canGoBack,
  canGoForward,
  onBack,
  onForward,
  onStart,
}) {
  return (
    <nav className="controls" aria-label="Opening navigation">
      <button type="button" onClick={onStart} title="Return to the starting position">
        ⏮ Start
      </button>

      <button type="button" onClick={onBack} disabled={!canGoBack}>
        ◀ Previous
      </button>

      <button type="button" onClick={onForward} disabled={!canGoForward}>
        Next ▶
      </button>
    </nav>
  );
}
