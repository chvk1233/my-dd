import type { StoreEvent } from "./types";

export function getEventSeverity(event: StoreEvent) {
  return event.severity || event.severity_hint || "low";
}

export function findEventById(events: StoreEvent[], eventId: string) {
  return events.find((event) => event.event_id === eventId) || events[0];
}