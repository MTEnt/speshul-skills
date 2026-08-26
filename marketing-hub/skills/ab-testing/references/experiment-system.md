# Experiment system

## Initial assessment

Define decision owner, observation, evidence, affected users, materiality, reversible and irreversible risks, expected traffic or units, outcome latency, contamination, seasonality, and whether a test can change the decision.

Use qualitative evaluation or a monitored rollout when volume cannot support causal estimation. Label the weaker inference.

## Hypothesis

```text
Observation and source:
Eligible population:
Change:
Expected behavior and direction:
Mechanism:
Primary outcome:
Practical effect worth acting on:
Guardrails:
Competing explanation:
```

## Test types

- user- or account-randomized A/B;
- cluster randomization for teams, regions, or accounts;
- holdout for campaigns, lifecycle programs, or product changes;
- switchback for time-dependent marketplaces or operations;
- factorial design for interacting factors when sample and analysis support it;
- multi-arm test for several meaningful alternatives;
- sequential design only with a declared valid method;
- geo or matched-market experiment when individual assignment is unavailable;
- pre/post or interrupted time series when no stronger design is feasible.

## Sample and duration

Specify baseline, variance or rate, minimum detectable practical effect, power, error tolerance, allocation, design effect, attrition, multiple comparisons, and expected eligible volume. Show assumptions and sensitivity. Do not select a large effect merely to obtain a convenient sample.

Use [sample_size.py](../scripts/sample_size.py) for an equal-allocation planning estimate when binary or continuous outcomes fit its assumptions. The result is not valid for clustered assignment, repeated measures, survival outcomes, ratio metrics, sequential tests, covariate adjustment, or unusual estimators without an appropriate method.

```text
python scripts/sample_size.py proportions --baseline 0.10 --mde 0.02 --power 0.80 --alpha 0.05
python scripts/sample_size.py means --stddev 12 --mde 3 --power 0.90 --alpha 0.05
```

Set minimum and maximum duration from sample need, weekly cycles, novelty, outcome delay, seasonality, and operational risk. Duration alone does not make a test valid.

## Metrics

Use one primary decision metric, diagnostic secondary measures, and harm or quality guardrails. Define numerator, denominator, eligible population, identity, time window, source, latency, deduplication, and owner. Avoid composite metrics whose weights cannot be justified.

## Variants and allocation

Change one interpretable mechanism when learning is the goal. Specify exact copy, interface, logic, audience, destination, and fallback. Use equal allocation by default for learning unless risk, economics, or adaptive design justifies another split.

## Implementation QA

Verify stable mutually exclusive assignment, correct exposure time, intended difference, identity behavior, bots and staff, duplicate events, sample-ratio mismatch, cross-device effects, simultaneous-test conflict, privacy, loading and error states, rollback, and logging.

## Analysis

Report sample, exposure, duration, data quality, primary estimate, uncertainty interval, practical threshold, guardrails, predefined segments, deviations, and decision. Examine novelty, carryover, interference, attrition, missing data, multiple comparisons, instrumentation changes, and stopping behavior.

## Experiment record

```markdown
# Experiment record
## Decision and evidence
## Hypothesis and mechanism
## Control, treatment, population, and assignment
## Metrics, sample, duration, and stop rule
## Implementation and QA
## Results and uncertainty
## Deviations and limitations
## Ship, iterate, stop, rerun, or investigate
## Follow-up and monitoring
```

## Program operations

Maintain an evidence-backed backlog, decision owner, review cadence, collision map, implementation capacity, QA ownership, analysis standard, and learning repository. Prioritize decision value and evidence, not experiment count. Retire low-value ideas and repeated cosmetic variants.
