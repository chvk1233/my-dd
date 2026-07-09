import { afterEach, describe, expect, it, vi } from "vitest";

describe("env config", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.resetModules();
  });

  it("uses default API base URL when env is unset", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "");
    const { API_BASE_URL } = await import("./env");
    expect(API_BASE_URL).toBe("http://127.0.0.1:5000");
  });

  it("reads NEXT_PUBLIC_API_BASE_URL from environment", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://localhost:9000");
    const { API_BASE_URL } = await import("./env");
    expect(API_BASE_URL).toBe("http://localhost:9000");
  });
});
