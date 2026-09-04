# Runtime, State, and Recovery

## Scheduler contract

Declare:

- node readiness: all required inputs, any incoming control, quorum, or explicit event;
- scheduler semantics: sequential, parallel superstep, queue, or event-driven;
- global and per-capability concurrency;
- fan-out and fan-in behavior;
- subgraph call/return mapping;
- cancellation polling points, in-flight policy, and an explicit `cancel_route` when cancellation has its own terminal;
- run deadline, cost/tool/model-call budgets, and expansion bounds;
- node states: `pending`, `ready`, `running`, `waiting`, `succeeded`, `failed`, `cancelled`, `skipped`;
- valid transitions and graph terminal reduction.

Do not assume framework defaults match GraphSpec. Compilation must record the mapping.

## State channels

Each channel declares type, source of truth, owner, allowed writers, reducer, concurrent-write policy, sensitivity, visibility, persistence, checkpoint policy, provenance, and migration version.

Use reducers only when associative/commutative behavior is defined or the runtime serializes writes. Reject silent last-write-wins. Branch-local scratch state should not leak into another branch's context unless the join contract projects it.

Keep conversation history, model context, run checkpoint, evidence record, and reusable memory distinct.

## Checkpoints, replay, and migration

A checkpoint records graph, prompt, model, tool, policy, state-schema, and migration versions plus completed side-effect identities. Resume only after compatibility and authorization checks.

Replay policy declares which nodes may be re-executed. Deterministic replay still needs pinned inputs. Model replay is a new attempt, not proof of reproducibility. Never replay an external effect unless idempotency scope remains valid or authoritative state proves no effect occurred.

State migration must be versioned, deterministic where possible, tested in both directions when rollback requires it, and rejected when required provenance is absent.

## Interrupt and resume

An interrupt declares checkpoint timing, durable resume token/identity, allowed resume node, expiry, revalidation steps, input schema, and cancellation route. Do not place a human interrupt after an unverified protected effect. Resume must not skip approval, policy, or freshness checks.

## Failure and recovery

Classify failures as contract, dependency, policy, timeout, budget, model/tool, state conflict, partial effect, or cancellation. Record the first invalid transition and the **failure frontier**: nodes/state that may be affected downstream.

Recovery options are bounded retry, targeted repair, alternate route, replan, resume, compensation, partial terminal, blocked terminal, or fail. Replanning changes the current run's bounded instantiated path; it does not silently promote a new persistent graph.

Compensation is a new side effect with its own authorization and outcome verification. It is not a database rollback promise.

## Terminal semantics

- `success`: all declared success criteria and outcome checks pass.
- `partial`: partial-success criteria pass and gaps are explicit.
- `blocked`: required external input/authority is unavailable.
- `failed`: criteria cannot be met within bounds.
- `cancelled`: cancellation policy completed, including any authorized reconciliation.

Node completion or a confident final message is not graph success.
