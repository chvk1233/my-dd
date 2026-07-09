"""학습된 TF-IDF + LogisticRegression baseline 추론."""

from pathlib import Path

import joblib
from sklearn.pipeline import Pipeline

MODELS_DIR = Path(__file__).parent / "models"

_sentiment_pipeline: Pipeline | None = None
_severity_pipeline: Pipeline | None = None


def _load_pipeline(name: str) -> Pipeline | None:
    path = MODELS_DIR / f"{name}_pipeline.joblib"
    if not path.exists():
        return None
    return joblib.load(path)


def load_models() -> bool:
    global _sentiment_pipeline, _severity_pipeline
    _sentiment_pipeline = _load_pipeline("sentiment")
    _severity_pipeline = _load_pipeline("severity")
    return _sentiment_pipeline is not None and _severity_pipeline is not None


def models_loaded() -> bool:
    return _sentiment_pipeline is not None and _severity_pipeline is not None


def predict(message: str) -> dict | None:
    if not models_loaded():
        if not load_models():
            return None

    assert _sentiment_pipeline is not None
    assert _severity_pipeline is not None

    text = message or ""
    sentiment = str(_sentiment_pipeline.predict([text])[0])
    severity = str(_severity_pipeline.predict([text])[0])

    sentiment_proba = _sentiment_pipeline.predict_proba([text])[0]
    severity_proba = _severity_pipeline.predict_proba([text])[0]
    confidence = round(float(max(sentiment_proba.max(), severity_proba.max())), 2)

    return {
        "sentiment": sentiment,
        "severity": severity,
        "confidence": confidence,
        "source": "tfidf_lr",
    }


if __name__ == "__main__":
    sample = "환불 처리 지연으로 고객이 불만을 제기했습니다."
    if load_models():
        print(predict(sample))
    else:
        print("모델이 없습니다. train_baseline.py를 먼저 실행하세요.")
