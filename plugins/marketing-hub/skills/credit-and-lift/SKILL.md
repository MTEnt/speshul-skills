---
name: credit-and-lift
description: Choose, interpret, implement, and reconcile how marketing credit is assigned and whether it caused anything: first and last touch, multi-touch, self-reported source, platform reporting, first-party capture, cohort payback, incrementality tests, and media-mix methods, with a table of what each system is designed to answer. Use when dashboards disagree or the business needs to know what drives revenue; use tracking-plan to fix the underlying event data.
license: MIT
metadata:
  version: "2.0.0"
  author: MTEnt
---

# Credit and Lift

Attribution allocates credit under a model; it does not automatically establish causal lift.

If `.agents/marketing-context.md` exists, read it first; it is the truth file every skill in this hub shares, and its evidence states are constraints. Read [attribution-system.md](references/attribution-system.md) for interpretation modes, business-model fit, first-party capture, report reconciliation, untracked influence, and the readout.

## Operating contract

1. Define the decision, conversion or revenue outcome, customer journey, systems, identity, consent, sales cycle, and source of truth.
2. Document each model's lookback, event time, identity, click and view rules, deduplication, offline handling, latency, and bias.
3. Preserve disagreements when systems answer different questions.
4. Use experiments or stronger causal methods when the question is incremental effect.
5. Recommend an operating view plus limitations and next validation.

Do not add credited conversions across incompatible systems or present a fractional model as observed customer reasoning.

## Return

The attribution readout: decision and source of truth, journey and identity model, what each system reports and why, model comparison, first-party implementation or repair, incrementality evidence, confidence and blind spots, operating recommendation, and next validation.
