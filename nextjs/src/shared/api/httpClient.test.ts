import { afterEach, describe, expect, it, vi } from "vitest";
import { requestJson } from "./httpClient";

vi.mock("@/shared/config/env", () => ({
  API_BASE_URL: "http://test-api.local",
}));

describe("httpClient", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns parsed JSON on success", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ status: "ok" }),
      }),
    );

    await expect(requestJson<{ status: string }>("/health")).resolves.toEqual({ status: "ok" });
    expect(fetch).toHaveBeenCalledWith("http://test-api.local/health", undefined);
  });

  it("throws when response is not ok", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
      }),
    );

    await expect(requestJson("/events")).rejects.toThrow("/events failed");
  });
});
