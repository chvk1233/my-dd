import { getEventSeverity, type StoreEvent } from "@/entities/store-event";

type EventListProps = { events: StoreEvent[]; selectedEventId: string; onSelect: (eventId: string) => void };

export function EventList({ events, selectedEventId, onSelect }: EventListProps) {
  return <div className="panel">
    <h2>사건 목록</h2>{events.map((event) => { const severity = getEventSeverity(event); 
    return <button key={event.event_id} className={`eventButton ${selectedEventId === event.event_id ? "selected" : ""}`} onClick={() => onSelect(event.event_id)}><strong>{event.event_id}</strong><span>{event.event_type}</span><span className={`badge ${severity}`}>{severity}</span></button>; })}</div>;
}
