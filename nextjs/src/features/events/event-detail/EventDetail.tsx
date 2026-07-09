import type { StoreEvent } from "@/entities/store-event";

export function EventDetail({ event }: { event?: StoreEvent }) {
  return <div className="panel wide"><h2>선택 사건</h2><p>{event?.message || "선택된 사건의 상세 메시지를 확인합니다."}</p><dl><dt>채널</dt><dd>{event?.channel}</dd><dt>상태</dt><dd>{event?.status}</dd></dl></div>;
}