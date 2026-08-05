---
name: graph-engineering
description: Design, simplify, audit, and repair AI-assisted workflow graphs with explicit node contracts, edge policies, state, evidence verification, bounded retries, approval gates, safe execution, and evaluation. Use when Codex must turn a complex request into the smallest sufficient workflow; choose between a direct operation, chain, router, parallel workers, evaluator loop, or bounded agent; review an existing agent or multi-agent architecture; or produce implementation-ready graph, state, failure, approval, and evaluation specifications.
---

# Graph Engineering

## Core rule

Choose the least complex workflow that can satisfy the declared outcome and mandatory controls. Treat a graph as a control mechanism, not a source of truth. Add a node only when it has measured value or implements a documented policy, security, or compliance requirement.

## Build or audit the workflow

### 1. Preserve the request and define success

Record:

- the exact request or immutable reference;
- the required deliverable and audience;
- run success criteria;
- partial-sufficiency criteria;
- constraints, non-goals, deadline, budget, and data classification;
- protected actions and the policy that defines them.

Keep run success criteria, node acceptance criteria, and partial-sufficiency criteria separate.

### 2. Select the smallest topology

Use this order:

| Condition | Start with |
| --- | --- |
| Deterministic and cheaply checked | Code, lookup, or one tool call |
| Narrow language task | One bounded model call |
| Fixed ordered subtasks | Short chain |
| Distinct input classes | Router with specialized paths |
| Genuinely separable work | Parallel branches with an explicit join |
| Inspectable quality threshold | Evaluator with a bounded repair loop |
| Dynamic path but bounded action space | Bounded agent |
| Path cannot yet be bounded safely | Human-led exploration |

Do not add agents merely to create debate, role-play, or apparent independence. Separately scoped branches can still share sources, framing, models, and correlated errors.

### 3. Specify executable contracts

For every node, declare:

- one bounded responsibility;
- owner and version;
- allowed inputs, state reads, and state writes;
- output schema;
- allowed tools, sources, targets, endpoints, and data classes;
- acceptance checks;
- timeout and retry policy;
- route after attempt exhaustion;
- forbidden actions;
- side-effect and approval status.

For every edge, declare the trigger, validated state passed forward, merge rule, and terminal route. Give every cycle an attempt cap and deadline.

Use append-only, versioned records for concurrent work. Do not permit silent last-write-wins merges.

### 4. Separate evidence jobs

Keep these roles distinct where material claims exist:

1. Collect candidate claims and evidence.
2. Verify that cited evidence supports the exact claim and scope.
3. Criticize logic, omissions, assumptions, and decision relevance.
4. Synthesize without changing claim type or verification status.
5. Verify the final deliverable against the original request and ledger.

Treat a factual claim as material when its falsity could change a run success check, decision, stated risk, or protected action. Preserve unsupported, contradicted, and unverifiable claims with their reasons. Resolve verification forks through explicit adjudication, not timestamps.

### 5. Gate protected actions

Separate proposal, approval, execution, and outcome verification.

- Bind approval to the exact action version, payload digest, target, scope, and expiry.
- Require one active terminal approval whose decision is `approve_exact`.
- Fail closed on version forks, revocation, drift, expired approval, or policy mismatch.
- Keep raw credentials behind pinned secret handles; never hide action-defining values such as recipients, amounts, commands, or configuration choices.
- Execute side effects only through a restricted executor.
- Confirm the authoritative post-action state before reporting success.

Do not retry a side effect unless provider idempotency still covers the exact action or authoritative status proves that the earlier attempt failed without producing the protected effect.

### 6. Design failure and termination paths

Define routes for invalid output, missing input, inaccessible evidence, conflicting evidence, timeouts, exhausted retries, budget exhaustion, policy failures, partial side effects, cancellation, and checkpoint-version drift.

Require a run deadline and append-only cancellation events. After cancellation, stop ordinary work; allow only bounded safety reconciliation authorized by policy.

### 7. Evaluate the graph

Compare the workflow with a simpler baseline on representative tasks. Measure task success, evidence quality, missed errors, false alarms, human corrections, cost, latency, recovery, and unintended actions. Remove optional nodes that do not earn their cost. Test mandatory controls for effectiveness even when they cannot be removed.

## Output contract

When designing a workflow, return:

1. A blunt topology decision and why it is the smallest sufficient design.
2. The simpler baseline considered.
3. A node table and edge table.
4. The state schema and merge rules.
5. Evidence, verification, and final-output checks.
6. Approval and restricted-execution rules for protected actions.
7. Retry, cancellation, partial-result, and terminal routes.
8. An evaluation plan and explicit unresolved risks.

When auditing an existing workflow, lead with the verdict. List concrete defects by severity, cite the affected contract or file, distinguish verified defects from inference, and recommend the smallest repair that closes each defect.

## Reference routing

- Read [references/philosophy.md](references/philosophy.md) when explaining principles, challenging multi-agent assumptions, or deciding whether a graph is justified.
- Read [references/playbook.md](references/playbook.md) when producing implementation-ready manifests, schemas, prompts, approval records, executor contracts, or release checks.
- Search the relevant heading first instead of loading both references when the task is narrow.
- Verify framework-specific behavior against current official documentation before presenting it as current fact.
