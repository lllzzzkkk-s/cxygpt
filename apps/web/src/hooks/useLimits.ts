import { useEffect, useState } from 'react';
import { openaiClient } from '../lib/openai';
import type { LimitsResponse } from '../types';

/**
 * 获取并缓存限额信息
 * @param enabled - 是否启用限额获取（通常在用户登录后才启用）
 */
export function useLimits(enabled = false) {
  const [limits, setLimits] = useState<LimitsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!enabled) return;

    let mounted = true;
    setLoading(true);

    const fetchLimits = async () => {
      try {
        const data = await openaiClient.getLimits();
        if (mounted) {
          setLimits(data);
          setError(null);
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Failed to fetch limits');
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    fetchLimits();

    return () => {
      mounted = false;
    };
  }, [enabled]);

  return { limits, loading, error };
}
