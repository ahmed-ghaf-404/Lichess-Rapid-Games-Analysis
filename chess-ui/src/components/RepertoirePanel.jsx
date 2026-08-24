import { memo, useCallback, useEffect, useMemo, useState } from "react";

import {
  analyzeRepertoireDivergence,
  buildRepertoireTree,
  suggestRepertoireLineName,
} from "../utils/repertoire";
import { useLocalization } from "../i18n/useLocalization";


function LineTree({ nodes, depth = 0, activeLineId, onSelect, formatNumber, t }) {
  if (!nodes.length) return null;

  return (
    <ul className="repertoire-tree">
      {nodes.map((line) => (
        <li key={line.id} style={{ "--repertoire-depth": depth }}>
          <button
            type="button"
            className={line.id === activeLineId ? "active" : ""}
            onClick={() => onSelect(line.id)}
          >
            <span>{line.name}</span>
            <small>{t("repertoire.savedMoves", { count: formatNumber(line.moves.length) })}</small>
          </button>
          <LineTree
            nodes={line.children}
            depth={depth + 1}
            activeLineId={activeLineId}
            onSelect={onSelect}
            formatNumber={formatNumber}
            t={t}
          />
        </li>
      ))}
    </ul>
  );
}


function RepertoirePanel({
  username,
  games,
  openingName,
  recommendation,
  repertoire,
  onMoveHover,
  onMoveLeave,
  onMoveSelect,
}) {
  const { formatNumber, t } = useLocalization();
  const getSuggestedLineName = useCallback(
    (name) => suggestRepertoireLineName(
      name,
      (family) => t("repertoire.suggestedName", { opening: family })
    ),
    [t]
  );
  const [activeLineId, setActiveLineId] = useState("");
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [lineName, setLineName] = useState(() => getSuggestedLineName(openingName));
  const [lineOpening, setLineOpening] = useState(openingName);
  const [parentLineId, setParentLineId] = useState("");
  const [writeKey, setWriteKey] = useState(
    () => window.sessionStorage.getItem("ccc-repertoire-key") || ""
  );
  const [statusMessage, setStatusMessage] = useState("");
  const [actionError, setActionError] = useState("");
  const [saving, setSaving] = useState(false);

  const lineTree = useMemo(() => buildRepertoireTree(repertoire.lines), [repertoire.lines]);
  const activeLine = repertoire.lines.find((line) => line.id === activeLineId) || null;
  const divergence = useMemo(
    () => analyzeRepertoireDivergence(games, repertoire.lines, username),
    [games, repertoire.lines, username]
  );

  useEffect(() => {
    if (!activeLineId && repertoire.lines.length) {
      setActiveLineId(repertoire.lines[0].id);
    } else if (
      activeLineId &&
      !repertoire.lines.some((line) => line.id === activeLineId)
    ) {
      setActiveLineId(repertoire.lines[0]?.id || "");
    }
  }, [activeLineId, repertoire.lines]);

  useEffect(() => {
    if (!showCreateForm) {
      setLineOpening(openingName);
      setLineName(getSuggestedLineName(openingName));
    }
  }, [getSuggestedLineName, openingName, showCreateForm]);

  function rememberWriteKey(value) {
    setWriteKey(value);
    if (value) window.sessionStorage.setItem("ccc-repertoire-key", value);
    else window.sessionStorage.removeItem("ccc-repertoire-key");
  }

  async function runAction(action, successMessage) {
    if (!writeKey) {
      setActionError(t("repertoire.needKey"));
      return;
    }
    setSaving(true);
    setActionError("");
    setStatusMessage("");
    try {
      await action();
      setStatusMessage(successMessage);
    } catch (error) {
      setActionError(error.message);
    } finally {
      setSaving(false);
    }
  }

  async function handleCreateLine(event) {
    event.preventDefault();
    await runAction(
      async () => {
        const created = await repertoire.createLine(
          {
            name: lineName,
            opening_name: lineOpening,
            parent_line_id: parentLineId || null,
          },
          writeKey
        );
        setActiveLineId(created.id);
        setShowCreateForm(false);
        setParentLineId("");
      },
      t("repertoire.created")
    );
  }

  function handleApprove(move) {
    if (!activeLineId) {
      setActionError(t("repertoire.needLine"));
      return;
    }
    runAction(
      () => repertoire.approveMove(activeLineId, move, writeKey),
      t("repertoire.added", {
        move: move.move_san,
        line: activeLine?.name || t("repertoire.theRepertoire"),
      })
    );
  }

  function handleDeleteMove(move) {
    runAction(
      () => repertoire.deleteMove(move.lineId, move.id, writeKey),
      t("repertoire.removed", { move: move.move_san })
    );
  }

  function handleDeleteLine() {
    if (!activeLine) return;
    runAction(
      () => repertoire.deleteLine(activeLine.id, writeKey),
      t("repertoire.deleted", { line: activeLine.name })
    );
  }

  const approvedUcis = new Set(repertoire.currentMoves.map((move) => move.move_uci));

  return (
    <section className="panel repertoire-panel">
      <div className="panel-heading">
        <div>
          <span className="panel-kicker repertoire-kicker">{t("repertoire.saved")}</span>
          <h2>{t("repertoire.title", { username })}</h2>
        </div>
        <span className="repertoire-badge">{t("repertoire.persisted")}</span>
      </div>

      {repertoire.loading ? <p className="muted-text">{t("repertoire.loading")}</p> : null}
      {repertoire.error ? <p className="error">{repertoire.error}</p> : null}

      <div className="repertoire-toolbar">
        <label>
          {t("repertoire.active")}
          <select value={activeLineId} onChange={(event) => setActiveLineId(event.target.value)}>
            <option value="">{t("repertoire.select")}</option>
            {repertoire.lines.map((line) => (
              <option key={line.id} value={line.id}>{line.name}</option>
            ))}
          </select>
        </label>
        <button type="button" onClick={() => setShowCreateForm((value) => !value)}>
          {showCreateForm ? t("repertoire.cancel") : t("repertoire.new")}
        </button>
      </div>

      {showCreateForm ? (
        <form className="repertoire-create-form" onSubmit={handleCreateLine}>
          <label>
            {t("repertoire.lineName")}
            <input value={lineName} onChange={(event) => setLineName(event.target.value)} minLength="3" maxLength="100" required />
          </label>
          <label>
            {t("repertoire.openingName")}
            <input value={lineOpening} onChange={(event) => setLineOpening(event.target.value)} minLength="2" maxLength="150" required />
          </label>
          <label>
            {t("repertoire.parent")}
            <select value={parentLineId} onChange={(event) => setParentLineId(event.target.value)}>
              <option value="">{t("repertoire.topLevel")}</option>
              {repertoire.lines.map((line) => (
                <option key={line.id} value={line.id}>{line.name}</option>
              ))}
            </select>
          </label>
          <button type="submit" disabled={saving}>{t("repertoire.create")}</button>
        </form>
      ) : null}

      <label className="repertoire-key-field">
        {t("repertoire.key")}
        <input
          type="password"
          value={writeKey}
          onChange={(event) => rememberWriteKey(event.target.value)}
          autoComplete="off"
          placeholder={t("repertoire.keyPlaceholder")}
        />
      </label>

      <div className="repertoire-section">
        <span className="section-label">{t("repertoire.positionMoves")}</span>
        {repertoire.currentMoves.length ? (
          <div className="repertoire-move-list">
            {repertoire.currentMoves.map((move) => (
              <div className="repertoire-move" key={`${move.lineId}-${move.id}`}>
                <button
                  type="button"
                  className="repertoire-play"
                  onMouseEnter={() => onMoveHover?.(move)}
                  onMouseLeave={onMoveLeave}
                  onClick={() => onMoveSelect?.(move)}
                >
                  <strong className="chess-notation">{move.move_san}</strong>
                  <span>{move.lineName}</span>
                </button>
                <button type="button" className="repertoire-remove" onClick={() => handleDeleteMove(move)} disabled={saving}>
                  {t("repertoire.remove")}
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p className="empty-copy">{t("repertoire.noMove")}</p>
        )}
      </div>

      {recommendation?.candidates?.length ? (
        <div className="repertoire-section">
          <span className="section-label">{t("repertoire.approve")}</span>
          <div className="repertoire-candidate-list">
            {recommendation.candidates.slice(0, 4).map((move) => (
              <button
                key={move.move_uci}
                type="button"
                disabled={saving || approvedUcis.has(move.move_uci)}
                onClick={() => handleApprove(move)}
              >
                <span className="chess-notation">{move.move_san}</span>
                <small>{approvedUcis.has(move.move_uci)
                  ? t("repertoire.alreadySaved")
                  : t("repertoire.addTo", { line: activeLine?.name || t("repertoire.selectedLine") })}</small>
              </button>
            ))}
          </div>
        </div>
      ) : null}

      <details className="repertoire-library">
        <summary>{t("repertoire.library", { count: formatNumber(repertoire.lines.length) })}</summary>
        {lineTree.length ? (
          <LineTree
            nodes={lineTree}
            activeLineId={activeLineId}
            onSelect={setActiveLineId}
            formatNumber={formatNumber}
            t={t}
          />
        ) : (
          <p className="empty-copy">{t("repertoire.emptyLibrary")}</p>
        )}
        {activeLine ? (
          <button type="button" className="danger-button" onClick={handleDeleteLine} disabled={saving}>
            {t("repertoire.deleteLine")}
          </button>
        ) : null}
      </details>

      <details className="repertoire-divergence">
        <summary>
          {t("repertoire.divergence", {
            divergent: formatNumber(divergence.divergenceCount),
            total: formatNumber(divergence.gamesWithRepertoirePositions),
          })}
        </summary>
        <p className="muted-text">
          {t("repertoire.aligned", { count: formatNumber(divergence.alignedCount) })}
        </p>
        {divergence.divergences.slice(0, 8).map((item) => (
          <div className="divergence-item" key={`${item.gameId}-${item.ply}`}>
            <strong>{item.openingName}</strong>
            <span>
              {t("repertoire.divergenceItem", {
                move: item.playedSan,
                ply: formatNumber(item.ply),
                saved: item.approvedMoves.join(" / "),
              })}
            </span>
          </div>
        ))}
      </details>

      {statusMessage ? <p className="form-success" role="status">{statusMessage}</p> : null}
      {actionError ? <p className="error" role="alert">{actionError}</p> : null}
    </section>
  );
}

export default memo(RepertoirePanel);
