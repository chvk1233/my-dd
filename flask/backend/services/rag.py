from pathlib import Path

import config


def count_docs() -> int:
    docs_dir = config.DOCS_DIR
    if not docs_dir.exists():
        return 0
    return len(list(docs_dir.glob("*.md")))


def search_docs(question: str, limit: int = 3) -> list[tuple[str, str]]:
    """Return list of (filename, excerpt) matching keywords in question."""
    docs_dir = config.DOCS_DIR
    if not docs_dir.exists():
        return []

    keywords = _extract_keywords(question)
    results: list[tuple[str, float, str]] = []

    for path in sorted(docs_dir.glob("*.md")):
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            continue
        score = _score_content(content, keywords)
        if score > 0 or not keywords:
            excerpt = _extract_excerpt(content, keywords)
            results.append((path.name, score, excerpt))

    results.sort(key=lambda x: x[1], reverse=True)
    if not results and docs_dir.exists():
        for path in sorted(docs_dir.glob("*.md"))[:limit]:
            content = path.read_text(encoding="utf-8")
            results.append((path.name, 0.0, content[:200]))

    return [(name, excerpt) for name, _, excerpt in results[:limit]]


def answer_question(question: str, event: dict | None = None) -> tuple[str, list[str]]:
    matches = search_docs(question)
    sources = [name for name, _ in matches]

    if not matches:
        return _fallback_answer(question, event), []

    excerpts = [excerpt for _, excerpt in matches]
    answer = _compose_answer(question, excerpts, event)
    return answer, sources


def _extract_keywords(text: str) -> list[str]:
    stopwords = {"은", "는", "이", "가", "을", "를", "에", "의", "와", "과", "먼저", "할", "것", "수", "있", "인", "한", "더"}
    tokens = []
    for token in text.replace("?", "").replace(".", "").split():
        token = token.strip()
        if len(token) >= 2 and token not in stopwords:
            tokens.append(token)
    if "환불" in text:
        tokens.append("환불")
    if "고객" in text:
        tokens.append("고객")
    return list(dict.fromkeys(tokens))


def _score_content(content: str, keywords: list[str]) -> float:
    if not keywords:
        return 0.0
    lower = content.lower()
    return sum(1 for kw in keywords if kw.lower() in lower)


def _extract_excerpt(content: str, keywords: list[str], max_len: int = 200) -> str:
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    for line in lines:
        if any(kw in line for kw in keywords):
            return line[:max_len]
    return (lines[0][:max_len] if lines else content[:max_len])


def _compose_answer(question: str, excerpts: list[str], event: dict | None) -> str:
    context = " ".join(excerpts[:2])
    if "환불" in question:
        return (
            "영수증과 결제 수단을 먼저 확인하고, 환불 가능 조건을 안내해야 합니다. "
            f"운영 문서 기준: {context[:150]}"
        )
    if event and event.get("message"):
        return f"관련 사건({event.get('event_id')})을 참고하여, {context[:180]}"
    return f"운영 문서에 따르면: {context[:200]}"


def _fallback_answer(question: str, event: dict | None) -> str:
    if "환불" in question:
        return "영수증과 결제 수단을 먼저 확인하고, 환불 가능 조건을 안내해야 합니다."
    if event:
        return f"사건 {event.get('event_id')} 관련하여 현장 매뉴얼을 확인한 뒤 고객에게 처리 현황을 안내하세요."
    return "운영 매뉴얼을 확인하여 표준 응대 절차에 따라 안내해 주세요."
