
export interface ChatRequest {
  question: string;
}

export interface ChatResponse {
  question: string;
  answer: string;
  status: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}
