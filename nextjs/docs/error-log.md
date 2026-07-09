# Error Log

## [에러 #1] 홈 페이지 컴포넌트 import 오류 (런타임 500)

- **발생일시**: 2026-06-30 01:13
- **발생 명령어**: `npm run dev` → `GET /`
- **발생 환경**: Windows 10 / Node v24.15.0 / npm
- **발생 위치**: `src/app/page.tsx:7`

### 에러 메시지

```text
Error: Element type is invalid: expected a string (for built-in components) or a class/function (for composite components) but got: undefined.
Check the render method of `Home`.
```

### 원인 분석

`page.tsx`가 백업 파일(`ApiFetchDashboardbak0626.tsx`)에서 존재하지 않는 `StateDesignDashboard`를 named import하고 있었습니다. 해당 백업 파일은 `ApiFetchDashboard`만 export하며, 실제 사용 중인 컴포넌트는 `ApiFetchDashboard.tsx`의 `ZustandDashboard`입니다.

### 수정 내용

* 수정 파일: `src/app/page.tsx`
* 수정 위치: import 및 JSX 렌더 대상
* 수정 이유: undefined 컴포넌트 렌더로 인한 500 오류 해결

### 변경 요약

```diff
- import { StateDesignDashboard } from "@/widgets/api-fetch-dashboard/ApiFetchDashboardbak0626";
+ import { ZustandDashboard } from "@/widgets/api-fetch-dashboard/ApiFetchDashboard";
- return <StateDesignDashboard />;
+ return <ZustandDashboard />;
```

### 검증 결과

```text
Invoke-WebRequest http://localhost:3000 → 200 OK
npm run build → 성공
```

### 재발 방지 메모

페이지 진입점은 백업(`*bak*`, `*BAK*`) 파일이 아닌 실제 export 파일을 import해야 합니다. 컴포넌트명 변경 시 `page.tsx` import를 함께 확인하세요.

---

## [에러 #2] zustand 패키지 누락 (빌드 실패)

- **발생일시**: 2026-06-30 01:47
- **발생 명령어**: `npm run build`
- **발생 환경**: Windows 10 / Node v24.15.0 / npm
- **발생 위치**: `src/store/useOpsStore.ts:1`

### 에러 메시지

```text
Module not found: Can't resolve 'zustand'
```

### 원인 분석

`useOpsStore.ts`에서 `zustand`를 사용하지만 `package.json` dependencies에 선언되어 있지 않았습니다.

### 수정 내용

* 수정 파일: `package.json`, `package-lock.json`
* 수정 위치: dependencies
* 수정 이유: 코드에서 사용 중인 필수 의존성 추가

### 변경 요약

```diff
+ "zustand": "^5.0.14"
```

### 검증 결과

```text
npm install zustand → 성공
npm run build → 성공
npx tsc --noEmit → 성공 (빌드 내 TypeScript 검사 통과)
```

### 재발 방지 메모

store/API 등 새 모듈 추가 시 `package.json` dependencies 동기화를 확인하세요.

---

## [에러 #3] fallbackEvents 타입 import 경로 오류

- **발생일시**: 2026-06-30 01:47
- **발생 명령어**: `npx tsc --noEmit`
- **발생 환경**: Windows 10 / Node v24.15.0 / npm
- **발생 위치**: `src/entities/store-event/fallbackEvents.ts:1`

### 에러 메시지

```text
error TS2307: Cannot find module '../types' or its corresponding type declarations.
```

### 원인 분석

`types.ts`는 같은 `store-event` 디렉터리에 있으나 `../types`로 잘못 참조하고 있었습니다.

### 수정 내용

* 수정 파일: `src/entities/store-event/fallbackEvents.ts`
* 수정 위치: import 경로
* 수정 이유: TypeScript 모듈 해석 오류 수정

### 변경 요약

```diff
- import type { StoreEvent } from "../types";
+ import type { StoreEvent } from "./types";
```

### 검증 결과

```text
npx tsc --noEmit → 성공
npm run build → 성공
```

### 재발 방지 메모

동일 디렉터리 타입은 `./types` 형태로 import합니다.

---

## [에러 #4] layout.tsx children 암시적 any 타입

- **발생일시**: 2026-06-30 01:47
- **발생 명령어**: `npx tsc --noEmit`
- **발생 환경**: Windows 10 / Node v24.15.0 / npm
- **발생 위치**: `src/app/layout.tsx:10`

### 에러 메시지

```text
error TS7031: Binding element 'children' implicitly has an 'any' type.
```

### 원인 분석

`strict` 모드에서 `children` props에 타입이 지정되지 않았습니다.

### 수정 내용

* 수정 파일: `src/app/layout.tsx`
* 수정 위치: RootLayout props
* 수정 이유: TypeScript strict 타입 오류 해결

### 변경 요약

```diff
+ import type { ReactNode } from "react";
- export default function RootLayout({ children }) {
+ export default function RootLayout({ children }: { children: ReactNode }) {
```

### 검증 결과

```text
npx tsc --noEmit → 성공
npm run build → 성공
```

### 재발 방지 메모

레이아웃/페이지 컴포넌트 props에는 `ReactNode` 등 명시적 타입을 지정하세요.
