import { describe, expect, it } from "vitest";
import { findEventById, getEventSeverity } from "./formatters";
import { fallbackEvents } from "./fallbackEvents";
import type { StoreEvent } from "./types";

describe("formatters", () => {
  it("getEventSeverity returns severity when present", () => {
    expect(getEventSeverity(fallbackEvents[0])).toBe("high");
  });

  it("getEventSeverity falls back to severity_hint then low", () => {
    const event: StoreEvent = {
      event_id: "evt-x",
      event_type: "test",
      channel: "counter",
      severity_hint: "medium",
      status: "mock",
      requires_response: false,
    };
    expect(getEventSeverity(event)).toBe("medium");
  });

  it("findEventById returns matching event", () => {
    expect(findEventById(fallbackEvents, "evt-002")?.event_id).toBe("evt-002");
  });

  it("findEventById returns first event when id is missing", () => {
    expect(findEventById(fallbackEvents, "missing")?.event_id).toBe("evt-001");
  });
});
