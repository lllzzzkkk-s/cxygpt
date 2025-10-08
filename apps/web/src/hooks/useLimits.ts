import { useEffect, useState } from 'react';
import { openaiClient } from '../lib/openai';
import type { LimitsResponse } from '../types';

/**
 * 获取并缓存限额信息
 */
export function useLimits() {
  const [limits, setLimits] = useState<LimitsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

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
  }, []);

  return { limits, loading, error };
}
