import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { fallbackEvents } from "@/entities/store-event";
import { fetchEventAnalysis, fetchEvents, fetchHealth } from "@/shared/api/opsApi";
import { useOpsStore } from "@/store/useOpsStore";
import { ZustandDashboard } from "./ApiFetchDashboard";

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

describe("ZustandDashboard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    resetStore();
    mockedFetchEventAnalysis.mockRejectedValue(new Error("offline"));
  });

  it("renders dashboard headings", async () => {
    mockedFetchHealth.mockResolvedValue({
      status: "ok",
      events_count: 3,
      docs_count: 3,
      llm_provider: "mock",
      kafka_topic: "store-events",
    });
    mockedFetchEvents.mockResolvedValue({ count: fallbackEvents.length, events: fallbackEvents });

    render(<ZustandDashboard />);

    expect(screen.getByRole("heading", { name: "Flask API 요청/응답 연결" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "사건 목록" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "AI 분석 결과" })).toBeInTheDocument();

    await waitFor(() => {
      expect(mockedFetchEvents).toHaveBeenCalled();
    });
  });

  it("shows fallback data and error when API fails", async () => {
    mockedFetchHealth.mockRejectedValue(new Error("network error"));
    mockedFetchEvents.mockRejectedValue(new Error("network error"));

    render(<ZustandDashboard />);

    await waitFor(() => {
      expect(screen.getByText("API 연결 실패: mock 사건을 표시합니다.")).toBeInTheDocument();
    });

    expect(screen.getByText("환불 처리 지연 문의")).toBeInTheDocument();
  });

  it("updates detail when another event is selected", async () => {
    mockedFetchHealth.mockResolvedValue({
      status: "ok",
      events_count: 3,
      docs_count: 3,
      llm_provider: "mock",
      kafka_topic: "store-events",
    });
    mockedFetchEvents.mockResolvedValue({ count: fallbackEvents.length, events: fallbackEvents });
    const user = userEvent.setup();

    render(<ZustandDashboard />);

    await waitFor(() => {
      expect(screen.getByText("환불 처리 지연 문의")).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /evt-002/ }));
    expect(screen.getByText("픽업 대기 시간 문의")).toBeInTheDocument();
  });
});
