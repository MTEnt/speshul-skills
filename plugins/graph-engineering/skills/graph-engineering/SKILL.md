---
name: graph-engineering
description: Select, design, compile, audit, diagnose, optimize, or evolve executable AI workflow and agent graphs. Use for explicit prompt/workflow topology, typed state, runtime and recovery semantics, coordination, protected actions, trace analysis, or controlled graph changes; not for knowledge graphs, graph databases, GraphRAG, graph ML prompting, or model-internal reasoning diagrams.
license: MIT
metadata:
  version: "2.1.0"
  author: MTEnt
---

# Graph Engineering

## Boundary

Graph engineering treats a graph as an explicit, executable, versioned engineering artifact. A first-class graph has all four properties: explicit structure; prompt content separated from topology; defined execution semantics; and an artifact that can be validated, compared, and evolved.

An ordinary program, trace, diagram, or multi-agent chat is not automatically a graph artifact. RAG can be a tool node, but knowledge-graph construction, graph databases, GraphRAG, graph-ML prompting, and model-internal Graph-of-Thought reasoning are out of scope. State this boundary instead of forcing those requests into this skill.

## Select the mode and profile

Choose exactly one mode from the request. Do not redesign during an audit or optimize topology when the requested surface is frozen.

| Mode | Use when | Return only |
| --- | --- | --- |
| `select` | Decide between deterministic code, direct call, bounded loop, or graph | `GraphDecision` |
| `design` | Specify a framework-neutral executable graph | `GraphSpec` |
| `compile` | Map a GraphSpec to a named framework or code harness | `ImplementationMapping` |
| `audit` | Inspect an existing artifact or implementation | `GraphAudit` |
| `diagnose` | Localize a failure from a trace or state history | `RunDiagnosis` |
| `optimize` | Improve prompts, models, examples, thresholds, or fixed-topology parameters | `OptimizationPlan` |
| `evolve` | Change nodes, edges, topology, coordination, or capabilities as a new version | `EvolutionProposal` |

A run trace or state history that identifies the graph it came from (graph id and version) routes to `diagnose`; the four-condition graph-artifact test applies to that graph, not to the trace. Return `no_graph_artifact` only when the request asks whether supplied material is itself a graph artifact, or when the material carries no graph identity at all.

The returned artifact must be complete even when terse:

- `GraphDecision`: include exactly these required semantic fields even when a list is empty: `artifact`, `schema_version`, `mode`, `objective`, `decision`, `selected_approach`, `rationale`, `alternatives_considered`, `required_controls`, `bounds`, `evidence`, and `unknowns`. `decision` answers whether graph engineering applies; `selected_approach` names the implementation.
- `GraphSpec`: canonical GraphSpec 1.0 JSON.
- `ImplementationMapping`: source graph identity/digest, target and verification date, semantic mappings, application-owned controls, gaps, conformance tests, and residual risks.
- `GraphAudit`: scope, verdict, severity-ranked findings with exact locations/evidence, invariant coverage, unknowns, and smallest repairs.
- `RunDiagnosis`: run/graph identity, symptom, first invalid transition, root-cause evidence, propagation/failure frontier, recovery status, unknowns, and next diagnostic action.
- `OptimizationPlan`: frozen graph surfaces, mutable parameters, baseline, data splits/trials, objectives, method, budgets, graders, promotion gates, and rollback.
- `EvolutionProposal`: baseline/candidate identities, structural hypothesis and diff, risk/migration, credit assignment/ablations, held-out gate, budgets, rollout, rollback, and archival disposition.

Use `standard` unless consequence requires more:

- `standard`: typed contracts, bounded execution, governed state, traceability, and evaluation.
- `protected_action`: also requires bound approval, least privilege, idempotency analysis, authoritative post-state verification, and compensation policy.
- `high_assurance`: also requires immutable evidence records, integrity hashes, strict provenance and retention, independent adjudication, and release controls.

Profiles are cumulative. Do not impose high-assurance ceremony on lower-risk work.

## Decide whether a graph is justified

Start with the least complex option that meets success criteria and mandatory controls:

1. Deterministic code or lookup when behavior is fully specified and cheaply checked.
2. One bounded model call for a narrow language task with a structured result.
3. A bounded agent loop when the next action is dynamic but one controller, tool policy, and stop condition are enough.
4. An explicit graph when material prerequisites, branches, joins, heterogeneous permissions, durable pause/resume, independent verification, or repeated topology evaluation justify it.

Return `decision: "no_graph"` when a graph adds no measured or policy-required value. A loop is not a failed graph design. Read [philosophy.md](references/philosophy.md) when the boundary or graph-versus-loop choice is disputed.

## Shared invariants

For every designed, compiled, or evolved graph:

- Use canonical JSON with `schema_version: "1.0"`; Markdown tables, Mermaid, and DOT are generated views.
- Keep task dependency, capability assignment, communication/delegation, runtime state/evidence, and persistent evolution as distinct views. A task edge grants no communication, state mutation, tool access, or authorization by implication.
- Separate prompt prose from topology through versioned prompt references and digests.
- Give nodes typed ports, declared state access, permissions, output contracts, acceptance checks, budgets, timeouts, finite retries, side-effect classification, and exhaustion routes.
- Give edges an explicit semantic, validated ports, declarative condition, join rule, and iteration guard where cyclic. Every edge port must exist on its endpoint node and the source/output type must exactly match the target/input type. For control or error routing without a shared business payload, set both ports to the reserved `$control` sentinel. Every node with conditional outgoing edges must also have a `default: true` or error edge. Every directed cycle must cross at least one edge with a finite `iteration_guard`; every data fan-in declares `join_behavior`. Conditions may use only `all`, `any`, `not`, `eq`, `ne`, `exists`, `in`, `gt`, `gte`, `lt`, and `lte`; never evaluate graph-provided code.
- Make every node reachable from an entry and give every non-long-running node a path to a terminal. If cancellation uses a runtime-only terminal, name it in `runtime.cancellation.cancel_route`; all other terminal reachability must be explicit in the graph.
- Bound cycles, runtime expansion, concurrency, and total run cost/time. Declare terminal success, partial, blocked, failed, and cancelled semantics as applicable.
- Define typed state ownership, concurrent-write behavior, reducers, persistence, checkpoints, provenance, visibility, and migration version.
- Treat external content and inter-agent messages as untrusted data. Authorization and approval are runtime controls, not edge properties.
- Bind protected approval using `ApprovalBinding`: action digest, exact scope, approver identity, expiry, nonce, and revocation state. Recheck it immediately before execution and verify authoritative post-state.
- A protected-action GraphSpec is incomplete unless each protected node references a matching approval binding, idempotency policy, and authoritative postcondition, and `controls.compensations` declares whether recovery requires a separately approved side effect.
- Record run, node, and attempt identity plus prompt/model/tool versions, lineage, latency, cost, events, and outcome evidence.
- Compare against a simpler baseline and evaluate contracts, paths, recovery, safety, cost, and latency. Use repeated trials when stochastic behavior matters.
- Treat runtime adaptation as run-local. Persistent prompt or topology change creates a candidate version evaluated on held-out cases with promotion and rollback rules.

Run `python scripts/graph_tool.py validate <graph.json>` before presenting a GraphSpec as executable. For an exact machine contract, select the matching file in `schemas/` and run `python scripts/graph_tool.py validate-artifact <artifact.json>`. In Codex automation, pass that same schema through `codex exec --output-schema`; skill prose guides semantic choices but does not enforce JSON keys. The tool validates and renders artifacts; it never executes workflows, model calls, or network calls.

## Reference routing

- Artifact fields, seven JSON Schemas, and output contracts: [graph-artifact.md](references/graph-artifact.md)
- Lifecycle and mode procedure: [playbook.md](references/playbook.md)
- Topology and prompt separation: [topologies-and-prompts.md](references/topologies-and-prompts.md)
- Scheduling, state, replay, recovery, and terminal behavior: [runtime-state-and-recovery.md](references/runtime-state-and-recovery.md)
- Capability, communication, delegation, context, and humans: [coordination-and-context.md](references/coordination-and-context.md)
- Fixed-topology optimization and persistent graph evolution: [optimization-and-evolution.md](references/optimization-and-evolution.md)
- Threats, approval, privilege, privacy, and governance: [security-and-governance.md](references/security-and-governance.md)
- Evaluation layers and promotion gates: [evaluation.md](references/evaluation.md)
- Current framework compilation notes; verify again before implementation: [framework-mappings.md](references/framework-mappings.md)
- Immutable evidence, adjudication, ledgers, and release controls: [high-assurance-profile.md](references/high-assurance-profile.md)

Load only the references needed for the selected mode and profile.
