"""Event analysis: KcELECTRA HF -> TF-IDF+LR -> keyword fallback."""

from ai import baseline_predict
from ai.keyword_rules import predict_sentiment, predict_severity


def _predict_hf(message: str) -> dict | None:
    try:
        from ai import hf_predict

        return hf_predict.predict(message)
    except Exception:
        return None


def analyze_event(event: dict) -> dict:
    message = event.get("message") or ""
    event_type = event.get("event_type", "")
    severity_hint = event.get("severity_hint")

    predicted_type = _predict_type(message, event_type)

    hf = _predict_hf(message)
    if hf:
        sentiment = hf["sentiment"]
        severity = hf["severity"] if severity_hint is None else severity_hint
        confidence = hf["confidence"]
        source = hf["source"]
    else:
        baseline = baseline_predict.predict(message)
        if baseline:
            sentiment = baseline["sentiment"]
            severity = baseline["severity"] if severity_hint is None else severity_hint
            confidence = baseline["confidence"]
            source = baseline["source"]
        else:
            sentiment = predict_sentiment(message)
            severity = predict_severity(message, severity_hint)
            confidence = _estimate_confidence(message, event_type, source="keyword_fallback")
            source = "keyword_fallback"

    action_required = severity in ("medium", "high")
    summary = _build_summary(predicted_type, message)

    return {
        "predicted_type": predicted_type,
        "sentiment": sentiment,
        "severity": severity,
        "action_required": action_required,
        "summary": summary,
        "confidence": confidence,
        "source": source,
    }


def _predict_type(message: str, event_type: str) -> str:
    text = message.lower()
    if any(kw in text for kw in ("환불", "결제", "취소", "refund")):
        return "refund"
    if any(kw in text for kw in ("지연", "대기", "늦", "delay")):
        return "delay"
    if any(kw in text for kw in ("품질", "포장", "상태", "quality")):
        return "quality"
    return event_type or "general"


def _build_summary(predicted_type: str, message: str) -> str:
    type_labels = {
        "refund": "환불",
        "delay": "지연/대기",
        "quality": "품질",
        "general": "일반",
    }
    label = type_labels.get(predicted_type, predicted_type)
    snippet = message[:40] + ("..." if len(message) > 40 else "")
    return f"{label} 관련 사건: {snippet}"


def _estimate_confidence(message: str, event_type: str, source: str) -> float:
    base = {"kcelectra_hf": 0.85, "tfidf_lr": 0.8, "keyword_fallback": 0.7}.get(source, 0.7)
    if event_type and event_type in message:
        base += 0.05
    if len(message) > 10:
        base += 0.05
    return min(round(base, 2), 0.95)
