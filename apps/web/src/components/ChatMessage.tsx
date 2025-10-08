import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Copy, Check } from 'lucide-react';
import type { Message } from '../types';
import { getMarkdownComponents, copyToClipboard, extractLanguage } from '../lib/markdown';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    const success = await copyToClipboard(message.content);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const roleStyles = {
    user: 'bg-blue-50 dark:bg-blue-900/20 ml-auto',
    assistant: 'bg-gray-50 dark:bg-gray-800/50',
    system: 'bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-500',
  };

  const roleLabels = {
    user: '你',
    assistant: 'AI',
    system: '系统',
  };

  return (
    <div
      className={`group relative max-w-3xl p-4 rounded-2xl shadow-sm ${roleStyles[message.role]}`}
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-sm font-semibold">
            {roleLabels[message.role][0]}
          </div>
        </div>

        <div className="flex-1 min-w-0">
          <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
            {roleLabels[message.role]} · {new Date(message.timestamp).toLocaleTimeString('zh-CN')}
          </div>

          {message.error ? (
            <div className="text-red-600 dark:text-red-400 text-sm">❌ {message.error}</div>
          ) : (
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  ...getMarkdownComponents(),
                  code: ({
                    inline,
                    className,
                    children,
                  }: {
                    inline?: boolean;
                    className?: string;
                    children?: React.ReactNode;
                  }) => {
                    if (inline) {
                      return (
                        <code className="px-1.5 py-0.5 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded text-sm font-mono">
                          {children}
                        </code>
                      );
                    }

                    const language = extractLanguage(className);
                    const code = String(children).replace(/\n$/, '');

                    return <CodeBlock language={language} code={code} />;
                  },
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        <button
          onClick={handleCopy}
          className="opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
          title="复制"
        >
          {copied ? (
            <Check className="w-4 h-4 text-green-600" />
          ) : (
            <Copy className="w-4 h-4 text-gray-600 dark:text-gray-400" />
          )}
        </button>
      </div>
    </div>
  );
}

// 代码块组件
function CodeBlock({ language, code }: { language: string; code: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    const success = await copyToClipboard(code);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="relative group my-4">
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 text-gray-200 rounded-t-lg">
        <span className="text-xs font-mono">{language || 'text'}</span>
        <button
          onClick={handleCopy}
          className="text-xs px-2 py-1 hover:bg-gray-700 rounded transition-colors"
        >
          {copied ? '已复制' : '复制代码'}
        </button>
      </div>
      <pre className="!mt-0 !rounded-t-none overflow-x-auto bg-gray-900 p-4">
        <code className="text-sm font-mono text-gray-100">{code}</code>
      </pre>
    </div>
  );
}
