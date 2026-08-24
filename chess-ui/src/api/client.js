import { createRequestId, logger } from "../utils/logger";

export const API_BASE_URL = import.meta.env.VITE_GAMES_API_URL || "/games";

export async function apiGet(path) {
  const url = `${API_BASE_URL}${path}`;
  const requestId = createRequestId();
  logger.debug("Games API request started", { requestId, method: "GET", path });
  let response;
  try {
    response = await fetch(url, { headers: { "X-Request-ID": requestId } });
  } catch (error) {
    logger.error("Games API network request failed", { requestId, path, error: error.message });
    throw error;
  }

  if (!response.ok) {
    const level = response.status >= 500 ? "error" : "warn";
    logger[level]("Games API request rejected", { requestId, path, status: response.status });
    throw new Error(`Request failed: ${response.status}`);
  }

  const json = await response.json();
  logger.info("Games API request completed", {
    path,
    requestId: response.headers.get("X-Request-ID") || requestId,
    status: response.status,
    itemCount: Array.isArray(json) ? json.length : undefined,
  });
  return json;
}
