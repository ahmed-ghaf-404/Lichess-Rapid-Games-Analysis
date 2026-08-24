import { useLocalization } from "../i18n/useLocalization";


export default function ErrorState({
  title,
  message,
  detail = "",
}) {
  const { t } = useLocalization();

  return (
    <section className="state-message state-card" role="alert">
      <span className="state-icon" aria-hidden="true">!</span>
      <div>
        <h2>{title || t("common.error")}</h2>
        <p className="error">{message}</p>
        {detail ? <p className="state-detail">{detail}</p> : null}
      </div>
    </section>
  );
}
