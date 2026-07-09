import { describe, expect, it } from "vitest";
import { fallbackEvents } from "./fallbackEvents";

describe("fallbackEvents", () => {
  it("provides mock events with required fields", () => {
    expect(fallbackEvents.length).toBeGreaterThan(0);
    for (const event of fallbackEvents) {
      expect(event.event_id).toBeTruthy();
      expect(event.event_type).toBeTruthy();
      expect(event.channel).toBeTruthy();
      expect(event.status).toBe("mock");
      expect(event.requires_response).toBe(true);
    }
  });

  it("includes distinct event ids", () => {
    const ids = fallbackEvents.map((event) => event.event_id);
    expect(new Set(ids).size).toBe(ids.length);
  });
});
