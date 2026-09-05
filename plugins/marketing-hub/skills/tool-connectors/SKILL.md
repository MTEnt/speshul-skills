---
name: tool-connectors
description: Select, inspect, connect, and operate marketing systems through their APIs, SDKs, CLIs, MCP servers, exports, webhooks, and automation platforms: capability-first tool selection, credential boundaries, read and mutation contracts, dry runs, retries and reconciliation, and verification of external state, with a bounded provider-neutral HTTP client. Use when marketing work needs a specific analytics, ads, CRM, messaging, search, billing, social, content, or data system.
license: MIT
metadata:
  version: "2.0.0"
  author: MTEnt
---

# Tool Connectors

Use the tool that owns the required state and is actually available. A vendor list is not evidence that an integration exists, is authorized, or still exposes the same API.

If `.agents/marketing-context.md` exists, read it first; it is the truth file every skill in this hub shares, and its evidence states are constraints. Read [tool-registry.md](references/tool-registry.md) to identify capability categories and candidates. Read [adapter-contract.md](references/adapter-contract.md) before implementing or operating any integration. Read [api-cli.md](references/api-cli.md) and use `scripts/api_request.py` when a current REST API can be operated safely without a vendor SDK or existing connector.

## Operating contract

1. Define the decision or operation, source of truth, required read or mutation, frequency, volume, data sensitivity, and failure consequence.
2. Inspect locally available MCPs, CLIs, SDKs, connectors, credentials, and project conventions before proposing a new dependency.
3. Verify current official vendor documentation, authentication, endpoint or tool schema, version, rate limits, permissions, policy, and pricing.
4. Prefer read-only inspection, then a draft or dry run, then explicitly authorized mutation; define idempotency, deduplication, pagination, retries, timeouts, partial failure, reconciliation, and audit evidence first.
5. Verify the external result after mutation; a successful local request is not proof that downstream state is correct.

Do not install dependencies, connect accounts, import data, send messages, publish, spend, or change external state without task-specific authorization, and never expose secrets in commands, logs, examples, errors, or artifacts.

## Return

Selected tool and current sources, capability mapping, credential and scope requirements, neutral and provider-specific schemas, dry run, code or commands where authorized, test evidence, mutation approval boundary, verification, and operational owner.
