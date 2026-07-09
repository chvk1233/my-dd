Part A. 기본 백엔드 흐름을 완성형 Flask API 서버로 확장하기

목표

현재 알고 있는 Kafka message, Consumer, 분석 함수, Flask `/events` 흐름을 바탕으로 완성형 API 서버 구조를 설계하고 보완합니다.

오늘은 실제 AI 모델을 완성하지 않습니다.
AI 분석, 보고서, 체크리스트, 챗봇 응답은 `mock` 또는 `fallback`으로 처리해도 됩니다.



A-1. 현재 백엔드 구조를 먼저 분석하기

작업

Cursor AI에게 현재 프로젝트 구조를 먼저 분석하게 하세요.
특정 정답 경로를 주지 말고, **현재 열려 있는 프로젝트 기준으로 Flask, Kafka, Consumer, 분석 함수 관련 파일을 찾아서 설명**하게 해야 합니다.

학생용 프롬프트
> 
> 현재 내가 열어 둔 프로젝트를 기준으로 백엔드 구조를 분석해줘.
> 
> 나는 기본 Dashboard와 기본 백엔드 흐름을 갖고 있는 상태라고 가정한다.
> 즉, Kafka message, Consumer, model_inference.py, Flask /events > 흐름은 배웠지만 완성형 API 서버는 아직 부족할 수 있다.
> 
> 먼저 코드를 수정하지 말고 아래 내용을 찾아서 설명해줘.
> 
> 1. Flask API 서버 역할을 하는 파일이 어디에 있는지
> 2. Kafka message를 받거나 처리하는 파일이 어디에 있는지
> 3. 분석 함수 또는 mock 분석 함수가 어디에 있는지
> 4. 사건 목록을 저장하거나 불러오는 코드가 어디에 있는지
> 5. 현재 구현된 API endpoint 목록
> 6. 완성형 관제센터가 되려면 추가로 필요한 endpoint
> 7. AI 모델이 없어도 fallback으로 동작해야 하는 부분


출력 형식:
- 파일 경로를 먼저 표로 정리해줘.
- 그 다음 Dashboard -> Flask API -> Consumer/분석/저장 흐름을 글로 설명해줘.
- 마지막에 "수정 전 확인해야 할 것" 체크리스트를 만들어줘.

프롬프트를 쓰는 이유

바로 “API 서버 만들어줘”라고 하면 AI가 새 파일을 마음대로 만들 수 있습니다.
먼저 현재 구조를 분석하게 해야 현재 만든 흐름을 유지하면서 확장할 수 있습니다.

학생이 답해야 할 질문

1. Flask API 서버는 화면과 분석 결과 사이에서 어떤 역할을 하는가?
2. Consumer와 Flask API는 같은 역할인가, 다른 역할인가?
3. `model_inference.py`는 전체 프로젝트에서 어디에 들어가는가?
4. AI 모델이 아직 없어도 fallback이 필요한 이유는 무엇인가?



A-2. 완성형 Flask API 계약 설계하기

작업

현재 기본 상태에서 완성형 관제센터가 되려면 어떤 API가 필요한지 설계하세요.

필수 API

API : 역할
GET /health : 서버 상태 확인
GET /events : 사건 목록 조회
GET /events/<event_id> : 사건 상세 조회
POST /ingest : 새 사건 접수


선택 API

API : 역할
POST /report : 점장 보고서 mock 생성
POST /tasks : 직원 체크리스트 mock 생성
POST /chat : 문서 기반 챗봇 mock 응답


학생용 프롬프트
> 현재 기본 백엔드 흐름을 완성형 Flask API 서버로 확장하려고 한다.
> 
> 오늘 목표는 실제 AI 모델을 붙이는 것이 아니라,
> 관제센터 UI가 호출할 수 있는 API 계약을 먼저 정하는 것이다.
> 
> 
> 필수 API:
> - GET /health
> - GET /events
> - GET /events/<event_id>
> - POST /ingest
> 
> 선택 API:
> - POST /report
> - POST /tasks
> - POST /chat
> 
> 각 API에 대해 다음을 표로 정리해줘.
> 
> 1. API 이름
> 2. 언제 호출되는지
> 3. request 예시
> 4. response 예시
> 5. 성공 기준
> 6. 실패하거나 AI가 없을 때 fallback 응답
> 7. 현재 기본 구조에서 무엇이 확장되는지
> 
> 주의사항:
> - 코드를 먼저 만들지 말고 API 계약부터 설계해줘.
> - AI/LLM 결과는 mock 또는 fallback으로 처리한다고 가정해줘.
> - Dashboard가 어떤 데이터를 필요로 하는지도 함께 설명해줘.

프롬프트를 쓰는 이유

API는 프론트엔드와 백엔드 사이의 약속입니다.
약속 없이 코드를 만들면 UI가 원하는 데이터와 서버가 주는 데이터가 달라질 수 있습니다.

학생이 답해야 할 질문

1. `/health`는 왜 필요한가?
2. `/events`와 `/events/<event_id>`는 왜 분리하는가?
3. `/ingest`는 사건 저장만 하는가, 분석 요청까지 포함할 수 있는가?
4. `/report`, `/tasks`, `/chat`을 mock으로 둬도 되는 이유는 무엇인가?



A-3. 최소 수정으로 Flask API 보완하기

작업

Cursor AI를 사용해 현재 백엔드 코드를 보완하세요.
단, 새 프로젝트를 만들지 말고 현재 구조를 유지해야 합니다.

학생용 프롬프트
> 
> 현재 프로젝트의 백엔드 코드를 최소 수정으로 보완해줘.
> 
> 출발점:
> - 나는 기본 Dashboard와 기본 백엔드 흐름을 갖고 있다.
> - Kafka message, Consumer, 분석 함수, Flask /events 흐름을 배웠다.
> - 실제 AI 모델은 오늘 구현하지 않는다.
> 
> 구현 목표:
> 1. GET /health가 JSON으로 서버 상태를 반환한다.
> 2. GET /events가 사건 목록을 반환한다.
> 3. GET /events/<event_id>가 사건 상세를 반환한다.
> 4. POST /ingest가 새 사건 message를 받아 저장하거나 fallback 분석 결과를 만든다.
> 5. AI 모델이 없어도 서버가 죽지 않고 mock/fallback 응답을 반환한다.
> 6. 프론트엔드에서 호출할 수 있도록 JSON 응답 구조를 안정적으로 유지한다.
> 
> 작업 방식:
> - 먼저 어떤 파일을 수정할지 계획을 설명해줘.
> - 그 다음 최소 수정 코드만 제안해줘.
> - 기존 구조를 크게 갈아엎지 마.
> - 실행 및 확인 방법을 마지막에 적어줘.
> 
> 내가 확인해야 할 것:
> - /health 응답
> - /events 응답
> - /ingest에 message를 보냈을 때 응답
> - fallback이 동작하는지

프롬프트를 쓰는 이유

이 프롬프트는 AI가 “새 백엔드 프로젝트”를 만들지 못하게 막습니다.
우리는 현재 결과물을 버리는 것이 아니라, 그 위에 완성형 API 서버를 확장하는 것입니다.

검증 기준

최소한 아래 중 2개 이상은 직접 확인하거나 구조를 설명하세요.

GET /health
GET /events
GET /events/<event_id>
POST /ingest

학생이 답해야 할 질문

1. 내가 수정하거나 생성한 API는 무엇인가?
2. 그 API는 Dashboard의 어느 화면에서 쓰일 수 있는가?
3. fallback 응답은 어떤 상황에서 필요한가?
4. 기본 백엔드 흐름에서 무엇이 완성형에 가까워졌는가?
