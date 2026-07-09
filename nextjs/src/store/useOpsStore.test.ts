import { beforeEach, describe, expect, it, vi } from "vitest";
import { fallbackEvents } from "@/entities/store-event";
import {
  fetchChat,
  fetchEventAnalysis,
  fetchEvents,
  fetchHealth,
  fetchReport,
  fetchTasks,
  ingestEvent,
} from "@/shared/api/opsApi";
import { useOpsStore } from "./useOpsStore";

vi.mock("@/shared/api/opsApi", () => ({
  fetchHealth: vi.fn(),
  fetchEvents: vi.fn(),
  fetchEventAnalysis: vi.fn(),
  ingestEvent: vi.fn(),
  fetchReport: vi.fn(),
  fetchTasks: vi.fn(),
  fetchChat: vi.fn(),
}));

const mockedFetchHealth = vi.mocked(fetchHealth);
const mockedFetchEvents = vi.mocked(fetchEvents);
const mockedFetchEventAnalysis = vi.mocked(fetchEventAnalysis);
const mockedIngestEvent = vi.mocked(ingestEvent);
const mockedFetchReport = vi.mocked(fetchReport);
const mockedFetchTasks = vi.mocked(fetchTasks);
const mockedFetchChat = vi.mocked(fetchChat);

function resetStore() {
  useOpsStore.setState({
    events: fallbackEvents,
    selectedEventId: fallbackEvents[0].event_id,
    health: null,
    analysis: null,
    loading: false,
    error: "",
    report: "",
    tasks: "",
    chatAnswer: "",
    chatSources: [],
  });
}

describe("useOpsStore", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    resetStore();
    mockedFetchEventAnalysis.mockRejectedValue(new Error("offline"));
  });

  it("has correct initial state", () => {
    const state = useOpsStore.getState();
    expect(state.events).toEqual(fallbackEvents);
    expect(state.selectedEventId).toBe(fallbackEvents[0].event_id);
    expect(state.loading).toBe(false);
    expect(state.error).toBe("");
  });

  it("loads events from API on success", async () => {
    const apiEvents = [
      {
        event_id: "evt-api-001",
        event_type: "refund",
        channel: "counter",
        message: "API event",
        severity: "high" as const,
        status: "open",
        requires_response: true,
      },
    ];
    mockedFetchHealth.mockResolvedValue({
      status: "ok",
      events_count: 1,
      docs_count: 3,
      llm_provider: "mock",
      kafka_topic: "store-events",
    });
    mockedFetchEvents.mockResolvedValue({ count: 1, events: apiEvents });
    mockedFetchEventAnalysis.mockResolvedValue({
      event: apiEvents[0],
      analysis: { predicted_type: "refund", severity: "high", confidence: 0.9, source: "api" },
    });

    await useOpsStore.getState().loadEvents();

    const state = useOpsStore.getState();
    expect(state.events).toEqual(apiEvents);
    expect(state.selectedEventId).toBe("evt-api-001");
    expect(state.health?.status).toBe("ok");
    expect(state.analysis?.source).toBe("api");
    expect(state.loading).toBe(false);
    expect(state.error).toBe("");
  });

  it("sets loading while fetching events", async () => {
    let resolveFetch!: (value: { count: number; events: typeof fallbackEvents }) => void;
    mockedFetchHealth.mockResolvedValue({
      status: "ok",
      events_count: 3,
      docs_count: 3,
      llm_provider: "mock",
      kafka_topic: "store-events",
    });
    mockedFetchEvents.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveFetch = resolve;
        }),
    );

    const loadPromise = useOpsStore.getState().loadEvents();
    expect(useOpsStore.getState().loading).toBe(true);

    resolveFetch({ count: fallbackEvents.length, events: fallbackEvents });
    await loadPromise;

    expect(useOpsStore.getState().loading).toBe(false);
  });

  it("falls back to mock events when API fails", async () => {
    mockedFetchHealth.mockRejectedValue(new Error("network error"));
    mockedFetchEvents.mockRejectedValue(new Error("network error"));

    await useOpsStore.getState().loadEvents();

    const state = useOpsStore.getState();
    expect(state.events).toEqual(fallbackEvents);
    expect(state.selectedEventId).toBe(fallbackEvents[0].event_id);
    expect(state.error).toBe("API 연결 실패: mock 사건을 표시합니다.");
    expect(state.loading).toBe(false);
  });

  it("updates selected event and reloads analysis fallback", async () => {
    useOpsStore.getState().selectEvent("evt-003");
    await Promise.resolve();
    expect(useOpsStore.getState().selectedEventId).toBe("evt-003");
    expect(useOpsStore.getState().analysis?.predicted_type).toBe("quality");
  });

  it("loads mock report when API fails", async () => {
    mockedFetchReport.mockRejectedValue(new Error("offline"));
    await useOpsStore.getState().loadReport();
    expect(useOpsStore.getState().report).toContain("mock 보고서");
  });

  it("loads mock tasks when API fails", async () => {
    mockedFetchTasks.mockRejectedValue(new Error("offline"));
    await useOpsStore.getState().loadTasks();
    expect(useOpsStore.getState().tasks).toContain("mock 체크리스트");
  });

  it("loads mock chat answer when API fails", async () => {
    mockedFetchChat.mockRejectedValue(new Error("offline"));
    await useOpsStore.getState().askChat("환불 정책은?");
    expect(useOpsStore.getState().chatAnswer).toContain("mock 답변");
    expect(useOpsStore.getState().chatSources.length).toBeGreaterThan(0);
  });

  it("submits ingest and reloads dashboard", async () => {
    mockedIngestEvent.mockResolvedValue({ message: "ok", event: fallbackEvents[0] });
    mockedFetchHealth.mockResolvedValue({
      status: "ok",
      events_count: 3,
      docs_count: 3,
      llm_provider: "mock",
      kafka_topic: "store-events",
    });
    mockedFetchEvents.mockResolvedValue({ count: 3, events: fallbackEvents });

    await useOpsStore.getState().ingestEvent({
      event_type: "refund",
      channel: "counter",
      message: "new event",
    });

    expect(mockedIngestEvent).toHaveBeenCalled();
    expect(mockedFetchEvents).toHaveBeenCalled();
  });
});
