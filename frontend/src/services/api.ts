
import type {
  ChatRequest,
  ChatResponse,
} from "../types/chat";

const API_BASE_URL = "http://localhost:8000";

export async function askQuestion(
  question: string
): Promise<ChatResponse> {
  const payload: ChatRequest = { question };

  const response = await fetch(
    `${API_BASE_URL}/api/chat`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    }
  );

  if (!response.ok) {
    throw new Error(
      `Backend request failed: ${response.status}`
    );
  }

  return (await response.json()) as ChatResponse;
}


export interface ColumnInfo {
  name: string;
  type: string;
}

export interface DatasetSchema {
  table_name: string;
  row_count: number;
  columns: ColumnInfo[];
}

export interface QueryResult {
  sql: string;
  columns: string[];
  rows: (string | number | boolean | null)[][];
  row_count: number;
  truncated: boolean;
}

export async function uploadCSV(
  file: File
): Promise<{ message: string; schema: DatasetSchema }> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(
    "http://localhost:8000/api/upload",
    {
      method: "POST",
      body: formData,
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail ?? "Upload failed");
  }

  return data;
}

export async function fetchSchema(): Promise<DatasetSchema> {
  const response = await fetch(
    "http://localhost:8000/api/schema"
  );

  if (!response.ok) {
    throw new Error("Failed to fetch schema");
  }

  return response.json();
}

export async function executeSQL(
  sql: string
): Promise<QueryResult> {
  const response = await fetch(
    "http://localhost:8000/api/query",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ sql }),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail ?? "SQL query failed");
  }

  return data;
}

export interface AgentQueryResponse {
  status: string;
  question: string;
  sql: string | null;
  result: QueryResult | null;
  error: string | null;
}

export async function analyzeData(
  question: string
): Promise<AgentQueryResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/agent/query`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Unable to analyze the dataset."
    );
  }

  return data as AgentQueryResponse;
}