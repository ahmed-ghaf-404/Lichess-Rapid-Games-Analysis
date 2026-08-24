const LEVELS = Object.freeze({
  debug: 10,
  info: 20,
  warn: 30,
  error: 40,
  critical: 50,
  off: Number.POSITIVE_INFINITY,
});

const configuredLevel = String(
  import.meta.env.VITE_LOG_LEVEL || (import.meta.env.DEV ? "debug" : "warn")
).toLowerCase();
const threshold = LEVELS[configuredLevel] ?? LEVELS.info;

export function createRequestId() {
  return globalThis.crypto?.randomUUID?.() ||
    `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;
}

function normalizeContext(context) {
  if (context instanceof Error) {
    return {
      errorName: context.name,
      errorMessage: context.message,
      stack: context.stack,
    };
  }
  return context;
}

function write(level, message, context) {
  if (LEVELS[level] < threshold) return;

  const payload = {
    timestamp: new Date().toISOString(),
    level,
    service: "chess-ui",
    message,
    ...(context === undefined ? {} : { context: normalizeContext(context) }),
  };
  const consoleMethod = level === "critical" ? "error" : level;
  console[consoleMethod](payload);
}

export const logger = Object.freeze({
  debug: (message, context) => write("debug", message, context),
  info: (message, context) => write("info", message, context),
  warn: (message, context) => write("warn", message, context),
  error: (message, context) => write("error", message, context),
  critical: (message, context) => write("critical", message, context),
});
