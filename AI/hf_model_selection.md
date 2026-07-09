# Hugging Face 모델 선택 확정 (5단계)

사용자가 4단계 탐색 결과를 바탕으로 적용 모델을 선택한 기록입니다.

---

## 1. 선택 결과

| 항목 | 내용 |
|------|------|
| **선택지** | **C** |
| **모델명** | KcELECTRA |
| **Hugging Face ID** | `beomi/KcELECTRA-base` |
| **구조** | ELECTRA (discriminator 기반 사전학습) |
| **선택 일자** | 2026-07-09 |
| **다음 단계** | 6단계 — `my-dd` 프로젝트 적용 |

---

## 2. 선택 이유 (프로젝트 관점)

### 2-1. 도메인 적합성

| 요소 | KcELECTRA | 본 프로젝트 |
|------|-----------|-------------|
| 학습 데이터 | 네이버 뉴스 **댓글·대댓글** | 매장 **고객 message** (민원·문의·불만) |
| 텍스트 특성 | 구어체, 신조어, 오탈자 | 실제 고객 메시지와 유사 |
| 태스크 | 감성 분류(NSMC) 등 검증됨 | sentiment / severity 분류 |

→ 고객 메시지는 뉴스/위키 기반 KLUE BERT보다 **댓글형 구어체**에 가깝기 때문에 C가 가장 적합합니다.

### 2-2. baseline 한계 보완 기대

`baseline_limitations.md`에서 확인된 문제와 KcELECTRA 기대 효과:

| baseline 한계 | KcELECTRA 기대 |
|---------------|----------------|
| 완곡 부정 ("괜찮긴 한데…") | 문맥 임베딩으로 전후 관계 파악 |
| 키워드 부재 ("실망했어요") | 서브워드 + 사전학습으로 의미 일반화 |
| negative/medium 쏠림 | 파인튜닝으로 클래스 균형 조정 가능 |
| 감정≠긴급도 혼동 | sentiment / severity **별도 헤드** 파인튜닝 |

### 2-3. 4단계 조건 충족

| add-part.md 조건 | KcELECTRA |
|------------------|-----------|
| 한국어 문장 처리 | ✅ 댓글 코퍼스 사전학습 |
| 문장 분류 사용 | ✅ `AutoModelForSequenceClassification` |
| baseline보다 문맥 이해 | ✅ ELECTRA + 구어체 특화 |
| Colab 테스트 가능 | ✅ ~475MB, T4 GPU |

---

## 3. 미선택 후보와 비교 (왜 C인가)

| 선택지 | 모델 | 미선택 이유 (본 프로젝트 기준) |
|--------|------|-------------------------------|
| A | KLUE RoBERTa | 범용·벤치마크 우수하나 **구어체 민원** 도메인은 Kc 계열이 더 가까움 |
| B | KLUE BERT | 동일 — 격식체 말뭉치 비중 높음 |
| D | KcBERT | 동일 제작자·도메인이나 **KcELECTRA가 KcBERT 대비 성능 우수** |
| E | KoELECTRA v3 | 범용 성능 좋으나 댓글/민원 톤 특화는 KcELECTRA가 유리 |

**결론:** 도메인(고객 민원 message) + 구어체 + 분류 성능을 동시에 만족하는 **C가 최적**.

---

## 4. 6단계 적용 계획 (예정)

### 4-1. 파인튜닝

| 항목 | 내용 |
|------|------|
| 데이터 | `AI/training_events_1200.csv` |
| 모델 1 | `beomi/KcELECTRA-base` + sentiment 헤드 (negative / neutral) |
| 모델 2 | `beomi/KcELECTRA-base` + severity 헤드 (low / medium / high) |
| 저장 위치 | `AI/models/hf/` + `flask/backend/ai/models/hf/` |

### 4-2. 프로젝트 연동

| 파일 | 변경 |
|------|------|
| `AI/train_hf_kcelectra.py` | Colab/로컬 파인튜닝 스크립트 |
| `flask/backend/ai/hf_predict.py` | KcELECTRA 추론 |
| `flask/backend/ai/model_inference.py` | 우선순위: `kcelectra_hf` → `tfidf_lr` → `keyword_fallback` |
| `flask/backend/requirements.txt` | `transformers`, `torch` 추가 |

### 4-3. API 응답

```json
{
  "sentiment": "negative",
  "severity": "medium",
  "source": "kcelectra_hf",
  "confidence": 0.91
}
```

### 4-4. 추론 우선순위 (6단계 확정안)

```
1. KcELECTRA (kcelectra_hf)     ← 이번에 추가
2. TF-IDF + LR (tfidf_lr)       ← 1단계 baseline
3. 키워드 규칙 (keyword_fallback)
```

---

## 5. 7단계 테스트 계획 (예정)

| 검증 항목 | 방법 |
|-----------|------|
| 오분류 10문장 | `baseline_limitations.md` §4 문장으로 before/after 비교 |
| Flask API | `POST /ingest` → `source: kcelectra_hf` 확인 |
| Dashboard | 분석 패널 sentiment/severity 표시 |
| pytest | `test_model_inference.py` 기대값 업데이트 |

---

## 6. Colab 빠른 시작 (6단계 참고용)

```python
!pip install transformers datasets torch accelerate scikit-learn pandas

MODEL_ID = "beomi/KcELECTRA-base"

from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID, num_labels=2)
```

---

## 7. 요약

- **5단계 완료:** 사용자가 **모델 C (`beomi/KcELECTRA-base`)** 선택 확정
- **선택 근거:** 매장 고객 message ≈ 댓글형 구어체, baseline 한계(완곡 부정·문맥) 보완 기대
- **다음:** 6단계에서 KcELECTRA 파인튜닝 및 `model_inference.py` 연동
