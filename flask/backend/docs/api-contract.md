# API Contract (Next.js ↔ Flask)

Base URL: `http://127.0.0.1:5000`

## GET /health

**Response (`HealthResponse`):**

```json
{
  "status": "ok",
  "events_count": 3,
  "docs_count": 4,
  "llm_provider": "mock",
  "kafka_topic": "store-events"
}
```

## GET /events

**Response (`EventsResponse`):**

- `events[]` uses `timestamp` (not `created_at`)
- `requires_response` is JSON boolean

## GET /events/<event_id>

**Response (`AnalysisResponse`):**

- `analysis` includes: `predicted_type`, `sentiment`, `severity`, `confidence`, `source`
- `action_required`, `summary` are stored in DB but not exposed in API

## POST /ingest

**Request (`IngestPayload`):**

```json
{
  "event_type": "refund",
  "channel": "counter",
  "message": "환불 처리 지연 문의",
  "severity_hint": "high"
}
```

`store_id` 미전송 시 기본값 `store-001` 적용.

**Response (`SimulateResponse`):**

```json
{
  "message": "event accepted",
  "event": { "event_id": "evt-004", "...": "..." }
}
```

## POST /report, POST /tasks

**Request:** `{ "event_id": "evt-001" }`  
**Response:** `{ "event_id": "...", "result": "..." }`

## POST /chat

**Request:** `{ "question": "...", "event_id": "evt-001" }`  
**Response:** `{ "answer": "...", "sources": ["refund_policy.md"] }`
