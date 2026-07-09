def test_ingest_success(client):
    response = client.post(
        "/ingest",
        json={
            "event_type": "refund",
            "channel": "counter",
            "message": "환불 처리 지연으로 고객이 불만을 제기했습니다.",
            "severity_hint": "high",
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "event accepted"
    assert data["event"]["event_id"] == "evt-004"
    assert data["event"]["requires_response"] is True
    assert "timestamp" in data["event"]

    events = client.get("/events").get_json()
    assert events["count"] == 4


def test_ingest_missing_message(client):
    response = client.post(
        "/ingest",
        json={"event_type": "refund", "channel": "counter"},
    )
    assert response.status_code == 400


def test_ingest_invalid_json(client):
    response = client.post(
        "/ingest",
        data="not json",
        content_type="application/json",
    )
    assert response.status_code == 400
