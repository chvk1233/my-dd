"""KcELECTRA HF 모델 추론 (AI 폴더용)."""

from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODELS_DIR = Path(__file__).parent / "models" / "hf"

_sentiment_bundle = None
_severity_bundle = None


def _load_task(task: str):
    task_dir = MODELS_DIR / task
    if not task_dir.exists():
        return None
    tokenizer = AutoTokenizer.from_pretrained(task_dir)
    model = AutoModelForSequenceClassification.from_pretrained(task_dir)
    model.eval()
    return tokenizer, model


def load_models() -> bool:
    global _sentiment_bundle, _severity_bundle
    _sentiment_bundle = _load_task("sentiment")
    _severity_bundle = _load_task("severity")
    return _sentiment_bundle is not None and _severity_bundle is not None


def _predict_label(bundle, message: str) -> tuple[str, float]:
    tokenizer, model = bundle
    inputs = tokenizer(message or "", return_tensors="pt", truncation=True, max_length=96)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1)[0]
        idx = int(torch.argmax(probs).item())
        label = model.config.id2label[idx]
        confidence = float(probs[idx].item())
    return label, confidence


def models_loaded() -> bool:
    return _sentiment_bundle is not None and _severity_bundle is not None


def predict(message: str) -> dict | None:
    if not models_loaded():
        if not load_models():
            return None

    assert _sentiment_bundle is not None
    assert _severity_bundle is not None

    sentiment, s_conf = _predict_label(_sentiment_bundle, message)
    severity, v_conf = _predict_label(_severity_bundle, message)
    return {
        "sentiment": sentiment,
        "severity": severity,
        "confidence": round(max(s_conf, v_conf), 2),
        "source": "kcelectra_hf",
    }


if __name__ == "__main__":
    sample = "괜찮긴 한데 다시는 안 올 것 같아요."
    result = predict(sample)
    print(result or "모델 없음 — train_hf_kcelectra.py 실행 필요")
