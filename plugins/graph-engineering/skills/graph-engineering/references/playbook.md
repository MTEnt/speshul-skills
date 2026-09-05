# Graph Engineering Lifecycle Playbook

Use this as a mode router, not as a requirement to perform every phase in one response.

## Lifecycle

`select -> specify -> validate -> compile -> execute -> observe -> diagnose -> optimize/evolve -> promote or roll back`

Execution belongs to the selected runtime, not `graph_tool.py`. Authorization to design or compile does not authorize running side effects.

## Select

1. Preserve the requested outcome, constraints, non-goals, consequence, and acceptable partial result.
2. Compare deterministic code, one model call, one bounded loop, and a graph.
3. Identify what explicit topology would control that the simpler option cannot.
4. Return only `GraphDecision`. A `no_graph` decision names the chosen alternative and its own bounds.

## Specify (`design`)

1. Select the assurance profile from consequence, not complexity.
2. Declare graph identity, success and partial-success criteria, entry points, terminals, budgets, representation, and topology binding.
3. Define typed node ports and state channels before prompts.
4. Add only edges with real data/control/error/interrupt/compensation meaning.
5. Define scheduler, joins, retries, cycles, expansion, cancellation, checkpoints, resume, and terminal behavior.
6. Add permissions, trust labels, approvals, idempotency, postconditions, and compensation where required.
7. Add observability, evaluation, and evolution policy.
8. Validate canonical JSON. Return only `GraphSpec`.

## Validate

Run structural and semantic checks before framework mapping:

```powershell
python scripts/graph_tool.py validate graph.json
python scripts/graph_tool.py validate-artifact graph.json
python scripts/graph_tool.py inspect graph.json
python scripts/graph_tool.py normalize graph.json --output graph.normalized.json
python scripts/graph_tool.py render graph.json --format mermaid --output graph.mmd
```

Validation proves conformance to declared contracts, not task quality, model reliability, or runtime correctness.

## Compile

1. Read the dated framework mapping and recheck current official documentation.
2. Map every GraphSpec semantic to a native primitive, adapter, or explicit application-owned mechanism.
3. Record gaps; never silently weaken a join, interrupt, approval, reducer, cancellation, or durability contract.
4. Produce code/config pointers and conformance tests. Return only `ImplementationMapping`.

## Audit

Inspect the artifact and, when provided, implementation evidence. Lead with the verdict. Report defects by severity with exact artifact paths or files. Separate verified defects from inference. Do not redesign unless requested. Return only `GraphAudit`.

## Observe and diagnose

Correlate run, node, attempt, prompt, model, tool, checkpoint, and state-version identifiers. Find the first contract violation or invalid state transition, then distinguish root cause, propagation, containment, recovery evidence, and unknowns. Do not infer success from a final message; check outcome evidence. Return only `RunDiagnosis`.

## Optimize

Freeze topology and permissions. Define the mutable prompt/model/example/threshold parameters, baseline, dataset split, repeated-trial policy, objective, budgets, and regression gates. Keep candidate outputs isolated. Return only `OptimizationPlan`.

## Evolve

Create a new candidate graph version. State the structural hypothesis, changed nodes/edges/capabilities, risk expansion, migration, held-out evaluation, ablations, promotion threshold, rollout, rollback, and archive status. Runtime adaptation alone is not evolution. Return only `EvolutionProposal`.

## Stop conditions

Stop design when the selected artifact is complete and validates. Stop diagnosis when the earliest supported failure and recovery disposition are identified or evidence is exhausted. Stop optimization/evolution when budgets or trial limits are reached, a candidate passes the promotion gate, or no candidate improves the baseline. Never convert repeated failure into an unbounded retry.

## Profile routing

- `standard`: use the core GraphSpec, runtime, evaluation, and security sections.
- `protected_action`: also read [security-and-governance.md](security-and-governance.md) and use the protected-action template.
- `high_assurance`: also read [high-assurance-profile.md](high-assurance-profile.md); its ledgers and release controls are conditional, not global defaults.
