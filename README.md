# my-dd — AI 매장 운영 관제센터

Flask API + Next.js Dashboard + AI 분석 파이프라인으로 구성된 매장 운영 관제센터 프로젝트입니다.

| 구성 | 경로 |
|------|------|
| 백엔드 | `flask/backend` |
| 프론트엔드 | `nextjs` |
| AI·전처리 | `AI` |

---

## 문서 목록 (루트)

과제 안내·분석·제출용 마크다운 파일입니다.

| 파일 | 설명 |
|------|------|
| `part-start.md` | 퀴즈 전체 개요, 출발점(기본 Dashboard/백엔드), 완성 기준, 제출물 안내 |
| `part-a.md` | Part A 과제: Flask API 확장 (분석·설계·구현 프롬프트, `/health`·`/events`·`/ingest` 등) |
| `part-b.md` | Part B 과제: 관제센터 UI 확장 (Zustand, API 상태·분석·보고서 패널 설계) |
| `part-c.md` | Part C 과제: `training_events_1200.csv` 텍스트 전처리 (토큰화·인코딩 실습) |
| `part-end.md` | 최종 제출 체크리스트 (`part-result.md`에 정리할 항목 1~11번 지시) |
| `part-procedure.md` | 과제 진행 절차 기록 (문서 분석, 코드 대조, Part C·add-part 작업 이력) |
| `part-result.md` | 최종 제출 답안 (구조 설명, API 역할, 전처리 결과, 프롬프트 정리 등) |
| `add-part.md` | add-part 확장 과제 원본 (baseline, 문제 분석, Hugging Face 탐색 요구사항) |
| `add-part-me.md` | `add-part.md` 요구사항을 프로젝트 코드와 대조·분석한 문서 |
| `add-part-endme.md` | add-part 1~7단계 작업 전체 정리 (단계별 작업·파일·프롬프트·결과) |

---

## 문서 목록 (add-part 1~7단계)

add-part 확장 작업에서 작성된 마크다운 파일입니다.

| 단계 | 파일 | 설명 |
|------|------|------|
| 1단계 | *(전용 md 없음)* | baseline 추가 — `AI/train_baseline.py`, `keyword_rules.py` 등 코드로 구현. 상세는 `add-part-endme.md` 1단계 참고 |
| 2단계 | `AI/baseline_readme.md` | TF-IDF+LR baseline·키워드 fallback 구조, 학습 데이터, 예측 흐름, 실행 방법 |
| 3단계 | `AI/baseline_limitations.md` | baseline 오분류 10예시, sentiment≠severity 설명, TF-IDF·키워드 한계 분석 |
| 4단계 | `AI/hf_model_survey.md` | Hugging Face 한국어 모델 5개 탐색·비교 (KLUE, KcELECTRA 등), Colab 테스트 안내 |
| 5단계 | `AI/hf_model_selection.md` | 적용 모델 **C (`beomi/KcELECTRA-base`)** 선택 확정 및 선택 이유 |
| 6단계 | *(전용 md 없음)* | KcELECTRA 파인튜닝·Flask 연동 — `AI/train_hf_kcelectra.py`, `hf_predict.py` 등. 상세는 `add-part-endme.md` 6단계 참고 |
| 7단계 | `AI/step7_integration_test.md` | Flask·Next.js 구동 테스트 결과, API 검증, pytest, fallback 동작 기록 |

### Part C 연계 문서 (`AI/`)

| 파일 | 설명 |
|------|------|
| `AI/c5_pipeline_connection.md` | 토큰화·인코딩 전처리가 관제센터 파이프라인(ingest → 분석 → Dashboard) 어디에 들어가는지 설명 |

---

## 빠른 실행

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

### 모델 재생성 (clone 후)

```powershell
cd AI
pip install -r requirements.txt
python train_baseline.py
python train_hf_kcelectra.py
```

모델 가중치(`*.safetensors`, `*.joblib`)는 `.gitignore`로 제외되어 있습니다. 위 스크립트로 재학습하세요.

---

## 분석 추론 우선순위

```
kcelectra_hf  →  tfidf_lr  →  keyword_fallback
```

---

## 읽는 순서 추천

1. `part-start.md` → `part-a.md` → `part-b.md` → `part-c.md` (기본 과제)
2. `add-part.md` → `add-part-me.md` → `add-part-endme.md` (확장 과제)
3. `AI/baseline_readme.md` → `baseline_limitations.md` → `hf_model_survey.md` → `hf_model_selection.md` → `step7_integration_test.md`
4. `part-result.md` (제출 답안 확인)

---

## 프로젝트 구동 전 준비 사항

Git에는 **모델 가중치**, **`node_modules`**, **빌드 결과물** 등이 포함되지 않습니다.  
clone 또는 pull 이후에는 아래 작업을 먼저 수행해야 정상적으로 구동됩니다.

### 사전 요구사항

| 항목 | 권장 버전 |
|------|-----------|
| Python | 3.10 이상 |
| Node.js | 18 이상 (Next.js 16) |
| npm | Node.js에 포함 |

Kafka는 기본적으로 **비활성화**(`KAFKA_ENABLED=false`)되어 있어, 별도 설치 없이도 로컬 구동이 가능합니다.

### 1. Python 패키지 설치

AI 학습 스크립트용:

```powershell
cd AI
pip install -r requirements.txt
```

Flask 백엔드 실행용:

```powershell
cd flask\backend
pip install -r requirements.txt
```

> 가상환경(`.venv`) 사용을 권장합니다. PyTorch·transformers 설치 시 용량이 큽니다.

### 2. AI 모델 파일 재생성

`.gitignore`로 아래 파일이 제외되어 있으므로, **학습 스크립트를 직접 실행**해 모델을 생성해야 합니다.

```text
**/*.joblib
**/*.safetensors
**/models/hf/
```

학습 스크립트는 `AI/models/`와 `flask/backend/ai/models/` **양쪽에 자동 저장**합니다.

```powershell
cd AI
python train_baseline.py
python train_hf_kcelectra.py
```

| 스크립트 | 생성 파일 | 소요 시간 |
|----------|-----------|-----------|
| `train_baseline.py` | `sentiment_pipeline.joblib`, `severity_pipeline.joblib` | 수 초~수십 초 |
| `train_hf_kcelectra.py` | `models/hf/sentiment/`, `models/hf/severity/` (safetensors) | 수 분~수십 분 (PC·GPU에 따라 다름) |

KcELECTRA 학습은 기본값이 빠른 모드(600샘플, 1 epoch)입니다. 전체 데이터로 학습하려면:

```powershell
python train_hf_kcelectra.py --max-samples 0 --epochs 3
```

KcELECTRA 로딩에 실패해도 API는 `tfidf_lr` → `keyword_fallback` 순으로 동작합니다.

### 3. Next.js 패키지 설치

`node_modules`는 Git에 포함하지 않습니다.

```powershell
cd nextjs
npm install
```

### 4. 서버 실행

**터미널 1 — Flask 백엔드**

```powershell
cd flask\backend
$env:PYTHONPATH = "."
python app.py
```

- 주소: `http://127.0.0.1:5000`
- 상태 확인: `GET http://127.0.0.1:5000/health`

**터미널 2 — Next.js 프론트엔드**

```powershell
cd nextjs
npm run dev
```

- 주소: `http://localhost:3000`
- API 연결: 기본값 `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:5000`

### 5. 구동 순서 요약

1. `AI` — `pip install -r requirements.txt`
2. `AI` — `train_baseline.py`, `train_hf_kcelectra.py` 실행
3. `flask/backend` — `pip install -r requirements.txt`
4. `flask/backend` — `python app.py` 실행
5. `nextjs` — `npm install` → `npm run dev` 실행
6. 브라우저에서 `http://localhost:3000` 접속

### 6. (선택) 백엔드 테스트

```powershell
cd flask\backend
$env:PYTHONPATH = "."
pytest
```

### 7. Git에 포함되지 않는 주요 항목

```text
node_modules/          # nextjs 의존성
.next/                 # Next.js 빌드 캐시
**/*.joblib            # TF-IDF baseline 모델
**/*.safetensors       # Hugging Face 모델 가중치
**/models/hf/          # KcELECTRA 파인튜닝 결과
flask/backend/data/*.db  # SQLite DB (실행 시 자동 생성)
.env                   # 환경 변수 (있을 경우)
```

### 8. 자주 발생하는 이슈

| 증상 | 대응 |
|------|------|
| 분석 결과가 항상 키워드 기반 | `train_baseline.py` 미실행 → baseline 모델 없음 |
| KcELECTRA 미사용, TF-IDF만 동작 | `train_hf_kcelectra.py` 미실행 또는 Windows에서 PyTorch DLL 로딩 실패 |
| 프론트 API 연결 실패 | Flask가 `5000` 포트에서 실행 중인지 확인 |
| `pytest` import 오류 | `flask/backend`에서 `$env:PYTHONPATH = "."` 설정 후 실행 |
