# Security and Governance

Select controls by consequence and trust boundary. Free-text instructions are documentation; enforce policy in runtime code outside model discretion.

## Threat coverage

| Threat | Required design response |
| --- | --- |
| Goal/instruction corruption | Immutable objective/policy refs; treat retrieved content and messages as untrusted |
| Prompt injection | Context trust labels, instruction/data separation, allowlisted tool arguments, output validation |
| Tool misuse | Least privilege, operation/target/network/data-class bounds, per-call policy check |
| Identity/privilege abuse | Authenticated principals, scoped capabilities, no privilege through graph edges/messages |
| Supply-chain compromise | Pinned prompt/model/tool/code versions and integrity/provenance checks |
| Unsafe code execution | Isolated executor, resource/network/filesystem limits, no arbitrary predicate execution |
| Memory/state poisoning | Ownership, provenance, validation, freshness, retention, migration, and write controls |
| Inter-agent spoofing | Sender identity, message schemas, allowed communication graph, replay protection |
| Cascading failure | Failure frontiers, cancellation propagation, circuit/budget bounds, safe terminals |
| Privacy leakage | Data minimization, sensitivity/visibility labels, egress policy, redacted traces |
| Behavioral drift | Versioned artifacts, repeated evals, monitoring, promotion and rollback gates |

The OWASP Agentic Top 10 and NIST AI RMF are risk-management inputs, not claims that a checklist makes an agent safe.

## Protected actions

For `protected_action` and `high_assurance`, separate:

1. proposal of the exact action;
2. policy validation;
3. approval bound through `ApprovalBinding`;
4. restricted execution;
5. authoritative outcome verification;
6. compensation proposal when needed.

The binding includes action digest, complete scope, approver identity, expiry, nonce, and revocation state. Fail closed on absence, mismatch, expiry, nonce reuse, revocation, target/payload drift, or policy-version drift. Do not hard-code a provider decision string such as `approve_exact` into GraphSpec.

Keep secrets behind versioned handles. Action-defining values such as recipient, amount, target, command, or environment are not secrets and must remain inspectable in the binding scope.

## Idempotency and partial effects

Classify every side effect as `none`, `read_only`, `idempotent`, `non_idempotent`, or `protected_action`. A retry around a non-idempotent or protected operation is permitted only when the exact payload and provider idempotency scope remain valid, or authoritative status proves the prior attempt produced no effect.

When outcome is ambiguous, stop ordinary retries, reconcile authoritative state, and require separate authorization for compensation.

## Network, tools, and data

Declare allowed operations, target patterns, endpoints, data classifications, cost limits, and executor identities. Validate URLs and tool arguments. Deny egress of restricted data by default. Trace identifiers and decisions without logging raw credentials or unnecessary sensitive payloads.

## Governance

Record owners, version status, review date, retention/deletion rules, incident route, promotion authority, rollback authority, and archival disposition. Approval to change a graph version does not approve actions performed by runs of that graph.

## References

- OWASP, [Top 10 for Agentic Applications for 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/).
- NIST, [AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework).
