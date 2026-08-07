import { z } from 'zod/v4';

const pageIdPattern = /^\d+$/;
const graphVersionPattern = /^v\d+\.\d+$/;

export interface AppConfig {
  readonly pageAccessToken?: string;
  readonly allowedPageIds: ReadonlySet<string>;
  readonly graphApiVersion: string;
  readonly previewTtlMs: number;
  readonly requestTimeoutMs: number;
  readonly maxMessageChars: number;
}

function optionalPositiveInteger(
  value: string | undefined,
  fallback: number,
  name: string,
): number {
  if (value === undefined || value.trim() === '') return fallback;

  const parsed = Number(value);
  if (!Number.isSafeInteger(parsed) || parsed <= 0) {
    throw new Error(`${name} must be a positive integer`);
  }

  return parsed;
}

export function loadConfig(env: NodeJS.ProcessEnv = process.env): AppConfig {
  const graphApiVersion = env.FACEBOOK_GRAPH_API_VERSION?.trim() || 'v26.0';
  if (!graphVersionPattern.test(graphApiVersion)) {
    throw new Error('FACEBOOK_GRAPH_API_VERSION must look like v26.0');
  }

  const pageIds = (env.FACEBOOK_PAGE_IDS ?? '')
    .split(',')
    .map((pageId) => pageId.trim())
    .filter(Boolean);

  for (const pageId of pageIds) {
    if (!pageIdPattern.test(pageId)) {
      throw new Error('FACEBOOK_PAGE_IDS must contain only comma-separated numeric Page IDs');
    }
  }

  const pageAccessToken = env.FACEBOOK_PAGE_ACCESS_TOKEN?.trim() || undefined;
  const previewTtlSeconds = optionalPositiveInteger(
    env.FACEBOOK_PREVIEW_TTL_SECONDS,
    900,
    'FACEBOOK_PREVIEW_TTL_SECONDS',
  );

  return {
    ...(pageAccessToken ? { pageAccessToken } : {}),
    allowedPageIds: new Set(pageIds),
    graphApiVersion,
    previewTtlMs: previewTtlSeconds * 1_000,
    requestTimeoutMs: optionalPositiveInteger(
      env.FACEBOOK_REQUEST_TIMEOUT_MS,
      15_000,
      'FACEBOOK_REQUEST_TIMEOUT_MS',
    ),
    maxMessageChars: optionalPositiveInteger(
      env.FACEBOOK_MAX_MESSAGE_CHARS,
      20_000,
      'FACEBOOK_MAX_MESSAGE_CHARS',
    ),
  };
}

export const numericPageIdSchema = z
  .string()
  .regex(pageIdPattern, 'page_id must be numeric');
