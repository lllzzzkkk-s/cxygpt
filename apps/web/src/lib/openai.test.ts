import { describe, it, expect } from 'vitest';
import { APIError, OpenAIClient } from './openai';

describe('OpenAIClient', () => {
  it('creates client with base URL', () => {
    const client = new OpenAIClient('http://localhost:8000');
    expect(client).toBeDefined();
  });

  it('creates client with default base URL', () => {
    const client = new OpenAIClient();
    expect(client).toBeDefined();
  });
});

describe('APIError', () => {
  it('creates error with message', () => {
    const error = new APIError('Test error', 500);
    expect(error.message).toBe('Test error');
    expect(error.status).toBe(500);
  });

  it('formats 413 error correctly', () => {
    const error = new APIError('Request too large', 413);
    expect(error.message).toContain('large');
    expect(error.status).toBe(413);
  });

  it('formats 429 error correctly', () => {
    const error = new APIError('Too many requests', 429);
    expect(error.status).toBe(429);
  });

  it('formats 503 error correctly', () => {
    const error = new APIError('Service unavailable', 503);
    expect(error.status).toBe(503);
  });
});
