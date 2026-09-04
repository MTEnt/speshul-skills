# Performance, resource bounds, rollout, and recovery

## Measure performance and bound growth when risk triggers it

Apply this section when performance is contractual or the change affects a hot path, large or untrusted inputs, persistent growth, external I/O, queues, caches, retries, batching, fan-out, or concurrency. Do not impose it on an unrelated low-risk edit.

- Define the representative workload, current baseline, relevant metric, and accepted budget before optimizing. If a performance claim cannot be measured in the available environment, label it unverified.
- Do not claim that a change is faster, more efficient, or scalable without repeatable before-and-after evidence under a representative workload.
- Do not add caching, concurrency, pooling, batching, lower-level code, or architectural complexity without an explicit requirement or an evidenced bottleneck.
- Measure the dimensions that can decide the acceptance criterion: latency distribution, throughput, CPU, memory and allocations, I/O, query count, storage growth, or cost. Do not hide tail behavior behind an irrelevant average or rely on a microbenchmark that omits the real bottleneck.
- Bound queues, caches, retries, batch sizes, fan-out, concurrency, retained temporary state, and other growth. Define backpressure, eviction, overflow, timeout, cancellation, and degradation behavior where applicable.
- Test expected limits and credible beyond-limit behavior while preserving correctness, contract behavior, and data integrity.

## Plan safe rollout and recovery when deployment is in scope

Apply this section only when a change can reach a shared or deployed environment, infrastructure, configuration, persistent data, external state, or overlapping software versions.

- Define the blast radius, rollout stages proportional to risk, health signals, observation window, stop criteria, and authorized recovery actions.
- Choose rollback, traffic reversal, feature disablement, restoration or reconciliation, or fix-forward based on state safety. Do not assume a code revert reverses schema, data, configuration, or external side effects.
- Preserve old-and-new compatibility until mixed versions and old persisted data can no longer occur. Test mixed-version behavior when the rollout can create it.
- For high-risk changes, verify the recovery path before production. If reversal is impossible, state that before mutation and use smaller stages, checkpoints, backups, reconciliation, or a tested fix-forward path.
- Treat an automatic halt or rollback as authorized only when an accepted plan or established policy defines its trigger and scope. It is containment, not proof that the underlying defect is corrected.
- Remove temporary flags, compatibility paths, and migration machinery after their documented exit conditions are met.
