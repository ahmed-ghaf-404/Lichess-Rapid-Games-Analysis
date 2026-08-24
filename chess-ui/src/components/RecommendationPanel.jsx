import { memo } from "react";
import { useLocalization } from "../i18n/useLocalization";


const REASON_KEYS = {
  "large peer sample": "reason.largePeerSample",
  "reasonable peer sample": "reason.reasonablePeerSample",
  "small peer sample": "reason.smallPeerSample",
  "common at your rating": "reason.commonAtRating",
  "played often in this pool": "reason.playedOften",
  "strong peer win rate": "reason.strongWinRate",
  "solid practical results": "reason.solidResults",
  "top engine move": "reason.topEngine",
  "engine-approved": "reason.engineApproved",
  "fits your repertoire": "reason.fitsRepertoire",
  "close to your repertoire": "reason.closeRepertoire",
};


function RecommendationPanel({
  sideToMove,
  recommendation,
  recommendationsEnabled = true,
  loading,
  error,
  onRecommendationsEnabledChange,
  onMoveHover,
  onMoveLeave,
  onMoveSelect,
}) {
  const { formatNumber, metadata, t } = useLocalization();
  const title = t(sideToMove === "white" ? "recommendation.turnWhite" : "recommendation.turnBlack");
  const heading = (showBadge = false) => (
    <div className="panel-heading">
      <div>
        <span className="panel-kicker">{t("recommendation.kicker")}</span>
        <h2>{title}</h2>
      </div>
      <div className="recommendation-heading-actions">
        {showBadge ? <span className="coach-badge">{t("recommendation.bestPractical")}</span> : null}
        <label className="recommendation-toggle">
          <input
            type="checkbox"
            checked={recommendationsEnabled}
            onChange={(event) => onRecommendationsEnabledChange?.(event.target.checked)}
          />
          {t("recommendation.compute")}
        </label>
      </div>
    </div>
  );

  if (!recommendationsEnabled) {
    return (
      <section className="panel recommendation-panel recommendation-disabled">
        {heading()}
        <p className="empty-copy">{t("recommendation.paused")}</p>
      </section>
    );
  }

  if (loading) {
    return (
      <section className="panel recommendation-panel" aria-busy="true">
        {heading()}
        <div className="recommendation-skeleton" aria-label={t("recommendation.loading")} />
      </section>
    );
  }

  if (error) {
    return (
      <section className="panel recommendation-panel">
        {heading()}
        <p className="error">{error}</p>
      </section>
    );
  }

  if (!recommendation || !recommendation.candidates?.length) {
    return (
      <section className="panel recommendation-panel">
        {heading()}
        <p className="empty-copy">{t("recommendation.none")}</p>
      </section>
    );
  }

  const [top, ...rest] = recommendation.candidates;

  return (
    <section className="panel recommendation-panel">
      {heading(true)}

      <button
        type="button"
        className="recommendation-hero"
        onMouseEnter={() => onMoveHover?.(top)}
        onMouseLeave={onMoveLeave}
        onClick={() => onMoveSelect?.(top)}
        title={t("recommendation.click")}
      >
        <span className="recommendation-label">{t("recommendation.move")}</span>
        <span className="recommendation-move chess-notation">{top.move_san}</span>
        <span className="recommendation-meta">
          {t("recommendation.score", {
            score: formatNumber(top.score),
            count: formatNumber(top.peer_games),
          })}
        </span>
        <span className="play-hint" aria-hidden="true">
          {t("recommendation.play")} <span>{metadata.direction === "rtl" ? "←" : "→"}</span>
        </span>
      </button>

      <div className="reason-block">
        <span className="section-label">{t("recommendation.why")}</span>

        {top.reasons?.length ? (
          <ul className="reason-list">
            {top.reasons.map((reason) => (
              <li key={reason}>{REASON_KEYS[reason] ? t(REASON_KEYS[reason]) : reason}</li>
            ))}
          </ul>
        ) : (
          <p className="empty-copy">{t("recommendation.noExplanation")}</p>
        )}
      </div>

      {rest.length ? <div>
        <span className="section-label candidate-heading">{t("recommendation.other")}</span>

        <div className="variation-list">
          {rest.slice(0, 3).map((move) => {
            const evaluation = Number.isFinite(move.engine_eval_cp)
              ? (sideToMove === "white"
                ? move.engine_eval_cp / 100
                : move.engine_eval_cp / -100).toFixed(2)
              : "—";
            const winRate = Number.isFinite(move.peer_frequency)
              ? `${Math.round(move.peer_frequency * 100)}%`
              : "—";

            return (
              <button
                key={move.move_uci}
                type="button"
                className="variation-button candidate-button"
                onMouseEnter={() => onMoveHover?.(move)}
                onMouseLeave={onMoveLeave}
                onClick={() => onMoveSelect?.(move)}
                title={t("recommendation.click")}
              >
                <span className="candidate-move chess-notation">{move.move_san}</span>
                <span className="variation-count">
                  {t("recommendation.candidateMeta", {
                    evaluation,
                    frequency: winRate,
                    count: formatNumber(move.peer_games),
                  })}
                </span>
              </button>
            );
          })}
        </div>
      </div> : null}
    </section>
  );
}

export default memo(RecommendationPanel);
