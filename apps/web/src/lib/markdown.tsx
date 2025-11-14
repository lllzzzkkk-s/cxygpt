// ========================
// Markdown 渲染工具
// ========================

import type { Components } from 'react-markdown';

// 代码语言映射
export const languageMap: Record<string, string> = {
  js: 'javascript',
  ts: 'typescript',
  py: 'python',
  sh: 'bash',
  yml: 'yaml',
};

/**
 * 从代码块中提取语言标识
 */
export function extractLanguage(className?: string): string {
  if (!className) return '';

  const match = /language-(\w+)/.exec(className);
  const lang = match ? match[1] : '';

  return lang ? languageMap[lang] || lang : '';
}

/**
 * 复制到剪贴板
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error('Failed to copy:', err);
    return false;
  }
}

/**
 * React Markdown 组件配置
 */
export function getMarkdownComponents(): Partial<Components> {
  return {
    // 代码块在组件中单独处理
    code: ({ children }) => {
      return (
        <code className="px-1 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-sm">{children}</code>
      );
    },

    // 表格
    table: ({ children }) => {
      return (
        <div className="overflow-x-auto my-4">
          <table className="min-w-full divide-y divide-gray-300 dark:divide-gray-700">
            {children}
          </table>
        </div>
      );
    },

    th: ({ children }) => {
      return (
        <th className="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide bg-gray-50 dark:bg-gray-800">
          {children}
        </th>
      );
    },

    td: ({ children }) => {
      return (
        <td className="px-3 py-2 text-sm border-t border-gray-200 dark:border-gray-700">
          {children}
        </td>
      );
    },

    // 链接
    a: ({ href, children }) => {
      return (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 dark:text-blue-400 hover:underline"
        >
          {children}
        </a>
      );
    },

    // 列表
    ul: ({ children }) => {
      return <ul className="list-disc list-inside my-2 space-y-1">{children}</ul>;
    },

    ol: ({ children }) => {
      return <ol className="list-decimal list-inside my-2 space-y-1">{children}</ol>;
    },

    // 引用
    blockquote: ({ children }) => {
      return (
        <blockquote className="border-l-4 border-gray-300 dark:border-gray-600 pl-4 my-2 italic text-gray-700 dark:text-gray-300">
          {children}
        </blockquote>
      );
    },

    // 标题
    h1: ({ children }) => {
      return <h1 className="text-2xl font-bold mt-4 mb-2">{children}</h1>;
    },

    h2: ({ children }) => {
      return <h2 className="text-xl font-bold mt-3 mb-2">{children}</h2>;
    },

    h3: ({ children }) => {
      return <h3 className="text-lg font-semibold mt-2 mb-1">{children}</h3>;
    },
  };
}
