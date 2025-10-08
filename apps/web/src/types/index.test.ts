import { describe, it, expect } from 'vitest';

describe('Type Definitions', () => {
  it('defines Message type correctly', () => {
    const message = {
      id: '1',
      role: 'user' as const,
      content: 'Hello',
      timestamp: Date.now(),
    };

    expect(message.id).toBeDefined();
    expect(message.role).toBe('user');
    expect(message.content).toBe('Hello');
    expect(message.timestamp).toBeGreaterThan(0);
  });

  it('defines ChatSession type correctly', () => {
    const session = {
      id: '1',
      name: 'Test Session',
      messages: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };

    expect(session.id).toBeDefined();
    expect(session.name).toBe('Test Session');
    expect(session.messages).toEqual([]);
  });

  it('defines ChatSettings type correctly', () => {
    const settings = {
      temperature: 0.7,
      top_p: 0.9,
      max_tokens: 512,
      systemPrompt: '',
      enableLongDoc: true,
    };

    expect(settings.temperature).toBe(0.7);
    expect(settings.top_p).toBe(0.9);
    expect(settings.max_tokens).toBe(512);
  });
});
