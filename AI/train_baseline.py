"""TF-IDF + LogisticRegression baseline 학습 (sentiment / severity)."""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

CSV_PATH = Path(__file__).parent / "training_events_1200.csv"
AI_MODELS_DIR = Path(__file__).parent / "models"
FLASK_MODELS_DIR = Path(__file__).resolve().parents[1] / "flask" / "backend" / "ai" / "models"

VECTORIZER_KWARGS = {
    "analyzer": "char_wb",
    "ngram_range": (2, 4),
    "min_df": 2,
    "max_features": 5000,
}


def build_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(**VECTORIZER_KWARGS)),
            ("clf", LogisticRegression(max_iter=1000, random_state=42)),
        ]
    )


def train_and_evaluate(X: pd.Series, y: pd.Series, label_name: str) -> Pipeline:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"\n=== {label_name} baseline ===")
    print(f"accuracy: {acc:.4f}")
    print(classification_report(y_test, preds, zero_division=0))
    return pipeline


def save_pipeline(pipeline: Pipeline, name: str, *target_dirs: Path) -> None:
    for target_dir in target_dirs:
        target_dir.mkdir(parents=True, exist_ok=True)
        out_path = target_dir / f"{name}_pipeline.joblib"
        joblib.dump(pipeline, out_path)
        print(f"saved: {out_path}")


def main() -> None:
    df = pd.read_csv(CSV_PATH)
    messages = df["message"].fillna("").astype(str)

    sentiment_model = train_and_evaluate(messages, df["sentiment"], "sentiment")
    severity_model = train_and_evaluate(messages, df["severity"], "severity")

    save_pipeline(sentiment_model, "sentiment", AI_MODELS_DIR, FLASK_MODELS_DIR)
    save_pipeline(severity_model, "severity", AI_MODELS_DIR, FLASK_MODELS_DIR)
    print("\n학습 완료.")


if __name__ == "__main__":
    main()
