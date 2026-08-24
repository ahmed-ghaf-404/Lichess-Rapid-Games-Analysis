import { useLocalization } from "../i18n/useLocalization";


function ProgressLine({ label, status, formatNumber, t }) {
  const total = Math.max(status?.total ?? 0, status?.completed ?? 0, 1);
  const completed = status?.completed ?? 0;
  const percent = Math.min(100, Math.round((completed / total) * 100));

  return (
    <div className="preload-progress-block">
      <div className="preload-progress-header">
        <span>{label}</span>
        <span>
          {t("dev.progress", {
            completed: formatNumber(completed),
            total: formatNumber(status?.total ?? 0),
            percent: formatNumber(percent),
          })}
        </span>
      </div>
      <div className="preload-progress-track">
        <div className="preload-progress-fill" style={{ width: `${percent}%` }} />
      </div>
      {status?.loading ? (
        <p className="preload-note">
          {t("dev.queued", { count: formatNumber(status.queued ?? 0) })}
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
  const { formatNumber, t } = useLocalization();
  if (!warmup?.settings) return null;

  const { settings } = warmup;

  return (
    <section className={`panel preload-panel developer-panel${compact ? " compact" : ""}`}>
      <span className="developer-label">{t("dev.tools")}</span>
      <div className="preload-title-row">
        <div>
          <h2>{t("dev.buffer")}</h2>
          <p className="preload-note">{t("dev.description")}</p>
        </div>
        <button type="button" onClick={warmup.restartStartup}>
          {t("dev.restart")}
        </button>
      </div>

      <div className="preload-toggle-row">
        <label>
          <input
            type="checkbox"
            checked={settings.startupEnabled}
            onChange={(event) => warmup.setSettings({ startupEnabled: event.target.checked })}
          />
          {t("dev.startupPreload")}
        </label>
        <label>
          <input
            type="checkbox"
            checked={settings.blockStartup}
            onChange={(event) => warmup.setSettings({ blockStartup: event.target.checked })}
          />
          {t("dev.wait")}
        </label>
      </div>

      <div className="preload-grid-controls">
        <NumberField
          label={t("dev.priority")}
          value={settings.maxLeafPositions}
          min={1}
          max={200}
          onChange={(value) => warmup.setSettings({ maxLeafPositions: value })}
          hint={t("dev.priorityHint")}
        />
        <NumberField
          label={t("dev.startupDepth")}
          value={settings.startupDepth}
          min={1}
          max={5}
          onChange={(value) => warmup.setSettings({ startupDepth: value })}
          hint={t("dev.depthHint")}
        />
        <NumberField
          label={t("dev.branches")}
          value={settings.startupBranching}
          min={1}
          max={8}
          onChange={(value) => warmup.setSettings({ startupBranching: value })}
          hint={t("dev.branchesHint")}
        />
        <NumberField
          label={t("dev.threshold")}
          value={settings.nearLeafThreshold}
          min={0}
          max={10}
          onChange={(value) => warmup.setSettings({ nearLeafThreshold: value })}
          hint={t("dev.thresholdHint")}
        />
        <NumberField
          label={t("dev.backgroundDepth")}
          value={settings.backgroundDepth}
          min={1}
          max={5}
          onChange={(value) => warmup.setSettings({ backgroundDepth: value })}
          hint={t("dev.backgroundDepthHint")}
        />
        <NumberField
          label={t("dev.backgroundBranches")}
          value={settings.backgroundBranching}
          min={1}
          max={8}
          onChange={(value) => warmup.setSettings({ backgroundBranching: value })}
          hint={t("dev.backgroundBranchesHint")}
        />
      </div>

      <div className="preload-summary">
        <span>{t("dev.startupEstimate", { count: formatNumber(warmup.estimatedStartupTotal) })}</span>
        <span>
          {t("dev.nearestLeaf", {
            distance: warmup.nearestLeafDistance == null
              ? t("dev.unknown")
              : formatNumber(warmup.nearestLeafDistance),
          })}
        </span>
        <span>{t("dev.backgroundEstimate", { count: formatNumber(warmup.estimatedBackgroundTotal) })}</span>
      </div>

      <ProgressLine label={t("dev.startup")} status={warmup.startup} formatNumber={formatNumber} t={t} />
      <ProgressLine
        label={`${t("dev.background")}${warmup.background?.reason ? ` · ${warmup.background.reason}` : ""}`}
        status={warmup.background}
        formatNumber={formatNumber}
        t={t}
      />

      <div className="preload-actions">
        <button type="button" onClick={warmup.skipStartup} disabled={!warmup.startup?.loading}>
          {t("dev.skip")}
        </button>
        <button type="button" onClick={() => warmup.runBackgroundPreload()} disabled={warmup.background?.loading}>
          {t("dev.fill")}
        </button>
      </div>
    </section>
  );
}
