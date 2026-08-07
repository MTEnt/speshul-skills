import { describe, expect, it, vi } from 'vitest';

import { GraphApiError } from '../src/errors.js';
import { FacebookClient } from '../src/facebook-client.js';

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

describe('FacebookClient', () => {
  it('uses an Authorization header and never places the token in the URL', async () => {
    const fetchMock = vi.fn(async (
      _input: Parameters<typeof fetch>[0],
      _init?: Parameters<typeof fetch>[1],
    ) => jsonResponse({ id: '123', name: 'Workshop' }));
    const client = new FacebookClient({
      accessToken: 'top-secret-token',
      graphApiVersion: 'v26.0',
      requestTimeoutMs: 1_000,
      fetchImpl: fetchMock as unknown as typeof fetch,
    });

    await client.getPage('123');

    const [input, init] = fetchMock.mock.calls[0]!;
    const url = String(input);
    const headers = new Headers(init?.headers);
    expect(url).toBe('https://graph.facebook.com/v26.0/123?fields=id%2Cname%2Ccategory%2Clink');
    expect(url).not.toContain('top-secret-token');
    expect(url).not.toContain('access_token');
    expect(headers.get('Authorization')).toBe('Bearer top-secret-token');
  });

  it('publishes JSON and maps photo responses to their Page post ID', async () => {
    const fetchMock = vi.fn(async (
      _input: Parameters<typeof fetch>[0],
      _init?: Parameters<typeof fetch>[1],
    ) => jsonResponse({ id: 'photo-1', post_id: '123_456' }));
    const client = new FacebookClient({
      accessToken: 'secret',
      graphApiVersion: 'v26.0',
      requestTimeoutMs: 1_000,
      fetchImpl: fetchMock as unknown as typeof fetch,
    });

    await expect(client.publishPhoto({
      pageId: '123',
      photoUrl: 'https://cdn.example.com/photo.jpg',
      message: 'Caption',
    })).resolves.toEqual({ id: '123_456', photoId: 'photo-1' });

    const [, init] = fetchMock.mock.calls[0]!;
    expect(JSON.parse(String(init?.body))).toEqual({
      url: 'https://cdn.example.com/photo.jpg',
      message: 'Caption',
      published: true,
    });
  });

  it('returns sanitized Graph error metadata', async () => {
    const fetchMock = vi.fn(async (
      _input: Parameters<typeof fetch>[0],
      _init?: Parameters<typeof fetch>[1],
    ) => jsonResponse({
      error: {
        message: 'Missing permission for token secret',
        code: 200,
        error_subcode: 2018078,
      },
    }, 403));
    const client = new FacebookClient({
      accessToken: 'secret',
      graphApiVersion: 'v26.0',
      requestTimeoutMs: 1_000,
      fetchImpl: fetchMock as unknown as typeof fetch,
    });

    const error = await client.getPage('123').catch((caught: unknown) => caught);
    expect(error).toBeInstanceOf(GraphApiError);
    expect(error).toMatchObject({
      message: 'Missing permission for token [REDACTED]',
      httpStatus: 403,
      graphCode: 200,
      graphSubcode: 2018078,
    });
    expect(JSON.stringify(error)).not.toContain('secret');
  });

  it('rejects non-JSON responses without echoing the response body', async () => {
    const fetchMock = vi.fn(async (
      _input: Parameters<typeof fetch>[0],
      _init?: Parameters<typeof fetch>[1],
    ) => new Response('proxy diagnostic containing private data', { status: 502 }));
    const client = new FacebookClient({
      accessToken: 'secret',
      graphApiVersion: 'v26.0',
      requestTimeoutMs: 1_000,
      fetchImpl: fetchMock as unknown as typeof fetch,
    });

    await expect(client.getPage('123')).rejects.toThrow('non-JSON response with HTTP 502');
  });

  it('rejects successful publish responses that do not contain a post ID', async () => {
    const fetchMock = vi.fn(async (
      _input: Parameters<typeof fetch>[0],
      _init?: Parameters<typeof fetch>[1],
    ) => jsonResponse({ success: true }));
    const client = new FacebookClient({
      accessToken: 'secret',
      graphApiVersion: 'v26.0',
      requestTimeoutMs: 1_000,
      fetchImpl: fetchMock as unknown as typeof fetch,
    });

    await expect(client.publishFeedPost({ pageId: '123', message: 'Hello' }))
      .rejects.toThrow('did not return a post ID');
  });
});
