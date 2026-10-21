
import { useState } from "react";
import ChatInput from "./components/ChatInput";
import ChatMessage from "./components/ChatMessage";
import { askQuestion } from "./services/api";
import type { Message } from "./types/chat";
import "./App.css";
import DatasetPanel from "./components/DatasetPanel";
import SQLPanel from "./components/SQLPanel";

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSend(question: string) {
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
      const response = await askQuestion(question);

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.answer,
      };

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
                AgenticSQL is processing...
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
