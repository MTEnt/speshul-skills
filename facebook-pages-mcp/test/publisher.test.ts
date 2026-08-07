import { describe, expect, it, vi } from 'vitest';

import type { AppConfig } from '../src/config.js';
import { GraphApiError } from '../src/errors.js';
import type { FacebookClient } from '../src/facebook-client.js';
import { PreviewStore } from '../src/preview-store.js';
import { FacebookPublisher } from '../src/publisher.js';

const now = Date.parse('2026-08-07T12:00:00.000Z');

function config(overrides: Partial<AppConfig> = {}): AppConfig {
  return {
    pageAccessToken: 'secret',
    allowedPageIds: new Set(['123']),
    graphApiVersion: 'v26.0',
    previewTtlMs: 900_000,
    requestTimeoutMs: 15_000,
    maxMessageChars: 20_000,
    ...overrides,
  };
}

function clientMock() {
  return {
    getPage: vi.fn(async () => ({ id: '123', name: 'Workshop' })),
    listRecentPosts: vi.fn(async () => []),
    getPost: vi.fn(async (postId: string) => ({ id: postId, permalink_url: 'https://facebook.example/post' })),
    publishFeedPost: vi.fn(async () => ({ id: '123_456' })),
    publishPhoto: vi.fn(async () => ({ id: '123_456', photoId: '789' })),
  };
}

function publisherWithMocks(client = clientMock()) {
  const store = new PreviewStore({
    ttlMs: 900_000,
    now: () => now,
    randomCode: () => 'ABCDEF12',
  });
  return {
    client,
    publisher: new FacebookPublisher({
      config: config(),
      previewStore: store,
      client: client as unknown as FacebookClient,
      now: () => now,
    }),
  };
}

describe('FacebookPublisher', () => {
  it('denies every Page not explicitly allowlisted', () => {
    const { publisher } = publisherWithMocks();

    expect(() => publisher.prepare({ pageId: '999', message: 'Nope' })).toThrow('not allowlisted');
  });

  it('normalizes and prepares text/link posts without contacting Facebook', () => {
    const { client, publisher } = publisherWithMocks();
    const preview = publisher.prepare({
      pageId: '123',
      message: '  Hello world  ',
      link: 'https://example.com/article',
    });

    expect(preview.draft).toEqual({
      pageId: '123',
      kind: 'feed',
      mode: 'publish_now',
      message: 'Hello world',
      link: 'https://example.com/article',
    });
    expect(client.publishFeedPost).not.toHaveBeenCalled();
  });

  it('enforces Meta schedule bounds and normalizes timestamps', () => {
    const { publisher } = publisherWithMocks();

    expect(() => publisher.prepare({
      pageId: '123',
      message: 'Too soon',
      scheduledAt: '2026-08-07T12:09:59.000Z',
    })).toThrow('between 10 minutes and 30 days');

    expect(() => publisher.prepare({
      pageId: '123',
      message: 'Too late',
      scheduledAt: '2026-09-06T12:00:01.000Z',
    })).toThrow('between 10 minutes and 30 days');

    const preview = publisher.prepare({
      pageId: '123',
      message: 'On time',
      scheduledAt: '2026-08-07T19:10:00+07:00',
    });
    expect(preview.draft.scheduledAt).toBe('2026-08-07T12:10:00.000Z');
  });

  it('requires a public HTTPS hostname for photos and rejects ambiguous combinations', () => {
    const { publisher } = publisherWithMocks();

    expect(() => publisher.prepare({
      pageId: '123',
      photoUrl: 'http://example.com/photo.jpg',
    })).toThrow('must use HTTPS');

    expect(() => publisher.prepare({
      pageId: '123',
      photoUrl: 'https://127.0.0.1/photo.jpg',
    })).toThrow('public hostname');

    expect(() => publisher.prepare({
      pageId: '123',
      link: 'https://example.com',
      photoUrl: 'https://cdn.example.com/photo.jpg',
    })).toThrow('both link and photo_url');

    expect(() => publisher.prepare({
      pageId: '123',
      link: 'https://username:password@example.com',
    })).toThrow('must not contain embedded credentials');
  });

  it('publishes an approved preview once and verifies the returned post', async () => {
    const { client, publisher } = publisherWithMocks();
    const preview = publisher.prepare({ pageId: '123', message: 'Approved' });

    await expect(publisher.publish(preview.previewId, preview.approvalPhrase)).resolves.toMatchObject({
      ok: true,
      action: 'publish_now',
      post_id: '123_456',
      verification: { status: 'verified' },
    });
    expect(client.publishFeedPost).toHaveBeenCalledTimes(1);
    await expect(publisher.publish(preview.previewId, preview.approvalPhrase)).rejects.toThrow('already used');
    expect(client.publishFeedPost).toHaveBeenCalledTimes(1);
  });

  it('reports successful publishing even when read-back verification fails', async () => {
    const client = clientMock();
    client.getPost.mockRejectedValueOnce(new GraphApiError('Read permission unavailable', 403, 200));
    const { publisher } = publisherWithMocks(client);
    const preview = publisher.prepare({ pageId: '123', message: 'Published' });

    await expect(publisher.publish(preview.previewId, preview.approvalPhrase)).resolves.toMatchObject({
      ok: true,
      post_id: '123_456',
      verification: {
        status: 'publish_succeeded_but_readback_failed',
        error: { code: 'GRAPH_API_ERROR', graph_code: 200 },
      },
    });
  });
});
