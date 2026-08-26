---
name: marketing-integrations
description: Select, inspect, connect, or operate marketing tools through available APIs, SDKs, CLIs, MCP servers, exports, webhooks, and automation platforms. Use when marketing work requires a specific analytics, ads, CRM, email, SMS, SEO, research, billing, referral, social, content, event, video, or data system.
---

# Marketing Integrations

Use the tool that owns the required state and is actually available. A vendor list is not evidence that an integration exists, is authorized, or still exposes the same API.

Read [tool-registry.md](references/tool-registry.md) to identify capability categories and candidates. Read [adapter-contract.md](references/adapter-contract.md) before implementing or operating any integration. Read [api-cli.md](references/api-cli.md) and use `scripts/api_request.py` when a current REST API can be operated safely without a vendor SDK or existing connector.

## Operating contract

1. Define the marketing decision or operation, source of truth, required read or mutation, frequency, volume, data sensitivity, and failure consequence.
2. Inspect locally available MCPs, CLIs, SDKs, application connectors, credentials, and project conventions before proposing a new dependency.
3. Verify current official vendor documentation, authentication, endpoint or tool schema, API version, rate limits, permissions, policy, and pricing where relevant.
4. Prefer read-only inspection, then a draft or dry run, then explicitly authorized mutation.
5. Redact secrets and sensitive data from commands, logs, examples, errors, and artifacts.
6. Define idempotency, deduplication, pagination, retries, timeouts, partial failure, reconciliation, and audit evidence before state-changing batches.
7. Verify the external result after mutation; a successful local request is not proof that downstream state is correct.

Do not install dependencies, connect accounts, import data, send messages, publish, spend, or change external state without task-specific authorization.
