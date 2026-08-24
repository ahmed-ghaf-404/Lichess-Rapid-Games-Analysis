import { describe, expect, it } from "vitest";

import {
  getAppMode,
  shouldShowCurrentLine,
  shouldShowDeveloperTools,
} from "./appMode";


describe("app mode", () => {
  it("uses Vite's development flag when no mode is configured", () => {
    expect(getAppMode({ DEV: true })).toBe("development");
    expect(getAppMode({ DEV: false })).toBe("production");
  });

  it("allows an explicit production build to hide developer panels", () => {
    const env = { DEV: true, VITE_APP_MODE: "production" };

    expect(getAppMode(env)).toBe("production");
    expect(shouldShowDeveloperTools(env)).toBe(false);
  });

  it("supports an explicit developer-tools override", () => {
    const env = {
      DEV: false,
      VITE_APP_MODE: "production",
      VITE_SHOW_DEVELOPER_TOOLS: "true",
    };

    expect(shouldShowDeveloperTools(env)).toBe(true);
    expect(shouldShowCurrentLine(env)).toBe(false);
  });

  it("shows the current line only in development mode", () => {
    expect(shouldShowCurrentLine({ DEV: true })).toBe(true);
    expect(
      shouldShowCurrentLine({
        DEV: false,
        VITE_APP_MODE: "production",
        VITE_SHOW_DEVELOPER_TOOLS: "true",
      })
    ).toBe(false);
  });
});
