import type {
  ChatCompletionRequest,
  ChatCompletionChunk,
  ErrorResponse,
  LimitsResponse,
} from '../types';
import { getAccessToken } from '../store/auth';
import { resolveApiBase } from './apiBase';

const API_BASE = resolveApiBase();

export class APIError extends Error {
  status: number;
  payload?: ErrorResponse;

  constructor(status: number, message: string, payload?: ErrorResponse) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.payload = payload;
  }

  getUserMessage(): string {
    if (this.payload?.error?.message) {
      return this.payload.error.message;
    }

    switch (this.status) {
      case 413:
        return '输入过长，请缩短问题或切换更高档位。';
      case 429:
        return '请求过多，请稍后重试。';
      case 503:
        return '系统繁忙，请稍后重试。';
      default:
        return '服务暂时不可用，请稍后再试。';
    }
  }
}

async function parseJson<T>(response: Response): Promise<T> {
  const text = await response.text();
  if (!text) {
    throw new APIError(response.status, 'Empty response body');
  }

  try {
    return JSON.parse(text) as T;
  } catch (err) {
    throw new APIError(response.status, 'Invalid JSON response');
  }
}

function buildHeaders(extra?: HeadersInit): HeadersInit {
  const base: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  const token = getAccessToken();
  if (token) {
    base.Authorization = `Bearer ${token}`;
  }

  if (!extra) {
    return base;
  }

  if (extra instanceof Headers) {
    extra.forEach((value, key) => {
      base[key] = value;
    });
  } else if (Array.isArray(extra)) {
    for (const [key, value] of extra) {
      if (typeof key === 'string' && typeof value === 'string') {
        base[key] = value;
      }
    }
  } else {
    Object.assign(base, extra as Record<string, string>);
  }

  return base;
}

async function request<T = unknown>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: buildHeaders(init?.headers),
    ...init,
  });

  if (!response.ok) {
    let payload: ErrorResponse | undefined;

    try {
      payload = await response.clone().json();
    } catch {
      /* ignore JSON parse errors */
    }

    throw new APIError(
      response.status,
      payload?.error?.message ?? `Request failed with status ${response.status}`,
      payload
    );
  }

  if (init?.method === 'HEAD' || response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

async function* streamCompletions(
  path: string,
  body: ChatCompletionRequest,
  signal?: AbortSignal
): AsyncGenerator<string, void, unknown> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify({ ...body, stream: true }),
    signal,
  });

  if (!response.ok || !response.body) {
    let payload: ErrorResponse | undefined;
    try {
      payload = await response.clone().json();
    } catch {
      /* ignore */
    }
    throw new APIError(
      response.status,
      payload?.error?.message ?? `Streaming request failed (${response.status})`,
      payload
    );
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });

    const events = buffer.split(/\r?\n\r?\n/);
    buffer = events.pop() ?? '';

    for (const event of events) {
      const lines = event.split(/\r?\n/).map(line => line.trim());

      for (const line of lines) {
        if (!line.startsWith('data:')) continue;

        const data = line.slice(5).trim();
        if (!data || data === '[DONE]') {
          if (data === '[DONE]') {
            return;
          }
          continue;
        }

        let chunk: ChatCompletionChunk | undefined;
        try {
          chunk = JSON.parse(data) as ChatCompletionChunk;
        } catch {
          continue;
        }

        const delta = chunk.choices?.[0]?.delta?.content;
        if (delta) {
          yield delta;
        }
      }
    }
  }
}

class OpenAIClient {
  async healthCheck(): Promise<{ ok: boolean }> {
    return request<{ ok: boolean }>('/healthz');
  }

  async getLimits(): Promise<LimitsResponse> {
    return request<LimitsResponse>('/v1/limits');
  }

  async *chatCompletionStream(
    body: ChatCompletionRequest,
    signal?: AbortSignal
  ): AsyncGenerator<string, void, unknown> {
    yield* streamCompletions('/v1/chat/completions', body, signal);
  }
}

export const openaiClient = new OpenAIClient();
