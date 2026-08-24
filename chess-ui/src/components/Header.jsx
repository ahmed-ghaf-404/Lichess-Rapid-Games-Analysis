import { useState } from "react";
import {
  normalizeLichessUsername,
  validateLichessUsername,
} from "../utils/lichessUser";
import { useLocalization } from "../i18n/useLocalization";

export default function Header({
  username,
  gameCount,
  rating,
  loading,
  warmup,
  appMode,
  showDeveloperTools,
  onUsernameChange,
}) {
  const { formatNumber, t } = useLocalization();
  const [draftUsername, setDraftUsername] = useState(username);
  const [validationError, setValidationError] = useState("");
  const startupCount = warmup?.startup?.completed ?? warmup?.completed ?? 0;
  const backgroundCount = warmup?.background?.completed ?? 0;

  function handleSubmit(event) {
    event.preventDefault();

    const nextError = validateLichessUsername(draftUsername);
    setValidationError(nextError);

    if (nextError) return;

    const normalizedUsername = normalizeLichessUsername(draftUsername);
    setDraftUsername(normalizedUsername);

    if (normalizedUsername !== username) {
      onUsernameChange(normalizedUsername);
    }
  }

  return (
    <header className="page-header">
      <div className="header-copy">
        <div className="eyebrow-row">
          <span className="eyebrow">{t("header.eyebrow")}</span>
          {showDeveloperTools ? (
            <span className="mode-badge">{t("header.mode", { mode: appMode })}</span>
          ) : null}
        </div>
        <h1>{t("header.title")}</h1>
        <p className="header-description">{t("header.description")}</p>

        {!loading && gameCount > 0 ? (
          <div className="player-summary" aria-live="polite">
            <span>@{username}</span>
            <span>{t("header.rapidGames", { count: formatNumber(gameCount) })}</span>
            <span>{t("header.rating", { rating: formatNumber(rating) })}</span>
          </div>
        ) : null}
      </div>

      <form className="player-picker" onSubmit={handleSubmit} noValidate>
        <label htmlFor="lichess-username">{t("header.analyzeLabel")}</label>
        <div className="player-picker-row">
          <span className="input-prefix" aria-hidden="true">@</span>
          <input
            id="lichess-username"
            name="username"
            value={draftUsername}
            onChange={(event) => {
              setDraftUsername(event.target.value);
              setValidationError("");
            }}
            autoComplete="off"
            spellCheck="false"
            aria-invalid={Boolean(validationError)}
            aria-describedby={validationError ? "username-error" : "username-hint"}
          />
          <button type="submit" disabled={loading}>
            {loading ? t("header.loading") : t("header.analyze")}
          </button>
        </div>
        {validationError ? (
          <p id="username-error" className="field-error" role="alert">
            {validationError}
          </p>
        ) : (
          <p id="username-hint" className="field-hint">
            {t("header.usernameHint")}
          </p>
        )}
      </form>

      {showDeveloperTools && warmup?.done ? (
        <p className="cache-status">
          {t("header.bufferReady")}
          {startupCount ? ` · ${t("header.startupWarmed", { count: formatNumber(startupCount) })}` : ""}
          {backgroundCount ? ` · ${t("header.backgroundWarmed", { count: formatNumber(backgroundCount) })}` : ""}
          {warmup.error ? ` · ${t("header.warmupWarning", { error: warmup.error })}` : ""}
        </p>
      ) : null}
    </header>
  );
}
