import { useLocalization } from "../i18n/useLocalization";


export default function MoveControls({
  canGoBack,
  canGoForward,
  onBack,
  onForward,
  onStart,
}) {
  const { t } = useLocalization();

  return (
    <nav className="controls" aria-label={t("moves.navigation")}>
      <button type="button" onClick={onStart} title={t("moves.startTitle")}>
        ⏮ {t("moves.start")}
      </button>

      <button type="button" onClick={onBack} disabled={!canGoBack}>
        ◀ {t("moves.previous")}
      </button>

      <button type="button" onClick={onForward} disabled={!canGoForward}>
        {t("moves.next")} ▶
      </button>
    </nav>
  );
}
