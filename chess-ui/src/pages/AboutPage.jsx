import SiteFooter from "../components/SiteFooter";
import SiteNavigation from "../components/SiteNavigation";
import { useLocalization } from "../i18n/useLocalization";


export default function AboutPage() {
  const { t } = useLocalization();

  return (
    <main className="app-shell content-page-shell">
      <SiteNavigation activePath="/about" />

      <article className="content-page">
        <header className="content-page-header">
          <span className="eyebrow">{t("about.eyebrow")}</span>
          <h1>{t("about.title")}</h1>
          <p>{t("about.intro")}</p>
        </header>

        <div className="content-card-grid">
          <section className="content-card">
            <h2>{t("about.whyTitle")}</h2>
            <p>{t("about.why")}</p>
          </section>

          <section className="content-card">
            <h2>{t("about.howTitle")}</h2>
            <p>{t("about.how")}</p>
          </section>

          <section className="content-card">
            <h2>{t("about.whoTitle")}</h2>
            <p>{t("about.who")}</p>
          </section>
        </div>
      </article>

      <SiteFooter />
    </main>
  );
}
