import { useLocalization } from "../i18n/useLocalization";


export default function SiteFooter() {
  const { t } = useLocalization();

  return (
    <footer className="app-footer">
      {t("footer.text")}
    </footer>
  );
}
