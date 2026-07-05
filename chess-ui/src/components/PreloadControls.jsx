function ProgressLine({ label, status }) {
  const total = Math.max(status?.total ?? 0, status?.completed ?? 0, 1);
  const completed = status?.completed ?? 0;
  const percent = Math.min(100, Math.round((completed / total) * 100));

  return (
    <div className="preload-progress-block">
      <div className="preload-progress-header">
        <span>{label}</span>
        <span>
          {completed} / {status?.total ?? 0} positions · {percent}%
        </span>
      </div>
      <div className="preload-progress-track">
        <div className="preload-progress-fill" style={{ width: `${percent}%` }} />
      </div>
      {status?.loading ? (
        <p className="preload-note">
          Loading {status.queued ?? 0} queued positions in the background…
        </p>
      ) : null}
      {status?.error ? <p className="error">{status.error}</p> : null}
    </div>
  );
}

function NumberField({ label, value, min, max, onChange, hint }) {
  return (
    <label className="preload-field">
      <span>{label}</span>
      <input
        type="number"
        min={min}
        max={max}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
      />
      {hint ? <small>{hint}</small> : null}
    </label>
  );
}

export default function PreloadControls({
  warmup,
  compact = false,
}) {
  if (!warmup?.settings) return null;

  const { settings } = warmup;

  return (
    <section className={`panel preload-panel${compact ? " compact" : ""}`}>
      <div className="preload-title-row">
        <div>
          <h2>Analysis buffer</h2>
          <p className="preload-note">
            Control how aggressively the UI fills Redis before and during play.
          </p>
        </div>
        <button type="button" onClick={warmup.restartStartup}>
          Restart preload
        </button>
      </div>

      <div className="preload-toggle-row">
        <label>
          <input
            type="checkbox"
            checked={settings.startupEnabled}
            onChange={(event) => warmup.setSettings({ startupEnabled: event.target.checked })}
          />
          Startup preload
        </label>
        <label>
          <input
            type="checkbox"
            checked={settings.blockStartup}
            onChange={(event) => warmup.setSettings({ blockStartup: event.target.checked })}
          />
          Wait before showing board
        </label>
      </div>

      <div className="preload-grid-controls">
        <NumberField
          label="Leaf positions"
          value={settings.maxLeafPositions}
          min={1}
          max={200}
          onChange={(value) => warmup.setSettings({ maxLeafPositions: value })}
          hint="How many opening-tree leaves to seed."
        />
        <NumberField
          label="Startup depth"
          value={settings.startupDepth}
          min={1}
          max={5}
          onChange={(value) => warmup.setSettings({ startupDepth: value })}
          hint="Ply levels from each leaf."
        />
        <NumberField
          label="Branches per leaf"
          value={settings.startupBranching}
          min={1}
          max={8}
          onChange={(value) => warmup.setSettings({ startupBranching: value })}
          hint="2 or 3 means top 2/3 candidate moves per node."
        />
        <NumberField
          label="Near-leaf threshold"
          value={settings.nearLeafThreshold}
          min={0}
          max={10}
          onChange={(value) => warmup.setSettings({ nearLeafThreshold: value })}
          hint="0 = at leaf, 1 = one move away."
        />
        <NumberField
          label="Background depth"
          value={settings.backgroundDepth}
          min={1}
          max={5}
          onChange={(value) => warmup.setSettings({ backgroundDepth: value })}
          hint="Extra ply levels to refill."
        />
        <NumberField
          label="Background branches"
          value={settings.backgroundBranching}
          min={1}
          max={8}
          onChange={(value) => warmup.setSettings({ backgroundBranching: value })}
          hint="Use 3 to load three more candidate moves."
        />
      </div>

      <div className="preload-summary">
        <span>Startup estimate: about {warmup.estimatedStartupTotal} positions</span>
        <span>
          Nearest opening-tree leaf: {warmup.nearestLeafDistance ?? "unknown"} move
          {warmup.nearestLeafDistance === 1 ? "" : "s"} away
        </span>
        <span>Background estimate: about {warmup.estimatedBackgroundTotal} positions</span>
      </div>

      <ProgressLine label="Startup" status={warmup.startup} />
      <ProgressLine label={`Background${warmup.background?.reason ? ` · ${warmup.background.reason}` : ""}`} status={warmup.background} />

      <div className="preload-actions">
        <button type="button" onClick={warmup.skipStartup} disabled={!warmup.startup?.loading}>
          Skip startup loading
        </button>
        <button type="button" onClick={() => warmup.runBackgroundPreload()} disabled={warmup.background?.loading}>
          Fill from current position
        </button>
      </div>
    </section>
  );
}
