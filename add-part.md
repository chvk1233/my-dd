1. baselien 추가
- TF-IDF + LogisticRegression 모델 적용 필요
- 고객 메시지 데이터셋 추가 필요
- 컬럼 안내
  - `message` : 고객 메시지
  - `sentiment` : 감정 라벨
  - `severity` : 긴급도 라벨
- 키워드 기반 모델 제작
  - 부정 감정 후보: 환불, 항의, 불만, 지연, 누락, 취소, 화남
  - high 후보: 환불, 중복 결제, 사고, 위험, 강하게 항의
  - medium 후보: 지연, 대기, 누락, 품절
  - low 후보: 문의, 확인, 요청

2. Baseline 문제 분석
- baseline 모델이 틀릴 가능성이 높은 메세지가 발견
  - '괜찮긴 한데 다시는 안 올 것 같아요.'
- 위 문장은 부정에 매우 가까움
- 고객 감정/긴급도 baseline 모델이 틀릴 가능성이 높은
고객 메시지 예시를 10개 생성 필요

- 감정 분석
- sentiment와 severity는 같은 값이 아님.
  - sentiment와 severity가 왜 다른 개념인지 설명 진행
- sentiment와 severity가 다른 예시 문장 생성 필요

- 고객 감정/긴급도 baseline 모델의 한계를 분석
- 분석 내용 설명 필요


3. Hugging Face 모델 탐색
- Hugging Face에서 사용할 수 있는 한국어 BERT 계열 모델을 탐색
- 조건
  - 1. 한국어 문장을 처리할 수 있어야 한다.
  - 2. 문장 분류에 사용할 수 있어야 한다.
  - 3. baseline보다 문맥 이해가 좋아야 한다.
  - 4. Colab에서 불러와 테스트할 수 있어야 한다.

- 후보 모델 3개 ~ 5개 산정 후 분석
