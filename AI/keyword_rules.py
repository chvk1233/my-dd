"""add-part.md 키워드 기반 sentiment/severity 규칙."""

NEGATIVE_SENTIMENT_KEYWORDS = ("환불", "항의", "불만", "지연", "누락", "취소", "화남")
HIGH_SEVERITY_KEYWORDS = ("환불", "중복 결제", "사고", "위험", "강하게 항의")
MEDIUM_SEVERITY_KEYWORDS = ("지연", "대기", "누락", "품절")
LOW_SEVERITY_KEYWORDS = ("문의", "확인", "요청")


def predict_sentiment(message: str) -> str:
    text = message or ""
    if any(kw in text for kw in NEGATIVE_SENTIMENT_KEYWORDS):
        return "negative"
    return "neutral"


def predict_severity(message: str, severity_hint: str | None = None) -> str:
    if severity_hint in ("low", "medium", "high"):
        return severity_hint

    text = message or ""
    if any(kw in text for kw in HIGH_SEVERITY_KEYWORDS):
        return "high"
    if any(kw in text for kw in MEDIUM_SEVERITY_KEYWORDS):
        return "medium"
    if any(kw in text for kw in LOW_SEVERITY_KEYWORDS):
        return "low"
    return "medium"
