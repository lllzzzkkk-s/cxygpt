import type { KnowledgeDocument, KnowledgeUploadResponse } from '../types';
import { APIError } from './openai';
import { getAccessToken } from '../store/auth';
import { resolveApiBase } from './apiBase';

const API_BASE = resolveApiBase();

async function toJson<T>(response: Response): Promise<T> {
  const text = await response.text();
  if (!text) {
    throw new APIError(response.status, 'Empty response body');
  }

  try {
    return JSON.parse(text) as T;
  } catch {
    throw new APIError(response.status, 'Invalid JSON response');
  }
}

async function handleResponse<T>(response: Response, parseBody = true): Promise<T> {
  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;

    try {
      const payload = await response.clone().json();
      message = payload?.error?.message ?? message;
    } catch {
      /* ignore JSON errors */
    }

    console.log('[Knowledge] Request failed:', {
      status: response.status,
      message,
      url: response.url,
    });

    // 401 错误：token 无效或过期，自动登出
    if (response.status === 401) {
      console.log('[Knowledge] 401 error detected, logging out...');
      const { useAuthStore } = await import('../store/auth');
      useAuthStore.getState().logout();
    }

    throw new APIError(response.status, message);
  }

  if (!parseBody || response.status === 204) {
    return undefined as T;
  }

  return toJson<T>(response);
}

export interface UploadDocumentOptions {
  metadata?: Record<string, unknown>;
  embeddingModel?: string;
}

class KnowledgeClient {
  async listDocuments(): Promise<KnowledgeDocument[]> {
    const response = await fetch(`${API_BASE}/v1/knowledge/documents`, {
      method: 'GET',
      headers: this.buildAuthHeaders(),
    });

    return handleResponse<KnowledgeDocument[]>(response);
  }

  async uploadDocument(
    file: File,
    options: UploadDocumentOptions = {}
  ): Promise<KnowledgeDocument> {
    const formData = new FormData();
    formData.append('file', file);

    if (options.embeddingModel) {
      formData.append('embedding_model', options.embeddingModel);
    }

    if (options.metadata) {
      formData.append('metadata', JSON.stringify(options.metadata));
    }

    const response = await fetch(`${API_BASE}/v1/knowledge/documents`, {
      method: 'POST',
      headers: this.buildAuthHeaders({ includeJson: false }),
      body: formData,
    });

    const payload = await handleResponse<KnowledgeUploadResponse>(response);
    return payload.document;
  }

  async requestEmbedding(documentId: string, embeddingModel?: string): Promise<KnowledgeDocument> {
    const response = await fetch(`${API_BASE}/v1/knowledge/documents/${documentId}/embed`, {
      method: 'POST',
      headers: this.buildAuthHeaders(),
      body: JSON.stringify({ embedding_model: embeddingModel ?? null }),
    });

    return handleResponse<KnowledgeDocument>(response);
  }

  async deleteDocument(documentId: string): Promise<void> {
    const response = await fetch(`${API_BASE}/v1/knowledge/documents/${documentId}`, {
      method: 'DELETE',
      headers: this.buildAuthHeaders({ includeJson: false }),
    });

    await handleResponse<void>(response, false);
  }

  private buildAuthHeaders(options?: { includeJson?: boolean }): HeadersInit {
    const headers: Record<string, string> = {};
    const token = getAccessToken();
    console.log(
      '[Knowledge] Building auth headers, token:',
      token ? `${token.substring(0, 20)}...` : 'null'
    );
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    if (options?.includeJson !== false) {
      headers['Content-Type'] = 'application/json';
    }
    return headers;
  }
}

export const knowledgeClient = new KnowledgeClient();
