# Flask API 서버 구축 결과

## 1. 목적

Next.js 대시보드의 유일한 백엔드 진입점으로 Flask API 서버를 구축했습니다.

## 2. 프로젝트 구조

```
backend/
├── app.py
├── config.py
├── requirements.txt
├── routes/          # 7개 API 엔드포인트
├── services/        # db, kafka, llm, rag
├── workers/         # consumer.py
├── ai/              # model_inference.py
├── data/docs/       # RAG 운영 문서
└── tests/           # pytest
```

## 3. 실행 방법

```bash
cd backend
pip install -r requirements.txt
python app.py
```

## 4. 환경변수

`.env.example` 참고. Kafka/LLM은 mock 모드 기본.

## 5. API 목록

7개 엔드포인트 모두 구현 완료 (health, events, events/<id>, ingest, report, tasks, chat).

## 6. Next.js 타입 계약

- `timestamp` 필드 사용 (`created_at` 아님)
- `HealthResponse` 5필드 필수
- `requires_response` JSON boolean
- ingest 시 `store_id` 기본값 `store-001`

## 7. SQLite 스키마

`events`, `analysis_results` 테이블. 시작 시 자동 초기화 및 seed 3건.

## 8. Kafka

선택적. `KAFKA_ENABLED=false` 기본. 실패 시 SQLite fallback.

## 9. LLM/RAG

mock 모드. `data/docs/*.md` 키워드 검색 기반.

## 10. 테스트

`pytest` — Flask test client, 임시 SQLite DB 사용.

## 11. Next.js 연동

Flask `5000` + Next.js `3000` 동시 실행.

## 12. 남은 이슈

- 실제 LLM/OpenAI 연동은 추후
- Kafka consumer 별도 프로세스 필요 (Kafka 사용 시)

## 13. 다음 단계

- Next.js `npm run verify` 통합 검증
- 실제 Kafka 클러스터 연동 테스트
