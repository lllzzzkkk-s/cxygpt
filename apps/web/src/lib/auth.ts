import type { LoginResponse, UserProfile } from '../types';
import { APIError } from './openai';
import { resolveApiBase } from './apiBase';

const API_BASE = resolveApiBase();

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init);
  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const payload = await response.clone().json();
      message = payload?.error?.message ?? message;
    } catch {
      /* ignore */
    }
    throw new APIError(response.status, message);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  return request<LoginResponse>('/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });
}

export async function fetchProfile(token: string): Promise<UserProfile> {
  return request<UserProfile>('/v1/auth/me', {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export async function refreshToken(token: string): Promise<string> {
  const response = await request<{ access_token: string }>('/v1/auth/refresh', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.access_token;
}
