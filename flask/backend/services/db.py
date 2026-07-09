import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
  event_id TEXT PRIMARY KEY,
  store_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  channel TEXT,
  message TEXT NOT NULL,
  severity_hint TEXT,
  severity TEXT,
  status TEXT NOT NULL,
  requires_response INTEGER DEFAULT 0,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS analysis_results (
  event_id TEXT PRIMARY KEY,
  predicted_type TEXT,
  sentiment TEXT,
  severity TEXT,
  action_required INTEGER DEFAULT 0,
  summary TEXT,
  confidence REAL,
  source TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(event_id) REFERENCES events(event_id)
);
"""

SEED_EVENTS = [
    {
        "event_id": "evt-001",
        "store_id": "store-001",
        "event_type": "refund",
        "channel": "counter",
        "message": "환불 처리 지연 문의",
        "severity_hint": "high",
        "severity": "high",
        "status": "open",
        "requires_response": 1,
    },
    {
        "event_id": "evt-002",
        "store_id": "store-001",
        "event_type": "delay",
        "channel": "mobile_order",
        "message": "픽업 대기 시간 문의",
        "severity_hint": "medium",
        "severity": "medium",
        "status": "open",
        "requires_response": 1,
    },
    {
        "event_id": "evt-003",
        "store_id": "store-001",
        "event_type": "quality",
        "channel": "delivery",
        "message": "포장 상태 불만",
        "severity_hint": "medium",
        "severity": "medium",
        "status": "open",
        "requires_response": 1,
    },
]

SEED_ANALYSIS = [
    {
        "event_id": "evt-001",
        "predicted_type": "refund",
        "sentiment": "negative",
        "severity": "high",
        "action_required": 1,
        "summary": "환불 처리 지연으로 인한 고객 불만 사건입니다.",
        "confidence": 0.92,
        "source": "rule_fallback",
    },
    {
        "event_id": "evt-002",
        "predicted_type": "delay",
        "sentiment": "neutral",
        "severity": "medium",
        "action_required": 1,
        "summary": "픽업 대기 시간 관련 문의 사건입니다.",
        "confidence": 0.85,
        "source": "rule_fallback",
    },
    {
        "event_id": "evt-003",
        "predicted_type": "quality",
        "sentiment": "negative",
        "severity": "medium",
        "action_required": 1,
        "summary": "포장 상태 불만 관련 품질 사건입니다.",
        "confidence": 0.88,
        "source": "rule_fallback",
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def get_connection(db_path: str | None = None) -> sqlite3.Connection:
    path = db_path or config.DATABASE_PATH
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str | None = None) -> None:
    conn = get_connection(db_path)
    try:
        conn.executescript(SCHEMA)
        conn.commit()
        _seed_if_empty(conn)
    finally:
        conn.close()


def _seed_if_empty(conn: sqlite3.Connection) -> None:
    count = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    if count > 0:
        return

    now = _utc_now()
    for event in SEED_EVENTS:
        conn.execute(
            """
            INSERT INTO events (
                event_id, store_id, event_type, channel, message,
                severity_hint, severity, status, requires_response, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event["event_id"],
                event["store_id"],
                event["event_type"],
                event["channel"],
                event["message"],
                event["severity_hint"],
                event["severity"],
                event["status"],
                event["requires_response"],
                now,
            ),
        )

    for analysis in SEED_ANALYSIS:
        conn.execute(
            """
            INSERT INTO analysis_results (
                event_id, predicted_type, sentiment, severity,
                action_required, summary, confidence, source, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                analysis["event_id"],
                analysis["predicted_type"],
                analysis["sentiment"],
                analysis["severity"],
                analysis["action_required"],
                analysis["summary"],
                analysis["confidence"],
                analysis["source"],
                now,
            ),
        )
    conn.commit()


def _row_to_store_event(row: sqlite3.Row, analysis: sqlite3.Row | None = None) -> dict[str, Any]:
    event = {
        "event_id": row["event_id"],
        "event_type": row["event_type"],
        "channel": row["channel"] or "",
        "message": row["message"],
        "status": row["status"],
        "requires_response": bool(row["requires_response"]),
        "timestamp": row["created_at"],
    }
    if row["severity"]:
        event["severity"] = row["severity"]
    if row["severity_hint"]:
        event["severity_hint"] = row["severity_hint"]

    if analysis:
        if analysis["predicted_type"]:
            event["predicted_type"] = analysis["predicted_type"]
        if analysis["confidence"] is not None:
            event["confidence"] = analysis["confidence"]
        if analysis["sentiment"]:
            event["sentiment"] = analysis["sentiment"]

    return event


def _row_to_analysis(row: sqlite3.Row) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if row["predicted_type"]:
        result["predicted_type"] = row["predicted_type"]
    if row["sentiment"]:
        result["sentiment"] = row["sentiment"]
    if row["severity"]:
        result["severity"] = row["severity"]
    if row["confidence"] is not None:
        result["confidence"] = row["confidence"]
    if row["source"]:
        result["source"] = row["source"]
    return result


def count_events(db_path: str | None = None) -> int:
    conn = get_connection(db_path)
    try:
        return conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    finally:
        conn.close()


def list_events(db_path: str | None = None) -> list[dict[str, Any]]:
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM events ORDER BY created_at DESC"
        ).fetchall()
        events = []
        for row in rows:
            analysis = conn.execute(
                "SELECT * FROM analysis_results WHERE event_id = ?",
                (row["event_id"],),
            ).fetchone()
            events.append(_row_to_store_event(row, analysis))
        return events
    finally:
        conn.close()


def get_event_with_analysis(
    event_id: str, db_path: str | None = None
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM events WHERE event_id = ?", (event_id,)
        ).fetchone()
        if not row:
            return None

        analysis_row = conn.execute(
            "SELECT * FROM analysis_results WHERE event_id = ?", (event_id,)
        ).fetchone()

        event = _row_to_store_event(row, analysis_row)
        analysis = _row_to_analysis(analysis_row) if analysis_row else {}
        return event, analysis
    finally:
        conn.close()


def get_event_raw(event_id: str, db_path: str | None = None) -> sqlite3.Row | None:
    conn = get_connection(db_path)
    try:
        return conn.execute(
            "SELECT * FROM events WHERE event_id = ?", (event_id,)
        ).fetchone()
    finally:
        conn.close()


def get_analysis_raw(event_id: str, db_path: str | None = None) -> sqlite3.Row | None:
    conn = get_connection(db_path)
    try:
        return conn.execute(
            "SELECT * FROM analysis_results WHERE event_id = ?", (event_id,)
        ).fetchone()
    finally:
        conn.close()


def next_event_id(db_path: str | None = None) -> str:
    conn = get_connection(db_path)
    try:
        rows = conn.execute("SELECT event_id FROM events").fetchall()
        max_num = 0
        for row in rows:
            eid = row["event_id"]
            if eid.startswith("evt-"):
                try:
                    max_num = max(max_num, int(eid.split("-", 1)[1]))
                except ValueError:
                    pass
        return f"evt-{max_num + 1:03d}"
    finally:
        conn.close()


def save_event_and_analysis(
    event_data: dict[str, Any],
    analysis_data: dict[str, Any],
    db_path: str | None = None,
) -> dict[str, Any]:
    conn = get_connection(db_path)
    try:
        now = _utc_now()
        conn.execute(
            """
            INSERT INTO events (
                event_id, store_id, event_type, channel, message,
                severity_hint, severity, status, requires_response, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_data["event_id"],
                event_data["store_id"],
                event_data["event_type"],
                event_data["channel"],
                event_data["message"],
                event_data.get("severity_hint"),
                event_data.get("severity"),
                event_data["status"],
                int(event_data.get("requires_response", False)),
                now,
            ),
        )
        conn.execute(
            """
            INSERT INTO analysis_results (
                event_id, predicted_type, sentiment, severity,
                action_required, summary, confidence, source, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                analysis_data["event_id"],
                analysis_data.get("predicted_type"),
                analysis_data.get("sentiment"),
                analysis_data.get("severity"),
                int(analysis_data.get("action_required", False)),
                analysis_data.get("summary"),
                analysis_data.get("confidence"),
                analysis_data.get("source"),
                now,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    result = get_event_with_analysis(event_data["event_id"], db_path)
    assert result is not None
    return result[0]


def process_ingested_event(payload: dict[str, Any], db_path: str | None = None) -> dict[str, Any]:
    """Create event, run inference, save to DB. Returns API event dict."""
    from ai.model_inference import analyze_event

    event_id = next_event_id(db_path)
    store_id = payload.get("store_id") or config.DEFAULT_STORE_ID

    inference_input = {
        "event_id": event_id,
        "event_type": payload["event_type"],
        "message": payload["message"],
        "severity_hint": payload.get("severity_hint"),
    }
    analysis = analyze_event(inference_input)

    severity = analysis.get("severity") or payload.get("severity_hint") or "medium"
    requires_response = analysis.get("action_required", False)

    event_data = {
        "event_id": event_id,
        "store_id": store_id,
        "event_type": payload["event_type"],
        "channel": payload["channel"],
        "message": payload["message"],
        "severity_hint": payload.get("severity_hint"),
        "severity": severity,
        "status": "open",
        "requires_response": requires_response,
    }
    analysis_data = {**analysis, "event_id": event_id}
    return save_event_and_analysis(event_data, analysis_data, db_path)
