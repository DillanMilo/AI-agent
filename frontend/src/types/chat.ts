export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  model_used: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

