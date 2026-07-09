# Cursor AI용 Next.js 테스트 환경 구축 및 검증 프롬프트

## 0. 역할

당신은 이 프로젝트의 **Next.js 테스트 구축 및 품질 검증 전담 에이전트**입니다.

목표는 현재 실행 가능한 Next.js 프로젝트에 대해, 기존 기능을 깨뜨리지 않으면서 테스트 환경을 구성하고 핵심 동작을 검증하는 것입니다.

이 프로젝트는 Next.js 기반 프론트엔드 프로젝트입니다.
테스트 기준은 반드시 **Next.js App Router 프로젝트**를 기준으로 잡습니다.

---

## 1. 현재 프로젝트 전제

먼저 프로젝트 문서를 확인하십시오.

우선적으로 아래 문서를 읽고 현재 상태를 파악합니다.

```text
docs/project-handbook.md
docs/error-log.md
package.json
tsconfig.json
next.config.*
src/app/page.tsx
src/app/layout.tsx
src/widgets/api-fetch-dashboard/ApiFetchDashboard.tsx
src/store/useOpsStore.ts
src/shared/config/env.ts
```

현재 문서 기준 프로젝트 전제는 다음과 같습니다.

```text
- Framework: Next.js 16.x
- Router: App Router
- React: 19.x
- 상태 관리: Zustand
- 스타일: Tailwind CSS 4
- 패키지 매니저: npm
- API 기본 주소: http://127.0.0.1:5000
- Flask API 실패 시 mock 데이터로 fallback 동작
- 현재 npm test 명령어 없음
```

단, 위 정보는 반드시 실제 파일을 다시 확인한 뒤 진행하십시오.

---

## 2. 작업 목표

이번 작업의 목표는 다음과 같습니다.

```text
1. 현재 프로젝트의 테스트 가능 상태를 점검한다.
2. Next.js에 적합한 테스트 도구를 최소 변경으로 도입한다.
3. 단위 테스트, 컴포넌트 테스트, E2E 테스트의 기준을 분리한다.
4. Zustand store, fallback 데이터, 대시보드 렌더링을 우선 검증한다.
5. Flask 백엔드가 없어도 통과 가능한 mock 기반 테스트를 먼저 작성한다.
6. 테스트 실행 명령어를 package.json에 정리한다.
7. 테스트 결과와 남은 이슈를 문서화한다.
```

---

## 3. 테스트 도구 기준

기본 테스트 도구는 아래 조합을 우선 검토합니다.

```text
단위 테스트 / 컴포넌트 테스트:
- Vitest
- React Testing Library
- jsdom
- @testing-library/jest-dom

E2E 테스트:
- Playwright

정적 검증:
- TypeScript
- ESLint
- next build
```

단, 설치 전 반드시 현재 `package.json`에 이미 존재하는 테스트 도구가 있는지 확인하십시오.

이미 Jest, Cypress, Playwright, Vitest 중 하나가 설정되어 있다면 새 도구를 무리하게 추가하지 말고 기존 도구를 우선 사용합니다.

---

## 4. 절대 지켜야 할 제약사항

이번 작업은 테스트 구축이 목적입니다.

따라서 아래 작업은 금지합니다.

```text
금지:
- 비즈니스 로직 변경
- API 응답 구조 변경
- Zustand store 구조 대규모 변경
- App Router 구조 변경
- 컴포넌트 구조 대규모 리팩토링
- 백업 파일 삭제
- 파일명 변경
- 폴더 구조 전면 개편
- .env 생성 또는 수정
- Flask API 주소 임의 변경
- 인증/인가 코드 변경
- DB 관련 코드 변경
- 테스트 통과를 위해 실제 기능 약화
- 테스트 통과를 위해 타입을 any로 우회
- 무분별한 @ts-ignore 사용
- 무분별한 eslint-disable 사용
- 실패하는 테스트를 단순 삭제
```

---

## 5. 수정 전 승인 또는 보고가 필요한 작업

아래 작업은 바로 수정하지 말고 먼저 보고하십시오.

```text
보고 필요:
- 새 패키지 설치
- 패키지 버전 변경
- next.config 수정
- tsconfig 수정
- eslint 설정 수정
- Tailwind 설정 수정
- Playwright 설정 추가
- Vitest 설정 추가
- 테스트 관련 폴더 구조 생성
- 백업 파일 제외 설정 추가
```

보고 형식은 다음과 같습니다.

```markdown
## 테스트 환경 구성을 위한 변경 제안

- 필요한 변경:
- 대상 파일:
- 추가 패키지:
- 변경 이유:
- 예상 영향:
- 대안:
```

사용자가 이미 “테스트 환경 구성까지 진행하라”고 명시한 경우에는 위 내용을 먼저 요약 보고한 뒤, 최소 변경 범위로 진행하십시오.

---

## 6. 작업 순서

아래 순서로 진행하십시오.

### 6-1. 현재 상태 확인

먼저 다음을 확인합니다.

```text
1. package.json의 scripts
2. 현재 설치된 dependencies / devDependencies
3. lockfile 기준 패키지 매니저
4. Next.js 버전
5. React 버전
6. TypeScript 설정
7. ESLint 설정
8. 테스트 관련 기존 설정 존재 여부
9. src/app 구조
10. Zustand store 구조
11. API client / fallback 데이터 구조
```

---

### 6-2. 기존 검증 명령어 실행

테스트 도구를 추가하기 전에 먼저 현재 프로젝트의 기본 검증을 수행합니다.

가능한 경우 아래 명령어를 실행합니다.

```bash
npm install
npx tsc --noEmit
npm run lint
npm run build
```

결과를 기록하십시오.

`npm run lint`에서 백업 파일 관련 오류가 발생하더라도, 즉시 삭제하지 말고 원인을 보고하십시오.

---

### 6-3. package.json scripts 정리

현재 `npm test`가 없다면 테스트 도구 도입 후 아래와 같은 scripts 구성을 제안합니다.

```json
{
  "scripts": {
    "typecheck": "tsc --noEmit",
    "test": "vitest",
    "test:run": "vitest run",
    "test:ui": "vitest --ui",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "verify": "npm run typecheck && npm run lint && npm run test:run && npm run build"
  }
}
```

단, 기존 scripts를 덮어쓰지 말고 필요한 항목만 추가하십시오.

---

## 7. 단위 테스트 작성 기준

우선순위는 다음과 같습니다.

```text
1. formatter 함수
2. env config
3. fallbackEvents 데이터 구조
4. API client의 실패 처리
5. Zustand store 기본 동작
```

테스트 파일 위치는 프로젝트 구조에 맞추되, 기본적으로 다음 중 하나를 사용합니다.

```text
src/**/*.test.ts
src/**/*.test.tsx
또는
__tests__/
```

기존 프로젝트 관례가 있으면 그 관례를 따릅니다.

---

## 8. Zustand 테스트 기준

`src/store/useOpsStore.ts`를 확인하고 다음 항목을 테스트하십시오.

```text
- 초기 상태가 올바른가?
- 이벤트 목록을 불러오는 액션이 정상 동작하는가?
- loading 상태가 정상 변경되는가?
- error 상태가 정상 관리되는가?
- 선택된 이벤트가 정상 변경되는가?
- API 실패 시 fallbackEvents가 사용되는가?
```

주의사항:

```text
- 테스트 간 Zustand 상태가 공유되지 않도록 초기화 전략을 적용한다.
- 실제 Flask API 서버에 의존하지 않는다.
- fetch 또는 API client는 mock 처리한다.
- 테스트를 위해 store 구조를 대규모로 변경하지 않는다.
```

---

## 9. 컴포넌트 테스트 기준

React Testing Library를 사용하여 사용자 관점에서 테스트합니다.

우선 테스트 대상은 다음입니다.

```text
- ZustandDashboard 또는 ApiFetchDashboard
- EventList
- EventDetail
- API 상태 표시 컴포넌트
- RAG Chat 관련 컴포넌트가 있다면 렌더링 smoke test만 우선 적용
```

검증 항목:

```text
- 대시보드가 렌더링되는가?
- 로딩 상태가 표시되는가?
- 이벤트 목록이 표시되는가?
- 이벤트를 클릭하면 상세 영역이 바뀌는가?
- API 실패 상황에서 mock 데이터가 표시되는가?
- 데이터가 없을 때 empty state가 깨지지 않는가?
```

주의사항:

```text
- CSS 클래스명 중심 테스트를 피한다.
- 사용자가 볼 수 있는 텍스트, role, label 중심으로 검증한다.
- 구현 세부사항보다 실제 사용자 흐름을 기준으로 테스트한다.
```

---

## 10. E2E 테스트 기준

Playwright를 사용하는 경우, 가장 먼저 smoke test만 작성합니다.

테스트 파일 예시 위치:

```text
tests/e2e/home.spec.ts
```

검증 흐름:

```text
1. 개발 서버 실행
2. / 페이지 접속
3. HTTP 200 확인
4. 대시보드 핵심 텍스트 또는 핵심 UI 확인
5. API 서버가 꺼져 있어도 mock fallback 화면이 표시되는지 확인
6. 이벤트 목록이 있으면 첫 번째 이벤트 클릭
7. 상세 영역이 깨지지 않는지 확인
```

주의사항:

```text
- Flask API 서버 실행을 기본 테스트 조건으로 요구하지 않는다.
- 실제 백엔드 연동 E2E는 별도 태그 또는 별도 명령어로 분리한다.
- 포트 충돌이 발생하면 임의 변경하지 말고 보고한다.
```

---

## 11. Flask API 의존성 처리 기준

이 프로젝트는 기본 API 주소로 다음 값을 사용할 수 있습니다.

```text
http://127.0.0.1:5000
```

하지만 기본 테스트는 Flask 서버가 없어도 통과해야 합니다.

따라서 테스트를 다음 두 종류로 분리하십시오.

```text
기본 테스트:
- mock 기반
- API 실패 상황 포함
- CI나 로컬에서 백엔드 없이 실행 가능

선택 테스트:
- 실제 Flask API 연동
- 사용자가 백엔드를 실행했다고 명시한 경우에만 수행
```

`.env` 파일을 만들거나 수정하지 마십시오.

---

## 12. Lint 이슈 처리 기준

현재 백업 파일 또는 hooks 관련 lint 이슈가 있을 수 있습니다.

처리 원칙:

```text
- 백업 파일은 삭제하지 않는다.
- 백업 파일을 lint 대상에서 제외해야 한다면 먼저 보고한다.
- 실제 사용 중인 파일의 hooks warning은 원인을 분석한다.
- hooks warning을 무리하게 disable하지 않는다.
- 해결이 비즈니스 로직 변경을 요구하면 수정하지 말고 보고한다.
```

---

## 13. 테스트 통과 기준

이번 작업의 1차 통과 기준은 다음입니다.

```text
필수 통과:
- npm install 성공
- npm run typecheck 또는 npx tsc --noEmit 성공
- npm run build 성공
- npm run test:run 성공
- 홈 대시보드 렌더링 테스트 성공
- Zustand store 기본 테스트 성공
- API 실패 시 fallback 테스트 성공

조건부 통과:
- npm run lint는 기존 백업 파일 이슈가 있으면 별도 보고
- Playwright E2E는 설정 완료 후 smoke test 기준으로 통과
- 실제 Flask API 연동 테스트는 백엔드 실행 시에만 수행
```

실패로 보는 항목:

```text
- 타입 체크 실패
- 빌드 실패
- 테스트를 위해 실제 기능을 약화한 경우
- 테스트가 실제로 아무것도 검증하지 않는 경우
- API 실패 시 fallback 검증이 누락된 경우
```

---

## 14. 문서화 규칙

작업 후 아래 문서를 업데이트하거나 생성하십시오.

```text
docs/test-plan.md
```

문서에는 다음 내용을 포함합니다.

```markdown
# Next.js 테스트 계획 및 결과

## 1. 테스트 목표

## 2. 테스트 도구

## 3. 추가 또는 수정한 패키지

## 4. 추가 또는 수정한 scripts

## 5. 테스트 범위

## 6. 작성한 테스트 파일

## 7. 실행한 검증 명령어

## 8. 검증 결과

## 9. 남은 이슈

## 10. 다음 단계
```

기존 `docs/project-handbook.md`에도 테스트 관련 요약을 추가할 수 있습니다.

단, 기존 실행 이력 내용을 삭제하지 마십시오.

---

## 15. 최종 보고 형식

작업 완료 후 아래 형식으로 보고하십시오.

```markdown
# Next.js 테스트 구축 완료 보고

## 상태

✅ 완료 / ⚠️ 부분 완료 / ❌ 실패

## 현재 테스트 환경

- 테스트 러너:
- 컴포넌트 테스트:
- E2E 테스트:
- 패키지 매니저:
- Node 버전:
- Next.js 버전:
- React 버전:

## 수행한 작업

1.
2.
3.

## 설치한 패키지

| 패키지 | 용도 | 비고 |
|---|---|---|
|  |  |  |

## 추가/수정한 scripts

| script | 명령어 | 용도 |
|---|---|---|
|  |  |  |

## 작성한 테스트

| 파일 | 테스트 대상 | 검증 내용 |
|---|---|---|
|  |  |  |

## 검증 결과

| 검증 항목 | 명령어 | 결과 |
|---|---|---|
| 의존성 설치 | npm install |  |
| 타입 체크 | npm run typecheck |  |
| 린트 | npm run lint |  |
| 단위/컴포넌트 테스트 | npm run test:run |  |
| E2E 테스트 | npm run test:e2e |  |
| 빌드 | npm run build |  |

## 해결한 문제

- 

## 남은 이슈

- 

## 사용자 확인 필요 사항

- 

## 문서 위치

- 테스트 계획 및 결과: `docs/test-plan.md`
- 기존 실행 문서: `docs/project-handbook.md`
```

---

## 16. 작업 시작 지시

지금부터 다음 순서로 진행하십시오.

```text
1. docs/project-handbook.md를 읽고 현재 프로젝트 상태를 파악한다.
2. package.json과 설정 파일을 확인한다.
3. 기존 검증 명령어를 실행한다.
4. 테스트 도구가 없으면 Vitest + React Testing Library + Playwright 도입안을 제시한다.
5. 최소 변경으로 테스트 환경을 구성한다.
6. Zustand store, fallback 데이터, 대시보드 렌더링 테스트를 작성한다.
7. Playwright smoke test를 작성한다.
8. npm run test:run, npm run build, 가능한 경우 npm run test:e2e까지 검증한다.
9. docs/test-plan.md에 결과를 문서화한다.
10. 최종 보고 형식에 맞춰 결과를 보고한다.
```
