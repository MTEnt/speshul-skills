---
name: marketing-automation
description: Turn a repeated marketing task into a bounded recurring loop with triggers, state, inputs, decisions, outputs, approvals, metrics, exception handling, and stop conditions. Use for scheduled reviews, content refresh, campaign monitoring, churn watch, lead follow-up, ad-fatigue checks, ranking alerts, or other recurring marketing operations; not for a one-off task.
---

# Marketing Automation

Automate a stable decision process, not ambiguity. A loop must be observable, bounded, reversible where possible, and interruptible by a human.

If `.agents/marketing-context.md` exists, read it before asking foundational product, audience, proof, or voice questions. Preserve its evidence states and surface stale or contradictory entries.

Use `$marketing-loops` for the canonical loop design, state, scheduling, approval, catalog, failure-handling, dry-run, and retirement workflow.

## Loop contract

1. Prove that the task recurs and has a stable trigger, inputs, decision rule, and useful output.
2. Define cadence or event trigger from the rate of change and cost of delay, not habit.
3. Specify state ownership, idempotency, deduplication, concurrency, retries, timeouts, and partial-failure recovery.
4. Separate read-only analysis, draft production, approval, and external mutation.
5. Bound spend, messages, records, runtime, fan-out, and retained state.
6. Record decisions, evidence, outputs, exceptions, and next scheduled state.
7. Define pause, stop, escalation, and retirement conditions before activation.
8. Test one dry run and one credible failure path before scheduling.

Do not schedule live work, send messages, publish, or change campaigns without explicit authorization for that action and scope.
