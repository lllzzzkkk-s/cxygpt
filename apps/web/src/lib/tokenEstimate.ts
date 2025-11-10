/**
 * 简单的 token 数估算。
 * GPT-风格模型大约 4 个字符 ≈ 1 token。
 */
export function estimateTokens(text: string): number {
  if (!text) return 0;

  const normalized = text
    .replace(/[^\S\n]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  if (!normalized) return 0;

  const approx = Math.ceil(normalized.length / 4);
  return Math.max(approx, 0);
}

export function getTokenColorClass(tokens: number, maxTokens: number): string {
  if (maxTokens <= 0) return 'text-gray-500';

  const ratio = tokens / maxTokens;

  if (ratio < 0.6) {
    return 'text-green-600 dark:text-green-400';
  }
  if (ratio < 0.9) {
    return 'text-yellow-600 dark:text-yellow-400';
  }
  return 'text-red-600 dark:text-red-400';
}

export function formatTokens(tokens?: number): string {
  if (!tokens || tokens <= 0) return '0';
  return tokens.toLocaleString('en-US');
}
