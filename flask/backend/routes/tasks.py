from flask import Blueprint, jsonify, request

from services import db, llm

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.post("/tasks")
def tasks():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "invalid JSON body"}), 400

    event_id = payload.get("event_id")
    if not event_id:
        return jsonify({"error": "event_id is required"}), 400

    result = db.get_event_with_analysis(event_id)
    if not result:
        return jsonify({"error": "event not found"}), 404

    event, analysis = result
    tasks_text = llm.generate_tasks(event, analysis)
    return jsonify({"event_id": event_id, "result": tasks_text})
