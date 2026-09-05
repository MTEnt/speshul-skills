# High-Assurance Profile

Use only when consequence, regulation, or explicit policy justifies the overhead. This profile extends `protected_action` and does not replace core GraphSpec.

## Evidence records

Use append-only or tamper-evident records appropriate to the risk:

- run manifest and immutable request reference;
- graph/prompt/model/tool/policy/schema versions and digests;
- node/attempt results with input/output artifact IDs;
- claim, evidence, verification, challenge, and adjudication ledgers;
- action proposals, approval bindings, executions, outcome verification, and compensation records;
- control events, checkpoints, migrations, evaluation, release, and rollback decisions.

Each record declares schema version, stable identity, run/node/attempt identity where applicable, producer, timestamps, input lineage, sensitivity, retention class, integrity digest/signature policy, and supersession status.

## Verification, criticism, repair, adjudication

Keep these contracts separate:

1. collector records candidate claims and locatable evidence;
2. verifier checks whether evidence exists and supports exact scope/date;
3. critic tests logic, omissions, assumptions, and decision relevance;
4. repair worker addresses only named defects within a finite attempt budget;
5. adjudicator resolves competing terminal records under a declared policy;
6. synthesizer preserves provenance, disagreement, and uncertainty;
7. final verifier checks the deliverable and authoritative outcome against original success criteria.

Do not erase unsupported, contradicted, or unverifiable claims. Independence claims must name actual context/source/model/organizational separation.

## Approval and execution separation

Proposal, policy check, approval, restricted execution, and outcome verification require distinct records and authority. Approval binds the canonical action digest and full scope through `ApprovalBinding`; no generic approval or conversation message authorizes execution. One-time nonce, expiry, revocation, policy drift, and terminal proposal status are checked immediately before execution.

## Retention and privacy

Define owner, access, encryption/signature requirements, retention/deletion, redaction, legal hold where applicable, and cross-run reuse policy. Never place raw credentials in prompts, ledgers, traces, or hashes susceptible to offline guessing. A hash is integrity metadata, not access control.

## Release controls

Before promotion:

- canonical GraphSpec validates and its digest matches reviewed views;
- implementation mapping has no silent semantic gaps;
- state migrations and rollback have been exercised;
- path, recovery, safety, permission, latency, and cost gates pass;
- independent adjudication closes material verification forks;
- protected-action controls pass negative tests;
- held-out evaluation meets the declared repeated-trial threshold;
- release and rollback authority records are present and current;
- artifacts and rejected candidates have archival dispositions.

Do not report `success` from documentation or model output alone; require declared outcome evidence.
