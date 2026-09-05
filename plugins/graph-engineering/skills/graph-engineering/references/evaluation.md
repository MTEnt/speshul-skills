# Graph Evaluation

Evaluation covers the artifact, runtime, traces, and real outcome. A diagram review alone is insufficient.

## Layers

| Layer | Examples |
| --- | --- |
| Static | Schema, reachability, bounded cycles/expansion/retries, ports, permissions, state writers |
| Node | Input/output contract, tool policy, acceptance, timeout, refusal/error behavior |
| Transition | Predicate truth table, default route, error/interrupt/compensation semantics |
| Path | Entry-terminal coverage, branches, cycles, exhaustion, partial and cancellation paths |
| State | Reducers, concurrency, checkpoints, migration, provenance, visibility |
| Trace | Valid node transitions, versions, lineage, attempts, cost/latency, failure localization |
| Outcome | Authoritative task success and partial-success checks |
| Recovery | Retry, replay, resume, replan, cancellation, partial effect, compensation |
| Safety | Injection, tool/permission boundaries, approval drift, secrets, privacy, cascading failure |
| Performance | End-to-end latency, cost, calls, queue/concurrency saturation, budget enforcement |
| Structural ablation | Remove/change a node or edge to test whether complexity earns its cost |

## Evaluation contract

Declare simpler baseline; datasets and versions; capability versus regression splits; held-out promotion set; repeated-trial policy; code-, model-, and human graders; grader calibration; path and contract coverage; performance budgets; mandatory safety gates; promotion threshold; and rollback trigger.

Prefer deterministic graders for deterministic outcomes. Model graders need explicit rubrics, an unknown/abstain outcome, and calibration against human judgment where material. Evaluate both transcripts and authoritative end state; a plausible message is not proof an action occurred.

For stochastic components, report the per-task trial policy and measure the statistic that matches the product need. One successful trial is not consistency. Keep environment state isolated across trials.

## Behavior suite for this skill

Cover selection, design, compile, audit, diagnose, optimize, and evolve. Include positive and negative routing:

- trivial direct work returns `no_graph`;
- parallel research defines a join and qualified independent verification;
- repair loop and unknown expansion are bounded;
- audit does not redesign;
- diagnosis uses trace evidence and localizes propagation;
- optimization freezes topology;
- evolution uses a held-out gate and rollback;
- protected action uses approval binding and post-state verification;
- GraphRAG is out of scope;
- informal agent conversation is not claimed as a first-class graph;
- framework mapping preserves semantics and records gaps.

Grade correct mode/decision, artifact completeness, bounds, state, evidence, security, and absence of unnecessary ceremony.

## References

- Anthropic, [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), accessed 2026-08-27.
- NIST, [AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework).
