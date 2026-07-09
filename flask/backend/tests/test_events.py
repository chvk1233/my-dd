def test_list_events(client):
    response = client.get("/events")
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] == 3
    assert len(data["events"]) == 3
    event = data["events"][0]
    assert "event_id" in event
    assert "requires_response" in event
    assert isinstance(event["requires_response"], bool)
    assert "timestamp" in event
    assert "created_at" not in event


def test_get_event_analysis(client):
    response = client.get("/events/evt-001")
    assert response.status_code == 200
    data = response.get_json()
    assert data["event"]["event_id"] == "evt-001"
    assert data["analysis"]["predicted_type"] == "refund"
    assert data["analysis"]["source"] == "rule_fallback"
    assert "action_required" not in data["analysis"]
    assert "summary" not in data["analysis"]


def test_get_event_not_found(client):
    response = client.get("/events/evt-999")
    assert response.status_code == 404
