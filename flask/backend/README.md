# Flask API 서버

Next.js 대시보드(`http://localhost:3000`)가 호출하는 Flask 백엔드 API 서버입니다.

## 요구 사항

- Python 3.12+
- pip

## 설치 및 실행

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
copy .env.example .env
python app.py
```

서버 주소: `http://127.0.0.1:5000`

## Next.js 연동

Next.js 프로젝트에서 `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:5000` 으로 설정 후:

```bash
# 터미널 1
cd backend && python app.py

# 터미널 2
cd nextJS && npm run dev
```

브라우저에서 `http://localhost:3000` 접속

## API 엔드포인트

| Method | Path | 설명 |
|---|---|---|
| GET | `/health` | API 상태 확인 |
| GET | `/events` | 사건 목록 |
| GET | `/events/<event_id>` | 사건 + AI 분석 |
| POST | `/ingest` | 사건 접수 |
| POST | `/report` | 점장 보고서 생성 |
| POST | `/tasks` | 직원 체크리스트 생성 |
| POST | `/chat` | RAG 챗봇 |

## Kafka (선택)

기본값은 Kafka 비활성화(`KAFKA_ENABLED=false`)입니다. Kafka 없이도 모든 API가 동작합니다.

Kafka 사용 시 `.env`에서 `KAFKA_ENABLED=true` 설정 후 consumer 실행:

```bash
python workers/consumer.py
```

**참고:** Kafka 사용 시 ingest 후 목록 반영까지 1~3초 지연될 수 있습니다. Kafka 없을 때는 ingest 즉시 SQLite에 저장·분석됩니다.

## 테스트

```bash
cd backend
pytest
```

## 환경변수

`.env.example` 참고

## 문서

- `docs/api-contract.md` — API 계약
- `docs/flask-build-result.md` — 구축 결과
