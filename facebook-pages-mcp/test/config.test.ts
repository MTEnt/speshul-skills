import { describe, expect, it } from 'vitest';

import { loadConfig } from '../src/config.js';

describe('loadConfig', () => {
  it('uses safe defaults without requiring a token at startup', () => {
    const config = loadConfig({});

    expect(config.pageAccessToken).toBeUndefined();
    expect([...config.allowedPageIds]).toEqual([]);
    expect(config.graphApiVersion).toBe('v26.0');
    expect(config.previewTtlMs).toBe(900_000);
    expect(config.requestTimeoutMs).toBe(15_000);
    expect(config.maxMessageChars).toBe(20_000);
  });

  it('normalizes runtime credentials and an explicit Page allowlist', () => {
    const config = loadConfig({
      FACEBOOK_PAGE_ACCESS_TOKEN: '  secret-token  ',
      FACEBOOK_PAGE_IDS: ' 123,456,123 ',
      FACEBOOK_GRAPH_API_VERSION: 'v27.0',
      FACEBOOK_PREVIEW_TTL_SECONDS: '60',
      FACEBOOK_REQUEST_TIMEOUT_MS: '5000',
      FACEBOOK_MAX_MESSAGE_CHARS: '1000',
    });

    expect(config.pageAccessToken).toBe('secret-token');
    expect([...config.allowedPageIds]).toEqual(['123', '456']);
    expect(config.graphApiVersion).toBe('v27.0');
    expect(config.previewTtlMs).toBe(60_000);
    expect(config.requestTimeoutMs).toBe(5_000);
    expect(config.maxMessageChars).toBe(1_000);
  });

  it.each([
    [{ FACEBOOK_PAGE_IDS: '123,abc' }, 'FACEBOOK_PAGE_IDS'],
    [{ FACEBOOK_GRAPH_API_VERSION: 'latest' }, 'FACEBOOK_GRAPH_API_VERSION'],
    [{ FACEBOOK_REQUEST_TIMEOUT_MS: '-1' }, 'FACEBOOK_REQUEST_TIMEOUT_MS'],
  ])('rejects invalid configuration', (env, expectedMessage) => {
    expect(() => loadConfig(env)).toThrow(expectedMessage);
  });
});
