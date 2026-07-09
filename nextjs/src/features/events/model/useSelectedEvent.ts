import { useMemo, useState } from "react";
import type { StoreEvent } from "@/entities/store-event";

export function useSelectedEvent(events: StoreEvent[]) {
    // selectedEventId : 선택된 이벤트의 ID
    //  -> 실제 상태값임. (사용자가 목록을 클릭했을때 변경될 값)
  const [selectedEventId, setSelectedEventId] = useState(events[0]?.event_id || "");
  // 결론은 구조 설명에 있음 ( 값이 바뀔때만 다시 계산하도록 처리)
  const selectedEvent = useMemo(() => events.find((event) => event.event_id === selectedEventId), [events, selectedEventId]);

  // 이 컴포넌트의 의의
  // 1. 같은 정보를 두번 저장하지 않겠다.
  // 2. 선택된 객체를 따로 저장하지 않으려고.
  //  -> 선택 상태 자체를 소유하지 않으면서 받은 목록을 보여주고
  //     클릭 사실만 관제센터에 전달하는 목적.
  return { selectedEvent, selectedEventId, setSelectedEventId };
}