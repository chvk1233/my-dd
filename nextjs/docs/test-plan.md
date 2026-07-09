# Next.js 테스트 계획 및 결과

> **작업 기준:** `TESTSCENARIO.md`  
> **최종 갱신:** 2026-06-30  
> **상태:** ✅ 완료

---

## 1. 테스트 목표

- Next.js App Router 프로젝트에 최소 변경으로 테스트 환경 구축
- Flask API 없이도 통과 가능한 mock 기반 테스트 우선 작성
- Zustand store, fallback 데이터, 대시보드 렌더링 검증
- E2E smoke test로 홈 페이지 실제 동작 확인

---

## 2. 테스트 도구

| 구분 | 도구 |
|---|---|
| 단위 / 컴포넌트 테스트 | Vitest 4.x |
| 컴포넌트 렌더링 | React Testing Library |
| DOM 환경 | jsdom |
| 매처 확장 | @testing-library/jest-dom |
| 사용자 인터랙션 | @testing-library/user-event |
| E2E 테스트 | Playwright |
| 정적 검증 | TypeScript, ESLint, `next build` |

---

## 3. 추가 또는 수정한 패키지

| 패키지 | 용도 |
|---|---|
| `vitest` | 테스트 러너 |
| `@vitejs/plugin-react` | Vitest에서 JSX 변환 |
| `jsdom` | 브라우저 DOM 시뮬레이션 |
| `@testing-library/react` | 컴포넌트 테스트 |
| `@testing-library/jest-dom` | DOM 매처 |
| `@testing-library/user-event` | 클릭 등 사용자 이벤트 |
| `@playwright/test` | E2E 테스트 |

---

## 4. 추가 또는 수정한 scripts

| script | 명령어 | 용도 |
|---|---|---|
| `typecheck` | `tsc --noEmit` | TypeScript 검사 |
| `test` | `vitest` | watch 모드 테스트 |
| `test:run` | `vitest run` | CI/일회성 테스트 |
| `test:ui` | `vitest --ui` | Vitest UI |
| `test:e2e` | `playwright test` | E2E smoke test |
| `test:e2e:ui` | `playwright test --ui` | Playwright UI |
| `verify` | typecheck + lint + test:run + build | 통합 검증 |

---

## 5. 테스트 범위

### 단위 테스트

- `formatters` — severity, event id 조회
- `fallbackEvents` — mock 데이터 구조
- `env` — API 기본 URL
- `httpClient` — 성공/실패 응답 처리
- `useOpsStore` — 초기 상태, loadEvents, loading, error, selectEvent, API 실패 fallback

### 컴포넌트 테스트

- `EventList` — 목록 렌더, 클릭 시 onSelect
- `EventDetail` — 상세 표시, empty state
- `ZustandDashboard` — 대시보드 렌더, API 실패 mock 표시, 이벤트 선택 시 상세 변경

### E2E 테스트

- `/` 접속 HTTP 200
- 대시보드 핵심 heading 표시
- mock/fallback 데이터 표시
- 이벤트 클릭 후 상세 영역 변경

### 제외 / 미구현

- 실제 Flask API 연동 E2E (백엔드 실행 시 별도 수행)
- `ApiHealthPanel`, `LocalChatPanel` 상세 테스트 (향후 확장)

---

## 6. 작성한 테스트 파일

| 파일 | 테스트 대상 | 검증 내용 |
|---|---|---|
| `src/entities/store-event/formatters.test.ts` | formatter | severity, findEventById |
| `src/entities/store-event/fallbackEvents.test.ts` | fallback 데이터 | 필수 필드, 고유 ID |
| `src/shared/config/env.test.ts` | env config | 기본 URL, env 오버라이드 |
| `src/shared/api/httpClient.test.ts` | API client | JSON 성공, HTTP 실패 |
| `src/store/useOpsStore.test.ts` | Zustand store | 초기값, 로딩, API 성공/실패, 선택 |
| `src/features/events/event-list/EventList.test.tsx` | EventList, EventDetail | 렌더, 클릭, placeholder |
| `src/widgets/api-fetch-dashboard/ApiFetchDashboard.test.tsx` | ZustandDashboard | 렌더, fallback, 선택 흐름 |
| `tests/e2e/home.spec.ts` | 홈 페이지 E2E | smoke test 전체 흐름 |

### 설정 파일

| 파일 | 설명 |
|---|---|
| `vitest.config.ts` | Vitest + path alias |
| `vitest.setup.ts` | jest-dom 설정 |
| `vitest-env.d.ts` | Vitest/RTL 타입 |
| `playwright.config.ts` | E2E + dev server 자동 기동 |

---

## 7. 실행한 검증 명령어

```bash
npm install
npx tsc --noEmit
npm run lint
npm run build
npm run test:run
npx playwright install chromium
npm run test:e2e
npm run typecheck
npm run verify  # (개별 명령어로 각각 성공 확인)
```

---

## 8. 검증 결과

| 검증 항목 | 명령어 | 결과 |
|---|---|---|
| 의존성 설치 | `npm install` | ✅ 성공 |
| 타입 체크 | `npm run typecheck` | ✅ 성공 |
| 린트 | `npm run lint` | ⚠️ warning 1건 (`ApiFetchDashboard.tsx` hooks deps) |
| 단위/컴포넌트 테스트 | `npm run test:run` | ✅ 7 files, 22 tests passed |
| E2E 테스트 | `npm run test:e2e` | ✅ 1 passed |
| 빌드 | `npm run build` | ✅ 성공 |

### 기준 검증 전 상태 (테스트 도구 도입 전)

| 항목 | 결과 |
|---|---|
| `npx tsc --noEmit` | ✅ 성공 |
| `npm run lint` | ⚠️ 백업 파일 1 error + warning 1건 |
| `npm run build` | ✅ 성공 |

---

## 9. 남은 이슈

| 이슈 | 비고 |
|---|---|
| `ApiFetchDashboard.tsx` `react-hooks/exhaustive-deps` warning | 비즈니스 로직 변경 없이 유지 |
| 실제 Flask API 연동 E2E | 백엔드 실행 시 별도 태그/스크립트로 분리 권장 |
| `npm audit` moderate 2건 | 테스트와 무관, 별도 검토 |

### 설정 변경 사항

- `eslint.config.mjs`: 백업 파일(`*BAK*`, `*bak*`) lint 대상에서 제외 — 삭제 없이 lint error 해소

---

## 10. 다음 단계

1. `ApiHealthPanel`, `LocalChatPanel` smoke test 추가
2. Flask API 연동 선택 테스트 (`test:e2e:api` 등 별도 script)
3. CI 파이프라인에 `npm run verify`, `npm run test:e2e` 연결
4. `ApiFetchDashboard.tsx` hooks warning — store 구조 변경 없이 해결 가능한지 검토

---

## 관련 문서

- `TESTSCENARIO.md` — 테스트 구축 프롬프트 원본
- `docs/project-handbook.md` — 프로젝트 통합 운영 문서
- `docs/error-log.md` — 실행/빌드 에러 이력
