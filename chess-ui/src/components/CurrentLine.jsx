import { useLocalization } from "../i18n/useLocalization";


export default function CurrentLine({ line, fen, showFen = false }) {
  const { formatNumber, t } = useLocalization();

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <span className="panel-kicker">{t("line.position")}</span>
          <h2>{t("line.current")}</h2>
        </div>
        <span className="ply-count">{t("line.ply", { count: formatNumber(line.length) })}</span>
      </div>

      {line.length ? (
        <div className="move-sequence chess-notation" aria-label={t("line.sequence")}>
          {line.map((node, index) => (
            <span className="move-token" key={node.id}>
              {index % 2 === 0 ? `${Math.floor(index / 2) + 1}. ` : ""}
              {node.san}
            </span>
          ))}
        </div>
      ) : (
        <p className="empty-copy">{t("line.empty")}</p>
      )}

      {showFen ? (
        <details className="developer-details">
          <summary>{t("line.fen")}</summary>
          <code className="fen-text">{fen}</code>
        </details>
      ) : null}
    </section>
  );
}
