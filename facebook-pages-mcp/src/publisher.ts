import { isIP } from 'node:net';

import type { AppConfig } from './config.js';
import { AccessDeniedError, ConfigurationError, InputError, serializeError } from './errors.js';
import { FacebookClient } from './facebook-client.js';
import { PreviewStore } from './preview-store.js';
import type { PostDraft, PreparedPost } from './types.js';

const MINIMUM_SCHEDULE_DELAY_MS = 10 * 60 * 1_000;
const MAXIMUM_SCHEDULE_DELAY_MS = 30 * 24 * 60 * 60 * 1_000;

export interface PreparePostInput {
  readonly pageId: string;
  readonly message?: string;
  readonly link?: string;
  readonly photoUrl?: string;
  readonly scheduledAt?: string;
}

export interface PublisherOptions {
  readonly config: AppConfig;
  readonly previewStore?: PreviewStore;
  readonly client?: FacebookClient;
  readonly now?: () => number;
}

function normalizeOptionalText(value: string | undefined): string | undefined {
  const normalized = value?.trim();
  return normalized ? normalized : undefined;
}

function normalizeUrl(value: string, label: string, requireHttps: boolean): string {
  let url: URL;
  try {
    url = new URL(value);
  } catch {
    throw new InputError(`${label} must be a valid absolute URL`);
  }

  const allowedProtocols = requireHttps ? ['https:'] : ['http:', 'https:'];
  if (!allowedProtocols.includes(url.protocol)) {
    throw new InputError(`${label} must use ${requireHttps ? 'HTTPS' : 'HTTP or HTTPS'}`);
  }

  if (url.username || url.password) {
    throw new InputError(`${label} must not contain embedded credentials`);
  }

  if (requireHttps) {
    const hostname = url.hostname.toLowerCase();
    if (
      hostname === 'localhost'
      || hostname.endsWith('.localhost')
      || isIP(hostname) !== 0
      || !hostname.includes('.')
    ) {
      throw new InputError(`${label} must use a public hostname, not localhost or an IP address`);
    }
  }

  return url.toString();
}

export class FacebookPublisher {
  private readonly config: AppConfig;
  private readonly previews: PreviewStore;
  private readonly client?: FacebookClient;
  private readonly now: () => number;

  constructor(options: PublisherOptions) {
    this.config = options.config;
    this.previews = options.previewStore ?? new PreviewStore({ ttlMs: options.config.previewTtlMs });
    this.now = options.now ?? Date.now;
    this.client = options.client ?? (
      options.config.pageAccessToken
        ? new FacebookClient({
            accessToken: options.config.pageAccessToken,
            graphApiVersion: options.config.graphApiVersion,
            requestTimeoutMs: options.config.requestTimeoutMs,
          })
        : undefined
    );
  }

  status(): {
    token_configured: boolean;
    allowed_page_ids: string[];
    graph_api_version: string;
    pending_previews: number;
    ready_for_writes: boolean;
  } {
    return {
      token_configured: Boolean(this.config.pageAccessToken),
      allowed_page_ids: [...this.config.allowedPageIds],
      graph_api_version: this.config.graphApiVersion,
      pending_previews: this.previews.pendingCount(),
      ready_for_writes: Boolean(this.config.pageAccessToken) && this.config.allowedPageIds.size > 0,
    };
  }

  async getPage(pageId: string) {
    this.assertPageAllowed(pageId);
    return this.getClient().getPage(pageId);
  }

  async listRecentPosts(pageId: string, limit: number) {
    this.assertPageAllowed(pageId);
    return this.getClient().listRecentPosts(pageId, limit);
  }

  async getPost(postId: string) {
    this.assertPostAllowed(postId);
    return this.getClient().getPost(postId);
  }

  prepare(input: PreparePostInput): PreparedPost {
    this.assertPageAllowed(input.pageId);

    const message = normalizeOptionalText(input.message);
    const link = input.link ? normalizeUrl(input.link, 'link', false) : undefined;
    const photoUrl = input.photoUrl ? normalizeUrl(input.photoUrl, 'photo_url', true) : undefined;
    const scheduledAt = normalizeOptionalText(input.scheduledAt);

    if (message && message.length > this.config.maxMessageChars) {
      throw new InputError(`message exceeds the configured ${this.config.maxMessageChars}-character limit`);
    }

    if (photoUrl && link) {
      throw new InputError('A post cannot contain both link and photo_url in this release');
    }

    if (photoUrl && scheduledAt) {
      throw new InputError('Scheduled photo posts are not supported in this release');
    }

    if (!message && !link && !photoUrl) {
      throw new InputError('Provide at least one of message, link, or photo_url');
    }

    let normalizedScheduledAt: string | undefined;
    if (scheduledAt) {
      const scheduleTime = Date.parse(scheduledAt);
      if (!Number.isFinite(scheduleTime)) {
        throw new InputError('scheduled_at must be an ISO 8601 date and time with a timezone');
      }

      const delay = scheduleTime - this.now();
      if (delay < MINIMUM_SCHEDULE_DELAY_MS || delay > MAXIMUM_SCHEDULE_DELAY_MS) {
        throw new InputError('scheduled_at must be between 10 minutes and 30 days from now');
      }
      normalizedScheduledAt = new Date(scheduleTime).toISOString();
    }

    const draft: PostDraft = {
      pageId: input.pageId,
      kind: photoUrl ? 'photo' : 'feed',
      mode: normalizedScheduledAt ? 'schedule' : 'publish_now',
      ...(message ? { message } : {}),
      ...(link ? { link } : {}),
      ...(photoUrl ? { photoUrl } : {}),
      ...(normalizedScheduledAt ? { scheduledAt: normalizedScheduledAt } : {}),
    };

    return this.previews.prepare(draft);
  }

  async publish(previewId: string, approvalPhrase: string): Promise<Record<string, unknown>> {
    const client = this.getClient();
    const prepared = this.previews.consume(previewId, approvalPhrase);
    this.assertPageAllowed(prepared.draft.pageId);

    const created = prepared.draft.kind === 'photo'
      ? await client.publishPhoto({
          pageId: prepared.draft.pageId,
          photoUrl: prepared.draft.photoUrl!,
          ...(prepared.draft.message ? { message: prepared.draft.message } : {}),
        })
      : await client.publishFeedPost({
          pageId: prepared.draft.pageId,
          ...(prepared.draft.message ? { message: prepared.draft.message } : {}),
          ...(prepared.draft.link ? { link: prepared.draft.link } : {}),
          ...(prepared.draft.scheduledAt ? { scheduledAt: prepared.draft.scheduledAt } : {}),
        });

    try {
      const verifiedPost = await client.getPost(created.id);
      return {
        ok: true,
        action: prepared.draft.mode,
        post_id: created.id,
        ...(created.photoId ? { photo_id: created.photoId } : {}),
        content_hash: prepared.contentHash,
        verification: { status: 'verified', post: verifiedPost },
      };
    } catch (error) {
      // Publishing succeeded. Do not turn a read-back problem into a retryable publish error.
      return {
        ok: true,
        action: prepared.draft.mode,
        post_id: created.id,
        ...(created.photoId ? { photo_id: created.photoId } : {}),
        content_hash: prepared.contentHash,
        verification: {
          status: 'publish_succeeded_but_readback_failed',
          error: serializeError(error),
        },
      };
    }
  }

  private assertPageAllowed(pageId: string): void {
    if (!this.config.allowedPageIds.has(pageId)) {
      throw new AccessDeniedError(
        `Page ${pageId} is not allowlisted. Add it to FACEBOOK_PAGE_IDS before restarting the server.`,
      );
    }
  }

  private assertPostAllowed(postId: string): void {
    const separatorIndex = postId.indexOf('_');
    const pageId = separatorIndex > 0 ? postId.slice(0, separatorIndex) : '';
    if (!pageId || !/^\d+_\d+$/.test(postId)) {
      throw new AccessDeniedError('post_id must use the pageId_postId format');
    }
    this.assertPageAllowed(pageId);
  }

  private getClient(): FacebookClient {
    if (!this.client) {
      throw new ConfigurationError(
        'FACEBOOK_PAGE_ACCESS_TOKEN is not configured. Set it in the MCP process environment and restart the server.',
      );
    }
    return this.client;
  }
}
