"use client";

import { useState } from "react";

type LocalChatPanelProps = {
  answer: string;
  sources?: string[];
  loading?: boolean;
  onAsk: (question: string) => Promise<void>;
};

export function LocalChatPanel({ answer, sources = [], loading, onAsk }: LocalChatPanelProps) {
  const [question, setQuestion] = useState("환불 요청 고객에게 먼저 확인할 것은?");

  return (
    <section className="panel">
      <h2>문서 챗봇 (RAG)</h2>
      <div className="inlineForm">
        <input
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          aria-label="질문"
        />
        <button type="button" disabled={loading} onClick={() => void onAsk(question)}>
          질문
        </button>
      </div>
      <pre>{answer || "아직 질문하지 않았습니다."}</pre>
      {sources.length > 0 && (
        <ul>
          {sources.map((source) => (
            <li key={source}>{source}</li>
          ))}
        </ul>
      )}
    </section>
  );
}
