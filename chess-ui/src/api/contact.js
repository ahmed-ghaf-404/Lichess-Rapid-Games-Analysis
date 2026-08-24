import { API_BASE_URL } from "./client";
import { createRequestId, logger } from "../utils/logger";


async function contactRequest(path, options = {}) {
  const requestId = createRequestId();
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        "X-Request-ID": requestId,
        ...options.headers,
      },
    });
  } catch (error) {
    logger.error("Contact API network request failed", { requestId, error });
    throw new Error("The contact service is unavailable. Please try again later.");
  }

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    logger.warn("Contact API request rejected", {
      requestId: response.headers.get("X-Request-ID") || requestId,
      status: response.status,
    });
    throw new Error(body.detail || "The message could not be sent.");
  }

  return body;
}


export function fetchContactChallenge() {
  return contactRequest("/contact/challenge", { method: "GET", headers: {} });
}


export function sendContactMessage(payload) {
  return contactRequest("/contact", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
