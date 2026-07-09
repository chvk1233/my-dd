# Cursor AI용 Flask API 서버 구축 프롬프트

## 0. 역할

당신은 이 프로젝트의 **Flask API 백엔드 구축 전담 에이전트**입니다.

이미 Next.js 기반 프론트엔드는 구현되어 있고, 테스트도 1차 완료된 상태입니다.

이번 작업의 목표는 기존 Next.js 프론트엔드가 호출할 수 있는 **Flask 기반 API 서버**를 구축하는 것입니다.

이 Flask 서버는 단순 CRUD 서버가 아니라 다음 역할을 수행해야 합니다.

```text
1. Next.js Dashboard의 유일한 백엔드 진입점 역할
2. 사건 접수 API 제공
3. Kafka store-events 토픽으로 사건 이벤트 전달
4. Kafka 미사용 또는 장애 시 SQLite fallback 저장
5. consumer.py가 Kafka 이벤트를 읽고 AI 분석 수행
6. model_inference.py가 사건 유형, 심각도, 조치 필요 여부, 요약 생성
7. SQLite에 원본 사건과 분석 결과 저장
8. Dashboard 조회용 API 제공
9. 보고서, 직원 체크리스트, RAG 챗봇 API 제공
10. LLM API Key 없이도 mock 모드로 시연 가능
```

반드시 **기존 Next.js 프로젝트와 API 계약을 맞추는 것**을 최우선으로 하십시오.

---

## 1. 반드시 먼저 읽어야 할 문서와 자료

작업 시작 전 아래 문서를 먼저 읽고 현재 프로젝트 상태와 API 계약을 파악하십시오.

```text
docs/project-handbook.md
docs/test-plan.md
docs/error-log.md
architecture-analysis.md
package.json
src/shared/config/env.ts
src/shared/api/opsApi.ts
src/shared/api/httpClient.ts
src/entities/store-event/types.ts
src/entities/store-event/fallbackEvents.ts
src/store/useOpsStore.ts
src/widgets/api-fetch-dashboard/ApiFetchDashboard.tsx
```

참고 이미지가 프로젝트에 포함되어 있다면 함께 확인하십시오.

```text
전체 아키텍처 구조도.png
그래서 나오는 프로젝트 구조도.png
```

이미지 기준 핵심 흐름은 다음과 같습니다.

```text
Next.js Dashboard
→ Flask /ingest
→ Kafka store-events
→ consumer.py
→ model_inference.py
→ SQLite 저장
→ Dashboard에서 /events, /events/<event_id> 조회
→ /report, /tasks, /chat으로 LLM/RAG 결과 활용
```

단, 문서와 이미지를 그대로 믿고 구현하지 말고, 반드시 실제 Next.js 코드의 API 호출 함수와 타입 정의를 확인한 뒤 Flask 응답 형태를 맞추십시오.

---

## 2. 현재 시스템 전제

현재 프로젝트 전제는 다음과 같습니다.

```text
Frontend:
- Next.js 16.x App Router
- React 19.x
- Zustand
- Tailwind CSS 4
- npm
- 기본 API 주소: http://127.0.0.1:5000
- Flask API 실패 시 fallbackEvents mock 데이터 사용

Backend:
- 이번 작업에서 Flask API 서버를 새로 구축
- 포트: 5000
- CORS: http://localhost:3000 허용
- DB: SQLite
- Kafka topic: store-events
- LLM/RAG: mock 모드 우선, real API는 추후 확장
```

---

## 3. 최종 목표

이번 작업의 최종 목표는 다음입니다.

```text
1. Flask API 서버를 프로젝트에 추가한다.
2. Next.js가 호출하는 API 계약에 맞춰 응답한다.
3. Flask 서버 단독 실행이 가능해야 한다.
4. Kafka 없이도 SQLite fallback으로 시연 가능해야 한다.
5. Kafka가 있으면 /ingest → Kafka → consumer.py → model_inference.py → SQLite 흐름이 가능해야 한다.
6. LLM API Key 없이도 /report, /tasks, /chat이 mock 응답을 반환해야 한다.
7. 모든 주요 API는 curl 또는 pytest로 검증 가능해야 한다.
8. 구축 결과를 문서화한다.
```

---

## 4. 구축 위치 결정

먼저 현재 프로젝트 루트 구조를 확인하십시오.

Flask 백엔드가 아직 없다면 다음 구조 중 하나를 제안하고, 최소 변경 원칙에 따라 진행하십시오.

권장 구조:

```text
backend/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── routes/
│   ├── __init__.py
│   ├── health.py
│   ├── events.py
│   ├── ingest.py
│   ├── report.py
│   ├── tasks.py
│   └── chat.py
├── services/
│   ├── __init__.py
│   ├── db.py
│   ├── kafka_producer.py
│   ├── llm.py
│   └── rag.py
├── workers/
│   ├── __init__.py
│   └── consumer.py
├── ai/
│   ├── __init__.py
│   └── model_inference.py
├── data/
│   ├── docs/
│   │   ├── refund_policy.md
│   │   ├── customer_response_guide.md
│   │   └── store_operations_manual.md
│   └── ops.db
└── tests/
    ├── test_health.py
    ├── test_events.py
    ├── test_ingest.py
    ├── test_report_tasks_chat.py
    └── test_model_inference.py
```

주의:

```text
- 기존 Next.js 파일 구조를 변경하지 않는다.
- 기존 프론트엔드 코드를 Flask에 맞추기 위해 임의로 바꾸지 않는다.
- 먼저 Flask가 Next.js의 기존 계약에 맞추는 방식으로 구현한다.
```

---

## 5. 절대 지켜야 할 제약사항

아래 작업은 금지합니다.

```text
금지:
- 기존 Next.js 비즈니스 로직 변경
- Next.js API 클라이언트 구조 대규모 변경
- Zustand store 구조 변경
- fallbackEvents 삭제
- 프론트엔드 테스트 삭제 또는 약화
- .env 파일 직접 생성 또는 실제 시크릿 입력
- OpenAI, Gemini 등 실제 API Key 하드코딩
- Kafka가 없으면 전체 서버가 실행되지 않게 만드는 구조
- SQLite DB 파일을 git에 강제로 포함하는 구조
- 인증/인가 기능 임의 추가
- Docker/Kubernetes 설정을 먼저 복잡하게 추가
- 테스트 통과를 위해 실제 API 동작을 약화
```

---

## 6. 구현 전 확인할 것

구현 전 다음을 확인하십시오.

```text
1. Next.js의 API base URL
2. Next.js가 호출하는 API 함수 목록
3. 각 API 함수가 기대하는 request/response 타입
4. fallbackEvents의 필드 구조
5. Dashboard가 표시하는 필드
6. EventDetail 또는 Analysis Panel이 기대하는 analysis 필드
7. report/tasks/chat 버튼 또는 UI가 기대하는 응답 구조
8. 현재 테스트에서 mock한 API 응답 형태
```

확인 후 아래 형식으로 요약하십시오.

```markdown
## Flask API 구현 전 확인 결과

- Next.js API base URL:
- 확인한 API client 파일:
- 확인한 타입 파일:
- 필요한 엔드포인트:
- 핵심 응답 필드:
- Flask가 맞춰야 할 계약:
```

---

## 7. Flask API 엔드포인트 구현 기준

다음 엔드포인트를 구현하십시오.

### 7-1. GET /health

목적:

```text
Flask API, SQLite, Kafka 설정, 문서 수, LLM 모드 상태 확인
```

응답 예시:

```json
{
  "status": "ok",
  "events_count": 3,
  "docs_count": 3,
  "llm_provider": "mock",
  "kafka_topic": "store-events",
  "kafka_enabled": false,
  "db": "sqlite"
}
```

---

### 7-2. GET /events

목적:

```text
Dashboard의 사건 목록 표시
```

응답은 Next.js가 기대하는 구조에 맞추십시오.

기본 예시:

```json
{
  "count": 3,
  "events": [
    {
      "event_id": "evt-001",
      "store_id": "store-001",
      "event_type": "refund",
      "channel": "counter",
      "message": "환불 처리 지연 문의",
      "severity": "high",
      "status": "open",
      "requires_response": true,
      "predicted_type": "refund",
      "confidence": 0.92,
      "created_at": "2026-06-30T10:00:00"
    }
  ]
}
```

주의:

```text
- 실제 Next.js 타입이 createdAt을 쓰면 createdAt으로 맞춘다.
- 실제 Next.js 타입이 created_at을 쓰면 created_at으로 맞춘다.
- 문서 예시보다 실제 코드의 타입을 우선한다.
```

---

### 7-3. GET /events/<event_id>

목적:

```text
사건 상세와 AI 분석 결과 반환
```

응답 예시:

```json
{
  "event": {
    "event_id": "evt-001",
    "store_id": "store-001",
    "event_type": "refund",
    "channel": "counter",
    "message": "환불 처리 지연 문의",
    "severity": "high",
    "status": "open",
    "requires_response": true,
    "created_at": "2026-06-30T10:00:00"
  },
  "analysis": {
    "predicted_type": "refund",
    "sentiment": "negative",
    "severity": "high",
    "action_required": true,
    "summary": "환불 처리 지연으로 인한 고객 불만 사건입니다.",
    "confidence": 0.92,
    "source": "model_inference"
  }
}
```

존재하지 않는 event_id는 404를 반환하십시오.

---

### 7-4. POST /ingest

목적:

```text
Next.js에서 생성한 매장 사건을 Flask가 접수한다.
```

요청 예시:

```json
{
  "event_type": "refund",
  "channel": "counter",
  "message": "고객이 환불 지연으로 불만을 제기했습니다.",
  "severity_hint": "high",
  "store_id": "store-001"
}
```

동작 기준:

```text
1. request body validation
2. event_id 생성
3. received/open 상태의 event 생성
4. Kafka 사용 가능하면 store-events topic으로 publish
5. Kafka 사용 불가하면 SQLite에 직접 저장
6. model_inference fallback 분석을 즉시 수행하거나, 최소한 조회 가능한 상태로 저장
7. Next.js에 event accepted 응답 반환
```

응답 예시:

```json
{
  "message": "event accepted",
  "event": {
    "event_id": "evt-004",
    "store_id": "store-001",
    "event_type": "refund",
    "channel": "counter",
    "message": "고객이 환불 지연으로 불만을 제기했습니다.",
    "severity": "high",
    "status": "open",
    "requires_response": true,
    "created_at": "2026-06-30T10:10:00"
  }
}
```

주의:

```text
- Kafka가 없어도 /ingest는 실패하지 않아야 한다.
- Kafka 실패 시 fallback 저장 경로가 반드시 있어야 한다.
- 발표 시연을 위해 ingest 직후 /events에서 사건이 보여야 한다.
```

---

### 7-5. POST /report

목적:

```text
선택된 사건과 분석 결과를 바탕으로 점장 보고서 생성
```

요청:

```json
{
  "event_id": "evt-001"
}
```

응답:

```json
{
  "event_id": "evt-001",
  "result": "점장 보고서 본문..."
}
```

mock 보고서에는 다음을 포함하십시오.

```text
- 사건 요약
- 심각도
- 고객 불만 원인
- 권장 대응
- 재발 방지 포인트
```

---

### 7-6. POST /tasks

목적:

```text
선택된 사건을 바탕으로 직원 체크리스트 생성
```

요청:

```json
{
  "event_id": "evt-001"
}
```

응답:

```json
{
  "event_id": "evt-001",
  "result": "직원 체크리스트 본문..."
}
```

mock 체크리스트에는 다음을 포함하십시오.

```text
- 즉시 확인할 항목
- 고객에게 안내할 내용
- 점장에게 보고할 내용
- 후속 처리
```

---

### 7-7. POST /chat

목적:

```text
운영 문서 기반 RAG 챗봇 응답 생성
```

요청:

```json
{
  "question": "환불 요청 고객에게 먼저 확인할 것은?",
  "event_id": "evt-001"
}
```

응답:

```json
{
  "answer": "영수증과 결제 수단을 먼저 확인하고, 환불 가능 조건을 안내해야 합니다.",
  "sources": ["refund_policy.md", "customer_response_guide.md"]
}
```

주의:

```text
- API Key가 없어도 mock RAG 응답이 가능해야 한다.
- data/docs/ 문서를 간단히 검색해서 sources를 반환한다.
- 문서 검색이 실패해도 서버가 죽지 않아야 한다.
```

---

## 8. SQLite 설계 기준

SQLite는 최소한 다음 테이블을 가져야 합니다.

```sql
CREATE TABLE IF NOT EXISTS events (
  event_id TEXT PRIMARY KEY,
  store_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  channel TEXT,
  message TEXT NOT NULL,
  severity_hint TEXT,
  severity TEXT,
  status TEXT NOT NULL,
  requires_response INTEGER DEFAULT 0,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS analysis_results (
  event_id TEXT PRIMARY KEY,
  predicted_type TEXT,
  sentiment TEXT,
  severity TEXT,
  action_required INTEGER DEFAULT 0,
  summary TEXT,
  confidence REAL,
  source TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(event_id) REFERENCES events(event_id)
);
```

구현 기준:

```text
- 앱 시작 시 DB와 테이블을 자동 초기화한다.
- seed 데이터가 없으면 3건 정도의 데모 사건을 넣는다.
- seed 데이터는 Next.js fallbackEvents와 비슷한 유형으로 구성한다.
- DB 접근 코드는 services/db.py로 분리한다.
- SQL injection 방지를 위해 parameterized query를 사용한다.
```

---

## 9. model_inference.py 구현 기준

`ai/model_inference.py`를 구현하십시오.

처음에는 실제 딥러닝 모델이 없어도 됩니다.

규칙 기반 fallback 분석을 우선 구현하십시오.

입력:

```python
{
    "event_id": "evt-001",
    "event_type": "refund",
    "message": "환불 처리 지연으로 고객이 불만을 제기했습니다.",
    "severity_hint": "high"
}
```

출력:

```python
{
    "predicted_type": "refund",
    "sentiment": "negative",
    "severity": "high",
    "action_required": True,
    "summary": "환불 처리 지연으로 인한 고객 불만 사건입니다.",
    "confidence": 0.85,
    "source": "rule_fallback"
}
```

분석 규칙 예시:

```text
- message에 환불, 결제, 취소 포함 → refund
- message에 불만, 항의, 화남, 지연 포함 → negative
- severity_hint가 있으면 우선 반영
- message에 경찰, 폭언, 위협, 사고 포함 → high
- message에 문의, 확인 포함 → low 또는 medium
- action_required는 medium/high이면 true
```

---

## 10. Kafka 연동 기준

Kafka는 선택적으로 동작해야 합니다.

필수 원칙:

```text
- Kafka가 없어도 Flask API 서버는 실행되어야 한다.
- Kafka가 없어도 /ingest, /events, /report, /tasks, /chat은 동작해야 한다.
- Kafka 사용 가능 시 /ingest에서 store-events topic으로 publish한다.
- Kafka publish 실패 시 SQLite fallback 저장으로 전환한다.
```

환경변수 예시:

```text
KAFKA_ENABLED=false
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=store-events
```

주의:

```text
- .env 파일을 직접 만들지 않는다.
- .env.example만 생성한다.
- 실제 환경값은 사용자가 입력하게 한다.
```

`services/kafka_producer.py` 기준:

```text
- kafka-python 또는 confluent-kafka 중 하나를 선택한다.
- 새 패키지가 필요하면 requirements.txt에 추가한다.
- Kafka 연결 실패는 예외로 서버 전체를 죽이지 않는다.
- publish_event(event) 함수는 성공/실패 boolean을 반환한다.
```

---

## 11. consumer.py 구현 기준

`workers/consumer.py`를 구현하십시오.

역할:

```text
1. Kafka store-events topic 구독
2. 메시지 수신
3. model_inference.analyze_event 호출
4. events + analysis_results를 SQLite에 저장 또는 업데이트
5. 로그 출력
```

주의:

```text
- consumer.py는 Flask app.py와 별도 프로세스로 실행 가능해야 한다.
- Kafka가 없으면 명확한 안내 메시지를 출력하고 종료하거나 대기한다.
- consumer.py가 없어도 Flask API 기본 기능은 동작해야 한다.
```

실행 예시:

```bash
python workers/consumer.py
```

---

## 12. LLM/RAG mock 모드 기준

처음에는 실제 OpenAI/Gemini API 연동을 하지 마십시오.

`services/llm.py`와 `services/rag.py`는 mock 우선으로 구현하십시오.

기준:

```text
- LLM_PROVIDER=mock 이면 규칙 기반 텍스트 생성
- OPENAI_API_KEY 없어도 /report, /tasks, /chat 정상 동작
- data/docs/*.md 파일을 간단히 읽고 keyword search로 sources 반환
- real LLM은 함수 구조만 남기고 실제 호출은 추후 확장 포인트로 표시
```

---

## 13. CORS 기준

Next.js 개발 서버와 연동하기 위해 CORS를 설정하십시오.

허용 origin:

```text
http://localhost:3000
http://127.0.0.1:3000
```

주의:

```text
- 개발용 전체 허용은 가능하지만, README에 로컬 개발용이라고 명시한다.
- preflight OPTIONS 요청도 정상 처리되어야 한다.
```

---

## 14. requirements.txt 기준

필요 최소 패키지를 사용하십시오.

예상 패키지:

```text
Flask
flask-cors
pytest
python-dotenv
```

Kafka를 구현하는 경우 다음 중 하나를 선택하십시오.

```text
kafka-python
또는
confluent-kafka
```

주의:

```text
- 불필요하게 무거운 프레임워크를 추가하지 않는다.
- LangChain, LlamaIndex는 이번 1차 구축에서는 추가하지 않는다.
- RAG는 우선 간단한 markdown keyword search로 구현한다.
```

---

## 15. 테스트 기준

Flask API에 대해 pytest 테스트를 작성하십시오.

테스트 대상:

```text
1. GET /health
2. GET /events
3. GET /events/<event_id>
4. POST /ingest
5. POST /report
6. POST /tasks
7. POST /chat
8. model_inference.analyze_event
9. DB 초기화 및 seed 데이터
```

테스트 기준:

```text
- Flask test client 사용
- 실제 Kafka 서버에 의존하지 않음
- 실제 LLM API에 의존하지 않음
- SQLite는 테스트용 임시 DB 사용
- 모든 API는 JSON 응답
- 실패 케이스도 포함
```

실패 케이스:

```text
- 존재하지 않는 event_id
- message 누락
- 잘못된 JSON body
- event_id 없는 report/tasks 요청
- question 없는 chat 요청
```

---

## 16. 통합 실행 검증 기준

Flask 서버를 실행한 뒤 다음 curl 검증이 가능해야 합니다.

```bash
curl http://127.0.0.1:5000/health

curl http://127.0.0.1:5000/events

curl http://127.0.0.1:5000/events/evt-001

curl -X POST http://127.0.0.1:5000/ingest \
  -H "Content-Type: application/json" \
  -d "{\"event_type\":\"refund\",\"channel\":\"counter\",\"message\":\"환불 처리 지연으로 고객이 불만을 제기했습니다.\",\"severity_hint\":\"high\",\"store_id\":\"store-001\"}"

curl -X POST http://127.0.0.1:5000/report \
  -H "Content-Type: application/json" \
  -d "{\"event_id\":\"evt-001\"}"

curl -X POST http://127.0.0.1:5000/tasks \
  -H "Content-Type: application/json" \
  -d "{\"event_id\":\"evt-001\"}"

curl -X POST http://127.0.0.1:5000/chat \
  -H "Content-Type: application/json" \
  -d "{\"event_id\":\"evt-001\",\"question\":\"환불 요청 고객에게 먼저 확인할 것은?\"}"
```

---

## 17. Next.js 연동 검증 기준

Flask 서버 실행 후 Next.js와 통합 검증하십시오.

순서:

```text
1. Flask 서버 실행: python app.py 또는 flask run
2. Next.js 서버 실행: npm run dev
3. 브라우저에서 http://localhost:3000 접속
4. Dashboard에서 API 상태 확인
5. 사건 생성 폼에서 신규 사건 생성
6. POST /ingest 성공 확인
7. 사건 목록에 신규 사건 표시 확인
8. 사건 상세에서 AI 분석 결과 확인
9. 보고서 생성 확인
10. 체크리스트 생성 확인
11. RAG Chat 질문/답변 확인
```

주의:

```text
- Next.js 코드를 먼저 고치려 하지 않는다.
- 응답 스키마 불일치가 있으면 먼저 Flask 응답을 Next.js 타입에 맞춘다.
- 정말 Next.js 수정이 필요하면 변경 이유와 대상 파일을 보고하고 진행한다.
```

---

## 18. 문서화 기준

작업 후 다음 문서를 생성하거나 업데이트하십시오.

```text
backend/README.md
backend/docs/api-contract.md
backend/docs/flask-build-result.md
```

문서 내용:

```markdown
# Flask API 서버 구축 결과

## 1. 목적

## 2. 프로젝트 구조

## 3. 실행 방법

## 4. 환경변수

## 5. API 목록

## 6. 요청/응답 예시

## 7. SQLite 스키마

## 8. Kafka 연동 방식

## 9. Kafka 없이 동작하는 fallback 모드

## 10. LLM/RAG mock 모드

## 11. 테스트 방법

## 12. Next.js 연동 방법

## 13. 남은 이슈

## 14. 다음 단계
```

기존 `docs/project-handbook.md`에도 Flask API 연동 요약을 추가할 수 있습니다.

단, 기존 내용을 삭제하지 마십시오.

---

## 19. 실행 완료 보고 형식

작업 완료 후 아래 형식으로 보고하십시오.

```markdown
# Flask API 서버 구축 완료 보고

## 상태

✅ 완료 / ⚠️ 부분 완료 / ❌ 실패

## 구축 위치

- 백엔드 경로:
- 실행 파일:
- 포트:
- DB:
- Kafka 사용 여부:
- LLM 모드:

## 구현한 API

| Method | Path | 상태 | 설명 |
|---|---|---|---|
| GET | /health |  |  |
| GET | /events |  |  |
| GET | /events/<event_id> |  |  |
| POST | /ingest |  |  |
| POST | /report |  |  |
| POST | /tasks |  |  |
| POST | /chat |  |  |

## 구현한 주요 파일

| 파일 | 역할 |
|---|---|
|  |  |

## SQLite 스키마

- events:
- analysis_results:

## Kafka 연동

- topic:
- producer:
- consumer:
- Kafka 미실행 시 fallback:

## LLM/RAG

- mock 모드:
- 운영 문서:
- sources 반환:

## 테스트 결과

| 검증 항목 | 명령어 | 결과 |
|---|---|---|
| 의존성 설치 | pip install -r requirements.txt |  |
| Flask 테스트 | pytest |  |
| health 확인 | curl /health |  |
| events 확인 | curl /events |  |
| ingest 확인 | curl /ingest |  |
| report/tasks/chat 확인 | curl |  |
| Next.js 연동 | 브라우저 확인 |  |

## 수정한 기존 Next.js 파일

| 파일 | 수정 여부 | 이유 |
|---|---|---|
|  |  |  |

## 남은 이슈

- 

## 사용자 확인 필요 사항

- 

## 문서 위치

- backend/README.md
- backend/docs/api-contract.md
- backend/docs/flask-build-result.md
```

---

## 20. 작업 시작 지시

지금부터 다음 순서로 진행하십시오.

```text
1. docs/project-handbook.md, docs/test-plan.md, architecture-analysis.md를 읽는다.
2. Next.js API client와 타입 파일을 확인한다.
3. Flask가 맞춰야 할 API 계약을 정리한다.
4. backend/ 구조가 없으면 최소 구조로 생성한다.
5. Flask app.py와 CORS를 구성한다.
6. SQLite 초기화와 seed 데이터를 구현한다.
7. /health, /events, /events/<event_id>를 먼저 구현한다.
8. /ingest를 구현하고 Kafka 실패 시 SQLite fallback 저장을 적용한다.
9. ai/model_inference.py에 규칙 기반 fallback 분석을 구현한다.
10. workers/consumer.py를 구현하되 Flask 기본 실행과 분리한다.
11. /report, /tasks, /chat mock LLM/RAG API를 구현한다.
12. pytest 테스트를 작성한다.
13. curl로 API를 검증한다.
14. 가능하면 Next.js와 통합 실행을 검증한다.
15. backend 문서를 작성한다.
16. 최종 보고 형식에 맞춰 결과를 보고한다.
```