import type { StoreEvent } from "@/entities/store-event";

// 입력,처리,출력
// 입력 : selectedEvent (이벤트 객체)
// 처리 : event가 있는가 없는가 확인
// 출력 : 상세 정보나 혹은 빈 상태 안내.

// 이벤트 하나를 속성(props)으로 받는다
//  -> 속성을 받은 이벤트를 처리.
export function EventDetail({ event }: { event?: StoreEvent }) {
  return (
    <div className="panel wide">
      <h2>선택 사건</h2>
      <p>{event?.message || "목록 API는 요약 필드만 제공합니다. 상세 API는 다음 단계에서 연결합니다."}</p>
      <dl>
        <dt>채널</dt><dd>{event?.channel}</dd>
        <dt>상태</dt><dd>{event?.status}</dd>
      </dl>
    </div>
  );
}
