# Integration adapter contract

## Capability before vendor

Describe the operation in provider-neutral terms before mapping it:

```text
read campaign performance
create an unpublished creative draft
upsert a consented contact
record an offline conversion
schedule an approved message
retrieve search performance
reconcile subscription state
```

This prevents vendor details from becoming the business contract.

## Discovery

1. Inspect the user's current tools and connector inventory.
2. Locate official API, SDK, CLI, MCP, export, webhook, and authentication documentation.
3. Confirm version, environment, account, object IDs, scopes, sandbox, rate and batch limits, and current deprecations.
4. Identify source of truth, downstream consumers, and whether the operation is read-only, draft, or external mutation.

Do not expose tokens while checking environment or configuration.

## Credential boundary

Use the platform's supported secret store or environment mechanism. Request only required scopes. Keep tokens out of prompts, command lines where process lists expose them, URLs, logs, fixtures, screenshots, and committed files. Define rotation and revocation owner.

## Read contract

Specify object, fields, filters, date basis, time zone, pagination, rate handling, freshness, identity, permissions, and missing or partial data. Preserve raw IDs and source timestamps needed for reconciliation.

## Mutation contract

```yaml
operation:
account_and_environment:
authorized_scope:
input_schema:
preconditions:
idempotency_key:
deduplication:
batch_limit:
dry_run_or_preview:
approval_evidence:
request:
expected_external_state:
verification_read:
partial_failure:
retry_policy:
rollback_or_correction:
audit_record:
```

Validate business meaning before sending. A syntactically valid campaign, contact, message, or payment mutation can still be unsafe or wrong.

## Dry run

A useful dry run shows method or tool, redacted endpoint or operation, account, object IDs, normalized payload, number of affected records, permissions, cost or spend impact, policy checks, and expected result. It must not call a write endpoint.

## Retries and reconciliation

Retry only evidenced transient failures and only when the operation is safe or idempotent. After timeout or ambiguous response, read external state using a stable identifier before retrying. For batches, retain per-record result and do not replay successes blindly.

## Verification

Read the mutated object or authoritative downstream state, compare expected and observed fields, check error or policy status, record external IDs and timestamps, and confirm downstream propagation where the task requires it.

## Error handling

Preserve vendor status, request ID, safe response details, and original cause. Redact secrets and sensitive records. Distinguish authentication, permission, validation, policy, quota, rate, conflict, not-found, transient service, and partial-batch errors.

## Implementation output

Return selected tool and current sources, capability mapping, credential and scope requirements, provider-neutral and provider-specific schemas, dry run, code or commands where authorized, test evidence, mutation approval boundary, verification, and operational owner.
