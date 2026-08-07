import { describe, expect, it } from 'vitest';

import { PreviewStore } from '../src/preview-store.js';
import type { PostDraft } from '../src/types.js';

const immediateDraft: PostDraft = {
  pageId: '123',
  kind: 'feed',
  mode: 'publish_now',
  message: 'Hello',
};

describe('PreviewStore', () => {
  it('creates a content-bound approval phrase and consumes it once', () => {
    const store = new PreviewStore({
      ttlMs: 60_000,
      now: () => Date.parse('2026-08-07T12:00:00.000Z'),
      randomCode: () => 'A1B2C3D4',
    });

    const preview = store.prepare(immediateDraft);
    expect(preview.approvalPhrase).toBe('PUBLISH A1B2C3D4');
    expect(preview.contentHash).toMatch(/^[a-f0-9]{64}$/);
    expect(preview.expiresAt).toBe('2026-08-07T12:01:00.000Z');
    expect(store.consume(preview.previewId, preview.approvalPhrase)).toEqual(preview);
    expect(() => store.consume(preview.previewId, preview.approvalPhrase)).toThrow('already used');
  });

  it('does not consume a preview when the approval phrase is wrong', () => {
    const store = new PreviewStore({ ttlMs: 60_000, randomCode: () => 'ABCDEF12' });
    const preview = store.prepare(immediateDraft);

    expect(() => store.consume(preview.previewId, 'PUBLISH WRONG')).toThrow('does not match');
    expect(store.consume(preview.previewId, preview.approvalPhrase)).toEqual(preview);
  });

  it('expires previews', () => {
    let now = Date.parse('2026-08-07T12:00:00.000Z');
    const store = new PreviewStore({
      ttlMs: 1_000,
      now: () => now,
      randomCode: () => 'ABCDEF12',
    });
    const preview = store.prepare(immediateDraft);

    now += 1_001;
    expect(() => store.consume(preview.previewId, preview.approvalPhrase)).toThrow('expired');
  });

  it('uses a schedule-specific approval phrase', () => {
    const store = new PreviewStore({ ttlMs: 60_000, randomCode: () => '11223344' });
    const preview = store.prepare({
      ...immediateDraft,
      mode: 'schedule',
      scheduledAt: '2026-08-08T12:00:00.000Z',
    });

    expect(preview.approvalPhrase).toBe('SCHEDULE 11223344');
  });
});
