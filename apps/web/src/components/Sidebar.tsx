import React, { useState, useRef, useEffect } from 'react';
import { Plus, Search, Pin, Trash2, Edit2 } from 'lucide-react';
import { useChatStore } from '../store/chat';
import { formatTokens } from '../lib/tokenEstimate';
import type { ChatSession } from '../types';

type SessionGroupProps = {
  title: string;
  sessions: ChatSession[];
};

export function Sidebar(): React.ReactElement | null {
  const sessions = useChatStore(state => state.sessions);
  const currentSessionId = useChatStore(state => state.currentSessionId);
  const createSession = useChatStore(state => state.createSession);
  const setCurrentSession = useChatStore(state => state.setCurrentSession);
  const deleteSession = useChatStore(state => state.deleteSession);
  const renameSession = useChatStore(state => state.renameSession);
  const togglePinSession = useChatStore(state => state.togglePinSession);
  const sidebarOpen = useChatStore(state => state.sidebarOpen);

  const [searchQuery, setSearchQuery] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingInitialName, setEditingInitialName] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editingId && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [editingId]);

  if (!sidebarOpen) return null;

  const filteredSessions = sessions.filter(s =>
    s.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // 分组：固定、今天、本周、更早
  const today = new Date().setHours(0, 0, 0, 0);
  const weekAgo = today - 7 * 24 * 60 * 60 * 1000;

  const pinned = filteredSessions.filter(s => s.pinned);
  const todaySessions = filteredSessions.filter(s => !s.pinned && s.updatedAt >= today);
  const weekSessions = filteredSessions.filter(
    s => !s.pinned && s.updatedAt < today && s.updatedAt >= weekAgo
  );
  const olderSessions = filteredSessions.filter(s => !s.pinned && s.updatedAt < weekAgo);

  const handleStartEdit = (id: string, name: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(id);
    setEditingInitialName(name);
  };

  const handleSaveEdit = (id: string, nextName?: string) => {
    const rawValue = nextName ?? inputRef.current?.value ?? editingInitialName;
    const trimmed = rawValue.trim();
    const currentName = sessions.find(s => s.id === id)?.name;

    if (trimmed && trimmed !== currentName) {
      renameSession(id, trimmed);
    }
    setEditingId(null);
    setEditingInitialName('');
  };

  const handleCancelEdit = () => {
    if (inputRef.current) {
      inputRef.current.value = editingInitialName;
    }
    setEditingId(null);
    setEditingInitialName('');
  };

  const SessionGroup = ({ title, sessions: groupSessions }: SessionGroupProps) => {
    if (groupSessions.length === 0) return null;

    return (
      <div className="mb-6">
        <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2 px-3">
          {title}
        </h3>
        <div className="space-y-1">
          {groupSessions.map(session => (
            <div
              key={session.id}
              className={`group relative px-3 py-2 rounded-lg cursor-pointer transition-colors ${
                session.id === currentSessionId
                  ? 'bg-blue-100 dark:bg-blue-900/30'
                  : 'hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
              onClick={() => {
                if (editingId !== session.id) {
                  setCurrentSession(session.id);
                }
              }}
            >
              {editingId === session.id ? (
                <input
                  key={session.id}
                  ref={inputRef}
                  type="text"
                  defaultValue={editingInitialName}
                  onBlur={e => handleSaveEdit(session.id, e.currentTarget.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleSaveEdit(session.id, (e.target as HTMLInputElement).value);
                    }
                    if (e.key === 'Escape') {
                      e.preventDefault();
                      handleCancelEdit();
                    }
                  }}
                  onMouseDown={e => e.stopPropagation()}
                  onClick={e => e.stopPropagation()}
                  className="w-full bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 border border-blue-500 dark:border-blue-400 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  autoFocus
                />
              ) : (
                <>
                  <div className="flex items-center justify-between pr-20">
                    <span className="text-sm font-medium truncate flex-1 text-gray-900 dark:text-gray-100">
                      {session.name}
                    </span>
                    {session.pinned && (
                      <Pin className="w-3 h-3 text-blue-600 dark:text-blue-400 fill-current flex-shrink-0 ml-2" />
                    )}
                  </div>

                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {new Date(session.updatedAt).toLocaleDateString('zh-CN')} ·{' '}
                    {session.totalTokens ? formatTokens(session.totalTokens) : '0'} tokens
                  </div>

                  <div className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
                    <button
                      onClick={e => {
                        e.stopPropagation();
                        togglePinSession(session.id);
                      }}
                      className="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded text-gray-600 dark:text-gray-300"
                      title={session.pinned ? '取消固定' : '固定'}
                    >
                      <Pin className={`w-3 h-3 ${session.pinned ? 'fill-current' : ''}`} />
                    </button>
                    <button
                      onClick={e => handleStartEdit(session.id, session.name, e)}
                      className="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded text-gray-600 dark:text-gray-300"
                      title="重命名"
                    >
                      <Edit2 className="w-3 h-3" />
                    </button>
                    <button
                      onClick={e => {
                        e.stopPropagation();
                        if (confirm('确定删除此对话？')) {
                          deleteSession(session.id);
                        }
                      }}
                      className="p-1 hover:bg-red-200 dark:hover:bg-red-900/50 rounded text-red-600 dark:text-red-400"
                      title="删除"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="w-64 border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 flex flex-col">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <button
          onClick={createSession}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span className="font-medium">新对话</span>
        </button>

        <div className="relative mt-3">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="搜索对话..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-gray-100 placeholder:text-gray-500 dark:placeholder:text-gray-400"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <SessionGroup title="固定" sessions={pinned} />
        <SessionGroup title="今天" sessions={todaySessions} />
        <SessionGroup title="本周" sessions={weekSessions} />
        <SessionGroup title="更早" sessions={olderSessions} />

        {filteredSessions.length === 0 && (
          <div className="text-center text-gray-500 dark:text-gray-400 text-sm mt-8">
            {searchQuery ? '未找到匹配的对话' : '暂无对话'}
          </div>
        )}
      </div>
    </div>
  );
}

export default Sidebar;
