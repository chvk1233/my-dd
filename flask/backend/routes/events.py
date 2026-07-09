from flask import Blueprint, jsonify

from services import db

events_bp = Blueprint("events", __name__)


@events_bp.get("/events")
def list_events():
    events = db.list_events()
    return jsonify({"count": len(events), "events": events})


@events_bp.get("/events/<event_id>")
def get_event(event_id: str):
    result = db.get_event_with_analysis(event_id)
    if not result:
        return jsonify({"error": "event not found"}), 404
    event, analysis = result
    return jsonify({"event": event, "analysis": analysis})
