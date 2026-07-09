# add-part 확장 작업 전체 정리 (1~7단계)

`add-part.md` 기반 확장 작업을 단계별로 정리한 최종 문서입니다.
`add-part-me.md` 참고필요

---

## 1단계 — baseline 추가

### 작업 내용

- `add-part.md` 1번 요구사항에 따라 **TF-IDF + LogisticRegression** baseline 모델 구축
- **키워드 기반 fallback** 규칙을 add-part.md 스펙에 맞게 정리
- `training_events_1200.csv`로 sentiment / severity 각각 학습
- Flask `model_inference.py`에 baseline 추론 연동
- 학습 결과: sentiment 정확도 100%, severity 정확도 68.3%

### 생성 파일

| 파일 | 위치 |
|------|------|
| `keyword_rules.py` | `AI/`, `flask/backend/ai/` |
| `train_baseline.py` | `AI/` |
| `baseline_predict.py` | `AI/`, `flask/backend/ai/` |
| `sentiment_pipeline.joblib` | `AI/models/`, `flask/backend/ai/models/` |
| `severity_pipeline.joblib` | `AI/models/`, `flask/backend/ai/models/` |
| `requirements.txt` (수정) | `AI/`, `flask/backend/` |

### 생성 파일 설명

| 파일 | 설명 |
|------|------|
| `keyword_rules.py` | add-part.md 키워드(부정 감정, high/medium/low)로 sentiment·severity 예측 |
| `train_baseline.py` | char n-gram TF-IDF + LogisticRegression 학습·저장 스크립트 |
| `baseline_predict.py` | 학습된 joblib pipeline 로드 후 추론 (`source: tfidf_lr`) |
| `*_pipeline.joblib` | sentiment·severity 각각의 TF-IDF+LR 학습 모델 |
| `model_inference.py` (수정) | baseline 우선 → 키워드 fallback 추론 체인 |

### 입력 프롬프트

> 1단계 시작

### agent 답변

- add-part.md 키워드 규칙을 `AI/`, `flask/backend/ai/`에 각각 구현
- `train_baseline.py`로 1200건 CSV에서 sentiment/severity 모델 학습 후 `AI/models/`, `flask/backend/ai/models/`에 저장
- `model_inference.py`를 수정해 TF-IDF+LR을 1차 분석기로, 키워드 규칙을 fallback으로 연결
- `scikit-learn`, `joblib` 의존성 추가 및 `pytest` 2건 통과 확인
- 추론 우선순위: `tfidf_lr` → `keyword_fallback`

---

## 2단계 — baseline 상세 설명

### 작업 내용

- 1단계에서 구축한 baseline의 **구조·데이터·예측 흐름**을 문서화
- TF-IDF 설정, 학습 결과, 키워드 fallback 규칙, Flask 연동 경로 설명
- Part C 전처리와의 관계, Hugging Face 모델과의 위치 정리

### 생성 파일

| 파일 | 위치 |
|------|------|
| `baseline_readme.md` | `AI/` |

### 생성 파일 설명

| 파일 | 설명 |
|------|------|
| `baseline_readme.md` | baseline 정의, 전체 구조도, 학습 데이터·라벨 분포, TF-IDF+LR 상세, 키워드 규칙, 예측 흐름, 실행 방법, Part C·HF와의 관계를 담은 상세 설명서 |

### 입력 프롬프트

> 2단계 진행

### agent 답변

- `AI/baseline_readme.md` 작성 (11개 섹션)
- baseline = TF-IDF+LR(주) + 키워드 fallback(보조) 구조 설명
- `message` → `analyze_event()` → sentiment/severity/confidence/source → Dashboard 흐름 도식화
- 학습 데이터 1200건, sentiment(negative/neutral), severity(low/medium/high) 분포 기록
- 실행 명령(`train_baseline.py`, `baseline_predict.py`, pytest) 정리

---

## 3단계 — baseline 문제점 분석

### 작업 내용

- `add-part.md` 2번 요구: baseline 오분류 가능 메시지 **10개** 정리
- **sentiment vs severity**가 다른 이유 및 대비 예시 문장 작성
- TF-IDF+LR·키워드 모델의 **구조적 한계** 분석
- 실제 baseline 예측 결과를 반영해 오분류 사례 표 작성

### 생성 파일

| 파일 | 위치 |
|------|------|
| `baseline_limitations.md` | `AI/` |

### 생성 파일 설명

| 파일 | 설명 |
|------|------|
| `baseline_limitations.md` | 완곡 부정·키워드 부재·클래스 편향 등 한계 유형, 오분류 10예시(실제 tfidf_lr/keyword 예측 포함), sentiment≠severity 설명, HF 도입 필요성 결론 |

### 입력 프롬프트

> 3단계 시작

### agent 답변

- `add-part.md` 예시 문장 `괜찮긴 한데 다시는 안 올 것 같아요.`를 중심으로 오분류 분석
- 키워드 모델은 "괜찮"에 속아 neutral로 오판, tfidf_lr은 학습 편향으로 negative/medium 쏠림 현상 확인
- sentiment(감정)와 severity(긴급도)는 독립 개념임을 표와 예시 10문장으로 설명
- `AI/baseline_limitations.md`에 한계 유형·결론·4단계 HF 탐색 연결 정리

---

## 4단계 — Hugging Face 모델 3~5개 탐색

### 작업 내용

- `add-part.md` 3번 요구: 한국어 BERT 계열 **후보 5개** 선정·분석
- Colab 호환, 문장 분류, baseline 대비 문맥 이해 개선 여부 검토
- 매장 고객 message 도메인 관점에서 적합도 평가
- 5단계 사용자 선택용 비교표(A~E) 작성

### 생성 파일

| 파일 | 위치 |
|------|------|
| `hf_model_survey.md` | `AI/` |

### 생성 파일 설명

| 파일 | 설명 |
|------|------|
| `hf_model_survey.md` | KLUE RoBERTa, KLUE BERT, KcELECTRA, KcBERT, KoELECTRA v3 후보별 장단점·HF ID·Colab 테스트 방법·선택지 A~E 비교표 |

### 입력 프롬프트

> 4단계 진행

### agent 답변

- add-part.md 4가지 조건(한국어, 분류, 문맥, Colab) 기준으로 5개 모델 탐색
- 매장 고객 message ≈ 댓글형 구어체 → **KcELECTRA/KcBERT** 도메인 적합도 높음 판단
- 범용·재현성 → **KLUE RoBERTa/BERT** 유리 판단
- Colab 파인튜닝 코드 예시, `baseline_limitations.md` 오분류 사례와의 기대 개선 매핑
- 5단계 선택용 A~E 표 제공, 1차 추천 **C. KcELECTRA** 제시

---

## 5단계 — Hugging Face 모델 선택 확정

### 작업 내용

- 4단계 탐색 결과를 바탕으로 사용자에게 모델 선택 안내
- 사용자가 **모델 C (KcELECTRA)** 선택 확정
- 선택 이유, 미선택 후보 비교, 6·7단계 적용 계획 문서화

### 생성 파일

| 파일 | 위치 |
|------|------|
| `hf_model_selection.md` | `AI/` |
| `add-part-endme.md` (초안) | 루트 |

### 생성 파일 설명

| 파일 | 설명 |
|------|------|
| `hf_model_selection.md` | 선택 모델 `beomi/KcELECTRA-base` 확정 기록, 선택 이유, 미선택 후보 비교, 6단계 파인튜닝·연동 계획 |
| `add-part-endme.md` | 전체 단계 진행 상황 추적용 문서 (본 문서로 최종 갱신) |

### 입력 프롬프트

> 모델 C 선택 후 5단계 진행

### agent 답변

- 사용자 선택 **C — `beomi/KcELECTRA-base` (KcELECTRA)** 확정
- 선택 근거: 댓글/구어체 사전학습 → 매장 고객 message 도메인 최적, baseline 완곡 부정 한계 보완 기대
- `AI/hf_model_selection.md`에 선택 기록·6단계 적용 계획(train_hf, hf_predict, model_inference 연동) 정리
- 추론 우선순위 확정: `kcelectra_hf` → `tfidf_lr` → `keyword_fallback`

---

## 6단계 — KcELECTRA 프로젝트 적용

### 작업 내용

- **10분 제한** fast 학습: 600건 샘플, 1 epoch, encoder freeze, classifier만 학습
- sentiment / severity KcELECTRA 파인튜닝 모델 저장
- Flask `hf_predict.py` + `model_inference.py` 연동
- `transformers`, `torch`, `accelerate` 의존성 추가

### 생성 파일

| 파일 | 위치 |
|------|------|
| `train_hf_kcelectra.py` | `AI/` |
| `hf_predict.py` | `AI/`, `flask/backend/ai/` |
| `models/hf/sentiment/` | `AI/`, `flask/backend/ai/` |
| `models/hf/severity/` | `AI/`, `flask/backend/ai/` |
| `model_inference.py` (수정) | `flask/backend/ai/` |
| `requirements.txt` (수정) | `AI/`, `flask/backend/` |
| `test_model_inference.py` (수정) | `flask/backend/tests/` |

### 생성 파일 설명

| 파일 | 설명 |
|------|------|
| `train_hf_kcelectra.py` | KcELECTRA 파인튜닝 스크립트 (fast 모드: 샘플 제한·1 epoch·encoder freeze) |
| `hf_predict.py` | 학습된 HF 모델 로드·추론 (`source: kcelectra_hf`), lazy load로 torch 오류 시 fallback |
| `models/hf/sentiment/` | sentiment 분류용 파인튜닝 모델·토크나이저 |
| `models/hf/severity/` | severity 분류용 파인튜닝 모델·토크나이저 |
| `model_inference.py` | 추론 우선순위: KcELECTRA → TF-IDF+LR → 키워드 |

### 입력 프롬프트

> 6단계 진행  
> 제한 시간 설정 : 10 분

### agent 답변

- 10분 제한에 맞춰 fast 학습 모드 적용 (600 samples, 1 epoch, encoder freeze)
- sentiment·severity KcELECTRA 모델을 `AI/models/hf/`, `flask/backend/ai/models/hf/`에 저장
- `hf_predict.py` lazy load 구현, `model_inference.py`에 3단계 fallback 체인 연결
- `AI/hf_predict.py` 단독 실행 시 `kcelectra_hf` 예측 확인 (예: `괜찮긴 한데…` → negative/medium, confidence 0.79)
- pytest 2건 통과, 전체 재학습은 `--max-samples 0` 명령으로 가능

---

## 7단계 — 구동 테스트

### 작업 내용

- Flask API 서버 기동 후 `/health`, `/events`, `/ingest`, `/events/<id>` 검증
- 완곡 부정 메시지 ingest 테스트 (`괜찮긴 한데 다시는 안 올 것 같아요.`)
- pytest 전체 **15 passed**
- Next.js `npm install` + `npm run dev` → Dashboard HTTP 200 확인
- Windows PyTorch DLL 간헐 오류 시 `tfidf_lr` fallback 동작 확인

### 생성 파일

| 파일 | 위치 |
|------|------|
| `step7_integration_test.md` | `AI/` |
| `add-part-endme.md` (갱신) | 루트 |

### 생성 파일 설명

| 파일 | 설명 |
|------|------|
| `step7_integration_test.md` | Flask·Next.js·pytest·KcELECTRA·fallback·알려진 이슈·재현 명령을 담은 구동 테스트 상세 기록 |
| `add-part-endme.md` | 1~7단계 전체 완료 상태 및 최종 정리 (본 문서) |

### 입력 프롬프트

> 7단계 진행

### agent 답변

- Flask `http://127.0.0.1:5000` 기동, API 엔드포인트 정상 응답 확인
- `POST /ingest`로 완곡 부정 메시지 접수 → `evt-004`, sentiment negative, severity medium 확인
- `pytest tests/` **15 passed**
- Next.js `http://localhost:3000` 기동, Dashboard 렌더(HTTP 200) 확인
- HF 로드 성공 시 `kcelectra_hf`, PyTorch DLL 실패 시 `tfidf_lr` 자동 fallback — 서버 중단 없이 end-to-end 흐름 완주
- **add-part 확장 1~7단계 전체 완료** 선언

---

## 전체 요약

| 단계 | 핵심 산출 | 상태 |
|------|-----------|------|
| 1 | TF-IDF+LR baseline + 키워드 fallback | ✅ |
| 2 | `baseline_readme.md` | ✅ |
| 3 | `baseline_limitations.md` | ✅ |
| 4 | `hf_model_survey.md` (후보 5개) | ✅ |
| 5 | `hf_model_selection.md` (C: KcELECTRA) | ✅ |
| 6 | KcELECTRA 파인튜닝 + Flask 연동 | ✅ |
| 7 | 구동 테스트 + `step7_integration_test.md` | ✅ |

### 최종 추론 우선순위

```
kcelectra_hf  →  tfidf_lr  →  keyword_fallback
```

### 구동 명령 (재현)

```powershell
# 터미널 1 — Flask
cd flask\backend
$env:PYTHONPATH = "."
python app.py

# 터미널 2 — Next.js
cd nextjs
npm install
npm run dev
```

브라우저: `http://localhost:3000`
