import SiteFooter from "../components/SiteFooter";
import SiteNavigation from "../components/SiteNavigation";
import { DEVELOPMENT_HISTORY } from "../content/developmentHistory";
import { useLocalization } from "../i18n/useLocalization";


export default function DevelopmentHistoryPage() {
  const { formatDate, t } = useLocalization();

  return (
    <main className="app-shell content-page-shell">
      <SiteNavigation activePath="/history" />

      <article className="content-page">
        <header className="content-page-header">
          <span className="eyebrow">{t("history.eyebrow")}</span>
          <h1>{t("history.title")}</h1>
          <p>{t("history.intro")}</p>
        </header>

        <ol className="history-timeline">
          {DEVELOPMENT_HISTORY.map((entry, index) => (
            <li key={`${entry.date}-${entry.titleKey}-${index}`}>
              <time dateTime={entry.date}>
                {formatDate(new Date(`${entry.date}T00:00:00Z`), {
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                  timeZone: "UTC",
                })}
              </time>
              <div className="history-entry">
                <h2>{t(entry.titleKey)}</h2>
                <ul>
                  {entry.detailKeys.map((detailKey) => <li key={detailKey}>{t(detailKey)}</li>)}
                </ul>
              </div>
            </li>
          ))}
        </ol>
      </article>

      <SiteFooter />
    </main>
  );
}
