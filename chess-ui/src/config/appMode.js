export function getAppMode(env = import.meta.env) {
  const configuredMode = env.VITE_APP_MODE?.toLowerCase();

  if (configuredMode === "development" || configuredMode === "production") {
    return configuredMode;
  }

  return env.DEV ? "development" : "production";
}

export function shouldShowDeveloperTools(env = import.meta.env) {
  return (
    getAppMode(env) === "development" ||
    env.VITE_SHOW_DEVELOPER_TOOLS === "true"
  );
}

export function shouldShowCurrentLine(env = import.meta.env) {
  return getAppMode(env) === "development";
}
