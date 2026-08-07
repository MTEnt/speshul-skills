import { GraphApiError } from './errors.js';
import type { CreatedPost, FacebookPage, FacebookPost } from './types.js';

export type FetchLike = typeof fetch;

interface FacebookClientOptions {
  readonly accessToken: string;
  readonly graphApiVersion: string;
  readonly requestTimeoutMs: number;
  readonly fetchImpl?: FetchLike;
}

interface GraphErrorPayload {
  readonly error?: {
    readonly message?: string;
    readonly code?: number;
    readonly error_subcode?: number;
  };
}

interface GraphListResponse<T> extends GraphErrorPayload {
  readonly data?: T[];
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

export class FacebookClient {
  private readonly baseUrl: string;
  private readonly accessToken: string;
  private readonly requestTimeoutMs: number;
  private readonly fetchImpl: FetchLike;

  constructor(options: FacebookClientOptions) {
    this.baseUrl = `https://graph.facebook.com/${options.graphApiVersion}`;
    this.accessToken = options.accessToken;
    this.requestTimeoutMs = options.requestTimeoutMs;
    this.fetchImpl = options.fetchImpl ?? fetch;
  }

  private sanitizeMessage(message: string): string {
    return message
      .split(this.accessToken).join('[REDACTED]')
      .split(encodeURIComponent(this.accessToken)).join('[REDACTED]');
  }

  async getPage(pageId: string): Promise<FacebookPage> {
    return this.request<FacebookPage>(pageId, {
      query: { fields: 'id,name,category,link' },
    });
  }

  async listRecentPosts(pageId: string, limit: number): Promise<FacebookPost[]> {
    const response = await this.request<GraphListResponse<FacebookPost>>(`${pageId}/feed`, {
      query: {
        fields: 'id,message,created_time,permalink_url,is_published,scheduled_publish_time,full_picture',
        limit: String(limit),
      },
    });
    return response.data ?? [];
  }

  async getPost(postId: string): Promise<FacebookPost> {
    return this.request<FacebookPost>(postId, {
      query: {
        fields: 'id,message,created_time,permalink_url,is_published,scheduled_publish_time,full_picture',
      },
    });
  }

  async publishFeedPost(input: {
    pageId: string;
    message?: string;
    link?: string;
    scheduledAt?: string;
  }): Promise<CreatedPost> {
    const body: Record<string, unknown> = {};
    if (input.message) body.message = input.message;
    if (input.link) body.link = input.link;

    if (input.scheduledAt) {
      body.published = false;
      body.scheduled_publish_time = Math.floor(Date.parse(input.scheduledAt) / 1_000);
    } else {
      body.published = true;
    }

    const response = await this.request<CreatedPost>(`${input.pageId}/feed`, {
      method: 'POST',
      body,
    });
    if (typeof response.id !== 'string' || response.id === '') {
      throw new GraphApiError('Facebook accepted the request but did not return a post ID');
    }
    return response;
  }

  async publishPhoto(input: {
    pageId: string;
    photoUrl: string;
    message?: string;
  }): Promise<CreatedPost> {
    const response = await this.request<{ id: string; post_id?: string }>(`${input.pageId}/photos`, {
      method: 'POST',
      body: {
        url: input.photoUrl,
        ...(input.message ? { message: input.message } : {}),
        published: true,
      },
    });

    if (typeof response.id !== 'string' || response.id === '') {
      throw new GraphApiError('Facebook accepted the photo request but did not return an ID');
    }
    if (response.post_id !== undefined && (typeof response.post_id !== 'string' || response.post_id === '')) {
      throw new GraphApiError('Facebook returned an invalid post ID for the published photo');
    }

    return {
      id: response.post_id ?? response.id,
      ...(response.post_id ? { photoId: response.id } : {}),
    };
  }

  private async request<T>(
    path: string,
    options: {
      method?: 'GET' | 'POST';
      body?: Record<string, unknown>;
      query?: Record<string, string>;
    } = {},
  ): Promise<T> {
    const url = new URL(`${this.baseUrl}/${path}`);
    for (const [name, value] of Object.entries(options.query ?? {})) {
      url.searchParams.set(name, value);
    }

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), this.requestTimeoutMs);

    let response: Response;
    try {
      response = await this.fetchImpl(url, {
        method: options.method ?? 'GET',
        headers: {
          Accept: 'application/json',
          Authorization: `Bearer ${this.accessToken}`,
          ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        },
        ...(options.body ? { body: JSON.stringify(options.body) } : {}),
        signal: controller.signal,
      });
    } catch (error) {
      if (controller.signal.aborted) {
        throw new GraphApiError('Facebook Graph API request timed out');
      }
      throw new GraphApiError(
        this.sanitizeMessage(
          `Facebook Graph API request failed: ${error instanceof Error ? error.message : 'network error'}`,
        ),
      );
    } finally {
      clearTimeout(timeout);
    }

    let payload: unknown;
    try {
      payload = await response.json();
    } catch {
      throw new GraphApiError(
        `Facebook Graph API returned a non-JSON response with HTTP ${response.status}`,
        response.status,
      );
    }

    const graphError = isRecord(payload) && isRecord(payload.error) ? payload.error : undefined;
    if (!response.ok || graphError) {
      const message = typeof graphError?.message === 'string'
        ? graphError.message
        : `Facebook Graph API returned HTTP ${response.status}`;
      throw new GraphApiError(
        this.sanitizeMessage(message),
        response.status,
        typeof graphError?.code === 'number' ? graphError.code : undefined,
        typeof graphError?.error_subcode === 'number' ? graphError.error_subcode : undefined,
      );
    }

    return payload as T;
  }
}
