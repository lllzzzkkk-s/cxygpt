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

// 知识库相关
export type KnowledgeDocumentStatus = 'uploaded' | 'embedding' | 'ready' | 'error';

export interface KnowledgeDocument {
  id: string;
  filename: string;
  display_name?: string;
  size_bytes: number;
  status: KnowledgeDocumentStatus;
  chunk_count?: number;
  embedding_model?: string;
  created_at: string;
  updated_at: string;
  error_message?: string | null;
  metadata?: Record<string, string | number | boolean>;
}

export interface KnowledgeUploadResponse {
  document: KnowledgeDocument;
}

// 认证
export interface UserProfile {
  id: string;
  username: string;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: UserProfile;
}
