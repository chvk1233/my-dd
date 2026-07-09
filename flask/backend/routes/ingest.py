from flask import Blueprint, jsonify, request

import config
from services import db, kafka_producer

ingest_bp = Blueprint("ingest", __name__)

REQUIRED_FIELDS = ("event_type", "channel", "message")


@ingest_bp.post("/ingest")
def ingest():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "invalid JSON body"}), 400

    missing = [f for f in REQUIRED_FIELDS if not payload.get(f)]
    if missing:
        return jsonify({"error": f"missing required fields: {', '.join(missing)}"}), 400

    store_id = payload.get("store_id") or config.DEFAULT_STORE_ID
    event_id = db.next_event_id()

    kafka_payload = {
        "event_id": event_id,
        "store_id": store_id,
        "event_type": payload["event_type"],
        "channel": payload["channel"],
        "message": payload["message"],
        "severity_hint": payload.get("severity_hint"),
    }

    published = kafka_producer.publish_event(kafka_payload)

    if published:
        event = {
            "event_id": event_id,
            "event_type": payload["event_type"],
            "channel": payload["channel"],
            "message": payload["message"],
            "status": "open",
            "requires_response": True,
        }
        if payload.get("severity_hint"):
            event["severity_hint"] = payload["severity_hint"]
            event["severity"] = payload["severity_hint"]
        return jsonify({"message": "event accepted", "event": event})

    event = db.process_ingested_event({**payload, "store_id": store_id})
    return jsonify({"message": "event accepted", "event": event})
