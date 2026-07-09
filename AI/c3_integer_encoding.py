from collections import Counter
from pathlib import Path

import pandas as pd


def tokenize(text: str) -> list[str]:
    return text.split()


def build_vocab(tokenized_sentences: list[list[str]], min_freq: int = 1) -> tuple[dict[str, int], dict[int, str]]:
    counter = Counter(token for sent in tokenized_sentences for token in sent)

    # 0: PAD, 1: UNK로 예약
    word_to_index = {"<PAD>": 0, "<UNK>": 1}
    for token, freq in counter.items():
        if freq >= min_freq:
            word_to_index[token] = len(word_to_index)

    index_to_word = {idx: word for word, idx in word_to_index.items()}
    return word_to_index, index_to_word


def encode_sentence(tokens: list[str], word_to_index: dict[str, int]) -> list[int]:
    unk_idx = word_to_index["<UNK>"]
    return [word_to_index.get(tok, unk_idx) for tok in tokens]


def main() -> None:
    csv_path = Path(__file__).parent / "training_events_1200.csv"
    df = pd.read_csv(csv_path)

    messages = df["message"].dropna().tolist()
    tokenized = [tokenize(msg) for msg in messages]

    # 1) 토큰 빈도
    counter = Counter(token for sent in tokenized for token in sent)
    print("[1] 상위 20개 토큰")
    for token, freq in counter.most_common(20):
        print(f"{token}: {freq}")

    # 2) 사전 생성
    word_to_index, index_to_word = build_vocab(tokenized)
    print("\n[2] vocabulary 크기:", len(word_to_index))
    print("[3] word_to_index 일부:", list(word_to_index.items())[:20])
    print("[4] index_to_word 일부:", [(k, index_to_word[k]) for k in range(min(20, len(index_to_word)))])

    # 3) 정수 시퀀스 변환
    encoded = [encode_sentence(sent, word_to_index) for sent in tokenized[:5]]
    print("\n[5] 정수 인코딩 샘플 5개")
    for i, seq in enumerate(encoded, start=1):
        print(f"sample{i}: {seq}")

    # 4) 새로운 문장(<UNK> 동작 확인)
    new_sentence = "신규 사건 테스트 문장 미등록단어"
    new_encoded = encode_sentence(tokenize(new_sentence), word_to_index)
    print("\n[6] <UNK> 동작 확인")
    print("원문:", new_sentence)
    print("인코딩:", new_encoded)

    print("\n[7] 설명")
    print("- 단어 사전은 토큰을 숫자 ID로 변환하기 위한 기준표")
    print("- 정수 인코딩은 의미 이해가 아니라 단순 ID 매핑")
    print("- 문장 길이가 다른 이유는 토큰 수가 문장마다 다르기 때문")


if __name__ == "__main__":
    main()

