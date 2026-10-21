
import { useEffect, useState } from "react";
import {
  uploadCSV,
  fetchSchema,
} from "../services/api";
import type { DatasetSchema } from "../services/api";

export default function DatasetPanel() {
  const [schema, setSchema] = useState<DatasetSchema | null>(null);
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    let cancelled = false;

    fetchSchema()
      .then((data) => {
        if (!cancelled) setSchema(data);
      })
      .catch(() => {
        if (!cancelled) {
          setError("Unable to load dataset schema.");
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  async function handleUpload(file: File) {
    setUploading(true);
    setError("");

    try {
      const result = await uploadCSV(file);
      setSchema(result.schema);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Upload failed"
      );
    } finally {
      setUploading(false);
    }
  }

  return (
    <section className="data-panel">
      <h2>Dataset Management</h2>

      <label htmlFor="csv-upload">Upload a CSV file</label>
      <input
        id="csv-upload"
        type="file"
        accept=".csv,text/csv"
        disabled={uploading}
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) void handleUpload(file);
          event.target.value = "";
        }}
      />

      {uploading && <p>Uploading dataset...</p>}
      {error && <p className="error-message">{error}</p>}

      {schema && (
        <div>
          <h3>Table: {schema.table_name}</h3>
          <p>Total rows: {schema.row_count}</p>

          <table className="results-table">
            <thead>
              <tr>
                <th>Column</th>
                <th>Data Type</th>
              </tr>
            </thead>
            <tbody>
              {schema.columns.map((column) => (
                <tr key={column.name}>
                  <td>{column.name}</td>
                  <td>{column.type}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
