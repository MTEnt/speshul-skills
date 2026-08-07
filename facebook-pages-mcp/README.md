# The Workshop AI Facebook Pages MCP

A local, safety-focused Model Context Protocol server for drafting, previewing, publishing, scheduling, and verifying posts on Facebook Pages.

This project is not affiliated with or endorsed by Meta.

The separate [Facebook Content Studio skill](https://github.com/MTEnt/speshul-skills/tree/main/facebook-content-studio) can prepare validated post packages and hand supported text, link, and photo posts to this server's approval flow.

## What it does

- Publishes text and link posts.
- Publishes a single photo from a public HTTPS URL.
- Schedules text and link posts between 10 minutes and 30 days ahead.
- Reads Page identity and recent posts.
- Verifies a newly created post without treating a read-back failure as a failed publish.
- Requires an expiring, single-use preview before any write.
- Restricts every Graph API call to explicitly allowlisted Page IDs.

It intentionally does not expose deletion, Messenger, comment moderation, arbitrary Graph API calls, local-file reads, or a network-facing MCP endpoint.

## Safety model

The server uses four layers:

1. **Runtime-only credential**: `FACEBOOK_PAGE_ACCESS_TOKEN` is read from the server process environment. It is never a tool argument or tool result.
2. **Page allowlist**: every Graph API call must target a Page in `FACEBOOK_PAGE_IDS`.
3. **Preview then commit**: `facebook_post_preview` creates the exact immutable payload, content hash, expiry, and approval phrase. `facebook_post_publish` consumes it once.
4. **No blind retry**: the preview is consumed before the network request. If a publish result is ambiguous, create and approve a new preview only after checking the Page.

The approval phrase reduces accidental writes and payload changes. It is not a security boundary against a malicious MCP client. Keep human confirmation enabled for write tools in your MCP client. Read [SECURITY.md](./SECURITY.md) before deployment.

## Meta prerequisites

You need:

- A Meta developer app.
- A Facebook Page on which the app user can perform the `CREATE_CONTENT` task.
- A Page access token valid for that Page.
- `pages_manage_posts`, with its `pages_read_engagement` and `pages_show_list` dependencies.

Meta's current Pages API examples use Graph API `v26.0`. The default can be changed with `FACEBOOK_GRAPH_API_VERSION` when Meta releases a newer version.

References:

- [Meta Pages API: Get Started](https://developers.facebook.com/documentation/pages-api/getting-started)
- [Meta Pages API: Posts](https://developers.facebook.com/documentation/pages-api/posts)
- [Meta Permissions Reference](https://developers.facebook.com/docs/permissions/#p)

Use Graph API Explorer only for development and validation. A product that onboards other Page owners needs a proper Facebook Login flow, per-user Page authorization, App Review where required, token lifecycle handling, privacy disclosures, and any required Business Verification.

## Install from source

Requirements: Node.js 20 or newer.

```bash
npm install
npm run verify
```

Build output is written to `dist/`:

```bash
npm run build
node dist/index.js
```

The server uses stdio. Configure it as a local process in any MCP client that supports stdio servers.

## Configuration

| Environment variable | Required | Default | Purpose |
|---|---:|---:|---|
| `FACEBOOK_PAGE_ACCESS_TOKEN` | For Graph calls | none | Page access token. Never pass it as a tool argument. |
| `FACEBOOK_PAGE_IDS` | For Graph calls | none | Comma-separated numeric Page allowlist. Most users should configure one Page per server instance. |
| `FACEBOOK_GRAPH_API_VERSION` | No | `v26.0` | Versioned Graph API path. |
| `FACEBOOK_PREVIEW_TTL_SECONDS` | No | `900` | How long an uncommitted preview remains valid. |
| `FACEBOOK_REQUEST_TIMEOUT_MS` | No | `15000` | Graph API request timeout. |
| `FACEBOOK_MAX_MESSAGE_CHARS` | No | `20000` | Local safety limit for post text. |

The server can start without a token so an MCP client can inspect its tools and safe configuration. Any Graph call returns `CONFIGURATION_ERROR` until a token is supplied and the process is restarted.

Copy `.env.example` only as a reference. The server deliberately does not auto-load `.env` files. Inject secrets through your MCP client's secret mechanism, an operating-system credential store, or a local launcher that reads one.

Never commit a real token, paste it into an issue, include it in an MCP tool call, or put it on a command line that will be saved in shell history.

### Generic MCP client configuration

After building, use the absolute path to `dist/index.js`:

```json
{
  "mcpServers": {
    "facebook-pages": {
      "command": "node",
      "args": ["/absolute/path/to/facebook-pages-mcp/dist/index.js"],
      "env": {
        "FACEBOOK_PAGE_IDS": "123456789012345",
        "FACEBOOK_PAGE_ACCESS_TOKEN": "inject-with-your-client-secret-store"
      }
    }
  }
}
```

Do not commit a client configuration containing the real token.

## Tools

| Tool | External effect |
|---|---|
| `facebook_connection_status` | None. Returns non-secret configuration only. |
| `facebook_page_get` | Read an allowlisted Page's identity. |
| `facebook_post_preview` | None on Facebook. Creates an expiring local preview. |
| `facebook_post_publish` | Publishes or schedules the exact approved preview. |
| `facebook_post_get` | Read one post belonging to an allowlisted Page. |
| `facebook_post_list_recent` | Read recent posts from an allowlisted Page. |

The server also exposes the `facebook-page-post-workflow` prompt and the non-secret `facebook://configuration` resource.

## Expected agent workflow

1. Call `facebook_connection_status`.
2. Call `facebook_page_get` and show the user the Page name and ID.
3. Draft the content.
4. Call `facebook_post_preview`.
5. Display the complete preview, schedule, expiry, content hash, and approval phrase.
6. Wait for explicit user approval of that exact preview.
7. Call `facebook_post_publish` once.
8. Report the post ID, permalink when available, and verification status.

Example preview input:

```json
{
  "page_id": "123456789012345",
  "message": "A new workshop is open for registration.",
  "link": "https://example.com/workshop"
}
```

Example scheduled input:

```json
{
  "page_id": "123456789012345",
  "message": "Registration closes tomorrow.",
  "scheduled_at": "2026-08-10T09:00:00+07:00"
}
```

Photo posts require a public HTTPS URL with a hostname. Local paths, IP-address URLs, embedded URL credentials, scheduled photos, and combined photo-plus-link posts are rejected.

## Development

```bash
npm run typecheck
npm test
npm run build
npm run verify
```

Tests use mocked Graph API responses and never need a Facebook token. No live post is created by the test suite.

See [CONTRIBUTING.md](./CONTRIBUTING.md) for change requirements and [CHANGELOG.md](./CHANGELOG.md) for release notes.

## Companion content skill

The separately installable [Facebook Content Studio skill](https://github.com/MTEnt/speshul-skills/tree/main/facebook-content-studio) adds research, progressive interviewing, continuity planning, Higgsfield routing, QA, and post-package validation. It does not change this server's publication boundary: text, links, and one public HTTPS photo are supported; video remains a manual Meta Business Suite handoff until a separately reviewed uploader implements Meta's additional User-token and App-ID requirements.
