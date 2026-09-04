---
name: recurring-loops
description: Turn a repeated marketing decision into a bounded, observable, interruptible loop: trigger and cadence, inputs and freshness, state and idempotency, decision rules, outputs, approval layers, limits, failure handling, dry run, monitoring, pause, and retirement, with a catalog of loop patterns across acquisition, paid, lifecycle, customer, partner, and revenue work. Use for scheduled reviews, campaign health, creative fatigue, content decay, churn watch, lead follow-up, and ranking alerts; not for a one-off task.
license: MIT
metadata:
  version: "2.0.0"
  author: MTEnt
---

# Recurring Loops

Automate a stable decision process, not unresolved strategy. A loop must be observable, bounded, interruptible, and safe under duplicate or partial execution.

If `.agents/marketing-context.md` exists, read it first; it is the truth file every skill in this hub shares, and its evidence states are constraints. Read [loop-system.md](references/loop-system.md) for qualification, the specification, state, cadence, approval layers, the catalog, orchestration, failure handling, dry run, and the loop report.

## Operating contract

1. Prove the task recurs and has stable inputs, decision rules, useful outputs, and a real owner.
2. Define state, freshness, idempotency, deduplication, concurrency, timeouts, retry limits, partial failure, reconciliation, and retention.
3. Separate read and analyze, draft, approve, mutate external state, and verify; bound spend, messages, records, runtime, fan-out, and data.
4. Define no-action, pause, escalation, stop, and retirement before activation.
5. Run a fixed-snapshot dry run and one credible failure path before scheduling, then recommendation-only mode before external mutation.

Do not schedule, send, publish, spend, or change live accounts without explicit authorization for that action and scope; fail closed when authority or state is unclear.

## Return

The loop specification, state design, approval layers, dry-run evidence, monitoring and loop report format, and pause, stop, and retirement rules.
