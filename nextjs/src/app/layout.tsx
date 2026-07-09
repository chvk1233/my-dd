import type { ReactNode } from "react";
import "./global.css";

export const metadata = {
    title: "Frontend 01 Mock Dashboard JSX",
    description: "JSX mock dashboard for the AI store operations course"
  };
  
// 모든 페이지를 감싸는 공통의 컴포넌트(껍데기)
// 공통 디자인 구축, 전역 CSS 로딩
  export default function RootLayout({ children }: { children: ReactNode }) {
    return (
      <html lang="ko">
        <body>{children}</body>
      </html>
    );
  }