import { useLocalization } from "../i18n/useLocalization";
import LanguageSwitcher from "./LanguageSwitcher";


const NAV_ITEMS = [
  { href: "/", labelKey: "nav.explorer" },
  { href: "/about", labelKey: "nav.about" },
  { href: "/history", labelKey: "nav.history" },
  { href: "/contact", labelKey: "nav.contact" },
];


export default function SiteNavigation({ activePath = window.location.pathname }) {
  const { t } = useLocalization();

  return (
    <nav className="site-navigation" aria-label={t("nav.primary")}>
      <a className="site-brand" href="/" aria-label={t("nav.home")}>
        <span className="site-brand-mark">CCC</span>
        <span>Choco Chess Coach</span>
      </a>

      <div className="site-navigation-actions">
        <div className="site-navigation-links">
          {NAV_ITEMS.map((item) => (
            <a
              key={item.href}
              href={item.href}
              aria-current={activePath === item.href ? "page" : undefined}
            >
              {t(item.labelKey)}
            </a>
          ))}
        </div>
        <LanguageSwitcher />
      </div>
    </nav>
  );
}
