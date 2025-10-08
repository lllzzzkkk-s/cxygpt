import React, { useState, useRef, type KeyboardEvent } from 'react';
import { Send, Square } from 'lucide-react';
import { useChatStore } from '../store/chat';
import { estimateTokens, getTokenColorClass } from '../lib/tokenEstimate';

interface ChatComposerProps {
  onSend: (content: string) => void;
  onStop: () => void;
  disabled?: boolean;
}

export function ChatComposer({ onSend, onStop, disabled }: ChatComposerProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const isStreaming = useChatStore(state => state.isStreaming);
  const limits = useChatStore(state => state.limits);

  const estimatedTokens = estimateTokens(input);
  const maxInputTokens = limits?.max_input_tokens || 2048;

  const handleSend = () => {
    if (!input.trim() || disabled) return;

    onSend(input.trim());
    setInput('');

    // 重置高度
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Enter 发送，Shift+Enter 换行
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);

    // 自动调整高度
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 200)}px`;
  };

  const tokenColorClass = getTokenColorClass(estimatedTokens, maxInputTokens);

  return (
    <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-4">
      <div className="max-w-3xl mx-auto">
        <div className="relative flex items-end gap-2">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            placeholder={
              isStreaming ? '正在生成回复...' : '输入消息...（Enter 发送，Shift+Enter 换行）'
            }
            disabled={disabled || isStreaming}
            className="flex-1 resize-none rounded-2xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 px-4 py-3 pr-12 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 min-h-[52px] max-h-[200px] placeholder:text-gray-400 dark:placeholder:text-gray-500"
            rows={1}
          />

          <button
            onClick={isStreaming ? onStop : handleSend}
            disabled={(!input.trim() && !isStreaming) || disabled}
            className={`absolute right-2 bottom-2 p-2 rounded-lg transition-colors ${
              isStreaming
                ? 'bg-red-500 hover:bg-red-600 text-white'
                : 'bg-blue-600 hover:bg-blue-700 text-white disabled:bg-gray-300 disabled:cursor-not-allowed'
            }`}
            title={isStreaming ? '停止生成' : '发送'}
          >
            {isStreaming ? (
              <Square className="w-5 h-5" fill="currentColor" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>

        <div className="flex items-center justify-between mt-2 text-xs">
          <div className={tokenColorClass}>
            {estimatedTokens} / {maxInputTokens} tokens
            {estimatedTokens > maxInputTokens && <span className="ml-2">⚠️ 超出输入限制</span>}
          </div>

          <div className="text-gray-500 dark:text-gray-400">
            {limits?.single_user ? '单人模式' : '多人模式'} · {limits?.profile}
          </div>
        </div>
      </div>
    </div>
  );
}
