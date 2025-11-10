import React, { type ComponentPropsWithoutRef, type ReactNode, type JSX } from 'react';

function element<K extends keyof JSX.IntrinsicElements>(
  tag: K,
  props: ComponentPropsWithoutRef<K>,
  children?: ReactNode
) {
  return React.createElement(tag, props, children);
}

export function getMarkdownComponents() {
  return {
    a: ({ href, children }: ComponentPropsWithoutRef<'a'>) =>
      element(
        'a',
        {
          href,
          target: '_blank',
          rel: 'noopener noreferrer',
          className:
            'text-blue-600 dark:text-blue-400 underline hover:text-blue-700 dark:hover:text-blue-300',
        },
        children
      ),
    ul: ({ children }: { children?: ReactNode }) =>
      element(
        'ul',
        { className: 'list-disc list-outside ml-6 space-y-1 text-sm leading-relaxed' },
        children
      ),
    ol: ({ children }: { children?: ReactNode }) =>
      element(
        'ol',
        { className: 'list-decimal list-outside ml-6 space-y-1 text-sm leading-relaxed' },
        children
      ),
    li: ({ children }: { children?: ReactNode }) =>
      element('li', { className: 'text-gray-700 dark:text-gray-200' }, children),
    blockquote: ({ children }: { children?: ReactNode }) =>
      element(
        'blockquote',
        {
          className:
            'border-l-4 border-blue-500 dark:border-blue-400 pl-4 italic text-gray-600 dark:text-gray-300',
        },
        children
      ),
    table: ({ children }: { children?: ReactNode }) =>
      element(
        'div',
        { className: 'overflow-x-auto my-4' },
        element(
          'table',
          { className: 'min-w-full border border-gray-300 dark:border-gray-700 text-sm' },
          children
        )
      ),
    th: ({ children }: { children?: ReactNode }) =>
      element(
        'th',
        {
          className:
            'border border-gray-300 dark:border-gray-700 bg-gray-100 dark:bg-gray-800 px-3 py-2 text-left font-medium text-gray-700 dark:text-gray-200',
        },
        children
      ),
    td: ({ children }: { children?: ReactNode }) =>
      element(
        'td',
        { className: 'border border-gray-300 dark:border-gray-700 px-3 py-2 text-gray-700 dark:text-gray-200' },
        children
      ),
    p: ({ children }: { children?: ReactNode }) =>
      element('p', { className: 'leading-relaxed text-gray-800 dark:text-gray-100' }, children),
  };
}

export async function copyToClipboard(text: string): Promise<boolean> {
  if (!text) return false;

  try {
    if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch {
    /* ignore clipboard write errors */
  }

  try {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'absolute';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    textarea.select();
    const success = document.execCommand('copy');
    document.body.removeChild(textarea);
    return success;
  } catch {
    return false;
  }
}

export function extractLanguage(className?: string): string {
  if (!className) return '';

  const match = className.match(/language-([\w+-]+)/i);
  if (match) {
    return match[1] ?? '';
  }

  const secondMatch = className.match(/lang-([\w+-]+)/i);
  if (secondMatch) {
    return secondMatch[1] ?? '';
  }

  return '';
}
