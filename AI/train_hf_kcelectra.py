"""KcELECTRA 파인튜닝 (sentiment / severity) — fast 모드 기본."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)

MODEL_ID = "beomi/KcELECTRA-base"
CSV_PATH = Path(__file__).parent / "training_events_1200.csv"
AI_OUT = Path(__file__).parent / "models" / "hf"
FLASK_OUT = Path(__file__).resolve().parents[1] / "flask" / "backend" / "ai" / "models" / "hf"

LABEL_CONFIG = {
    "sentiment": {
        "labels": ["negative", "neutral"],
        "id2label": {0: "negative", 1: "neutral"},
        "label2id": {"negative": 0, "neutral": 1},
    },
    "severity": {
        "labels": ["low", "medium", "high"],
        "id2label": {0: "low", 1: "medium", 2: "high"},
        "label2id": {"low": 0, "medium": 1, "high": 2},
    },
}


class MessageDataset(Dataset):
    def __init__(self, texts: list[str], labels: list[int], tokenizer, max_length: int):
        self.encodings = tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=max_length,
            return_tensors="pt",
        )
        self.labels = torch.tensor(labels)

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, idx: int) -> dict:
        item = {k: v[idx] for k, v in self.encodings.items()}
        item["labels"] = self.labels[idx]
        return item


def freeze_encoder(model) -> None:
    for name, param in model.named_parameters():
        if "classifier" not in name:
            param.requires_grad = False


def train_task(
    task: str,
    df: pd.DataFrame,
    tokenizer,
    out_dirs: list[Path],
    epochs: int,
    batch_size: int,
    max_length: int,
    max_samples: int | None,
) -> Path:
    cfg = LABEL_CONFIG[task]
    data = df[["message", task]].dropna()
    if max_samples:
        data = data.head(max_samples)

    texts = data["message"].astype(str).tolist()
    labels = [cfg["label2id"][v] for v in data[task].astype(str).tolist()]

    train_texts, eval_texts, train_labels, eval_labels = train_test_split(
        texts, labels, test_size=0.15, random_state=42, stratify=labels
    )

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_ID,
        num_labels=len(cfg["labels"]),
        id2label=cfg["id2label"],
        label2id=cfg["label2id"],
    )
    freeze_encoder(model)

    train_ds = MessageDataset(train_texts, train_labels, tokenizer, max_length)
    eval_ds = MessageDataset(eval_texts, eval_labels, tokenizer, max_length)

    args = TrainingArguments(
        output_dir=f"./hf_output_{task}",
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        eval_strategy="epoch",
        save_strategy="no",
        logging_steps=50,
        report_to="none",
        use_cpu=not torch.cuda.is_available(),
    )

    trainer = Trainer(model=model, args=args, train_dataset=train_ds, eval_dataset=eval_ds)
    trainer.train()

    primary = out_dirs[0] / task
    primary.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(primary)
    tokenizer.save_pretrained(primary)

    for d in out_dirs[1:]:
        target = d / task
        target.mkdir(parents=True, exist_ok=True)
        model.save_pretrained(target)
        tokenizer.save_pretrained(target)

    print(f"[{task}] saved -> {primary}")
    return primary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--max-length", type=int, default=96)
    parser.add_argument("--max-samples", type=int, default=600, help="0=전체")
    args = parser.parse_args()

    max_samples = None if args.max_samples == 0 else args.max_samples
    df = pd.read_csv(CSV_PATH)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

    out_dirs = [AI_OUT, FLASK_OUT]
    for task in ("sentiment", "severity"):
        train_task(
            task,
            df,
            tokenizer,
            out_dirs,
            epochs=args.epochs,
            batch_size=args.batch_size,
            max_length=args.max_length,
            max_samples=max_samples,
        )

    print("KcELECTRA 학습 완료.")


if __name__ == "__main__":
    main()
