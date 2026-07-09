"use client";

import { useEffect } from "react";
import { ApiHealthPanel } from "@/features/api-health/ApiHealthPanel";
import { EventAnalysisPanel } from "@/features/events/event-analysis/EventAnalysisPanel";
import { EventDetail } from "@/features/events/event-detail/EventDetail";
import { IngestEventForm } from "@/features/events/event-ingest/IngestEventForm";
import { EventList } from "@/features/events/event-list/EventList";
import { LocalChatPanel } from "@/features/rag-chat/LocalChatPanel";
import { selectCurrentEvent } from "@/store/selectors";
import { useOpsStore } from "@/store/useOpsStore";

export function ZustandDashboard() {
  const store = useOpsStore();
  const selectedEvent = selectCurrentEvent(store.events, store.selectedEventId);

  useEffect(() => {
    void useOpsStore.getState().loadDashboard();
  }, []);

  return (
    <main className="dashboard">
      <ApiHealthPanel health={store.health} error={store.error} />
      <section className="toolbar">
        <button type="button" onClick={() => void store.loadDashboard()} disabled={store.loading}>
          {store.loading ? "불러오는 중" : "API 새로고침"}
        </button>
        <IngestEventForm disabled={store.loading} onSubmit={store.ingestEvent} />
      </section>
      <section className="layout">
        <EventList
          events={store.events}
          selectedEventId={store.selectedEventId}
          onSelect={store.selectEvent}
        />
        <div>
          <EventDetail event={selectedEvent} />
          <EventAnalysisPanel analysis={store.analysis} event={selectedEvent} />
        </div>
      </section>
      <section className="panel">
        <h2>LLM 활용 결과</h2>
        <div className="inlineForm">
          <button type="button" disabled={store.loading} onClick={() => void store.loadReport()}>
            점장 보고서 (/report)
          </button>
          <button type="button" disabled={store.loading} onClick={() => void store.loadTasks()}>
            직원 체크리스트 (/tasks)
          </button>
        </div>
        {store.report && (
          <>
            <h3>보고서</h3>
            <pre>{store.report}</pre>
          </>
        )}
        {store.tasks && (
          <>
            <h3>체크리스트</h3>
            <pre>{store.tasks}</pre>
          </>
        )}
      </section>
      <LocalChatPanel
        answer={store.chatAnswer}
        sources={store.chatSources}
        loading={store.loading}
        onAsk={store.askChat}
      />
    </main>
  );
}
