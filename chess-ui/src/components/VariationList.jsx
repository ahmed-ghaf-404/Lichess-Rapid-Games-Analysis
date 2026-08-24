import { memo } from "react";
import { useLocalization } from "../i18n/useLocalization";


function VariationList({ childrenNodes, sideToMove, onSelect }) {
  const { formatNumber, t } = useLocalization();

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <span className="panel-kicker">{t("variations.history")}</span>
          <h2>{t("variations.popular")}</h2>
        </div>
        <span className="turn-badge">
          {t(sideToMove === "white" ? "recommendation.turnWhite" : "recommendation.turnBlack")}
        </span>
      </div>

      {childrenNodes.length === 0 ? (
        <p>{t("variations.none")}</p>
      ) : (
        <div className="variation-list">
          {childrenNodes.map((node) => (
            <button
              key={node.id}
              type="button"
              className="variation-button"
              onClick={() => onSelect(node.id)}
            >
              <span className="candidate-move chess-notation">{node.san}</span>
              <span className="variation-count">
                {t("variations.games", { count: formatNumber(node.visitCount) })}
              </span>
            </button>
          ))}
        </div>
      )}
    </section>
  );
}

export default memo(VariationList);
