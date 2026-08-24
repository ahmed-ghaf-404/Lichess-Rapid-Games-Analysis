import { useLocalization } from "../i18n/useLocalization";


export default function LoadingState({ message, detail = "", children = null }) {
  const { t } = useLocalization();

  return (
    <section className="state-message state-card" aria-live="polite" aria-busy="true">
      <span className="loading-mark" aria-hidden="true" />
      <div>
        <h2>{message || t("common.loading")}</h2>
        {detail ? <p className="state-detail">{detail}</p> : null}
      </div>
      {children}
    </section>
  );
}
