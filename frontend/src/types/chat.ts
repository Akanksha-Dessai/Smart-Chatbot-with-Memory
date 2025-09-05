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
  memory_stats: {
    total_users: number;
    total_conversations: number;
    max_memories_per_user: number;
  };
  openai_model: string;
}

export interface Memory {
  id: string;
  memory?: string;
  content?: string;
  metadata?: {
    timestamp?: string;
    importance?: number;
    type?: string;
    [key: string]: any;
  };
  score?: number;
  created_at?: string;
  updated_at?: string;
}
