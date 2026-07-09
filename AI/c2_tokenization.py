import re
from pathlib import Path

import pandas as pd


def whitespace_tokenize(text: str) -> list[str]:
    return text.split()


def simple_korean_morph_like_tokenize(text: str) -> list[str]:
    # 외부 형태소 라이브러리 없이 실행 가능하도록 간단 정규식 기반 토큰화
    # 한글/영문/숫자를 분리해 숫자·시간·온도 같은 정보를 최대한 보존한다.
    return re.findall(r"[가-힣]+|[A-Za-z]+|\d+|[%℃도분시원]+", text)


def main() -> None:
    csv_path = Path(__file__).parent / "training_events_1200.csv"
    df = pd.read_csv(csv_path)

    if "message" not in df.columns:
        raise ValueError("message 컬럼이 없습니다.")

    sample = df["message"].dropna().head(10).tolist()

    print("[1] message 샘플 10개 토큰화 비교")
    for idx, msg in enumerate(sample, start=1):
        split_tokens = whitespace_tokenize(msg)
        morph_like_tokens = simple_korean_morph_like_tokenize(msg)
        print(f"\n--- 샘플 {idx} ---")
        print("원문:", msg)
        print("split() :", split_tokens)
        print("morph-like:", morph_like_tokens)

    print("\n[2] 사건 판단 중요 토큰 예시")
    important_keywords = ["환불", "지연", "온도", "결제", "불만", "위협", "품질", "10", "2", "12"]
    print(important_keywords)

    print("\n[3] 해석")
    print("- split() 장점: 구현이 매우 간단하고 빠름")
    print("- split() 한계: 조사/어미 분리가 어렵고 기호 결합 단어 처리 약함")
    print("- 형태소 분석(또는 형태소 유사 분해) 필요 이유: 사건 판단 핵심 어휘를 더 정확히 추출 가능")


if __name__ == "__main__":
    main()

