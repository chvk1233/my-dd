import numpy as np


def tokenize(text: str) -> list[str]:
    return text.split()


def build_vocab(sentences: list[str]) -> dict[str, int]:
    vocab = {"<PAD>": 0}
    for sentence in sentences:
        for token in tokenize(sentence):
            if token not in vocab:
                vocab[token] = len(vocab)
    return vocab


def integer_encode(sentence: str, vocab: dict[str, int]) -> list[int]:
    return [vocab[token] for token in tokenize(sentence)]


def to_one_hot_numpy(encoded: list[int], vocab_size: int) -> np.ndarray:
    one_hot = np.zeros((len(encoded), vocab_size), dtype=np.int32)
    for i, token_id in enumerate(encoded):
        one_hot[i, token_id] = 1
    return one_hot


def main() -> None:
    sample_sentences = [
        "환불 처리 지연 문의",
        "픽업 대기 시간 문의",
        "포장 상태 불만",
    ]

    print("[1] 샘플 문장 3개")
    for s in sample_sentences:
        print("-", s)

    vocab = build_vocab(sample_sentences)
    vocab_size = len(vocab)
    print("\n[2] word_to_index")
    print(vocab)
    print("vocabulary size:", vocab_size)

    print("\n[3] 정수 인코딩 + numpy 원-핫 인코딩")
    for idx, sentence in enumerate(sample_sentences, start=1):
        encoded = integer_encode(sentence, vocab)
        one_hot = to_one_hot_numpy(encoded, vocab_size)
        print(f"\n문장{idx}: {sentence}")
        print("정수 인코딩:", encoded)
        print("원-핫 shape:", one_hot.shape)
        print(one_hot)

    print("\n[4] 설명")
    print("- 원-핫의 1은 해당 위치 단어가 현재 토큰임을 의미")
    print("- vocabulary size가 커질수록 벡터 길이와 메모리 사용량 증가")
    print("- 장점: 직관적이고 단어 구분이 명확")
    print("- 한계: 희소(sparse)하고 의미 유사도를 표현하지 못함")
    print("- 실제 서비스는 임베딩을 더 자주 사용")


if __name__ == "__main__":
    main()

