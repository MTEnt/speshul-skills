---
name: attribution
description: Choose, interpret, implement, and reconcile marketing attribution across first touch, last touch, multi-touch, self-reported source, platform reporting, first-party tracking, incrementality, cohort economics, and media-mix methods. Use when dashboards disagree or the business needs to understand which marketing contributes to revenue.
---

# Attribution

Attribution allocates credit under a model; it does not automatically establish causal lift.

If `.agents/marketing-context.md` exists, read it first. Read [attribution-system.md](references/attribution-system.md) for interpretation, first-party capture, business-model choices, reconciliation, and output.

## Operating contract

1. Define the decision, conversion or revenue outcome, customer journey, systems, identity, consent, sales cycle, and source of truth.
2. Document each model's lookback, event time, identity, click and view rules, deduplication, offline handling, latency, and bias.
3. Preserve disagreements when systems answer different questions.
4. Use experiments or stronger causal methods when the question is incremental effect.
5. Recommend an operating view plus limitations and next validation.

Do not add credited conversions across incompatible systems or present a fractional model as observed customer reasoning.
