---
name: experiment-design
description: Design, size, implement, analyze, and govern controlled tests: A/B and multi-arm tests, holdouts, switchbacks, factorial and geo designs, with hypothesis records, sample and duration planning, guardrails, implementation QA, uncertainty reporting, and an experimentation backlog. Use for any decision between measurable alternatives; ships a sample-size script.
license: MIT
metadata:
  version: "2.0.0"
  author: MTEnt
---

# Experiment Design

Run an experiment only when exposure and outcomes can answer a decision and the organization can act on the result.

If `.agents/marketing-context.md` exists, read it first; it is the truth file every skill in this hub shares, and its evidence states are constraints. Read [experiment-system.md](references/experiment-system.md) for assessment, hypothesis, test types, sample and duration, metrics, variants, QA, analysis, the experiment record, and program operations. Use `scripts/sample_size.py` for equal-allocation planning estimates within its stated assumptions.

## Operating contract

1. Start from an observed problem and a falsifiable mechanism, not a preferred variant.
2. Choose the design according to the decision and constraints; label weaker inference when volume cannot support causal estimation.
3. Predefine population, assignment, exposure, primary metric, practical threshold, guardrails, sample method, duration, and decision rule.
4. Verify implementation and instrumentation before interpreting results.
5. Report uncertainty, deviations, data-quality problems, and commercial consequences.

Do not peek repeatedly and stop only when the favored result wins, or treat statistical significance as proof of mechanism or business value.

## Return

The experiment record: decision and evidence, hypothesis, arms and assignment, metrics and sample, implementation QA, results with uncertainty, deviations, the ship or iterate or stop decision, and follow-up.
