# Hugging Face 한국어 모델 탐색 보고서

add-part.md 3번 요구사항에 따라, baseline(TF-IDF+LR)을 대체·보완할 **한국어 BERT 계열 오픈 모델** 5개를 탐색·분석한 문서입니다.

---

## 1. 탐색 목적·조건

### 1-1. 목적

3단계(`baseline_limitations.md`)에서 확인한 **완곡 부정·문맥 의존·감정/긴급도 분리** 한계를 줄이기 위해, 문맥 이해가 가능한 사전학습 모델을 선정합니다.

### 1-2. add-part.md 선정 조건

| # | 조건 | 확인 방법 |
|---|------|-----------|
| 1 | 한국어 문장 처리 가능 | 한국어 코퍼스 사전학습 여부 |
| 2 | 문장 분류에 사용 가능 | `AutoModelForSequenceClassification` 파인튜닝 |
| 3 | baseline보다 문맥 이해 우수 | 완곡 표현·역접 구조 처리 기대 |
| 4 | Colab에서 로드·테스트 가능 | `transformers` + GPU(T4) 메모리 내 로드 |

### 1-3. 본 프로젝트 적용 태스크

| 태스크 | 입력 | 출력 클래스 |
|--------|------|-------------|
| sentiment 분류 | `message` | negative, neutral |
| severity 분류 | `message` | low, medium, high |

→ 모델 2개 파인튜닝 또는 동일 백본에 헤드 2개 구성 (6단계에서 구현)

---

## 2. 후보 모델 5개 요약

| 순위 | 모델명 | Hugging Face ID | 구조 | 용량(약) | Colab T4 |
|------|--------|-----------------|------|----------|----------|
| 1 | **KLUE RoBERTa** | `klue/roberta-base` | RoBERTa | ~500MB | ✅ |
| 2 | **KLUE BERT** | `klue/bert-base` | BERT | ~450MB | ✅ |
| 3 | **KcELECTRA** | `beomi/KcELECTRA-base` | ELECTRA | ~475MB | ✅ |
| 4 | **KcBERT** | `beomi/kcbert-base` | BERT | ~417MB | ✅ |
| 5 | **KoELECTRA v3** | `monologg/koelectra-base-v3-discriminator` | ELECTRA | ~423MB | ✅ |

---

## 3. 후보별 상세 분석

### 3-1. KLUE RoBERTa (`klue/roberta-base`)

| 항목 | 내용 |
|------|------|
| 개발 | KLUE 벤치마크 팀 (한국어 NLU 표준) |
| 사전학습 | 대규모 한국어 말뭉치, RoBERTa 방식 |
| 분류 적합성 | KLUE-TC(토픽 분류), NLI, STS 등 **분류·이해 태스크** 공식 지원 |
| baseline 대비 기대 | 양방향 문맥 + 서브워드 → **완곡 표현·문맥 역접**에 유리 |
| Colab | `transformers` 표준 로드, base 크기 T4에서 파인튜닝 가능 |
| 라이선스 | Apache 2.0 (모델 카드 기준) |

**장점**
- KLUE 벤치마크에서 BERT-base 대비 **전반적 성능 우수**
- 논문·레시피·예제 풍부 → 학습 재현 용이

**단점**
- 뉴스/위키 중심 말뭉치 → **구어체·고객 민원** 톤과는 거리 있을 수 있음

**매장 메시지 적합도:** ★★★★☆ (범용·안정, 첫 실험용으로 적합)

---

### 3-2. KLUE BERT (`klue/bert-base`)

| 항목 | 내용 |
|------|------|
| 개발 | KLUE 벤치마크 팀 |
| 사전학습 | 한국어 BERT-base |
| 분류 적합성 | `AutoModelForSequenceClassification` 파인튜닝 문서·튜토리얼 多 |
| baseline 대비 기대 | TF-IDF 대비 **문맥 임베딩** 기반 분류 |
| Colab | ✅ 표준 지원 |
| 라이선스 | Apache 2.0 |

**장점**
- 한국어 NLP **사실상 표준 baseline PLM**
- 자료·커뮤니티·호환성 최고

**단점**
- RoBERTa-base 대비 벤치마크 점수 다소 낮은 편
- 구어체 민원 문장에는 Kc 계열이 더 맞을 수 있음

**매장 메시지 적합도:** ★★★★☆ (안정적 기본 선택)

---

### 3-3. KcELECTRA (`beomi/KcELECTRA-base`)

| 항목 | 내용 |
|------|------|
| 개발 | Beomi |
| 사전학습 | **네이버 뉴스 댓글·대댓글** (구어체, 오탈자, 신조어 포함) |
| 분류 적합성 | NSMC(감성 분류) 등 댓글 태스크에서 KcBERT 대비 우수 |
| baseline 대비 기대 | **고객 불만·항의 메시지**와 도메인 유사도 높음 |
| Colab | ✅ (~475MB) |
| 라이선스 | MIT |

**장점**
- **구어체·비정형 텍스트**에 특화 → 매장 고객 message와 궁합 좋음
- KcBERT 대비 downstream 성능 향상 (제작자 벤치마크)

**단점**
- 댓글 도메인 편향 → 지나치게 공격적 톤에 맞춰질 수 있음
- ELECTRA 구조는 BERT 대비 학습·추론 코드가 약간 다름

**매장 메시지 적합도:** ★★★★★ (도메인 최적 후보)

---

### 3-4. KcBERT (`beomi/kcbert-base`)

| 항목 | 내용 |
|------|------|
| 개발 | Beomi |
| 사전학습 | 네이버 뉴스 **댓글** 코퍼스 |
| 분류 적합성 | 감성 분류(NSMC) 등에 널리 사용 |
| baseline 대비 기대 | 키워드 없는 **실망·불만** 표현에 KcELECTRA 다음으로 유리 |
| Colab | ✅ (~417MB, 상대적으로 가벼움) |
| 라이선스 | MIT |

**장점**
- **고객 메시지 톤**과 가장 가까운 학습 데이터 중 하나
- 모델 크기 작아 Colab에서 빠른 실험 가능

**단점**
- 동일 제작자의 **KcELECTRA가 대체 모델**로 권장됨
- KLUE 벤치마크 일부 태스크에서 RoBERTa/KoELECTRA보다 낮음

**매장 메시지 적합도:** ★★★★☆ (KcELECTRA 부담 시 대안)

---

### 3-5. KoELECTRA v3 (`monologg/koelectra-base-v3-discriminator`)

| 항목 | 내용 |
|------|------|
| 개발 | monologg |
| 사전학습 | 한국어 위키·뉴스 등 + ELECTRA v3 |
| 분류 적합성 | KorNLI, PAWS, NER 등 **분류·이해** 벤치마크 상위권 |
| baseline 대비 기대 | 일반 한국어 문맥 이해 강점, **격식체·설명체** 문장에 유리 |
| Colab | ✅ (~423MB) |
| 라이선스 | Apache 2.0 |

**장점**
- 범용 한국어 이해 **성능 대비 안정**
- KLUE·KoELECTRA 생태계에서 검증됨

**단점**
- 댓글/구어체 특화는 Kc 계열보다 약할 수 있음
- v2/v3 버전 혼동 주의 → **v3 discriminator** 사용 권장

**매장 메시지 적합도:** ★★★★☆ (범용 고성능 대안)

---

## 4. baseline 한계와 모델별 기대 개선

`baseline_limitations.md` §4 오분류 10예시 기준 **기대 개선 방향**:

| 어려운 메시지 유형 | TF-IDF+LR / 키워드 | HF BERT 기대 |
|--------------------|-------------------|--------------|
| 완곡 부정 ("괜찮긴 한데…") | 키워드 neutral 오판 | **문맥 전체**로 부정 인식 |
| 키워드 부재 ("실망했어요") | neutral | 학습 시 패턴 일반화 |
| 감정≠긴급도 분리 | 둘 다 medium 쏠림 | **라벨별 독립 파인튜닝**으로 분리 |
| 긍정 문장 ("맛은 괜찮았어요") | negative 오판 | positive/neutral 구분 |
| 표현 변형 ("결제가 두 번") | "중복 결제" 미매칭 | 서브워드로 의미 연결 |

**도메인 관점 1차 추천:** 고객 민원 message → **KcELECTRA** 또는 **KcBERT**  
**범용·재현성 관점 1차 추천:** **KLUE RoBERTa** 또는 **KLUE BERT**

---

## 5. Colab 테스트 방법 (공통)

### 5-1. 설치

```python
!pip install transformers datasets torch accelerate scikit-learn
```

### 5-2. 모델 로드 (분류 헤드)

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_ID = "klue/roberta-base"  # 후보별로 변경

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_ID,
    num_labels=2,  # sentiment: negative/neutral
)
```

### 5-3. 파인튜닝 데이터

```python
import pandas as pd
df = pd.read_csv("training_events_1200.csv")
# sentiment 모델: df[["message", "sentiment"]]
# severity 모델: df[["message", "severity"]]
```

### 5-4. 빠른 검증 (3단계 오분류 예시)

```python
test_sentences = [
    "괜찮긴 한데 다시는 안 올 것 같아요.",
    "오늘 커피 맛은 괜찮았어요.",
    "결제가 두 번 됐는데 즉시 확인 부탁드립니다.",
]
# 파인튜닝 후 predict → baseline_limitations.md §4와 비교
```

### 5-5. Colab GPU 메모리

| 모델 | base 추론 | base 파인튜닝 (batch 16) |
|------|-----------|--------------------------|
| 5개 후보 전부 | T4(16GB) ✅ | T4 ✅ (fp16 권장) |
| large 변형 | ⚠️ 메모리 부족 가능 | A100 권장 |

→ 본 탐색은 **base** 크기만 대상으로 함.

---

## 6. 비교 표 (5단계 선택용)

| 모델 | HF ID | 구어체 적합 | 벤치마크 검증 | 분류 용이성 | Colab | 종합 추천 |
|------|-------|-------------|---------------|-------------|-------|-----------|
| KLUE RoBERTa | `klue/roberta-base` | ★★★ | ★★★★★ | ★★★★★ | ✅ | **범용 1순위** |
| KLUE BERT | `klue/bert-base` | ★★★ | ★★★★★ | ★★★★★ | ✅ | **안정 기본** |
| KcELECTRA | `beomi/KcELECTRA-base` | ★★★★★ | ★★★★ | ★★★★ | ✅ | **도메인 1순위** |
| KcBERT | `beomi/kcbert-base` | ★★★★★ | ★★★★ | ★★★★ | ✅ | 도메인 2순위 |
| KoELECTRA v3 | `monologg/koelectra-base-v3-discriminator` | ★★★ | ★★★★★ | ★★★★ | ✅ | 범용 2순위 |

---

## 7. 5단계(사용자 선택) 안내 초안

아래 중 **하나**를 선택해 6단계 프로젝트 적용에 사용합니다.

| 선택지 | 모델 | 추천 대상 |
|--------|------|-----------|
| **A** | `klue/roberta-base` | 벤치마크·재현성·문서 풍부, 첫 HF 실험 |
| **B** | `klue/bert-base` | 가장 널리 쓰이는 한국어 BERT, 안정적 |
| **C** | `beomi/KcELECTRA-base` | **매장 고객 민원 문장** 도메인 최적 |
| **D** | `beomi/kcbert-base` | 가벼운 Colab 실험, 구어체 특화 |
| **E** | `monologg/koelectra-base-v3-discriminator` | 범용 고성능 ELECTRA |

**개인적 1차 추천 (본 프로젝트):**  
→ **C. KcELECTRA** (고객 message ≈ 댓글형 구어체)  
→ 차선: **A. KLUE RoBERTa** (비교·보고용 범용 baseline)

---

## 8. 6~7단계 연동 계획

| 단계 | 작업 |
|------|------|
| 6. 적용 | Colab 파인튜닝 → `AI/models/hf/` 저장 → `model_inference.py`에 `source: bert_hf` 경로 추가 |
| 7. 테스트 | `baseline_limitations.md` §4 10문장 + Flask `/ingest` + Dashboard |

필요 패키지 (Flask 연동 시):

```
transformers>=4.36.0
torch>=2.0.0
```

---

## 9. 요약

- add-part.md 조건을 만족하는 **한국어 BERT/ELECTRA 계열 5개** 후보를 선정·분석했다.
- 매장 고객 `message` 특성상 **KcELECTRA / KcBERT**가 도메인 적합도가 높고, **KLUE RoBERTa / BERT**는 범용·재현성 면에서 유리하다.
- 5단계에서 사용자가 A~E 중 선택하면, 6단계에서 `training_events_1200.csv`로 파인튜닝 후 `my-dd`에 연동한다.
