import type {
  AnalysisResponse,
  ChatRequest,
  ChatResponse,
  EventActionRequest,
  EventsResponse,
  HealthResponse,
  IngestPayload,
  ReportResponse,
  SimulateResponse,
  TasksResponse,
} from "@/entities/store-event";
import { requestJson } from "./httpClient";

export function fetchHealth() {
  return requestJson<HealthResponse>("/health");
}

export function fetchEvents() {
  return requestJson<EventsResponse>("/events");
}

export function fetchEventAnalysis(eventId: string) {
  return requestJson<AnalysisResponse>(`/events/${eventId}`);
}

export function ingestEvent(payload: IngestPayload) {
  return requestJson<SimulateResponse>("/ingest", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function fetchReport(payload: EventActionRequest) {
  return requestJson<ReportResponse>("/report", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function fetchTasks(payload: EventActionRequest) {
  return requestJson<TasksResponse>("/tasks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function fetchChat(payload: ChatRequest) {
  return requestJson<ChatResponse>("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}
