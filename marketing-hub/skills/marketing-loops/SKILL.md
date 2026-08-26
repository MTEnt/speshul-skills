---
name: marketing-loops
description: Design, adapt, schedule, dry-run, monitor, pause, and retire recurring agent-driven marketing workflows with explicit triggers, state, decisions, outputs, approvals, metrics, guardrails, failure handling, and stop conditions. Use for weekly reviews, campaign health, creative fatigue, content refresh, churn watch, lead follow-up, ranking alerts, and always-on operations.
---

# Marketing Loops

Automate a stable decision process, not unresolved strategy. A loop must be observable, bounded, interruptible, and safe under duplicate or partial execution.

If `.agents/marketing-context.md` exists, read it first. Read [loop-system.md](references/loop-system.md) for anatomy, state, cadence, catalog, orchestration, guardrails, dry runs, and authoring.

## Operating contract

1. Prove the task recurs and has stable inputs, decision rules, useful outputs, and a real owner.
2. Define state, freshness, idempotency, deduplication, concurrency, timeouts, retry limits, partial failure, reconciliation, and retention.
3. Separate read and analyze, draft, approve, mutate external state, and verify.
4. Bound spend, messages, records, runtime, fan-out, and data.
5. Define no-action, pause, escalation, stop, and retirement before activation.
6. Run a fixed-snapshot dry run and one credible failure path before scheduling.

Do not schedule, send, publish, spend, or change live accounts without explicit authorization for that action and scope.
