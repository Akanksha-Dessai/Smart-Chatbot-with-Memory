// TypeScript types for chat functionality

export interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: string;
}

export interface StreamChunk {
  content: string;
  done: boolean;
}

export interface ChatRequest {
  user_id: string;
  message: string;
}

export interface ChatResponse {
  user_id: string;
  message: string;
  response: string;
  timestamp: string;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  app_name: string;
  version: string;
  openai_model: string;
}
