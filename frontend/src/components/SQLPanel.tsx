
import { useState } from "react";
import { executeSQL } from "../services/api";
import type { QueryResult } from "../services/api";

const DEFAULT_SQL =
  "SELECT product, SUM(revenue) AS total_revenue " +
  "FROM sales_data GROUP BY product " +
  "ORDER BY total_revenue DESC LIMIT 5";

export default function SQLPanel() {
  const [sql, setSQL] = useState(DEFAULT_SQL);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleExecute() {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      setResult(await executeSQL(sql));
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Query failed"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="data-panel">
      <h2>SQL Analytics</h2>

      <textarea
        className="sql-editor"
        value={sql}
        onChange={(event) => setSQL(event.target.value)}
        rows={5}
        maxLength={5000}
        spellCheck={false}
        aria-label="SQL query"
      />

      <button
        className="primary-button"
        onClick={handleExecute}
        disabled={loading || !sql.trim()}
      >
        {loading ? "Running..." : "Execute SQL"}
      </button>

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {result && (
        <div>
          <p>Returned {result.row_count} rows</p>
          {result.truncated && (
            <p>Results may be limited to 100 rows.</p>
          )}

          <div className="table-scroll">
            <table className="results-table">
              <thead>
                <tr>
                  {result.columns.map((column, index) => (
                    <th key={index}>{column}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result.rows.map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    {row.map((value, colIndex) => (
                      <td key={colIndex}>
                        {value === null ? "NULL" : String(value)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  );
}
