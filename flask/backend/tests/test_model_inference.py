from ai.model_inference import analyze_event


def test_analyze_refund():
    result = analyze_event({
        "event_id": "test-001",
        "event_type": "refund",
        "message": "환불 처리 지연으로 고객이 불만을 제기했습니다.",
        "severity_hint": "high",
    })
    assert result["predicted_type"] == "refund"
    assert result["sentiment"] == "negative"
    assert result["severity"] == "high"
    assert result["action_required"] is True
    assert result["source"] in ("kcelectra_hf", "tfidf_lr", "keyword_fallback")
    assert 0 < result["confidence"] <= 1


def test_analyze_delay():
    result = analyze_event({
        "event_id": "test-002",
        "event_type": "delay",
        "message": "픽업 대기 시간 문의",
        "severity_hint": "medium",
    })
    assert result["predicted_type"] == "delay"
