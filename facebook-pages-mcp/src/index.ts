#!/usr/bin/env node

import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

import { loadConfig } from './config.js';
import { createMcpServer } from './server.js';

async function main(): Promise<void> {
  const config = loadConfig();
  const server = createMcpServer(config);
  const transport = new StdioServerTransport();

  await server.connect(transport);
  console.error('theworkshopai-facebook-pages-mcp is running on stdio');
  console.error(`Graph API: ${config.graphApiVersion}`);
  console.error(`Allowed Pages: ${config.allowedPageIds.size}`);
  console.error(`Token configured: ${config.pageAccessToken ? 'yes' : 'no'}`);

  const shutdown = async () => {
    await server.close();
    process.exit(0);
  };

  process.once('SIGINT', shutdown);
  process.once('SIGTERM', shutdown);
}

main().catch((error: unknown) => {
  console.error(`Fatal server error: ${error instanceof Error ? error.message : 'Unexpected error'}`);
  process.exit(1);
});
