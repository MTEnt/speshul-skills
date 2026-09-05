# Optimization and Evolution

## Fixed-topology optimization

Use `optimize` when nodes, edges, state schema, permissions, and assurance profile are frozen. Mutable surfaces may include prompt instructions/examples, model choice, decoding parameters, router thresholds, retrieval parameters, or other declared node/edge parameters.

An `OptimizationPlan` defines:

- immutable graph version and digest;
- mutable parameters and search space;
- baseline and candidate isolation;
- training/development/held-out splits;
- repeated trials and randomization policy;
- task, contract, safety, latency, and cost objectives;
- optimizer/search method and total budgets;
- regression, promotion, and rollback gates.

Do not optimize on the held-out promotion set. Preserve candidate failures and optimizer provenance. A better aggregate score cannot waive a mandatory safety or contract gate.

Prompt optimizers such as DSPy-style methods, gradient/search methods for fixed graphs, or manual iteration are implementation choices; GraphSpec records the allowed surface and evaluation contract.

## Persistent evolution

Use `evolve` when changing node/edge topology, coordination, state, capability, permission, or assurance. Evolution always creates a candidate graph version.

The proposal includes:

- structural hypothesis and expected mechanism;
- normalized semantic diff from baseline;
- state/checkpoint migration and compatibility;
- permission and risk expansion;
- credit-assignment method;
- structural ablations that isolate the claimed benefit;
- held-out evaluation, budgets, and promotion criteria;
- staged rollout, rollback trigger, and archive status.

Topology search systems such as GPTSwarm, AFlow, and ADAS demonstrate research approaches, not production guarantees. Treat generated architectures as untrusted candidates subject to the same validation and held-out gates as human proposals.

## Runtime adaptation versus evolution

Runtime routing, replanning, work-queue expansion, and agent-selected actions are run-local and bounded by the active graph version. They become persistent evolution only through a recorded candidate, evaluation, approval, promotion, and rollback path.

## Promotion

Promote only when mandatory gates pass and improvement exceeds the declared threshold with the required uncertainty/repeated-trial policy. Store the baseline, candidate, data version, evaluator versions, results, decision, and rollback pointer. Archive rejected candidates with disposition; do not let them silently re-enter production.

## References

- Zhuge et al., [GPTSwarm: Language Agents as Optimizable Graphs](https://arxiv.org/abs/2402.16823).
- Zhang et al., [AFlow: Automating Agentic Workflow Generation](https://arxiv.org/abs/2410.10762).
- Hu et al., [Automated Design of Agentic Systems](https://arxiv.org/abs/2408.08435).
- DSPy, [Optimizers](https://github.com/stanfordnlp/dspy/blob/main/docs/docs/learn/optimization/optimizers.md).
