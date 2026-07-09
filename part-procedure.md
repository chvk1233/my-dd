my-dd 과제 진행 절차 기록

1) 과제 문서 순차 분석
- part-start.md, part-a.md, part-b.md, part-c.md를 순서대로 읽고 전체 구조를 분석했다.
- 과제의 핵심이 "정답 코드 복붙"이 아니라, 현재 프로젝트를 기준으로 확장하고 그 과정(프롬프트 의도/수용/수정)을 설명하는 것임을 확인했다.

2) 전체 요구사항 통합 정리
- Part A: Flask API 확장(health/events/detail/ingest + 선택 report/tasks/chat)
- Part B: Dashboard UI 확장(API 상태, 분석 패널, 보고서/체크리스트, fallback 표시)
- Part C: training_events_1200.csv 기반 텍스트 전처리(토큰화/정수 인코딩/원-핫)
- 제출물: 프롬프트 목록, 사용 이유, 수용/거절 근거, 검증 결과, 전처리 결과 정리 필요

3) 실제 코드베이스와 요구사항 대조 수행
- 프로젝트 구조를 확인한 결과:
  - 백엔드: flask/backend
  - 프론트엔드: nextjs
  - 전처리 데이터: AI/training_events_1200.csv
- 핵심 파일을 읽어 Part A/B/C 요구사항 대비 현황을 점검했다.

4) 대조 결과 요약
- Part A(백엔드): 구현 완료 수준
  - /health, /events, /events/<event_id>, /ingest 모두 구현 확인
  - /report, /tasks, /chat 선택 API도 구현 확인
  - Kafka producer/consumer + rule_fallback(model_inference) + DB 저장 흐름 확인
- Part B(프론트): 구현 완료 수준
  - Zustand store 확장(state/action), API 상태 패널, 분석 패널, 보고서/체크리스트, 오류/fallback 처리 확인
  - ingest 폼, chat 패널까지 연결 확인
- Part C(전처리): 미착수
  - AI 폴더에는 training_events_1200.csv만 있고 실습 코드(.py/.ipynb) 부재 확인
- 제출 문서:
  - part-result.md는 비어 있음 확인

5) 현재 사용자의 추가 요청
- 요청 1: part-procedure.md에 지금까지 대화/작업 내용을 정리 기록
- 요청 2: AI 하위 폴더에서만 Part C 실습 코드 작성
  - C-1 CSV 확인 코드
  - C-2 토큰화 실습 코드
  - C-3 정수 인코딩 실습 코드
  - C-4 원-핫 인코딩 실습 코드
  - C-5 프로젝트 연결 설명(md)

6) 이번 작업에서 반영한 원칙
- 기존 flask/nextjs 코드는 수정하지 않고, 사용자 지시대로 AI 폴더 내 전처리 산출물만 생성한다.
- C-1~C-4는 단계별로 독립 실행 가능한 파이썬 스크립트로 만든다.
- C-5는 전처리 단계가 관제센터 파이프라인 어디에 들어가는지 설명 문서로 작성한다.

