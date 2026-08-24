import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App";
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
    <App />
  </StrictMode>
);
