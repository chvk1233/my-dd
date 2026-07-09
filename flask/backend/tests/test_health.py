def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["events_count"] == 3
    assert data["docs_count"] >= 3
    assert data["llm_provider"] == "mock"
    assert data["kafka_topic"] == "store-events"
