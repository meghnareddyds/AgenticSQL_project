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

      {message.sql && (
        <div className="generated-sql">
          <h4>Generated SQL</h4>

          <pre>
            <code>{message.sql}</code>
          </pre>
        </div>
      )}

      {message.result && (
        <div className="query-results">
          <h4>Query Results</h4>

          <p className="result-count">
            {message.result.row_count} rows returned
          </p>

          <div className="results-table-wrapper">
            <table className="results-table">
              <thead>
                <tr>
                  {message.result.columns.map(
                    (column, index) => (
                      <th key={`${column}-${index}`}>
                        {column}
                      </th>
                    )
                  )}
                </tr>
              </thead>

              <tbody>
                {message.result.rows.map(
                  (row, rowIndex) => (
                    <tr key={rowIndex}>
                      {row.map((value, colIndex) => (
                        <td key={colIndex}>
                          {value === null
                            ? "NULL"
                            : String(value)}
                        </td>
                      ))}
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>

          {message.result.truncated && (
            <p className="result-warning">
              Results may be limited to 100 rows.
            </p>
          )}
        </div>
      )}
    </div>
  );
}