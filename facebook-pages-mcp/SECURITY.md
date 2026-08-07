# Security policy

## Credential handling

- Provide `FACEBOOK_PAGE_ACCESS_TOKEN` only through the MCP server process environment or a secret manager used by the MCP client.
- Never put access tokens in tool arguments, URLs, logs, screenshots, issues, commits, or chat messages.
- The Graph client sends credentials using the `Authorization: Bearer` header.
- Tool results expose only whether a token is configured, never its value or derived token data.
- Rotate the Page token immediately if it may have been exposed.

## Intended deployment

This release is a local stdio MCP server. Do not expose it directly over HTTP, deploy it as an unauthenticated shared service, or reuse one process for unrelated users.

Most installations should run one server instance for one Page access token and one Page ID. If multiple Page IDs are allowlisted, the configured token must legitimately authorize every Page.

## Write authorization

Publishing is an external side effect. The preview and approval phrase protect against accidental one-step writes, stale previews, changed payloads, and duplicate retries. They do not prove that a human approved the action because an MCP client can see both values.

Use an MCP client that requires human confirmation for `facebook_post_publish`. The tool must be called only after the user has seen and explicitly approved the Page, message, link or photo, publication time, and exact preview.

## Deliberate exclusions

The server does not provide:

- Post, photo, video, or comment deletion.
- Messenger access.
- Comment moderation.
- Arbitrary Graph API paths or fields.
- Tool-based token retrieval.
- Local-file reads or uploads.
- A remote HTTP transport.

Adding any of these changes the threat model and requires a separate security review.

## Reporting a vulnerability

Use the hosting repository's private security-advisory feature when available. Do not open a public issue containing an access token, exploit details, or private Page information.

Include the affected version, reproduction steps using dummy credentials, security impact, and a proposed mitigation if known.
