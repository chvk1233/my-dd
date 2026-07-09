"use client";

import { useEffect, useMemo, useState } from "react";
import { fallbackEvents, type HealthResponse, type StoreEvent } from "@/entities/store-event";
import { ApiHealthPanel } from "@/features/api-health/ApiHealthPanel";
import { EventDetail } from "@/features/events/event-detail/EventDetail";
import { EventList } from "@/features/events/event-list/EventList";
import { fetchEvents, fetchHealth } from "@/shared/api/opsApi";

export function ApiFetchDashboard() {
  // 상태관리 인데 위치가 바뀔지도?
  // events : 사건 목록(데이터 목록 -> 서버에서 불러올거.)
  //  -> 
  const [events, setEvents] = useState<StoreEvent[]>(fallbackEvents);
  const [selectedEventId, setSelectedEventId] = useState(fallbackEvents[0].event_id);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const selectedEvent = useMemo(
    () => events.find((event) => event.event_id === selectedEventId) || events[0],
    [events, selectedEventId],
  );

  async function load() {
    setLoading(true);
    setError("");

    try {
      const [healthResult, eventsResult] = await Promise.all([fetchHealth(), fetchEvents()]);
      setHealth(healthResult);
      setEvents(eventsResult.events);
      setSelectedEventId(eventsResult.events[0]?.event_id || fallbackEvents[0].event_id);
    } catch {
      setEvents(fallbackEvents);
      setSelectedEventId(fallbackEvents[0].event_id);
      setError("Flask API 연결 실패: mock 사건을 표시합니다.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  return (
    <main className="dashboard">
      <ApiHealthPanel health={health} error={error} />
      <section className="toolbar">
        <button onClick={load} disabled={loading}>{loading ? "불러오는 중" : "API 새로고침"}</button>
      </section>
      <section className="layout">
        <EventList events={events} selectedEventId={selectedEventId} onSelect={setSelectedEventId} />
        <EventDetail event={selectedEvent} />
      </section>
    </main>
  );
}