def test_report(client):
    response = client.post("/report", json={"event_id": "evt-001"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["event_id"] == "evt-001"
    assert "점장 보고서" in data["result"]


def test_tasks(client):
    response = client.post("/tasks", json={"event_id": "evt-001"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["event_id"] == "evt-001"
    assert "체크리스트" in data["result"]


def test_chat(client):
    response = client.post(
        "/chat",
        json={
            "event_id": "evt-001",
            "question": "환불 요청 고객에게 먼저 확인할 것은?",
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "answer" in data
    assert "영수증" in data["answer"]
    assert isinstance(data["sources"], list)


def test_report_missing_event_id(client):
    response = client.post("/report", json={})
    assert response.status_code == 400


def test_chat_missing_question(client):
    response = client.post("/chat", json={"event_id": "evt-001"})
    assert response.status_code == 400


def test_report_not_found(client):
    response = client.post("/report", json={"event_id": "evt-999"})
    assert response.status_code == 404
