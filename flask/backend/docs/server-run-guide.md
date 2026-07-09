# Flask 서버 직접 실행 가이드

Flask API 서버를 직접 실행하는 방법을 경로와 명령어 중심으로 정리한 문서입니다.

---

## 1. 경로 구조 (정확한 절대 경로)

프로젝트는 아래처럼 구성되어 있습니다.

| 구분 | 정확한 경로 |
|---|---|
| **프로젝트 루트** | `C:\Users\freelancer\Desktop\flask` |
| **Flask 백엔드 (실행 위치)** | `C:\Users\freelancer\Desktop\flask\backend` |
| **서버 진입점** | `C:\Users\freelancer\Desktop\flask\backend\app.py` |
| **의존성 목록** | `C:\Users\freelancer\Desktop\flask\backend\requirements.txt` |
| **환경변수 예시** | `C:\Users\freelancer\Desktop\flask\backend\.env.example` |
| **환경변수 파일 (직접 생성)** | `C:\Users\freelancer\Desktop\flask\backend\.env` |
| **SQLite DB (실행 시 자동 생성)** | `C:\Users\freelancer\Desktop\flask\backend\data\ops.db` |
| **RAG 운영 문서** | `C:\Users\freelancer\Desktop\flask\backend\data\docs\` |

**중요:** 서버는 반드시 `backend` 폴더에서 실행해야 합니다. `app.py`가 같은 폴더의 `routes/`, `services/`, `config.py` 등을 import하기 때문입니다.

---

## 2. 최초 1회 설정 (아직 안 했다면)

PowerShell을 열고 아래 순서대로 실행합니다.

### 2-1. 백엔드 폴더로 이동

```powershell
cd C:\Users\freelancer\Desktop\flask\backend
```

### 2-2. (선택) 가상환경 생성 및 활성화

```powershell
python -m venv C:\Users\freelancer\Desktop\flask\backend\.venv
C:\Users\freelancer\Desktop\flask\backend\.venv\Scripts\Activate.ps1
```

가상환경을 쓰지 않아도, 시스템 Python 3.12로 바로 실행할 수 있습니다.

### 2-3. 패키지 설치

```powershell
python -m pip install -r C:\Users\freelancer\Desktop\flask\backend\requirements.txt
```

### 2-4. (선택) 환경변수 파일 생성

```powershell
copy C:\Users\freelancer\Desktop\flask\backend\.env.example C:\Users\freelancer\Desktop\flask\backend\.env
```

`.env`가 없어도 기본값으로 동작합니다.

- 호스트: `127.0.0.1`
- 포트: `5000`
- Kafka: 비활성 (`KAFKA_ENABLED=false`)

---

## 3. 서버 실행 명령어

### 방법 A — 권장 (`app.py` 직접 실행)

```powershell
cd C:\Users\freelancer\Desktop\flask\backend
python app.py
```

또는 절대 경로로:

```powershell
python C:\Users\freelancer\Desktop\flask\backend\app.py
```

이때 작업 디렉터리가 `backend`가 아니면 import 오류가 날 수 있으므로, **`cd` 후 실행하는 방식을 권장**합니다.

### 방법 B — Flask CLI 사용

```powershell
cd C:\Users\freelancer\Desktop\flask\backend
$env:FLASK_APP = "app.py"
flask run --host 127.0.0.1 --port 5000
```

---

## 4. 정상 실행 확인

터미널에 아래와 비슷한 메시지가 보이면 성공입니다.

```text
 * Running on http://127.0.0.1:5000
```

브라우저 또는 PowerShell에서 확인:

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:5000/health" -UseBasicParsing
```

정상 응답 예:

```json
{
  "status": "ok",
  "events_count": 3,
  "docs_count": 4,
  "llm_provider": "mock",
  "kafka_topic": "store-events"
}
```

---

## 5. 서버 종료

서버가 실행 중인 터미널에서:

```text
Ctrl + C
```

---

## 6. Next.js와 함께 쓸 때

Next.js 프로젝트 경로: `C:\Users\freelancer\Desktop\nextJS`

```powershell
# 터미널 1 — Flask
cd C:\Users\freelancer\Desktop\flask\backend
python app.py

# 터미널 2 — Next.js
cd C:\Users\freelancer\Desktop\nextJS
npm run dev
```

- Flask: `http://127.0.0.1:5000`
- Next.js: `http://localhost:3000`

---

## 7. 자주 하는 실수

| 문제 | 원인 | 해결 |
|---|---|---|
| `ModuleNotFoundError: No module named 'routes'` | `flask` 폴더가 아닌 상위 폴더에서 실행 | `cd C:\Users\freelancer\Desktop\flask\backend` 후 실행 |
| 포트 충돌 | 5000번 포트 사용 중 | `.env`에서 `FLASK_PORT=5001` 등으로 변경 |
| `pip` 패키지 없음 | 의존성 미설치 | `pip install -r requirements.txt` 실행 |

---

## 8. 가장 단순한 실행 (요약)

```powershell
cd C:\Users\freelancer\Desktop\flask\backend
python app.py
```
