import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "@fontsource-variable/noto-sans/wght.css";
import "@fontsource-variable/noto-serif/wght.css";
import "@fontsource-variable/noto-sans-arabic/wght.css";
import "@fontsource-variable/noto-sans-jp/wght.css";
import "./index.css";
import App from "./App";
import { LocalizationProvider } from "./i18n/Localization";
import { logger } from "./utils/logger";

logger.info("UI starting", { mode: import.meta.env.MODE });

window.addEventListener("error", (event) => {
  logger.error("Unhandled browser error", event.error || { message: event.message });
});

window.addEventListener("unhandledrejection", (event) => {
  logger.critical("Unhandled promise rejection", event.reason);
});

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <LocalizationProvider>
      <App />
    </LocalizationProvider>
  </StrictMode>
);
