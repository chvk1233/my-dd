import { findEventById } from "@/entities/store-event";
import type { StoreEvent } from "@/entities/store-event";

export function selectCurrentEvent(events: StoreEvent[], selectedEventId: string) {
  return findEventById(events, selectedEventId);
}