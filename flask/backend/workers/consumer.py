"""Kafka consumer: store-events → model_inference → SQLite."""

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
from ai.model_inference import analyze_event
from services import db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("consumer")


def process_message(payload: dict) -> None:
    event_id = payload["event_id"]
    existing = db.get_event_raw(event_id)
    if existing:
        logger.info("Event %s already exists, skipping", event_id)
        return

    inference_input = {
        "event_id": event_id,
        "event_type": payload["event_type"],
        "message": payload["message"],
        "severity_hint": payload.get("severity_hint"),
    }
    analysis = analyze_event(inference_input)
    severity = analysis.get("severity") or payload.get("severity_hint") or "medium"

    event_data = {
        "event_id": event_id,
        "store_id": payload.get("store_id", config.DEFAULT_STORE_ID),
        "event_type": payload["event_type"],
        "channel": payload.get("channel", ""),
        "message": payload["message"],
        "severity_hint": payload.get("severity_hint"),
        "severity": severity,
        "status": "open",
        "requires_response": analysis.get("action_required", False),
    }
    analysis_data = {**analysis, "event_id": event_id}
    db.save_event_and_analysis(event_data, analysis_data)
    logger.info("Saved event %s with analysis", event_id)


def run_consumer() -> None:
    if not config.KAFKA_ENABLED:
        print("KAFKA_ENABLED=false — consumer requires Kafka. Set KAFKA_ENABLED=true in .env")
        sys.exit(1)

    try:
        from kafka import KafkaConsumer
    except ImportError:
        print("kafka-python not installed. Run: pip install -r requirements.txt")
        sys.exit(1)

    db.init_db()

    logger.info(
        "Starting consumer on topic=%s servers=%s",
        config.KAFKA_TOPIC,
        config.KAFKA_BOOTSTRAP_SERVERS,
    )

    consumer = KafkaConsumer(
        config.KAFKA_TOPIC,
        bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS.split(","),
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        group_id="store-events-consumer",
    )

    for message in consumer:
        try:
            process_message(message.value)
        except Exception as exc:
            logger.error("Failed to process message: %s", exc)


if __name__ == "__main__":
    run_consumer()
