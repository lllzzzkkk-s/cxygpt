import { create } from 'zustand';
import { persist } from 'zustand/middleware';

import type { UserProfile } from '../types';
import { APIError } from '../lib/openai';
import { fetchProfile, login as loginApi, refreshToken as refreshTokenApi } from '../lib/auth';
import { useChatStore } from './chat';

interface AuthState {
  accessToken: string | null;
  user: UserProfile | null;
  loading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  refreshProfile: () => Promise<void>;
  refreshAccessToken: () => Promise<void>;
  clearError: () => void;
}

function extractErrorMessage(error: unknown): string {
  if (error instanceof APIError) {
    return error.getUserMessage();
  }
  if (error instanceof Error) {
    return error.message;
  }
  return '登录失败，请稍后重试。';
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      accessToken: null,
      user: null,
      loading: false,
      error: null,
      async login(username: string, password: string) {
        set({ loading: true, error: null });
        try {
          const response = await loginApi(username, password);
          useChatStore.getState().resetState();
          set({
            accessToken: response.access_token,
            user: response.user,
            loading: false,
            error: null,
          });
          return true;
        } catch (err) {
          set({ loading: false, error: extractErrorMessage(err) });
          return false;
        }
      },
      logout() {
        useChatStore.getState().resetState();
        set({ accessToken: null, user: null, error: null });
      },
      async refreshProfile() {
        const token = get().accessToken;
        if (!token) return;
        set({ loading: true, error: null });
        try {
          const profile = await fetchProfile(token);
          set({ user: profile, loading: false });
        } catch (err) {
          useChatStore.getState().resetState();
          set({ loading: false, error: extractErrorMessage(err), accessToken: null, user: null });
        }
      },
      async refreshAccessToken() {
        const token = get().accessToken;
        if (!token) return;
        try {
          const newToken = await refreshTokenApi(token);
          set({ accessToken: newToken });
        } catch (err) {
          useChatStore.getState().resetState();
          set({ error: extractErrorMessage(err), accessToken: null, user: null });
        }
      },
      clearError() {
        if (get().error) {
          set({ error: null });
        }
      },
    }),
    {
      name: 'cxygpt-auth',
      partialize: state => ({ accessToken: state.accessToken, user: state.user }),
    }
  )
);

export const getAccessToken = (): string | null => useAuthStore.getState().accessToken;
