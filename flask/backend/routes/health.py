from flask import Blueprint, jsonify

import config
from services import db, kafka_producer, rag

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "events_count": db.count_events(),
        "docs_count": rag.count_docs(),
        "llm_provider": config.LLM_PROVIDER,
        "kafka_topic": config.KAFKA_TOPIC,
    })
