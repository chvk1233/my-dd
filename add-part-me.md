# add-part.md 분석 및 적용 정리

`add-part.md` 요구사항을 `my-dd` 프로젝트와 대조·분석한 결과를 정리한 문서입니다.

---

## 1. add-part.md 요구사항 (업데이트 반영)

### 1-1. baseline 추가

- TF-IDF + LogisticRegression 모델 적용
- 고객 메시지 데이터셋 (`message`, `sentiment`, `severity`)
- 키워드 기반 모델
  - 부정 감정: 환불, 항의, 불만, 지연, 누락, 취소, 화남
  - high: 환불, 중복 결제, 사고, 위험, 강하게 항의
  - medium: 지연, 대기, 누락, 품절
  - low: 문의, 확인, 요청

### 1-2. Baseline 문제 분석

- baseline이 틀릴 가능성이 높은 메시지 분석
  - 예: `괜찮긴 한데 다시는 안 올 것 같아요.` → 표면은 완화되어 보이지만 부정 감정에 가까움
- 위와 같은 **오분류 가능성이 높은 고객 메시지 예시 10개** 생성 필요
- `sentiment`와 `severity`는 **같은 값이 아님**
  - 두 개념이 왜 다른지 설명
  - sentiment와 severity가 다른 예시 문장 생성 필요
- 고객 감정/긴급도 baseline 모델의 **한계 분석 및 설명** 필요

### 1-3. Hugging Face 모델 탐색

- 한국어 BERT 계열 모델 탐색 (후보 3~5개 선정 후 분석)
- 조건
  1. 한국어 문장 처리 가능
  2. 문장 분류에 사용 가능
  3. baseline보다 문맥 이해가 좋아야 함
  4. Colab에서 불러와 테스트 가능

---

## 2. 프로젝트 적용 가능성 (전체 결론)

**결론: 적용 가능.** 다만 섹션별로 준비 상태가 다름.

| 섹션 | 현재 상태 | 적용 가능성 |
|------|-----------|-------------|
| 1. baseline 추가 | 데이터·파이프라인 있음 / TF-IDF+LR·키워드 정렬 미완 | ⚠️ 부분 가능 |
| 2. Baseline 문제 분석 | 분석 문서·예시 문장·한계 설명 산출물 없음 | ❌ 신규 작성 필요 |
| 3. Hugging Face 탐색 | 모델 후보 조사·Colab 테스트 없음 | ❌ 신규 조사 필요 |

---

## 3. 섹션 1 — baseline 추가 (코드 대조)

### 이미 갖춰진 것

| 항목 | 내용 |
|------|------|
| 데이터셋 | `AI/training_events_1200.csv` (1200건, `message`/`sentiment`/`severity` 포함) |
| 분석 연결 | `model_inference.py` → `consumer.py` / `db.process_ingested_event()` → `/ingest` → Dashboard |
| 키워드 모델 | `flask/backend/ai/model_inference.py`에 rule_fallback 구현 (키워드 목록은 add-part.md와 불일치) |

### 아직 없는 것

- TF-IDF + LogisticRegression 학습 스크립트
- `scikit-learn` 의존성 및 모델 저장/로드
- `model_inference.py`와 baseline 모델 연동

### 권장 적용 위치

| 작업 | 위치 |
|------|------|
| 모델 학습 | `AI/train_baseline.py` |
| 모델 파일 | `AI/models/` 또는 `flask/backend/ai/models/` |
| 추론 연동 | `flask/backend/ai/model_inference.py` |
| 키워드 규칙 | `model_inference.py` 또는 `keyword_rules.py` |

권장 패턴: **LR primary + 키워드 fallback**. API/UI 응답 형식이 같으면 Next.js 변경은 최소화 가능.

---

## 4. 섹션 2 — Baseline 문제 분석 (신규 요구 해석)

### 4-1. 왜 baseline이 틀리기 쉬운가

TF-IDF + 키워드 baseline은 **표면 단어·빈도**에 의존합니다.  
`괜찮긴 한데 다시는 안 올 것 같아요.`처럼 **완곡·부정·이중 부정** 표현은 키워드가 약하거나 없어 오분류되기 쉽습니다.

| 한계 유형 | 설명 | 예시 |
|-----------|------|------|
| 완곡 부정 | 겉으로는 중립/긍정처럼 보임 | "괜찮긴 한데 다시는 안 올 것 같아요." |
| 키워드 부재 | 학습/규칙에 없는 표현 | "기대했던 것과 달라서 실망했어요." |
| 문맥 의존 | 앞뒤 맥락 없이 단어만 보면 판단 어려움 | "그냥 그렇습니다." |
| irony/반어 | 실제 감정과 표면 표현 불일치 | "정말 잘 하시네요(불만 톤)" |

→ **오분류 가능 메시지 10개**는 위 유형을 골고루 포함해 작성하는 것이 적절합니다.

### 4-2. sentiment vs severity (다른 개념)

| 구분 | sentiment (감정) | severity (긴급도) |
|------|------------------|-------------------|
| 의미 | 고객이 느끼는 감정 톤 | 운영 대응 우선순위·긴급성 |
| 값 예 | negative, neutral, positive | low, medium, high |
| 핵심 | "기분이 어떤가" | "얼마나 빨리 대응해야 하는가" |

**다른 예시 문장**

| 문장 | sentiment | severity | 이유 |
|------|-----------|----------|------|
| "환불 가능 여부만 확인해 주세요." | neutral | low | 단순 문의, 감정 격하지 않음 |
| "9분 넘게 기다렸는데 아직 안 나왔어요." | negative | medium | 불만 있으나 즉각 위험은 아님 |
| "결제가 두 번 됐는데 즉시 확인 부탁드립니다." | negative | high | 금전 피해 가능, 즉시 대응 필요 |
| "오늘 커피 맛은 괜찮았어요." | positive | low | 긍정적이나 운영 긴급 이슈 아님 |

→ baseline은 두 라벨을 **독립적으로** 학습·예측해야 하며, 같은 문장이라도 sentiment와 severity가 다를 수 있습니다.

### 4-3. 프로젝트 반영 시 필요 산출물

- 오분류 가능 메시지 10개 (+ 예상 라벨·오분류 이유)
- sentiment ≠ severity 설명문
- 대비 예시 문장 세트
- baseline 한계 분석 문서 (키워드/TF-IDF 한계 중심)

→ 산출 위치 후보: `AI/baseline_limitations.md` (§2 표 참고: 현재 미작성)

---

## 5. 섹션 3 — Hugging Face 모델 탐색 (신규 요구 해석)

### 5-1. 요구 의도

baseline(TF-IDF+LR) 한계를 넘어 **문맥 이해**가 가능한 한국어 사전학습 모델을 Colab에서 시험 적용하는 단계입니다.

### 5-2. 탐색 시 확인할 항목 (후보 3~5개 선정용)

| 항목 | 확인 내용 |
|------|-----------|
| 모델명/저장소 | Hugging Face model id |
| 한국어 지원 | 한국어 코퍼스 사전학습 여부 |
| 태스크 | `AutoModelForSequenceClassification` 등 분류 헤드 사용 가능 여부 |
| 라이선스 | 상업/연구 사용 가능 여부 |
| Colab 호환 | `transformers` + GPU 메모리 내 로드 가능 여부 |
| baseline 대비 | 완곡 표현·문맥 의존 문장에서 개선 여부 |

### 5-3. 탐색 후보 예시 (조사 시작점)

실제 선정·벤치마크는 Colab에서 검증 필요. 아래는 **탐색 시작용 후보**입니다.

| 후보 | Hugging Face id (예) | 특징 |
|------|----------------------|------|
| KLUE BERT | `klue/bert-base` | 한국어 벤치마크 기반, 분류 태스크에 널리 사용 |
| KcBERT | `beomi/kcbert-base` | 댓글/구어체에 강점 |
| KoELECTRA | `monologg/koelectra-base-v3-discriminator` | ELECTRA 구조, 분류 성능 우수 사례多 |
| KR-BERT | `snunlp/KR-BERT-base` | 한국어 특화 토크나이저 |
| KoBERT (SKT) | `skt/kobert-base-v1` | 초기 한국어 BERT, 레거시 호환 |

### 5-4. 프로젝트 연동 관점

- **지금 단계**: 탐색·Colab 실험 (Flask 서버 연동은 이후)
- Part C 전처리(C-1~C-4)와 연결: BERT는 내부 토크나이저 사용 → 원-핫 대신 **서브워드 임베딩**으로 전환
- `model_inference.py`의 `source`를 `"bert_hf"` 등으로 확장 가능

→ §2 표 참고: HF 연동 코드·의존성(`transformers`, `torch`) 현재 없음

---

## 6. 통합 작업 우선순위

| 순서 | 작업 | 산출물 |
|------|------|--------|
| 1 | 키워드 규칙을 add-part.md 스펙에 맞게 정리 | `keyword_rules.py` 또는 `model_inference.py` 수정 |
| 2 | TF-IDF + LogisticRegression 학습 | `AI/train_baseline.py`, `AI/models/` |
| 3 | baseline 한계·sentiment/severity 분석 문서 | `AI/baseline_limitations.md` 등 |
| 4 | 오분류 가능 메시지 10개 + 대비 예시 | 분석 문서 또는 CSV 보조 |
| 5 | Hugging Face 후보 3~5개 Colab 비교 | `AI/hf_model_survey.md`, Colab 노트북 |
| 6 | (선택) 최종 모델을 `model_inference.py`에 연동 | API `source` 필드 확장 |

---

## 7. 적용 시 주의점

1. `requirements.txt`에 `scikit-learn` 추가 필요 (baseline)
2. Hugging Face 사용 시 `transformers`, `torch` 추가 및 GPU/메모리 고려
3. `test_model_inference.py`는 baseline/BERT 도입 후 기대값 수정 필요
4. 한국어 TF-IDF는 char n-gram 또는 형태소 토큰화 검토 권장
5. Flask 서버는 당분간 rule_fallback 유지하고, Colab 실험 후 단계적 연동 권장

---

## 8. 이전 대화·프롬프트 정리

| 순서 | 사용자 프롬프트 | 당시 작업·결과 |
|------|-----------------|----------------|
| 1 | add-part.md를 프로젝트에 적용 가능한지 확인 | §3 기준으로 **적용 가능** 판단. 데이터·파이프라인은 있으나 TF-IDF+LR 미구현 |
| 2 | 위 분석 내용을 add-part-me.md에 정리 | add-part.md 1번(baseline) 중심으로 최초 문서 작성 |
| 3 | add-part.md 업데이트 반영 + 이전 프롬프트 하단 정리 + 중복 제거 | 2·3번 섹션(Baseline 문제 분석, HF 탐색) 분석 추가, §6·§8·§9로 문서 재구성 |

---

## 9. 한 줄 요약

add-part.md는 **baseline 구축 → baseline 한계 분석 → Hugging Face 대안 탐색**의 3단계 확장 과제이며, `my-dd`는 데이터·파이프라인은 갖춰져 있으나 **학습 코드·분석 문서·HF 탐색 산출물은 아직 없다**. 우선 TF-IDF+LR baseline과 한계 분석을 완료한 뒤, Colab에서 한국어 BERT 후보를 비교하는 순서가 자연스럽다.
