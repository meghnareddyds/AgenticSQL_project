
import type { Message } from "../types/chat";

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({
  message,
}: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={`message ${
        isUser ? "user-message" : "assistant-message"
      }`}
    >
      <div className="message-label">
        {isUser ? "You" : "AgenticSQL"}
      </div>

      <div className="message-content">
        {message.content}
      </div>
    </div>
  );
}
