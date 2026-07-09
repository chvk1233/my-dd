export type Severity = "low" | "medium" | "high";
export type StoreEvent = { event_id: string; event_type: string; channel: string; message?: string; severity?: Severity; severity_hint?: Severity; status: string; requires_response: boolean; };
export type EventsResponse = { count: number; events: StoreEvent[] };
export type AnalysisResponse = { event: StoreEvent; analysis: Record<string, unknown> };
export type ReportResponse = { event_id: string; result: string };
export type TasksResponse = { event_id: string; result: string };
export type ChatResponse = { answer: string; sources?: string[] };
