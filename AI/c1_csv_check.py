import pandas as pd
from pathlib import Path


def main() -> None:
    csv_path = Path(__file__).parent / "training_events_1200.csv"
    print(f"[1] CSV 경로: {csv_path}")

    # 1) CSV 읽기
    df = pd.read_csv(csv_path)

    # 2) 상위 샘플 확인
    print("\n[2] df.head()")
    print(df.head())

    # 3) 기본 정보 확인
    print("\n[3] df.info()")
    df.info()

    # 4) 컬럼 목록 확인
    print("\n[4] 컬럼 목록")
    print(list(df.columns))

    # 5) message 샘플 5개
    print("\n[5] message 샘플 5개")
    if "message" in df.columns:
        print(df["message"].head(5).to_string(index=False))
    else:
        print("message 컬럼이 없습니다. 컬럼명을 다시 확인하세요.")

    # 6) label 후보 컬럼 탐색
    # event_type, severity, sentiment, requires_response 등을 후보로 본다.
    print("\n[6] label 역할 후보 컬럼")
    candidates = [col for col in df.columns if col in ("event_type", "label", "severity", "sentiment", "requires_response")]
    print(candidates if candidates else "명시적 label 후보를 찾지 못했습니다.")

    # 7) 결측치 확인
    print("\n[7] 결측치 개수")
    print(df.isna().sum())


if __name__ == "__main__":
    main()

