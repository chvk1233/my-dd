"use client";

import { useState } from "react";
import type { IngestPayload } from "@/entities/store-event";

type IngestEventFormProps = {
  disabled?: boolean;
  onSubmit: (payload: IngestPayload) => Promise<void>;
};

export function IngestEventForm({ disabled, onSubmit }: IngestEventFormProps) {
  const [eventType, setEventType] = useState("refund");
  const [channel, setChannel] = useState("counter");
  const [message, setMessage] = useState("환불 처리 지연 문의");

  return (
    <form
      className="inlineForm"
      onSubmit={(event) => {
        event.preventDefault();
        void onSubmit({ event_type: eventType, channel, message, severity_hint: "high" });
      }}
    >
      <input value={eventType} onChange={(e) => setEventType(e.target.value)} aria-label="사건 유형" />
      <input value={channel} onChange={(e) => setChannel(e.target.value)} aria-label="채널" />
      <input value={message} onChange={(e) => setMessage(e.target.value)} aria-label="메시지" />
      <button type="submit" disabled={disabled}>사건 접수 (/ingest)</button>
    </form>
  );
}
