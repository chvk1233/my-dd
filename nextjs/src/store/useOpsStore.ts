import { create } from "zustand";
import {
  fallbackEvents,
  findEventById,
  type AnalysisResult,
  type HealthResponse,
  type IngestPayload,
  type StoreEvent,
} from "@/entities/store-event";
import {
  fetchChat,
  fetchEventAnalysis,
  fetchEvents,
  fetchHealth,
  fetchReport,
  fetchTasks,
  ingestEvent as postIngest,
} from "@/shared/api/opsApi";

type OpsState = {
  events: StoreEvent[];
  selectedEventId: string;
  health: HealthResponse | null;
  analysis: AnalysisResult | null;
  loading: boolean;
  error: string;
  report: string;
  tasks: string;
  chatAnswer: string;
  chatSources: string[];
  loadDashboard: () => Promise<void>;
  loadEvents: () => Promise<void>;
  loadAnalysis: () => Promise<void>;
  ingestEvent: (payload: IngestPayload) => Promise<void>;
  loadReport: () => Promise<void>;
  loadTasks: () => Promise<void>;
  askChat: (question: string) => Promise<void>;
  selectEvent: (eventId: string) => void;
};

function analysisFromEvent(eventId: string): AnalysisResult {
  const event = findEventById(fallbackEvents, eventId);
  return {
    predicted_type: event.predicted_type || event.event_type,
    severity: event.severity || event.severity_hint,
    confidence: event.confidence,
    source: "mock",
  };
}

export const useOpsStore = create<OpsState>((set, get) => ({
  events: fallbackEvents,
  selectedEventId: fallbackEvents[0].event_id,
  health: null,
  analysis: analysisFromEvent(fallbackEvents[0].event_id),
  loading: false,
  error: "",
  report: "",
  tasks: "",
  chatAnswer: "",
  chatSources: [],

  async loadDashboard() {
    set({ loading: true, error: "" });
    try {
      const [healthResult, eventsResult] = await Promise.all([fetchHealth(), fetchEvents()]);
      const selectedEventId = eventsResult.events[0]?.event_id || fallbackEvents[0].event_id;
      set({
        health: healthResult,
        events: eventsResult.events,
        selectedEventId,
        error: "",
      });
      await get().loadAnalysis();
    } catch {
      set({
        health: null,
        events: fallbackEvents,
        selectedEventId: fallbackEvents[0].event_id,
        analysis: analysisFromEvent(fallbackEvents[0].event_id),
        error: "API 연결 실패: mock 사건을 표시합니다.",
      });
    } finally {
      set({ loading: false });
    }
  },

  async loadEvents() {
    await get().loadDashboard();
  },

  async loadAnalysis() {
    const { selectedEventId } = get();
    try {
      const result = await fetchEventAnalysis(selectedEventId);
      set({ analysis: result.analysis });
    } catch {
      set({ analysis: analysisFromEvent(selectedEventId) });
    }
  },

  async ingestEvent(payload: IngestPayload) {
    set({ loading: true, error: "" });
    try {
      await postIngest(payload);
      await get().loadDashboard();
    } catch {
      set({ error: "사건 접수 실패: Flask /ingest API를 확인하세요." });
    } finally {
      set({ loading: false });
    }
  },

  async loadReport() {
    const { selectedEventId } = get();
    set({ loading: true });
    try {
      const result = await fetchReport({ event_id: selectedEventId });
      set({ report: result.result });
    } catch {
      set({ report: `mock 보고서: ${selectedEventId} 사건에 대한 점장 보고서를 생성할 수 없습니다.` });
    } finally {
      set({ loading: false });
    }
  },

  async loadTasks() {
    const { selectedEventId } = get();
    set({ loading: true });
    try {
      const result = await fetchTasks({ event_id: selectedEventId });
      set({ tasks: result.result });
    } catch {
      set({
        tasks: `mock 체크리스트 (${selectedEventId}):\n1. 고객 응대 내용 확인\n2. 환불 정책 매뉴얼 검토\n3. 후속 조치 기록`,
      });
    } finally {
      set({ loading: false });
    }
  },

  async askChat(question: string) {
    const { selectedEventId } = get();
    set({ loading: true });
    try {
      const result = await fetchChat({ question, event_id: selectedEventId });
      set({
        chatAnswer: result.answer || "답변을 받지 못했습니다.",
        chatSources: result.sources || [],
      });
    } catch {
      set({
        chatAnswer: `mock 답변: "${question}" — 운영 매뉴얼·환불 정책 문서를 확인하세요.`,
        chatSources: ["운영 매뉴얼 (mock)", "환불 정책 (mock)"],
      });
    } finally {
      set({ loading: false });
    }
  },

  selectEvent(eventId) {
    set({ selectedEventId: eventId, report: "", tasks: "" });
    void get().loadAnalysis();
  },
}));
