const DEFAULT_FALLBACK = 'http://127.0.0.1:8001';

function stripTrailingSlash(url: string): string {
  return url.replace(/\/+$/, '');
}

function normalizeHostname(hostname: string): string {
  if (hostname.includes(':') && !hostname.startsWith('[') && !hostname.endsWith(']')) {
    return `[${hostname}]`;
  }
  return hostname;
}

export function resolveApiBase(): string {
  try {
    const fromEnv = (import.meta.env.VITE_API_GATEWAY_URL as string | undefined)?.trim();
    if (fromEnv) {
      return stripTrailingSlash(fromEnv);
    }

    if (typeof window !== 'undefined') {
      const { protocol, hostname, port } = window.location;
      const devPort = (import.meta.env.VITE_API_GATEWAY_PORT as string | undefined)?.trim();
      const safeHostname = normalizeHostname(hostname);
      const inferredProtocol = protocol === 'https:' ? 'https:' : 'http:';

      if (import.meta.env.DEV) {
        const targetPort = devPort || '8001';
        return stripTrailingSlash(`${inferredProtocol}//${safeHostname}:${targetPort}`);
      }

      const portSegment = port ? `:${port}` : '';
      if (protocol && hostname) {
        return stripTrailingSlash(`${protocol}//${safeHostname}${portSegment}`);
      }
    }
  } catch {
    /* fallback below */
  }

  return stripTrailingSlash(DEFAULT_FALLBACK);
}
