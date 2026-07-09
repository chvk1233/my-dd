# Baseline 모델 상세 설명

1단계에서 구축한 **TF-IDF + LogisticRegression baseline**과 **키워드 fallback**의 구조·데이터·예측 흐름을 정리한 문서입니다.

---

## 1. Baseline이란?

매장 운영 관제센터에서 고객 `message`를 받아 **감정(sentiment)** 과 **긴급도(severity)** 를 자동 분류하는 1차 모델입니다.

| 구분 | 방식 | source 값 |
|------|------|-----------|
| 주 모델 | TF-IDF + LogisticRegression | `tfidf_lr` |
| 보조 모델 | add-part.md 키워드 규칙 | `keyword_fallback` |

모델 파일이 없거나 로드에 실패하면 키워드 규칙으로 자동 전환됩니다.

---

## 2. 전체 구조

```
고객 message
    │
    ▼
┌─────────────────────────────────────┐
│  model_inference.analyze_event()    │
│  (flask/backend/ai/)                │
└─────────────────────────────────────┘
    │
    ├─► baseline_predict.predict()     ──► TF-IDF + LR (우선)
    │       sentiment_pipeline.joblib
    │       severity_pipeline.joblib
    │
    └─► keyword_rules (fallback)       ──► 키워드 매칭
            predict_sentiment()
            predict_severity()
    │
    ▼
분석 결과: sentiment, severity, confidence, source, ...
    │
    ▼
Dashboard / SQLite 저장
```

---

## 3. 학습 데이터

| 항목 | 내용 |
|------|------|
| 파일 | `AI/training_events_1200.csv` |
| 건수 | 1,200건 |
| 입력 컬럼 | `message` (고객 메시지) |
| 라벨 컬럼 | `sentiment`, `severity` |

### 라벨 분포

| 라벨 | 클래스 | 건수 |
|------|--------|------|
| sentiment | negative | 900 |
| sentiment | neutral | 300 |
| severity | medium | 600 |
| severity | high | 450 |
| severity | low | 150 |

- `sentiment`는 **negative / neutral** 2클래스 (positive 없음)
- `severity`는 **low / medium / high** 3클래스
- 두 라벨은 **독립 모델**로 각각 학습합니다.

---

## 4. TF-IDF + LogisticRegression 모델

### 4-1. 왜 이 조합인가?

| 단계 | 역할 |
|------|------|
| TF-IDF | 문장을 숫자 벡터로 변환 (단어/문자 빈도 기반) |
| LogisticRegression | 벡터를 받아 클래스 확률로 분류 |

딥러닝 없이도 빠르게 학습·추론할 수 있어 **baseline(기준선)** 으로 적합합니다.  
이후 Hugging Face BERT 모델과 성능을 비교하는 기준이 됩니다.

### 4-2. 벡터화 설정

```python
TfidfVectorizer(
    analyzer="char_wb",    # 문자 n-gram (한국어 띄어쓰기 한계 보완)
    ngram_range=(2, 4),    # 2~4글자 조합
    min_df=2,              # 2회 미만 등장 토큰 제외
    max_features=5000,   # 최대 5000차원
)
```

한국어는 단순 `split()` 토큰화보다 **문자 n-gram**이 형태소 분석기 없이도 비교적 안정적입니다.

### 4-3. 분류기

```python
LogisticRegression(max_iter=1000, random_state=42)
```

- `sentiment` 전용 pipeline 1개
- `severity` 전용 pipeline 1개  
→ 총 **2개의 독립 pipeline** (각각 TF-IDF + LR 포함)

### 4-4. 학습·평가 방식

- train/test = **80% / 20%** (`stratify=y`로 클래스 비율 유지)
- 평가 지표: accuracy, precision, recall, f1-score

### 4-5. 학습 결과 (1단계 실행 기준)

| 모델 | 테스트 정확도 | 비고 |
|------|---------------|------|
| sentiment | **100%** | negative/neutral 구분 매우 안정 |
| severity | **68.3%** | 3클래스라 난이도 높음, 개선 여지 있음 |

severity 정확도가 낮은 이유는 medium/high/low 경계가 문맥에 따라 달라지기 때문이며, 3단계(문제점 분석)에서 다룹니다.

---

## 5. 키워드 Fallback 모델

add-part.md 스펙에 맞춘 규칙 기반 분류입니다. ML 모델이 없을 때 사용합니다.

### 5-1. Sentiment (감정)

| 조건 | 결과 |
|------|------|
| 부정 키워드 포함 | `negative` |
| 그 외 | `neutral` |

**부정 키워드:** 환불, 항의, 불만, 지연, 누락, 취소, 화남

### 5-2. Severity (긴급도)

우선순위: `severity_hint` → high 키워드 → medium → low → 기본값 medium

| 우선순위 | 키워드 | 결과 |
|----------|--------|------|
| 1 | (API에서 전달된 hint) | hint 그대로 사용 |
| 2 | 환불, 중복 결제, 사고, 위험, 강하게 항의 | `high` |
| 3 | 지연, 대기, 누락, 품절 | `medium` |
| 4 | 문의, 확인, 요청 | `low` |
| 5 | 해당 없음 | `medium` |

---

## 6. 예측 흐름 (상세)

### 6-1. Flask 서버에서의 흐름

```
POST /ingest  또는  Kafka Consumer
        │
        ▼
model_inference.analyze_event(event)
        │
        ├─ predicted_type  ← 키워드 기반 event_type 추정 (refund/delay/quality/general)
        │
        ├─ sentiment, severity
        │     ├─ baseline_predict.predict(message) 성공 → tfidf_lr
        │     └─ 실패 → keyword_rules → keyword_fallback
        │
        ├─ severity_hint가 있으면 severity는 hint 우선 (tfidf_lr 사용 시에도)
        │
        ├─ action_required ← severity가 medium/high이면 True
        ├─ summary ← predicted_type + message 앞 40자
        └─ confidence ← predict_proba 최댓값 (tfidf_lr) 또는 규칙 기반 추정
        │
        ▼
SQLite 저장 → GET /events, /events/<id> → Dashboard 표시
```

### 6-2. confidence 계산

| source | 계산 방식 |
|--------|-----------|
| `tfidf_lr` | sentiment·severity predict_proba 중 **최댓값** |
| `keyword_fallback` | 기본 0.7 + (event_type 일치 +0.05) + (문장 길이 +0.05), 최대 0.95 |

### 6-3. 예측 예시

**입력**

```json
{
  "message": "환불 처리 지연으로 고객이 불만을 제기했습니다.",
  "event_type": "refund",
  "severity_hint": "high"
}
```

**출력 (tfidf_lr 사용 시)**

```json
{
  "predicted_type": "refund",
  "sentiment": "negative",
  "severity": "high",
  "action_required": true,
  "confidence": 0.92,
  "source": "tfidf_lr",
  "summary": "환불 관련 사건: 환불 처리 지연으로 고객이 불만을 제기했습니다."
}
```

---

## 7. 파일 구조

```
my-dd/
├── AI/
│   ├── training_events_1200.csv      # 학습 데이터
│   ├── keyword_rules.py              # 키워드 규칙
│   ├── train_baseline.py             # 학습 스크립트
│   ├── baseline_predict.py           # 추론 (AI 폴더용)
│   ├── baseline_readme.md            # 본 문서
│   ├── requirements.txt
│   └── models/
│       ├── sentiment_pipeline.joblib
│       └── severity_pipeline.joblib
│
└── flask/backend/ai/
    ├── keyword_rules.py              # Flask용 키워드 규칙
    ├── baseline_predict.py           # 추론 (Flask용)
    ├── model_inference.py            # analyze_event() 진입점
    └── models/
        ├── sentiment_pipeline.joblib   # 학습 시 자동 복사
        └── severity_pipeline.joblib
```

---

## 8. 실행 방법

### 8-1. 의존성 설치

```powershell
cd AI
pip install -r requirements.txt
```

### 8-2. 모델 학습

```powershell
cd AI
python train_baseline.py
```

출력: sentiment/severity 정확도, classification_report, 모델 저장 경로

### 8-3. 단독 추론 테스트

```powershell
cd AI
python baseline_predict.py
```

### 8-4. Flask 연동 확인

```powershell
cd flask\backend
pip install -r requirements.txt
$env:PYTHONPATH = "."
python -m pytest tests/test_model_inference.py -q
```

---

## 9. Part C 전처리와의 관계

| Part C 단계 | Baseline에서의 역할 |
|-------------|---------------------|
| C-1 CSV 확인 | `training_events_1200.csv` 구조 파악 → 학습 데이터로 사용 |
| C-2 토큰화 | TF-IDF는 내부적으로 char n-gram 토큰화 수행 |
| C-3 정수 인코딩 | TF-IDF가 희소 정수 행렬로 변환 (직접 word_to_index는 사용 안 함) |
| C-4 원-핫 | TF-IDF 가중치 벡터가 이에 해당 (단, 차원 축소·가중치 적용) |

Baseline은 Part C에서 배운 전처리 개념을 **scikit-learn Pipeline**으로 실무에 가깝게 적용한 형태입니다.

---

## 10. Hugging Face 모델과의 위치

| 항목 | Baseline (현재) | HF BERT (4~6단계 예정) |
|------|-----------------|------------------------|
| 문맥 이해 | 약함 (단어/문자 빈도) | 강함 (사전학습 문맥) |
| 학습 속도 | 빠름 | 느림 (GPU 권장) |
| 완곡 표현 | 취약 | 상대적으로 우수 |
| 용도 | 기준선·빠른 프로토타입 | 성능 개선 목표 |

3단계에서 baseline 한계를 분석한 뒤, 4~6단계에서 HF 모델로 대체·보완합니다.

---

## 11. 요약

- **입력:** 고객 `message` 한 문장
- **출력:** `sentiment`, `severity`, `confidence`, `source` 등
- **주 모델:** TF-IDF(char 2~4gram) + LogisticRegression × 2 (sentiment / severity)
- **보조:** add-part.md 키워드 규칙 (모델 미로드 시)
- **연동:** `model_inference.py` → Flask `/ingest`, Consumer → Dashboard
