import json
import logging

import config

logger = logging.getLogger(__name__)

_producer = None
_kafka_available = False


def _init_producer():
    global _producer, _kafka_available
    if not config.KAFKA_ENABLED:
        return
    try:
        from kafka import KafkaProducer

        _producer = KafkaProducer(
            bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS.split(","),
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
        )
        _kafka_available = True
        logger.info("Kafka producer connected to %s", config.KAFKA_BOOTSTRAP_SERVERS)
    except Exception as exc:
        logger.warning("Kafka producer unavailable: %s", exc)
        _producer = None
        _kafka_available = False


def is_kafka_enabled() -> bool:
    return config.KAFKA_ENABLED and _kafka_available


def publish_event(event: dict) -> bool:
    global _producer, _kafka_available
    if not config.KAFKA_ENABLED:
        return False
    if _producer is None:
        _init_producer()
    if not _kafka_available or _producer is None:
        return False
    try:
        _producer.send(config.KAFKA_TOPIC, event)
        _producer.flush(timeout=5)
        logger.info("Published event %s to topic %s", event.get("event_id"), config.KAFKA_TOPIC)
        return True
    except Exception as exc:
        logger.warning("Kafka publish failed: %s", exc)
        _kafka_available = False
        return False
