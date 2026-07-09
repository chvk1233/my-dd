# Flask API 서버 구축 프롬프트 점검 결과

> **점검 대상:** `docs/apiServerBuild.md`  
> **참조 문서:** `docs/architecture-analysis.md`, 구조도 PNG 2종, Next.js 소스  
> **점검일:** 2026-06-30  
> **점검 범위:** 프롬프트 정확성·누락·수정 권장사항 (코드 구현 없음)

---

## 목차

1. [종합 평가](#1-종합-평가)
2. [구조도·프로젝트 방향 일치 여부](#2-구조도프로젝트-방향-일치-여부)
3. [architecture-analysis.md 대비 점검](#3-architecture-analysismd-대비-점검)
4. [Next.js 현재 상태](#4-nextjs-현재-상태)
5. [apiServerBuild.md 누락·보완 항목](#5-apiserverbuildmd-누락보완-항목)
6. [apiServerBuild.md 수정 권장 패치](#6-apiserverbuildmd-수정-권장-패치)
7. [최종 체크리스트](#7-최종-체크리스트)
8. [다음 단계](#8-다음-단계)

---

## 1. 종합 평가

| 항목 | 판정 | 비고 |
|---|---|---|
| 구조도·Flask 구축 방향 | ✅ 적합 | Next.js → Flask → Kafka → AI → SQLite → LLM/RAG |
| API 엔드포인트·URL | ✅ 정확 | 7개 경로가 `opsApi.ts`와 일치 |
| 백엔드 폴더 구조 (`backend/`) | ✅ 적합 | `architecture-analysis.md`와 호환 |
| Next.js 타입 계약 | ⚠️ 부분 불일치 | `created_at`, `HealthResponse` 확장 필드 등 |
| 문서 경로 참조 | ❌ 오류 | `architecture-analysis.md` 경로 누락 |
| 통합 검증 시나리오 (섹션 17) | ✅ 적합 | 현재 대시보드 UI와 일치 |

**결론:** `apiServerBuild.md`는 Flask 구축 프롬프트로 **사용 가능**하나, 본 문서 6절 수정 사항을 `apiServerBuild.md`에 반영한 뒤 사용하는 것을 권장합니다.

---

## 2. 구조도·프로젝트 방향 일치 여부

### 2-1. 일치하는 내용

- Flask = Next.js Dashboard의 **유일한 백엔드 진입점**
- 브라우저는 Kafka에 **직접 연결하지 않음**
- `POST /ingest` → Kafka `store-events` → `consumer.py` → `model_inference.py` → SQLite
- Kafka 미사용·장애 시 **SQLite fallback** 저장
- `GET /events`, `GET /events/<event_id>` 조회
- `POST /report`, `/tasks`, `/chat` — LLM/RAG (mock 우선)
- 5분 시연 흐름(접수 → 전달 → 분석 → 활용)과 `apiServerBuild.md` 섹션 17 통합 검증 순서

### 2-2. 보완 권장

| 항목 | 권장 |
|---|---|
| 구축 단계 | `architecture-analysis.md` 8절 Phase 1~5를 `apiServerBuild.md` 20절과 명시적으로 연결 |
| 시연 완료 기준 | [`그래서 나오는 프로젝트 구조도.png`](../그래서%20나오는%20프로젝트%20구조도.png) 8단계를 Flask **완료 체크리스트**로 추가 |
| 백엔드 폴더명 | `architecture-analysis.md`의 `flask-api/` 예시 대신 **`backend/`로 통일** 명시 |

---

## 3. architecture-analysis.md 대비 점검

### 3-1. 문서 경로 오류

| `apiServerBuild.md` 현재 | 올바른 경로 |
|---|---|
| `architecture-analysis.md` (섹션 1, 20) | **`docs/architecture-analysis.md`** |

### 3-2. API URL — 정확함

| Method | Path | Next.js 함수 (`src/shared/api/opsApi.ts`) |
|---|---|---|
| GET | `/health` | `fetchHealth()` |
| GET | `/events` | `fetchEvents()` |
| GET | `/events/<event_id>` | `fetchEventAnalysis(id)` |
| POST | `/ingest` | `ingestEvent()` |
| POST | `/report` | `fetchReport()` |
| POST | `/tasks` | `fetchTasks()` |
| POST | `/chat` | `fetchChat()` |

**Base URL:** `http://127.0.0.1:5000` (`NEXT_PUBLIC_API_BASE_URL` in `src/shared/config/env.ts`)

### 3-3. 응답 필드명 — 수정 필요

#### `StoreEvent` (`src/entities/store-event/types.ts`)

실제 필드:

```text
event_id, event_type, channel, message?, severity?, severity_hint?,
sentiment?, status, requires_response, confidence?, predicted_type?, timestamp?
```

| `apiServerBuild.md` 예시 | 실제 Next.js | 수정 권장 |
|---|---|---|
| `created_at` | **`timestamp`** (optional) | API 응답은 `timestamp` 사용. DB 내부 `created_at`은 허용 |
| `store_id` in event | **타입에 없음** | optional, 필수 아님 |
| `status: "open"` | fallback은 `"mock"` | seed는 `"open"` 가능, 타입은 `string` |

#### `GET /health` — `HealthResponse`

Next.js 타입 필수 5개:

```json
{
  "status": "ok",
  "events_count": 3,
  "docs_count": 3,
  "llm_provider": "mock",
  "kafka_topic": "store-events"
}
```

`apiServerBuild.md` 7-1의 `kafka_enabled`, `db`는 **TypeScript 타입에 없음**. 추가 필드는 허용하되 위 5개는 **필수**로 명시 필요.

`ApiHealthPanel`은 `status`, `events_count`만 UI에 표시합니다.

#### `AnalysisResult` — `GET /events/<event_id>`

Next.js `AnalysisResult`:

```text
predicted_type?, sentiment?, severity?, confidence?, source?
```

`apiServerBuild.md` 7-3의 `action_required`, `summary`는 **TypeScript 타입·UI에 없음**.

| 구분 | 처리 |
|---|---|
| SQLite / `model_inference.py` | `action_required`, `summary` 유지 가능 |
| API `analysis` JSON | 최소 `predicted_type`, `severity`, `confidence`, `source` (+ `sentiment` 권장) |
| `EventAnalysisPanel` UI | `predicted_type`, `severity`, `confidence`, `source` 표시 |

---

## 4. Next.js 현재 상태

현재 `ZustandDashboard` (`src/widgets/api-fetch-dashboard/ApiFetchDashboard.tsx`)는 다음 API를 호출합니다.

| UI / Store action | API |
|---|---|
| `loadDashboard()` | `GET /health` + `GET /events` |
| `IngestEventForm` → `ingestEvent` | `POST /ingest` |
| `selectEvent` → `loadAnalysis` | `GET /events/<id>` |
| 보고서 버튼 → `loadReport` | `POST /report` |
| 체크리스트 버튼 → `loadTasks` | `POST /tasks` |
| `LocalChatPanel` → `askChat` | `POST /chat` |

`apiServerBuild.md`에 **“프론트 API 클라이언트는 7개 엔드포인트를 이미 호출 중”** 이라고 명시하는 것을 권장합니다. 섹션 17 통합 검증 시나리오는 **현재 코드와 일치**합니다.

### `IngestPayload` 실제 전송값

`IngestEventForm` (`src/features/events/event-ingest/IngestEventForm.tsx`)은 `store_id`를 **보내지 않습니다**:

```json
{
  "event_type": "refund",
  "channel": "counter",
  "message": "환불 처리 지연 문의",
  "severity_hint": "high"
}
```

Flask `/ingest`는 **`store_id` 미전송 시 기본값** (예: `"store-001"`) 처리가 필요합니다.

### Next.js TypeScript API 계약 (Flask 단일 기준)

| 엔드포인트 | Request 타입 | Response 타입 |
|---|---|---|
| GET `/health` | — | `HealthResponse` |
| GET `/events` | — | `EventsResponse` |
| GET `/events/<event_id>` | — | `AnalysisResponse` |
| POST `/ingest` | `IngestPayload` | `SimulateResponse` |
| POST `/report` | `EventActionRequest` | `ReportResponse` |
| POST `/tasks` | `EventActionRequest` | `TasksResponse` |
| POST `/chat` | `ChatRequest` | `ChatResponse` |

---

## 5. apiServerBuild.md 누락·보완 항목

| # | 누락 항목 | 권장 반영 위치 |
|---|---|---|
| 1 | `docs/architecture-analysis.md` 정확한 경로 | 섹션 1, 20 |
| 2 | Next.js TypeScript 계약 표 | 섹션 6 |
| 3 | `NEXT_PUBLIC_API_BASE_URL` | 섹션 2, 13 |
| 4 | 읽을 파일: `IngestEventForm`, `EventAnalysisPanel`, `LocalChatPanel` | 섹션 1 |
| 5 | Phase 1~5 구축 순서 | 섹션 20 (`architecture-analysis.md` 8절 참조) |
| 6 | 5분 시연 8단계 체크리스트 | 섹션 17 보강 또는 신규 섹션 |
| 7 | ingest 후 목록 반영 지연 (Kafka 비동기) | 섹션 7-4, README |
| 8 | Kafka 없을 때 ingest 즉시 inference + SQLite | 섹션 7-4 (시연용) |
| 9 | `requires_response` JSON boolean | 섹션 8 (SQLite INTEGER ↔ API boolean) |
| 10 | 운영 문서 FAQ | `data/docs/faq.md` 추가 또는 3개 문서에 포함 명시 |
| 11 | Flask 연동 후 `npm run verify` | 섹션 17, 19 |
| 12 | 선택 E2E: `npm run test:e2e` (Flask 실행 시) | `TESTSCENARIO.md` 참조 |

---

## 6. apiServerBuild.md 수정 권장 패치

### 6-1. 섹션 1 — 읽을 문서

```diff
 docs/project-handbook.md
 docs/test-plan.md
 docs/error-log.md
-architecture-analysis.md
+docs/architecture-analysis.md
 package.json
 ...
 src/widgets/api-fetch-dashboard/ApiFetchDashboard.tsx
+src/features/api-health/ApiHealthPanel.tsx
+src/features/events/event-ingest/IngestEventForm.tsx
+src/features/events/event-analysis/EventAnalysisPanel.tsx
+src/features/rag-chat/LocalChatPanel.tsx
```

### 6-2. 섹션 7-1 `/health` 응답 예시

필수 5개 필드만 타입 계약. `kafka_enabled`, `db` 등은 optional 확장:

```json
{
  "status": "ok",
  "events_count": 3,
  "docs_count": 3,
  "llm_provider": "mock",
  "kafka_topic": "store-events"
}
```

### 6-3. 섹션 7-2·7-3 event 필드

```diff
- "created_at": "2026-06-30T10:00:00"
+ "timestamp": "2026-06-30T10:00:00"
```

`store_id`는 `StoreEvent` 타입에 없으므로 optional. seed 데이터는 `fallbackEvents.ts` 3건과 유사하게 구성.

### 6-4. 섹션 7-4 ingest 보완 문구 (추가)

```text
- IngestEventForm은 store_id를 보내지 않을 수 있음 → Flask에서 기본 store_id 부여
- Kafka 미사용 시: ingest 요청 처리 시 model_inference 즉시 실행 후 SQLite 저장 (시연 즉시 반영)
- Kafka 사용 시: consumer 비동기 처리로 목록 반영 1~3초 지연 가능 → README에 명시
```

### 6-5. 섹션 20 작업 시작

```diff
-1. docs/project-handbook.md, docs/test-plan.md, architecture-analysis.md를 읽는다.
+1. docs/project-handbook.md, docs/architecture-analysis.md, docs/test-plan.md, docs/apiServerBuildResult.md를 읽는다.
```

---

## 7. 최종 체크리스트

| # | 점검 항목 | 결과 |
|---|---|---|
| 1 | 구조도 흐름과 Flask 역할 | ✅ |
| 2 | API URL 7개 | ✅ |
| 3 | `docs/architecture-analysis.md` 경로 | ❌ 수정 필요 |
| 4 | `created_at` → `timestamp` | ❌ 수정 필요 |
| 5 | `HealthResponse` 5필드 필수 | ❌ 수정 필요 |
| 6 | `AnalysisResult` vs `action_required`/`summary` | ⚠️ 명시 필요 |
| 7 | ingest `store_id` 기본값 | ⚠️ 보완 필요 |
| 8 | Phase 1~5·5분 시연 체크리스트 | ⚠️ 추가 권장 |
| 9 | Next.js 7 API 이미 연동 | ⚠️ 명시 권장 |
| 10 | `NEXT_PUBLIC_API_BASE_URL` | ⚠️ 추가 권장 |
| 11 | 통합 후 `npm run verify` | ⚠️ 추가 권장 |

---

## 8. 다음 단계

1. `apiServerBuild.md`에 본 문서 6절 수정 권장 패치 반영
2. `backend/` Flask 프로젝트 구축 시작 (Phase 1: `/health`, `/events`, `/events/<id>`)
3. Flask 실행 후 Next.js `npm run dev` 통합 검증
4. 실제 구축 완료 시 `backend/docs/flask-build-result.md`에 구축 결과 기록

---

## 관련 문서

| 문서 | 설명 |
|---|---|
| [docs/apiServerBuild.md](./apiServerBuild.md) | 점검 대상 — Flask 구축 프롬프트 |
| [docs/architecture-analysis.md](./architecture-analysis.md) | Flask 구축 분석 (구조도 기반) |
| [docs/project-handbook.md](./project-handbook.md) | Next.js 운영 문서 |
| [docs/test-plan.md](./test-plan.md) | Frontend 테스트 계획·결과 |
| [전체 아키텍처 구조도.png](../전체%20아키텍처%20구조도.png) | 시스템 아키텍처 원본 |
| [그래서 나오는 프로젝트 구조도.png](../그래서%20나오는%20프로젝트%20구조도.png) | 5분 시연 흐름 원본 |
