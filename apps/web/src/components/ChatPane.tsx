import React, { useRef } from 'react';
import { useChatStore } from '../store/chat';
import { ChatMessage } from './ChatMessage';
import { ChatComposer } from './ChatComposer';
import { openaiClient, APIError } from '../lib/openai';
import { useAutoScroll } from '../hooks/useAutoScroll';
import { ArrowDown } from 'lucide-react';

export function ChatPane() {
  const { containerRef, scrollToBottom, showScrollButton } = useAutoScroll<HTMLDivElement>();
  const abortControllerRef = useRef<AbortController | null>(null);
  const { currentSessionId, sessions, settings, addMessage, updateMessage, setIsStreaming } =
    useChatStore();

  const currentSession = sessions.find(s => s.id === currentSessionId);

  const handleSend = async (content: string) => {
    if (!currentSessionId || !currentSession) return;

    // 添加用户消息
    addMessage(currentSessionId, {
      id: crypto.randomUUID(),
      role: 'user',
      content,
    });

    // 创建 AI 消息占位符
    const aiMessageId = crypto.randomUUID();
    addMessage(currentSessionId, {
      id: aiMessageId,
      role: 'assistant',
      content: '',
    });

    setIsStreaming(true);

    // 准备请求
    const messages = [
      ...(settings.systemPrompt
        ? [{ role: 'system' as const, content: settings.systemPrompt }]
        : []),
      ...currentSession.messages.map(m => ({
        role: m.role,
        content: m.content,
      })),
      { role: 'user' as const, content },
    ];

    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    let fullContent = '';

    try {
      const stream = openaiClient.chatCompletionStream(
        {
          model: 'qwen3-14b',
          messages,
          max_tokens: settings.max_tokens,
          temperature: settings.temperature,
          top_p: settings.top_p,
        },
        abortController.signal
      );

      for await (const chunk of stream) {
        fullContent += chunk;
        updateMessage(currentSessionId, aiMessageId, { content: fullContent });
      }
    } catch (err) {
      if (err instanceof APIError) {
        updateMessage(currentSessionId, aiMessageId, {
          error: err.getUserMessage(),
          content: '',
        });
      } else if ((err as Error).name !== 'AbortError') {
        updateMessage(currentSessionId, aiMessageId, {
          error: '网络错误，请检查网关是否启动',
          content: '',
        });
      }
    } finally {
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  };

  const handleStop = () => {
    abortControllerRef.current?.abort();
    setIsStreaming(false);
  };

  if (!currentSession) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-500">
        <div className="text-center">
          <p className="text-lg mb-2">👋 欢迎使用 CxyGPT</p>
          <p className="text-sm">创建或选择一个会话开始对话</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col relative">
      <div ref={containerRef} className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {currentSession.messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <p className="text-lg mb-2">💬 开始新对话</p>
              <p className="text-sm">在下方输入您的问题</p>
            </div>
          </div>
        ) : (
          currentSession.messages.map(message => <ChatMessage key={message.id} message={message} />)
        )}

        {showScrollButton && (
          <button
            onClick={scrollToBottom}
            className="fixed bottom-24 right-8 p-3 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-colors"
            title="滚动到底部"
          >
            <ArrowDown className="w-5 h-5" />
          </button>
        )}
      </div>

      <ChatComposer onSend={handleSend} onStop={handleStop} />
    </div>
  );
}

// 导出为默认组件
export default ChatPane;
