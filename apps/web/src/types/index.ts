// ========================
// 类型定义
// ========================

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
  tokens?: number;
  error?: string;
}

export interface ChatSession {
  id: string;
  name: string;
  messages: Message[];
  createdAt: number;
  updatedAt: number;
  pinned?: boolean;
  totalTokens?: number;
}

export interface LimitsResponse {
  max_input_tokens: number;
  max_output_tokens: number;
  rate_qps: number;
  rate_tpm: number;
  queue_size: number;
  single_user: boolean;
  profile: string;
}

export interface ChatCompletionRequest {
  model: string;
  messages: Array<{
    role: 'system' | 'user' | 'assistant';
    content: string;
  }>;
  stream?: boolean;
  max_tokens?: number;
  temperature?: number;
  top_p?: number;
}

export interface ChatCompletionChunk {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: Array<{
    index: number;
    delta: {
      role?: string;
      content?: string;
    };
    finish_reason?: string | null;
  }>;
}

export interface ChatSettings {
  temperature: number;
  top_p: number;
  max_tokens: number;
  systemPrompt: string;
  enableLongDoc: boolean;
}

export interface ErrorResponse {
  error: {
    message: string;
    type: string;
    code?: number;
  };
}
