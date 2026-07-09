import type { AnalysisResult, StoreEvent } from "@/entities/store-event";

type EventAnalysisPanelProps = {
  analysis: AnalysisResult | null;
  event?: StoreEvent;
};

export function EventAnalysisPanel({ analysis, event }: EventAnalysisPanelProps) {
  const predictedType = analysis?.predicted_type || event?.predicted_type || event?.event_type || "-";
  const severity = analysis?.severity || event?.severity || event?.severity_hint || "-";
  const confidence = analysis?.confidence ?? event?.confidence;
  const source = analysis?.source || "event";

  return (
    <section className="panel">
      <h2>AI 분석 결과</h2>
      <dl>
        <dt>predicted_type</dt>
        <dd>{predictedType}</dd>
        <dt>severity</dt>
        <dd>{severity}</dd>
        <dt>confidence</dt>
        <dd>{confidence != null ? confidence : "-"}</dd>
        <dt>source</dt>
        <dd>{source}</dd>
      </dl>
    </section>
  );
}
