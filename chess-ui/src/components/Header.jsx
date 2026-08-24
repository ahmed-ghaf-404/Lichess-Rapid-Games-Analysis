import { useState } from "react";
import {
  normalizeLichessUsername,
  validateLichessUsername,
} from "../utils/lichessUser";

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
          <span className="eyebrow">CCC · Opening intelligence</span>
          {showDeveloperTools ? (
            <span className="mode-badge">{appMode} view</span>
          ) : null}
        </div>
        <h1>Choco Chess Coach</h1>
        <p className="header-description">
          Turn a player’s rapid-game history into an opening map and practical,
          engine-informed recommendations.
        </p>

        {!loading && gameCount > 0 ? (
          <div className="player-summary" aria-live="polite">
            <span>@{username}</span>
            <span>{gameCount} rapid games</span>
            <span>{rating} rating</span>
          </div>
        ) : null}
      </div>

      <form className="player-picker" onSubmit={handleSubmit} noValidate>
        <label htmlFor="lichess-username">Analyze a Lichess player</label>
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
            {loading ? "Loading…" : "Analyze"}
          </button>
        </div>
        {validationError ? (
          <p id="username-error" className="field-error" role="alert">
            {validationError}
          </p>
        ) : (
          <p id="username-hint" className="field-hint">
            Try any player whose games have been imported.
          </p>
        )}
      </form>

      {showDeveloperTools && warmup?.done ? (
        <p className="cache-status">
          Analysis buffer ready
          {startupCount ? ` · ${startupCount} startup positions warmed` : ""}
          {backgroundCount ? ` · ${backgroundCount} background positions warmed` : ""}
          {warmup.error ? ` · Warmup warning: ${warmup.error}` : ""}
        </p>
      ) : null}
    </header>
  );
}
