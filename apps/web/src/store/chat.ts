import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { ChatSession, Message, ChatSettings, LimitsResponse } from '../types';

interface ChatStore {
  // 会话管理
  sessions: ChatSession[];
  currentSessionId: string | null;

  // 设置
  settings: ChatSettings;
  limits: LimitsResponse | null;

  // UI 状态
  sidebarOpen: boolean;
  settingsDrawerOpen: boolean;
  knowledgeDrawerOpen: boolean;
  isStreaming: boolean;

  // Actions
  createSession: () => void;
  deleteSession: (id: string) => void;
  renameSession: (id: string, name: string) => void;
  setCurrentSession: (id: string) => void;
  togglePinSession: (id: string) => void;

  addMessage: (sessionId: string, message: Omit<Message, 'timestamp'> & { id?: string }) => void;
  updateMessage: (sessionId: string, messageId: string, content: Partial<Message>) => void;
  deleteMessage: (sessionId: string, messageId: string) => void;

  updateSettings: (settings: Partial<ChatSettings>) => void;
  setLimits: (limits: LimitsResponse) => void;

  toggleSidebar: () => void;
  toggleSettingsDrawer: () => void;
  toggleKnowledgeDrawer: () => void;
  setIsStreaming: (streaming: boolean) => void;
  resetState: () => void;
}

const defaultSettings: ChatSettings = {
  temperature: 0.7,
  top_p: 0.9,
  max_tokens: 512,
  systemPrompt: '',
  enableLongDoc: true,
};

export const useChatStore = create<ChatStore>()(
  persist(
    (set, get) => ({
      // 初始状态
      sessions: [],
      currentSessionId: null,

      settings: { ...defaultSettings },

      limits: null,
      sidebarOpen: true,
      settingsDrawerOpen: false,
      knowledgeDrawerOpen: false,
      isStreaming: false,

      // 会话操作
      createSession: () => {
        const newSession: ChatSession = {
          id: crypto.randomUUID(),
          name: `新对话 ${new Date().toLocaleString('zh-CN', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' })}`,
          messages: [],
          createdAt: Date.now(),
          updatedAt: Date.now(),
          totalTokens: 0,
        };

        set(state => ({
          sessions: [newSession, ...state.sessions],
          currentSessionId: newSession.id,
        }));
      },

      deleteSession: id => {
        set(state => ({
          sessions: state.sessions.filter(s => s.id !== id),
          currentSessionId:
            state.currentSessionId === id ? state.sessions[0]?.id || null : state.currentSessionId,
        }));
      },

      renameSession: (id, name) => {
        set(state => ({
          sessions: state.sessions.map(s =>
            s.id === id ? { ...s, name, updatedAt: Date.now() } : s
          ),
        }));
      },

      setCurrentSession: id => {
        set({ currentSessionId: id });
      },

      togglePinSession: id => {
        set(state => ({
          sessions: state.sessions.map(s => (s.id === id ? { ...s, pinned: !s.pinned } : s)),
        }));
      },

      // 消息操作
      addMessage: (sessionId, message) => {
        const newMessage: Message = {
          ...message,
          id: message.id ?? crypto.randomUUID(),
          timestamp: Date.now(),
        };

        set(state => ({
          sessions: state.sessions.map(s =>
            s.id === sessionId
              ? {
                  ...s,
                  messages: [...s.messages, newMessage],
                  updatedAt: Date.now(),
                  totalTokens: (s.totalTokens || 0) + (message.tokens || 0),
                }
              : s
          ),
        }));
      },

      updateMessage: (sessionId, messageId, content) => {
        set(state => ({
          sessions: state.sessions.map(s =>
            s.id === sessionId
              ? {
                  ...s,
                  messages: s.messages.map(m => (m.id === messageId ? { ...m, ...content } : m)),
                  updatedAt: Date.now(),
                }
              : s
          ),
        }));
      },

      deleteMessage: (sessionId, messageId) => {
        set(state => ({
          sessions: state.sessions.map(s =>
            s.id === sessionId
              ? {
                  ...s,
                  messages: s.messages.filter(m => m.id !== messageId),
                  updatedAt: Date.now(),
                }
              : s
          ),
        }));
      },

      // 设置操作
      updateSettings: newSettings => {
        set(state => ({
          settings: { ...state.settings, ...newSettings },
        }));
      },

      setLimits: limits => {
        set({ limits });

        // 自动调整 max_tokens 不超过限制
        const currentMaxTokens = get().settings.max_tokens;
        if (currentMaxTokens > limits.max_output_tokens) {
          set(state => ({
            settings: {
              ...state.settings,
              max_tokens: limits.max_output_tokens,
            },
          }));
        }
      },

      // UI 操作
      toggleSidebar: () => {
        set(state => ({ sidebarOpen: !state.sidebarOpen }));
      },

      toggleSettingsDrawer: () => {
        set(state => ({ settingsDrawerOpen: !state.settingsDrawerOpen }));
      },

      toggleKnowledgeDrawer: () => {
        set(state => ({ knowledgeDrawerOpen: !state.knowledgeDrawerOpen }));
      },

      setIsStreaming: streaming => {
        set({ isStreaming: streaming });
      },

      resetState: () => {
        set({
          sessions: [],
          currentSessionId: null,
          settings: { ...defaultSettings },
          limits: null,
          sidebarOpen: true,
          settingsDrawerOpen: false,
          knowledgeDrawerOpen: false,
          isStreaming: false,
        });
      },
    }),
    {
      name: 'cxygpt-chat-storage',
      partialize: state => ({
        sessions: state.sessions,
        currentSessionId: state.currentSessionId,
        settings: state.settings,
        sidebarOpen: state.sidebarOpen,
      }),
    }
  )
);
