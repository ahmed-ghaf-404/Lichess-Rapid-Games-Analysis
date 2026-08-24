import { SUPPORTED_LOCALES } from "../i18n/locales";
import { useLocalization } from "../i18n/useLocalization";


export default function LanguageSwitcher() {
  const { locale, setLocale, t } = useLocalization();

  return (
    <label className="language-switcher">
      <span className="visually-hidden">{t("language.label")}</span>
      <select
        value={locale}
        onChange={(event) => setLocale(event.target.value)}
        aria-label={t("language.label")}
      >
        {SUPPORTED_LOCALES.map((option) => (
          <option key={option.id} value={option.id}>
            {option.flag} {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}
