# GraphSpec 1.0 and Output Artifacts

JSON is normative. Tables, Mermaid, DOT, and framework code are views or mappings.

## Machine schemas

Exact output shape is enforced outside prompt prose. Use the schema matching the selected mode:

| Artifact | Schema |
| --- | --- |
| `GraphDecision` | [`graph-decision.schema.json`](../schemas/graph-decision.schema.json) |
| `GraphSpec` | [`graph-spec.schema.json`](../schemas/graph-spec.schema.json) |
| `ImplementationMapping` | [`implementation-mapping.schema.json`](../schemas/implementation-mapping.schema.json) |
| `GraphAudit` | [`graph-audit.schema.json`](../schemas/graph-audit.schema.json) |
| `RunDiagnosis` | [`run-diagnosis.schema.json`](../schemas/run-diagnosis.schema.json) |
| `OptimizationPlan` | [`optimization-plan.schema.json`](../schemas/optimization-plan.schema.json) |
| `EvolutionProposal` | [`evolution-proposal.schema.json`](../schemas/evolution-proposal.schema.json) |

Validate a saved artifact with `python scripts/graph_tool.py validate-artifact artifact.json`. For Codex automation, pass the schema to `codex exec --output-schema`. An unconstrained fresh-session test evaluates semantic mode/decision behavior; a schema-constrained test evaluates machine-contract conformance. Do not conflate the two.

## GraphSpec 1.0

Top-level sections:

| Section | Required content |
| --- | --- |
| `schema_version` | Exactly `1.0` |
| `graph` | `id`, `version`, objective, success/partial criteria, constraints, non-goals, risk profile, assurance profile, entries, terminals, budgets, representation, topology binding |
| `nodes` | Typed executable contracts |
| `edges` | Typed transitions and routing |
| `prompts` | External prompt references, versions, digests, variables, output contracts, optimizer surfaces |
| `context_policies` | Trusted/untrusted projections and limits |
| `state` | Typed channels, ownership/reducers, persistence, checkpoints, provenance, migrations |
| `runtime` | Scheduler, readiness, concurrency, expansion, subgraphs, cancellation, interrupts, resume, transitions |
| `controls` | Authorization, approvals, tools/network/secrets, trust labels, idempotency, postconditions, compensation |
| `observability` | Event schema, identities, versions, metrics, lineage, evidence |
| `evaluation` | Baseline, data, trials, graders, coverage, recovery/safety/performance, promotion |
| `evolution` | Mutable surfaces, versions, credit assignment, held-out gate, ablations, rollout/rollback/archive |

### Node contract

Each node declares unique `id`; `execution_kind` (`deterministic`, `model`, `agent`, `tool`, `human`, `subgraph`); semantic role; typed input/output `ports`; prompt/model/tool/capability refs; context policy; state reads/writes; permissions; timeout; finite retry policy; side-effect class; outcomes; structured output schema reference; and acceptance conditions.

Ports use `{ "name": "result", "type": "ResultV1", "required": true }`. A data edge must connect compatible types. Control-only edges use the reserved `$control` port at both ends.

### Edge contract

Each edge declares `id`, `source`, `source_port`, `target`, `target_port`, and `semantic` (`control`, `data`, `error`, `interrupt`, `compensation`). Endpoint types match exactly; control or error routing without a shared payload uses `$control` at both ends. Conditional edges use the constrained predicate language and a routed outcome. Fan-in declares `join_behavior`; every directed cycle crosses at least one edge whose `iteration_guard` has finite `max_iterations` and an exit condition.

Predicates are JSON expression trees using only:

```json
{"all": [{"exists": "state.result"}, {"gte": ["state.score", 0.8]}]}
```

Allowed operators: `all`, `any`, `not`, `eq`, `ne`, `exists`, `in`, `gt`, `gte`, `lt`, `lte`. Values are data. Implementations must not evaluate source text as code.

### ApprovalBinding

Provider-neutral protected approval requires:

```json
{
  "id": "deploy-approval",
  "action_digest": "sha256:<digest>",
  "scope": {"operation": "deploy", "target": "service-a", "environment": "production"},
  "approver_identity": "identity-ref",
  "expires_at": "RFC3339 timestamp",
  "nonce": "single-use value",
  "revoked": false
}
```

The runtime must validate the digest, full scope, identity policy, expiry, nonce reuse, and revocation immediately before execution. The graph definition references the binding contract; a run record carries the actual signed/attested approval.

## Conditional output contracts

Return only the selected artifact, with facts/evidence distinguished from inference.

### GraphDecision

`artifact`, `schema_version`, `mode`, exact objective, graph decision (`no_graph`, `graph`, `human_led`, `out_of_scope`, `no_graph_artifact`), selected approach (`deterministic_code`, `direct_call`, `bounded_loop`, `graph`, `human_led`, `not_applicable`), rationale, simpler alternatives, required controls, bounds, evidence, unknowns.

### GraphSpec

The canonical JSON contract above. Do not wrap it in a second prose design unless the user asks for an explanation.

### ImplementationMapping

Graph ID/version/digest, target framework/version/date checked, semantic mapping table, adapters/application-owned controls, unsupported gaps, code/config locations, conformance tests, residual risks.

### GraphAudit

Artifact identity, scope, verdict, findings by severity with exact locations/evidence, invariant coverage, unknowns, and smallest repairs. No unsolicited redesign.

### RunDiagnosis

Run and graph identity, observed symptom, first invalid transition/contract violation, root-cause evidence, propagation path, failure frontier, containment/recovery status, unknowns, and next diagnostic action.

### OptimizationPlan

Frozen topology/version, mutable parameters, baseline, data splits, trials, objective and constraints, optimizer/search method, candidate isolation, graders, budgets, regression/promotion gates, rollback.

### EvolutionProposal

Baseline/candidate versions, structural hypothesis, exact graph diff, risk/permission expansion, state migration, credit assignment and ablations, held-out evaluation, budgets, promotion, rollout, rollback, archival disposition.
