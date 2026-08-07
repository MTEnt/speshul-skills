import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { InMemoryTransport } from '@modelcontextprotocol/sdk/inMemory.js';
import { afterEach, describe, expect, it } from 'vitest';

import { loadConfig } from '../src/config.js';
import { createMcpServer } from '../src/server.js';

describe('MCP server', () => {
  const closeCallbacks: Array<() => Promise<void>> = [];

  afterEach(async () => {
    await Promise.all(closeCallbacks.splice(0).map((close) => close()));
  });

  async function connect() {
    const server = createMcpServer(loadConfig({ FACEBOOK_PAGE_IDS: '123' }));
    const client = new Client({ name: 'test-client', version: '1.0.0' });
    const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
    await Promise.all([server.connect(serverTransport), client.connect(clientTransport)]);
    closeCallbacks.push(async () => {
      await client.close();
      await server.close();
    });
    return client;
  }

  it('exposes only the intended six tools', async () => {
    const client = await connect();
    const result = await client.listTools();

    expect(result.tools.map((tool) => tool.name)).toEqual([
      'facebook_connection_status',
      'facebook_page_get',
      'facebook_post_preview',
      'facebook_post_publish',
      'facebook_post_get',
      'facebook_post_list_recent',
    ]);
  });

  it('never returns an access token in status and can preview without one', async () => {
    const client = await connect();
    const status = await client.callTool({ name: 'facebook_connection_status', arguments: {} });
    const preview = await client.callTool({
      name: 'facebook_post_preview',
      arguments: { page_id: '123', message: 'Draft only' },
    });

    expect(JSON.stringify(status)).not.toContain('FACEBOOK_PAGE_ACCESS_TOKEN');
    expect(JSON.stringify(status)).toContain('"token_configured":false');
    expect(preview.isError).not.toBe(true);
    expect(JSON.stringify(preview)).toContain('approval_phrase');
  });

  it('returns a configuration error instead of attempting a publish without a token', async () => {
    const client = await connect();
    const previewResult = await client.callTool({
      name: 'facebook_post_preview',
      arguments: { page_id: '123', message: 'Draft only' },
    });
    const preview = previewResult.structuredContent as {
      preview: { preview_id: string; approval_phrase: string };
    };
    const publishResult = await client.callTool({
      name: 'facebook_post_publish',
      arguments: {
        preview_id: preview.preview.preview_id,
        approval_phrase: preview.preview.approval_phrase,
      },
    });

    expect(publishResult.isError).toBe(true);
    expect(JSON.stringify(publishResult)).toContain('CONFIGURATION_ERROR');
  });

  it('classifies expected content validation failures as invalid input', async () => {
    const client = await connect();
    const result = await client.callTool({
      name: 'facebook_post_preview',
      arguments: { page_id: '123', photo_url: 'http://example.com/photo.jpg' },
    });

    expect(result.isError).toBe(true);
    expect(JSON.stringify(result)).toContain('INVALID_INPUT');
  });
});
