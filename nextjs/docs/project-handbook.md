# Next.js 프로젝트 통합 운영·실행 문서

> **문서 목적:** 프로젝트 실행, 디버깅, 에러 해결에 필요한 운영 규칙·작업 결과·에러 이력을 한곳에 정리합니다.  
> **최종 갱신:** 2026-06-30  
> **현재 상태:** ✅ 실행 가능 (개발 서버 `http://localhost:3000`)

---

## 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [프로젝트 구조](#2-프로젝트-구조)
3. [실행 방법](#3-실행-방법)
4. [환경 변수](#4-환경-변수)
5. [작업 수행 결과 (2026-06-30)](#5-작업-수행-결과-2026-06-30)
6. [수정 파일 요약](#6-수정-파일-요약)
7. [검증 결과](#7-검증-결과)
8. [에러 로그](#8-에러-로그)
9. [남은 이슈](#9-남은-이슈)
10. [Cursor AI 운영 규칙 (섹션 0~15)](#10-cursor-ai-운영-규칙-섹션-015)
11. [테스트 환경 (2026-06-30)](#11-테스트-환경-2026-06-30)
12. [아키텍처 구조도 분석](#12-아키텍처-구조도-분석)

---

## 1. 프로젝트 개요

| 항목 | 내용 |
|---|---|
| 프로젝트명 | nextjs |
| 프레임워크 | Next.js 16.2.9 (Turbopack) |
| UI | React 19.2.4 |
| 상태 관리 | Zustand 5.x |
| 스타일 | Tailwind CSS 4 |
| 패키지 매니저 | npm (`package-lock.json`) |
| Node 버전 | v24.15.0 |
| 실행 환경 | Windows 10 |

이 프로젝트는 AI 매장 운영(Ops) 대시보드 프론트엔드입니다. 홈(`/`)에서 `ZustandDashboard`가 렌더링되며, Flask API(`http://127.0.0.1:5000`)와 연동합니다. API 연결 실패 시 mock 사건 데이터로 폴백합니다.

---

## 2. 프로젝트 구조

```
nextJS/
├── docs/
│   ├── error-log.md          # 에러 상세 이력 (본 문서 8절과 동기화)
│   └── project-handbook.md   # 본 통합 문서
├── src/
│   ├── app/                  # Next.js App Router (layout, page)
│   ├── entities/             # 도메인 타입·mock·formatter
│   ├── features/             # 기능 단위 UI (events, api-health, rag-chat)
│   ├── widgets/              # 페이지 조합 위젯 (ApiFetchDashboard)
│   ├── store/                # Zustand 전역 상태
│   ├── shared/               # API 클라이언트, env 설정
│   └── lib/                  # 레거시 API·타입
├── package.json
├── tsconfig.json
├── next.config.ts
├── AGENTS.md                 # Next.js 버전 주의사항
└── CLAUDE.md
```

### 주요 진입점

| 파일 | 역할 |
|---|---|
| `src/app/page.tsx` | `/` 라우트 — `ZustandDashboard` 렌더 |
| `src/widgets/api-fetch-dashboard/ApiFetchDashboard.tsx` | Zustand 기반 대시보드 위젯 |
| `src/store/useOpsStore.ts` | 이벤트 목록·선택 상태·API 로딩 |
| `src/shared/config/env.ts` | `NEXT_PUBLIC_API_BASE_URL` 기본값 정의 |

### 백업 파일 (참고용, 진입점에서 사용 금지)

- `ApiFetchDashboardbak0626.tsx`
- `EventListBAK0626.tsx`
- `EventDetailBAK0626.tsx`

---

## 3. 실행 방법

### 의존성 설치

```bash
npm install
```

### 개발 서버

```bash
npm run dev
```

접속: [http://localhost:3000](http://localhost:3000)

### 프로덕션 빌드·실행

```bash
npm run build
npm run start
```

### 검증 명령어

| 명령어 | 설명 |
|---|---|
| `npm run lint` | ESLint |
| `npx tsc --noEmit` | TypeScript 타입 체크 |
| `npm run build` | 프로덕션 빌드 |
| `npm test` | **해당 명령어 없음** |

---

## 4. 환경 변수

`.env.example` 파일은 없습니다. `src/shared/config/env.ts`에서 기본값을 사용합니다.

| 변수명 | 기본값 | 설명 |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | `http://127.0.0.1:5000` | Flask API 베이스 URL |

> **주의:** `.env` 파일은 사용자 승인 없이 생성·수정하지 않습니다. 실제 값이 필요하면 사용자에게 요청합니다.

---

## 5. 작업 수행 결과 (2026-06-30)

### 상태

✅ **실행 완료** — 개발 서버 HTTP 200, 프로덕션 빌드 성공

### 수행한 작업

1. 프로젝트 구조·`package.json`·설정 파일 점검
2. `npm install`로 의존성 확인
3. `npm run dev` 실행 후 런타임 500 오류 발견 및 분석
4. import 오류, TypeScript 오류, 누락 패키지(`zustand`) 수정
5. `lint` / `tsc` / `build` 검증
6. `docs/error-log.md` 생성 및 오류 기록
7. 본 통합 문서(`docs/project-handbook.md`) 작성

### 해결한 에러

| # | 제목 | 영향 |
|---|---|---|
| 1 | 홈 페이지 컴포넌트 import 오류 | 런타임 500 |
| 2 | `zustand` 패키지 누락 | 빌드 실패 |
| 3 | `fallbackEvents` 타입 import 경로 오류 | 타입 체크 실패 |
| 4 | `layout.tsx` children 암시적 any | 타입 체크 실패 |

---

## 6. 수정 파일 요약

| 파일 | 수정 이유 |
|---|---|
| `src/app/page.tsx` | 존재하지 않는 `StateDesignDashboard` → `ZustandDashboard`로 교체 |
| `src/entities/store-event/fallbackEvents.ts` | `../types` → `./types` 경로 수정 |
| `src/app/layout.tsx` | `children: ReactNode` 타입 추가 |
| `package.json` | 누락된 `zustand` 의존성 추가 |
| `package-lock.json` | `zustand` 설치 반영 |
| `docs/error-log.md` | 에러 추적 문서 신규 생성 |
| `docs/project-handbook.md` | 본 통합 문서 신규 생성 |

---

## 7. 검증 결과

| 검증 항목 | 명령어 | 결과 |
|---|---|---|
| 의존성 확인 | `npm install` | ✅ 성공 |
| 타입 체크 | `npx tsc --noEmit` | ✅ 성공 |
| 린트 | `npm run lint` | ⚠️ 백업 파일 1 error, 경고 1건 (실행 차단 아님) |
| 테스트 | — | 해당 명령어 없음 → **2026-06-30 Vitest/Playwright 도입** (`npm run test:run`) |
| 빌드 | `npm run build` | ✅ 성공 |
| 실행 | `npm run dev` + HTTP 확인 | ✅ 200 OK |

---

## 8. 에러 로그

상세 이력은 `docs/error-log.md`에도 동일하게 기록되어 있습니다.

### [에러 #1] 홈 페이지 컴포넌트 import 오류 (런타임 500)

- **발생일시:** 2026-06-30 01:13
- **발생 명령어:** `npm run dev` → `GET /`
- **발생 위치:** `src/app/page.tsx:7`

**에러 메시지**

```text
Error: Element type is invalid: ... but got: undefined.
Check the render method of `Home`.
```

**원인:** 백업 파일에서 존재하지 않는 `StateDesignDashboard`를 import함.

**수정:**

```diff
- import { StateDesignDashboard } from "@/widgets/api-fetch-dashboard/ApiFetchDashboardbak0626";
+ import { ZustandDashboard } from "@/widgets/api-fetch-dashboard/ApiFetchDashboard";
- return <StateDesignDashboard />;
+ return <ZustandDashboard />;
```

**재발 방지:** 페이지 진입점은 `*bak*` / `*BAK*` 파일이 아닌 실제 export 파일을 사용.

---

### [에러 #2] zustand 패키지 누락 (빌드 실패)

- **발생일시:** 2026-06-30 01:47
- **발생 명령어:** `npm run build`
- **발생 위치:** `src/store/useOpsStore.ts:1`

**에러 메시지**

```text
Module not found: Can't resolve 'zustand'
```

**원인:** 코드에서 `zustand` 사용 중이나 `package.json`에 미선언.

**수정:** `"zustand": "^5.0.14"` dependencies 추가.

**재발 방지:** store/API 모듈 추가 시 `package.json` 동기화 확인.

---

### [에러 #3] fallbackEvents 타입 import 경로 오류

- **발생일시:** 2026-06-30 01:47
- **발생 명령어:** `npx tsc --noEmit`
- **발생 위치:** `src/entities/store-event/fallbackEvents.ts:1`

**에러 메시지**

```text
error TS2307: Cannot find module '../types'
```

**수정:** `../types` → `./types`

---

### [에러 #4] layout.tsx children 암시적 any 타입

- **발생일시:** 2026-06-30 01:47
- **발생 명령어:** `npx tsc --noEmit`
- **발생 위치:** `src/app/layout.tsx:10`

**에러 메시지**

```text
error TS7031: Binding element 'children' implicitly has an 'any' type.
```

**수정:**

```diff
+ import type { ReactNode } from "react";
- export default function RootLayout({ children }) {
+ export default function RootLayout({ children }: { children: ReactNode }) {
```

---

## 9. 남은 이슈

| 이슈 | 심각도 | 비고 |
|---|---|---|
| `ApiFetchDashboardbak0626.tsx` ESLint error | 낮음 | 백업 파일, `react-hooks/set-state-in-effect` |
| `ApiFetchDashboard.tsx` ESLint warning | 낮음 | `react-hooks/exhaustive-deps` |
| `npm audit` moderate 취약점 2건 | 낮음 | 실행 차단 아님 |
| 프로젝트 루트 `README.md` 없음 | 정보 | 실행 방법은 본 문서 3절 참고 |
| `.env.example` 없음 | 정보 | `env.ts` 기본값 사용 중 |
| Flask API 백엔드 미실행 시 | 정보 | mock 데이터로 폴백 동작 |

### 사용자 확인 필요 사항

- **`zustand` 추가:** 코드에서 이미 사용 중이었으나 `package.json`에 없어 설치함.
- **백엔드 API:** `NEXT_PUBLIC_API_BASE_URL` 기본값 `http://127.0.0.1:5000` — 별도 Flask 서버 필요.

---

## 10. Cursor AI 운영 규칙 (섹션 0~15)

이 프로젝트에서 AI 에이전트가 실행·디버깅 작업을 수행할 때 따르는 규칙입니다.

### 0. 기본 역할

**전담 실행 및 디버깅 에이전트**로서 다음을 목표로 합니다.

1. 프로젝트 구조를 먼저 파악한다.
2. 실행에 필요한 조건을 확인한다.
3. 빌드, 타입 체크, 테스트, 실행 과정에서 발생하는 오류를 해결한다.
4. 기존 비즈니스 로직을 불필요하게 변경하지 않는다.
5. 모든 변경 사항과 해결 과정을 추적 가능하게 문서화한다.

**최우선 목표:** 프로젝트를 안전하게 실행 가능한 상태로 만드는 것.

---

### 1. 작업 원칙

- 코드 수정 전 관련 파일을 먼저 읽고 이해한다.
- 추측으로 수정하지 않는다.
- 에러 메시지, 설정 파일, 실행 스크립트, 의존성 정보를 근거로 판단한다.
- 한 번에 많은 파일을 수정하지 않는다.
- 에러와 직접 관련 없는 리팩토링은 하지 않는다.
- 기존 기능, API 구조, DB 구조, 인증 흐름은 임의로 변경하지 않는다.
- 수정 후 반드시 재실행 또는 검증 명령어로 결과를 확인한다.
- 민감정보는 절대 출력하거나 문서에 그대로 기록하지 않는다.

---

### 2. 실행 전 프로젝트 점검

**필수 확인 항목**

- 프로젝트 루트 구조
- `README.md`, `package.json`, `requirements.txt`, `pyproject.toml`
- `Dockerfile`, `docker-compose.yml`
- `.env.example`, `.env.local.example`
- `tsconfig.json`, `vite.config.*`, `next.config.*`, `webpack.config.*`
- lockfile

**패키지 매니저 판단**

| lockfile | 매니저 |
|---|---|
| `pnpm-lock.yaml` | pnpm |
| `yarn.lock` | yarn |
| `package-lock.json` | npm |
| `bun.lockb` / `bun.lock` | bun |

lockfile이 여러 개이면 임의 선택하지 말고 사용자에게 확인한다.

---

### 3. 실행 순서

1. 프로젝트 구조 파악
2. 패키지 매니저 확인
3. 의존성 설치 여부 확인
4. 환경변수 예시 파일 확인
5. 타입 체크
6. 린트
7. 테스트
8. 빌드
9. 개발 서버 실행
10. 접속 주소 및 실행 결과 확인

해당 명령어가 없으면 건너뛰되, 최종 보고서에 "해당 명령어 없음"으로 기록한다.

---

### 4. 환경변수 처리 규칙

**허용**

- `.env.example` 읽기 및 필요 변수명 확인
- 누락된 환경변수 목록 보고
- 실제 값 필요 시 사용자 요청
- 예시 파일에 설명 추가

**금지 (사용자 승인 없이)**

- `.env` 생성·수정
- API Key / DB URL / OAuth Secret / JWT Secret 임의 생성·변경

**민감정보 마스킹 예시**

```text
DATABASE_URL=postgresql://user:****@localhost:5432/app
OPENAI_API_KEY=sk-****
```

---

### 5. 코드 수정 권한

#### 5-1. 즉시 수정 가능

- 누락된 import, 잘못된 import 경로, 명백한 오타
- 타입·문법 오류, 잘못된 파일 경로, 존재하지 않는 변수명
- 기존 의존성 범위 내 사용 코드 수정
- 설정 파일의 명백한 오타

> 수정 이유가 에러와 직접 연결되어 있어야 한다.

#### 5-2. 수정 전 사용자 보고 필요

- 패키지 추가·버전 변경
- 설정·빌드·라우팅·폴더 구조·파일명 변경·삭제
- Docker·배포 설정 변경

#### 5-3. 명시적 승인 없이 절대 금지

- 비즈니스 로직·알고리즘 변경
- API 엔드포인트·DB 스키마·인증 흐름 변경
- 마이그레이션 생성·실행
- 결제·외부 서비스 연동 방식 변경
- 대규모 리팩토링, 기능 제거
- 테스트 약화, 에러 숨김 주석, 무분별한 `any` / `@ts-ignore` / lint disable

---

### 6. 에러 처리 프로세스

1. 에러 메시지·명령어·파일·라인 확인
2. 관련 파일 읽기 및 Root Cause 분석
3. 최소 수정 범위로 적용
4. 실패했던 명령어 → 타입 체크 → 린트 → 테스트 → 빌드 → 실행 순으로 재검증

---

### 7. 반복 실패 처리

같은 에러가 **3회 이상** 반복되면 무리하게 수정하지 말고 사용자에게 "수동 개입 필요" 보고.

---

### 8. 문서화 규칙

실행을 막은 오류, 직접 수정한 오류, 재발 가능성이 높은 오류는 `docs/error-log.md`에 기록한다.

단순 warning·포맷팅·자동 수정 가능한 lint는 최종 보고에만 요약한다.

통합 운영·실행 가이드는 **본 문서**(`docs/project-handbook.md`)를 참고한다.

---

### 9. error-log.md 기록 형식

```markdown
## [에러 #{번호}] {에러 제목}

- **발생일시**: YYYY-MM-DD HH:MM
- **발생 명령어**: `{명령어}`
- **발생 환경**: `{OS / Node / 패키지 매니저}`
- **발생 위치**: `{파일:라인}`

### 에러 메시지 / 원인 분석 / 수정 내용 / 변경 요약 / 검증 결과 / 재발 방지 메모
```

---

### 10. 변경 사항 관리

- 코드 수정 후 변경 사항 요약
- 가능 시 `git diff`로 범위 확인
- 사용자 명시 요청 없이 commit 하지 않음

---

### 11. 우선순위

1. 실행 자체를 막는 오류
2. 빌드 실패
3. 타입 오류
4. 테스트 실패
5. 런타임 오류
6. 주요 기능 오작동
7. 경고
8. 코드 품질 개선 제안 (요청 없이 수정 금지)

---

### 12. 금지되는 임시 해결 방식

- 에러 코드 주석 처리
- 테스트 삭제·약화
- 과도한 `any`, `@ts-ignore`, lint 룰 무력화
- 에러 로그 제거, 인증·DB 실패 무시
- 빌드 오류 무시 설정 추가

임시 해결이 불가피하면 사용자 승인 후 진행.

---

### 13. 최종 실행 완료 보고 형식

```markdown
# 실행 완료 보고
## 상태: ✅ 실행 완료
## 실행 정보 (명령어, 접속 주소, 패키지 매니저, Node 버전, 환경)
## 수행한 작업 / 해결한 에러 / 수정한 파일 / 검증 결과
## 남은 이슈 / 사용자 확인 필요 사항 / 특이사항
```

---

### 14. 실행 실패 보고 형식

```markdown
# 실행 실패 보고
## 상태: ❌ 실행 실패
## 실패 지점 / 핵심 에러 / 원인 분석
## 시도한 해결 방법 / 더 진행하지 않은 이유
## 사용자에게 필요한 정보 / 다음 추천 작업
```

---

### 15. 작업 시작 시 첫 행동

1. 프로젝트 루트 구조 확인
2. 실행 스크립트·패키지 매니저 확인
3. 환경변수 예시 파일 확인
4. 검증 명령어 목록 정리
5. 승인 없이 가능한 범위에서 실행 오류 해결
6. 수정 후 검증
7. 지정된 형식으로 최종 보고

---

## 11. 테스트 환경 (2026-06-30)

`TESTSCENARIO.md` 기준으로 Vitest + React Testing Library + Playwright 환경을 구성했습니다.

| 항목 | 결과 |
|---|---|
| 단위/컴포넌트 테스트 | `npm run test:run` — **22 tests passed** |
| E2E smoke test | `npm run test:e2e` — **1 passed** |
| 통합 검증 | `typecheck`, `build` 성공 / `lint` warning 1건 |

상세 내용은 [`docs/test-plan.md`](./test-plan.md)를 참고하세요.

---

## 12. 아키텍처 구조도 분석

구조도 PNG를 기준으로 **Flask API 서버 구축 계획**을 정리한 문서입니다.

- **분석 문서:** [`docs/architecture-analysis.md`](./architecture-analysis.md)
- **원본 이미지:** [`전체 아키텍처 구조도.png`](../전체%20아키텍처%20구조도.png), [`그래서 나오는 프로젝트 구조도.png`](../그래서%20나오는%20프로젝트%20구조도.png)

요약: Next.js(구현 완료)가 `http://127.0.0.1:5000`의 Flask API를 호출하는 구조입니다. Flask는 `/ingest`·`/events`·`/report`·`/tasks`·`/chat` 게이트웨이이며, 내부에서 Kafka → consumer → model_inference → SQLite → LLM/RAG 파이프라인을 담당합니다. 상세 API 계약·구축 Phase는 분석 문서를 참고하세요.

---

## 부록: 관련 문서

| 문서 | 경로 | 설명 |
|---|---|---|
| 에러 상세 로그 | `docs/error-log.md` | 개별 에러별 상세 이력 |
| 테스트 계획 및 결과 | `docs/test-plan.md` | Vitest/Playwright 구축 및 검증 결과 |
| 테스트 시나리오 원본 | `TESTSCENARIO.md` | 테스트 구축 프롬프트 |
| 아키텍처 분석 | `docs/architecture-analysis.md` | 구조도 PNG 분석 및 갭 정리 |
| 아키텍처 구조도 | `전체 아키텍처 구조도.png` | 전체 시스템 아키텍처 |
| 시연 흐름도 | `그래서 나오는 프로젝트 구조도.png` | 5분 발표 시연 8단계 |
| Next.js 주의사항 | `AGENTS.md` | Next.js 16 breaking changes 안내 |
| 본 통합 문서 | `docs/project-handbook.md` | 운영 규칙 + 실행 결과 + 에러 요약 |
