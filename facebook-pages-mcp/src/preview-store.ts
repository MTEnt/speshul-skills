import { createHash, randomBytes, timingSafeEqual } from 'node:crypto';

import { PreviewError } from './errors.js';
import type { PostDraft, PreparedPost } from './types.js';

export interface PreviewStoreOptions {
  readonly ttlMs: number;
  readonly now?: () => number;
  readonly randomCode?: () => string;
  readonly maxEntries?: number;
}

function stableDraftJson(draft: PostDraft): string {
  return JSON.stringify({
    pageId: draft.pageId,
    kind: draft.kind,
    mode: draft.mode,
    message: draft.message ?? null,
    link: draft.link ?? null,
    photoUrl: draft.photoUrl ?? null,
    scheduledAt: draft.scheduledAt ?? null,
  });
}

function safeEqual(left: string, right: string): boolean {
  const leftBuffer = Buffer.from(left);
  const rightBuffer = Buffer.from(right);
  if (leftBuffer.length !== rightBuffer.length) return false;
  return timingSafeEqual(leftBuffer, rightBuffer);
}

export class PreviewStore {
  private readonly previews = new Map<string, PreparedPost>();
  private readonly ttlMs: number;
  private readonly now: () => number;
  private readonly randomCode: () => string;
  private readonly maxEntries: number;

  constructor(options: PreviewStoreOptions) {
    this.ttlMs = options.ttlMs;
    this.now = options.now ?? Date.now;
    this.randomCode = options.randomCode ?? (() => randomBytes(4).toString('hex').toUpperCase());
    this.maxEntries = options.maxEntries ?? 100;
  }

  prepare(draft: PostDraft): PreparedPost {
    this.removeExpired();
    if (this.previews.size >= this.maxEntries) {
      throw new PreviewError('Too many pending previews. Wait for one to expire and try again.', 'PREVIEW_LIMIT');
    }

    const now = this.now();
    const previewId = randomBytes(16).toString('hex');
    const code = this.randomCode();
    const verb = draft.mode === 'schedule' ? 'SCHEDULE' : 'PUBLISH';
    const prepared: PreparedPost = {
      previewId,
      approvalPhrase: `${verb} ${code}`,
      contentHash: createHash('sha256').update(stableDraftJson(draft)).digest('hex'),
      createdAt: new Date(now).toISOString(),
      expiresAt: new Date(now + this.ttlMs).toISOString(),
      draft,
    };

    this.previews.set(previewId, prepared);
    return prepared;
  }

  consume(previewId: string, approvalPhrase: string): PreparedPost {
    this.removeExpired();
    const prepared = this.previews.get(previewId);
    if (!prepared) {
      throw new PreviewError(
        'Preview not found, expired, or already used. Create a new preview before publishing.',
        'PREVIEW_NOT_FOUND',
      );
    }

    if (!safeEqual(prepared.approvalPhrase, approvalPhrase.trim())) {
      throw new PreviewError('The approval phrase does not match this preview.', 'APPROVAL_MISMATCH');
    }

    // Remove before the network request. This prevents retries from creating duplicate posts
    // when the caller cannot tell whether Facebook accepted an earlier request.
    this.previews.delete(previewId);
    return prepared;
  }

  pendingCount(): number {
    this.removeExpired();
    return this.previews.size;
  }

  private removeExpired(): void {
    const now = this.now();
    for (const [previewId, prepared] of this.previews.entries()) {
      if (Date.parse(prepared.expiresAt) <= now) this.previews.delete(previewId);
    }
  }
}
