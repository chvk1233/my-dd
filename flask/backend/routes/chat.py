from flask import Blueprint, jsonify, request

from services import db, rag

chat_bp = Blueprint("chat", __name__)


@chat_bp.post("/chat")
def chat():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "invalid JSON body"}), 400

    question = payload.get("question")
    if not question:
        return jsonify({"error": "question is required"}), 400

    event = None
    event_id = payload.get("event_id")
    if event_id:
        result = db.get_event_with_analysis(event_id)
        if result:
            event, _ = result

    answer, sources = rag.answer_question(question, event)
    return jsonify({"answer": answer, "sources": sources})
