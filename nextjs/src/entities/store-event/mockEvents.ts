import type { StoreEvent } from "./types";

export const mockEvents: StoreEvent[] = [
  { event_id: "evt-001", event_type: "refund", channel: "counter", message: "환불 처리 지연 문의", severity: "high", status: "mock", requires_response: true },
  { event_id: "evt-002", event_type: "delay", channel: "mobile_order", message: "픽업 대기 시간 문의", severity: "medium", status: "mock", requires_response: true },
  { event_id: "evt-003", event_type: "quality", channel: "delivery", message: "포장 상태 불만", severity: "medium", status: "mock", requires_response: true }
];