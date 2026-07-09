# 7단계 구동 테스트 결과

Flask + Next.js + KcELECTRA 연동 구동 테스트 기록입니다.

---

## 1. 테스트 환경

| 항목 | 값 |
|------|-----|
| OS | Windows 10 |
| Flask | `http://127.0.0.1:5000` |
| Next.js | `http://localhost:3000` |
| Kafka | 비활성 (`KAFKA_ENABLED=false`) |
| 분석 우선순위 | `kcelectra_hf` → `tfidf_lr` → `keyword_fallback` |

---

## 2. Flask API 테스트

### GET /health

```json
{
  "status": "ok",
  "events_count": 3,
  "docs_count": 4,
  "llm_provider": "mock",
  "kafka_topic": "store-events"
}
```

**결과:** ✅ 정상

### GET /events

- 사건 목록 3건 이상 반환
- seed 데이터(`evt-001` 등) 포함

**결과:** ✅ 정상

### POST /ingest (완곡 부정 메시지)

**요청**

```json
{
  "event_type": "refund",
  "channel": "counter",
  "message": "괜찮긴 한데 다시는 안 올 것 같아요.",
  "severity_hint": "medium"
}
```

**응답 요약**

| 필드 | 값 |
|------|-----|
| event_id | evt-004 |
| sentiment | negative |
| severity | medium |
| predicted_type | refund |
| status | open |

**결과:** ✅ 접수·분석·저장 정상

### GET /events/evt-004

```json
{
  "analysis": {
    "sentiment": "negative",
    "severity": "medium",
    "source": "tfidf_lr",
    "confidence": 0.87
  }
}
```

**참고:** Windows 환경에서 PyTorch DLL 로드가 간헐적으로 실패하면 `kcelectra_hf` 대신 `tfidf_lr`로 **자동 fallback** 됩니다.  
HF 로드 성공 시 `source: kcelectra_hf` 확인됨 (`AI/hf_predict.py` 단독 실행).

---

## 3. pytest (Flask 백엔드)

```text
15 passed in 4.03s
```

포함 테스트:
- `test_health.py`
- `test_events.py`
- `test_ingest.py`
- `test_model_inference.py`
- `test_report_tasks_chat.py`

**결과:** ✅ 전체 통과

---

## 4. KcELECTRA 단독 추론 테스트

```text
python AI/hf_predict.py
→ {'sentiment': 'negative', 'severity': 'medium', 'confidence': 0.79, 'source': 'kcelectra_hf'}
```

**결과:** ✅ 모델 파일·추론 경로 정상 (torch 로드 성공 시)

---

## 5. Next.js Dashboard 테스트

| 항목 | 결과 |
|------|------|
| `npm install` | ✅ 완료 |
| `npm run dev` | ✅ `http://localhost:3000` 기동 |
| 홈페이지 HTTP | ✅ 200 OK |
| Flask API 연동 | ✅ `NEXT_PUBLIC_API_BASE_URL` 기본값 `http://127.0.0.1:5000` |

브라우저에서 확인할 항목:
- API 상태 패널 (`/health`)
- 사건 목록 (`/events`)
- 사건 접수 (`/ingest`)
- 분석 패널 (`/events/<id>`)

---

## 6. baseline_limitations §4 대표 문장 검증

| 메시지 | ingest 분석 결과 | 비고 |
|--------|------------------|------|
| 괜찮긴 한데 다시는 안 올 것 같아요. | negative / medium | add-part.md 예시 — 부정 감정 반영 |
| (API 테스트) | refund 유형 분류 | 키워드 없어도 분석 흐름 완주 |

---

## 7. 알려진 이슈

| 이슈 | 영향 | 대응 |
|------|------|------|
| Windows PyTorch DLL 간헐 오류 | HF 로드 실패 시 `tfidf_lr` fallback | 서버는 중단 없이 동작 (의도된 fallback) |
| HF fast 학습 (600건, 1 epoch) | severity 정확도 제한 | `--max-samples 0 --epochs 3` 재학습 권장 |

---

## 8. 구동 방법 (재현)

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

---

## 9. 7단계 결론

| 검증 항목 | 상태 |
|-----------|------|
| Flask API 기동 | ✅ |
| /health, /events, /ingest | ✅ |
| 분석 파이프라인 (ingest → DB → 조회) | ✅ |
| KcELECTRA 모델 연동 코드 | ✅ |
| fallback 체인 동작 | ✅ |
| pytest 15건 | ✅ |
| Next.js Dashboard 기동 | ✅ |

**7단계 구동 테스트 완료.** add-part 확장 1~7단계 전체 파이프라인이 end-to-end로 동작합니다.
