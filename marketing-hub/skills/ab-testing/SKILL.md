---
name: ab-testing
description: Design, implement, analyze, document, and govern A/B tests, split tests, multivariate tests, holdouts, and growth experimentation programs. Use for hypotheses, variants, sample size, test duration, statistical uncertainty, experiment backlogs, or decisions between measurable alternatives.
---

# Ab Testing

Run an experiment only when exposure and outcomes can answer a decision and the organization can act on the result.

If `.agents/marketing-context.md` exists, read it first. Read [experiment-system.md](references/experiment-system.md) for hypotheses, designs, sample planning, implementation, analysis, and program operations.

## Operating contract

1. Start from an observed problem and a falsifiable mechanism, not a preferred variant.
2. Choose randomized experiment, holdout, switchback, factorial design, monitored rollout, qualitative test, or observational comparison according to the decision and constraints.
3. Predefine population, assignment, exposure, primary metric, practical threshold, guardrails, sample method, duration, and decision rule.
4. Verify implementation and instrumentation before interpreting results.
5. Report uncertainty, deviations, data-quality problems, and commercial consequences.

Do not repeatedly peek and stop only when the favored result wins, or treat statistical significance as proof of mechanism or business value.
