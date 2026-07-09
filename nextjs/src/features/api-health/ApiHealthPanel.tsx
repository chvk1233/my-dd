import type { HealthResponse } from "@/entities/store-event";

type ApiHealthPanelProps = {
  health: HealthResponse | null;
  error: string;
};

export function ApiHealthPanel({ health, error }: ApiHealthPanelProps) {
  return (
    <section className="hero">
      <p className="eyebrow">Frontend 02</p>
      <h1>Flask API 요청/응답 연결</h1>
      <p>{health ? `API ${health.status} · events ${health.events_count}` : "API 상태 확인 중"}</p>
      {error && <p className="notice">{error}</p>}
    </section>
  );
}