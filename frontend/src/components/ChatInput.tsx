
import { useState } from "react";
import type { FormEvent } from "react";

interface ChatInputProps {
  onSend: (question: string) => Promise<void>;
  loading: boolean;
}

export default function ChatInput({
  onSend,
  loading,
}: ChatInputProps) {
  const [question, setQuestion] = useState("");

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();

    const text = question.trim();
    if (!text || loading) return;

    setQuestion("");
    await onSend(text);
  }

  return (
    <form className="chat-form" onSubmit={handleSubmit}>
      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a question about your data..."
        rows={3}
        maxLength={2000}
        disabled={loading}
      />

      <button
        type="submit"
        disabled={loading || !question.trim()}
      >
        {loading ? "Processing..." : "Ask AgenticSQL"}
      </button>
    </form>
  );
}

