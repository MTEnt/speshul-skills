import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import * as z from 'zod/v4';

import type { AppConfig } from './config.js';
import { numericPageIdSchema } from './config.js';
import { serializeError } from './errors.js';
import { FacebookPublisher } from './publisher.js';

type ToolData = Record<string, unknown>;

function success(data: ToolData) {
  return {
    content: [{ type: 'text' as const, text: JSON.stringify(data, null, 2) }],
    structuredContent: data,
  };
}

function failure(error: unknown) {
  const data = { ok: false, error: serializeError(error) };
  return {
    content: [{ type: 'text' as const, text: JSON.stringify(data, null, 2) }],
    structuredContent: data,
    isError: true,
  };
}

async function runTool(action: () => ToolData | Promise<ToolData>) {
  try {
    return success(await action());
  } catch (error) {
    return failure(error);
  }
}

export function createMcpServer(config: AppConfig, publisher = new FacebookPublisher({ config })) {
  const server = new McpServer({
    name: 'theworkshopai-facebook-pages-mcp',
    version: '0.1.0',
  });

  server.registerTool(
    'facebook_connection_status',
    {
      title: 'Facebook connection status',
      description: 'Check safe server configuration. Never returns an access token.',
      inputSchema: {},
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false,
      },
    },
    async () => success({ ok: true, ...publisher.status() }),
  );

  server.registerTool(
    'facebook_page_get',
    {
      title: 'Get Facebook Page',
      description: 'Get the identity of an allowlisted Facebook Page before drafting or publishing.',
      inputSchema: {
        page_id: numericPageIdSchema.describe('Numeric Facebook Page ID from FACEBOOK_PAGE_IDS'),
      },
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: true,
      },
    },
    async ({ page_id }) => runTool(async () => ({ ok: true, page: await publisher.getPage(page_id) })),
  );

  server.registerTool(
    'facebook_post_preview',
    {
      title: 'Preview Facebook Page post',
      description: [
        'Prepare an exact, expiring Facebook Page post preview without contacting Facebook.',
        'Returns a preview_id, content hash, and approval_phrase.',
        'Show the complete preview and approval phrase to the user. Do not call facebook_post_publish unless the user explicitly approves that exact preview.',
        'Supports text, links, immediate public-HTTPS photos, and scheduled text/link posts.',
      ].join(' '),
      inputSchema: {
        page_id: numericPageIdSchema.describe('Numeric allowlisted Facebook Page ID'),
        message: z.string().optional().describe('Post text or photo caption'),
        link: z.string().optional().describe('Optional absolute HTTP or HTTPS link for a feed post'),
        photo_url: z.string().optional().describe('Optional public HTTPS image URL. Cannot be combined with link or scheduled_at.'),
        scheduled_at: z.string().optional().describe('Optional ISO 8601 date/time with timezone, 10 minutes to 30 days from now'),
      },
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: false,
        openWorldHint: false,
      },
    },
    async ({ page_id, message, link, photo_url, scheduled_at }) => runTool(() => {
      const preview = publisher.prepare({
        pageId: page_id,
        ...(message === undefined ? {} : { message }),
        ...(link === undefined ? {} : { link }),
        ...(photo_url === undefined ? {} : { photoUrl: photo_url }),
        ...(scheduled_at === undefined ? {} : { scheduledAt: scheduled_at }),
      });
      return {
        ok: true,
        preview: {
          preview_id: preview.previewId,
          approval_phrase: preview.approvalPhrase,
          content_hash: preview.contentHash,
          created_at: preview.createdAt,
          expires_at: preview.expiresAt,
          post: {
            page_id: preview.draft.pageId,
            kind: preview.draft.kind,
            mode: preview.draft.mode,
            ...(preview.draft.message ? { message: preview.draft.message } : {}),
            ...(preview.draft.link ? { link: preview.draft.link } : {}),
            ...(preview.draft.photoUrl ? { photo_url: preview.draft.photoUrl } : {}),
            ...(preview.draft.scheduledAt ? { scheduled_at: preview.draft.scheduledAt } : {}),
          },
        },
      };
    }),
  );

  server.registerTool(
    'facebook_post_publish',
    {
      title: 'Publish approved Facebook Page post',
      description: [
        'External write action. Publishes or schedules the exact single-use preview created by facebook_post_preview.',
        'Call only after the user explicitly approves the displayed Page, content, media, timing, and exact approval phrase.',
        'A failed or ambiguous call consumes the preview to prevent duplicate posting. Create a new preview instead of blindly retrying.',
      ].join(' '),
      inputSchema: {
        preview_id: z.string().regex(/^[a-f0-9]{32}$/).describe('Single-use preview ID returned by facebook_post_preview'),
        approval_phrase: z.string().min(1).describe('Exact approval phrase returned with the preview and explicitly approved by the user'),
      },
      annotations: {
        readOnlyHint: false,
        destructiveHint: false,
        idempotentHint: false,
        openWorldHint: true,
      },
    },
    async ({ preview_id, approval_phrase }) => runTool(() => publisher.publish(preview_id, approval_phrase)),
  );

  server.registerTool(
    'facebook_post_get',
    {
      title: 'Get Facebook Page post',
      description: 'Read back one post whose ID belongs to an allowlisted Page.',
      inputSchema: {
        post_id: z.string().regex(/^\d+_\d+$/).describe('Facebook post ID in pageId_postId format'),
      },
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: true,
      },
    },
    async ({ post_id }) => runTool(async () => ({ ok: true, post: await publisher.getPost(post_id) })),
  );

  server.registerTool(
    'facebook_post_list_recent',
    {
      title: 'List recent Facebook Page posts',
      description: 'List recent posts from one allowlisted Facebook Page for verification and content review.',
      inputSchema: {
        page_id: numericPageIdSchema.describe('Numeric allowlisted Facebook Page ID'),
        limit: z.number().int().min(1).max(100).default(10).describe('Number of posts, from 1 to 100'),
      },
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: true,
      },
    },
    async ({ page_id, limit }) => runTool(async () => ({
      ok: true,
      page_id,
      posts: await publisher.listRecentPosts(page_id, limit),
    })),
  );

  server.registerPrompt(
    'facebook-page-post-workflow',
    {
      title: 'Draft and publish a Facebook Page post safely',
      description: 'A preview-first workflow for creating Facebook Page content with explicit approval.',
      argsSchema: {
        goal: z.string().describe('What the user wants the Facebook post to accomplish'),
      },
    },
    async ({ goal }) => ({
      messages: [{
        role: 'user' as const,
        content: {
          type: 'text' as const,
          text: [
            `Create a Facebook Page post for this goal: ${goal}`,
            '',
            'Workflow requirements:',
            '1. Confirm the target Page with facebook_page_get.',
            '2. Draft the post and call facebook_post_preview.',
            '3. Display the exact Page, message, link or photo, schedule, expiry, and approval phrase.',
            '4. Do not publish until the user explicitly approves that exact preview.',
            '5. After approval, call facebook_post_publish once.',
            '6. Report the returned post ID, permalink when available, and verification status.',
          ].join('\n'),
        },
      }],
    }),
  );

  server.registerResource(
    'facebook-pages-mcp-configuration',
    'facebook://configuration',
    {
      title: 'Facebook Pages MCP safe configuration',
      description: 'Non-secret server status and Page allowlist.',
      mimeType: 'application/json',
    },
    async () => ({
      contents: [{
        uri: 'facebook://configuration',
        mimeType: 'application/json',
        text: JSON.stringify(publisher.status(), null, 2),
      }],
    }),
  );

  return server;
}
