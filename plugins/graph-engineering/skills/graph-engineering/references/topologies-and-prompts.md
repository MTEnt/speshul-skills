# Topologies and Prompt Contracts

Choose topology from dependency and control needs, not role names.

| Pattern | Use when | Required guard |
| --- | --- | --- |
| Chain | Fixed ordered dependencies | Failure and partial-result terminal |
| Router | Distinct validated input classes | Exhaustive routes plus default/failure |
| Fan-out/fan-in | Branches are genuinely separable | Concurrency bound and deterministic join/reducer |
| Evaluator-repair | Acceptance criterion is inspectable | Targeted repair, attempt/deadline cap, escalation |
| Planner-executor | Work plan must be produced before bounded execution | Plan schema, capability allowlist, replan limit |
| Handoff | Active responsibility changes | Handoff schema, context filter, allowed recipients |
| Supervisor | One controller dispatches specialists | Finite action set, delegation depth, stop rule |
| Work queue | Runtime data determines item count | Item/schema validation, queue and worker bounds |
| Event-driven | External events activate work | Deduplication, ordering, idempotency, late-event policy |
| Subgraph | Reusable contract deserves its own lifecycle | Versioned boundary and mapped terminals |
| Human-gated | Judgment or authorization must pause execution | Durable interrupt, exact resume and expiry rules |
| Hybrid | Different regions need different semantics | Explicit boundary; do not hide a loop inside an unbounded node |

## Prompt separation

Topology references prompt contracts; it does not embed mutable prompt prose. A prompt contract contains:

- stable ID, version, digest, and location;
- purpose and supported node IDs;
- variables with types, trust labels, and required status;
- context construction policy and size/freshness limits;
- structured output schema and refusal/error outcomes;
- model constraints when required;
- examples and their provenance;
- allowed optimizer surfaces (`instructions`, `examples`, `model`, `temperature`, or none);
- tests and compatibility range.

Changing prompt content without changing topology is an optimization candidate. Changing required variables or output schema may be breaking and must be classified by `graph_tool diff`.

## Routing conditions

Keep conditions declarative and inspectable. Reference validated state or a routed outcome; never embed Python, JavaScript, shell, SQL, template expressions, or natural-language instructions for execution.

Use a default edge for unknown classifications. Treat malformed router output as an explicit error route, not as a guessed branch.

## Cycles

A cycle is valid only when every strongly connected component has:

- a finite graph/run iteration bound;
- at least one satisfiable exit route;
- a deadline or budget bound;
- a route when the limit is reached;
- state that distinguishes attempts;
- no unsafe implicit retry of non-idempotent effects.

## Dynamic topology

Runtime expansion must validate generated work items against a schema and cap nodes, edges, depth, queue length, concurrency, and total budget. A model may propose work items; deterministic runtime policy accepts, rejects, or truncates them. Generated topology gains no undeclared permission.
