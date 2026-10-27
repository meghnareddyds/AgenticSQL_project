import { useState } from "react";

import ChatInput from "./components/ChatInput";
import ChatMessage from "./components/ChatMessage";
import DatasetPanel from "./components/DatasetPanel";
import SQLPanel from "./components/SQLPanel";

import {
  askQuestion,
  analyzeData,
} from "./services/api";

import type { Message } from "./types/chat";

import "./App.css";

type ChatMode = "ai" | "analyze";

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [mode, setMode] = useState<ChatMode>("analyze");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSend(question: string) {
    if (loading || !question.trim()) {
      return;
    }

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: question,
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setLoading(true);
    setError("");

    try {
      let assistantMessage: Message;

      if (mode === "ai") {
        const response = await askQuestion(question);

        assistantMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.answer,
        };
      } else {
        const response = await analyzeData(question);

        assistantMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content:
            "Analysis completed using your uploaded dataset.",
          sql: response.sql ?? undefined,
          result: response.result ?? undefined,
        };
      }

      setMessages((previous) => [
        ...previous,
        assistantMessage,
      ]);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="logo">SQL</div>

        <div>
          <h1>AgenticSQL</h1>
          <p>AI-Powered Data Analytics Platform</p>
        </div>
      </header>

      <main className="main-container">
        <section className="welcome-section">
          <h2>Ask questions about your data</h2>
          <p>
            Explore datasets using natural language.
            Generate SQL queries and discover insights.
          </p>
        </section>

        <section className="chat-container">
          <div className="mode-selector">
            <button
              type="button"
              className={
                mode === "analyze"
                  ? "mode-button active"
                  : "mode-button"
              }
              onClick={() => setMode("analyze")}
              disabled={loading}
            >
              Analyze Data
            </button>

            <button
              type="button"
              className={
                mode === "ai"
                  ? "mode-button active"
                  : "mode-button"
              }
              onClick={() => setMode("ai")}
              disabled={loading}
            >
              Ask AI
            </button>
          </div>

          <div className="mode-description">
            {mode === "analyze"
              ? "Ask questions about your uploaded dataset. AgenticSQL will generate and execute validated SQL."
              : "Ask general questions about SQL and data analytics."}
          </div>

          <div className="messages">
            {messages.length === 0 && (
              <div className="empty-state">
                <h3>Welcome to AgenticSQL</h3>
                <p>
                  Try asking: Show me the top 5
                  products by revenue.
                </p>
              </div>
            )}

            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
              />
            ))}

            {loading && (
              <p className="loading-text">
                {mode === "analyze"
                  ? "Generating SQL and analyzing your data..."
                  : "AgenticSQL is thinking..."}
              </p>
            )}
          </div>

          {error && (
            <div className="error-message" role="alert">
              {error}
            </div>
          )}

          <ChatInput
            onSend={handleSend}
            loading={loading}
          />
        </section>

        <DatasetPanel />
        <SQLPanel />
      </main>
    </div>
  );
}

export default App;

