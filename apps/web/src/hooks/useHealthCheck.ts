import { useEffect, useState } from 'react';
import { openaiClient } from '../lib/openai';

/**
 * 健康检查轮询
 */
export function useHealthCheck(intervalMs: number = 10000) {
  const [healthy, setHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    let mounted = true;

    const check = async () => {
      try {
        const result = await openaiClient.healthCheck();
        if (mounted) {
          setHealthy(result.ok);
        }
      } catch {
        if (mounted) {
          setHealthy(false);
        }
      }
    };

    // 立即检查
    check();

    // 定时轮询
    const timer = setInterval(check, intervalMs);

    return () => {
      mounted = false;
      clearInterval(timer);
    };
  }, [intervalMs]);

  return healthy;
}
