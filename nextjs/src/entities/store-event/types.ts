export type Severity = "low" | "medium" | "high";

export type StoreEvent = {
  event_id: string;
  event_type: string;
  channel: string;
  message?: string;
  severity?: Severity;
  severity_hint?: Severity;
  sentiment?: string;
  status: string;
  requires_response: boolean;
  confidence?: number;
  predicted_type?: string;
  timestamp?: string;
};

export type EventsResponse = { count: number; events: StoreEvent[] };
export type HealthResponse = { status: string; events_count: number; docs_count: number; llm_provider: string; kafka_topic: string };
export type AnalysisResult = { predicted_type?: string; sentiment?: string; severity?: Severity; confidence?: number; source?: string };
export type AnalysisResponse = { event: StoreEvent; analysis: AnalysisResult };
export type ReportResponse = { event_id: string; result: string };
export type TasksResponse = { event_id: string; result: string };
export type ChatResponse = { answer?: string; sources?: string[] };
export type SimulateResponse = { message: string; event: StoreEvent };
export type IngestPayload = {
  event_type: string;
  channel: string;
  message: string;
  severity_hint?: Severity;
  store_id?: string;
};
export type ChatRequest = { question: string; event_id?: string };
export type EventActionRequest = { event_id: string };