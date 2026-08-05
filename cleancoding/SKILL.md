---
name: cleancoding
description: Enforce evidence-backed, maintainable engineering for software implementation, debugging, refactoring, review, and release-sensitive changes. Use when changing code or configuration; defining acceptance criteria; investigating recurring failures; protecting contracts, trust boundaries, stateful behavior, error integrity, or authoritative documentation; assessing performance, resource growth, or deployment recovery; controlling coupling; removing duplication; simplifying design; or avoiding speculative functionality. Select the correct task workflow, track repeated corrective loops, and apply DRY, KISS, and YAGNI.
---

# Clean Coding

## Apply the operating contract

- Protect correctness, data integrity, security, accepted contracts, and explicit user requirements before applying style heuristics.
- Select the workflow that matches the task. Do not force bug-fixing language onto features, refactors, or reviews.
- For a defect, fix the verified cause in the layer that owns the violated behavior or invariant.
- Do not implement a workaround, band-aid, symptom suppression, or temporary mitigation as the completed solution.
- Do not hide failures with arbitrary retries or delays, swallowed exceptions, hard-coded special cases, duplicated branches, disabled tests, weakened types, ignored lint rules, or bypassed security checks.
- Add fallback behavior only when the accepted contract requires it and the fallback is bounded, observable, and tested. Do not add a fallback merely to make a failure disappear.
- Treat a retry as legitimate only when evidence identifies a transient failure mode and the operation has verified bounds and safe/idempotent behavior. Reconcile the outcome of any state-changing attempt before retrying it.
- Keep work scoped to the current requirement while completing everything needed for correctness, safety, and maintainability.
- Verify behavior with evidence. Do not call a change complete because the code looks plausible.

## Select the workflow and define the acceptance contract

Before editing, classify the task as a defect or incident, feature, refactor, review, or an explicit combination. Write a proportional acceptance contract containing:

- The required observable behavior
- The current baseline or exact failure evidence when a failure exists
- Relevant edge cases and failure cases
- Constraints, preserved behavior, and non-goals
- Affected observable contracts and known consumers
- Relevant trust boundaries, state risks, resource limits, documentation, and deployment constraints
- The checks that will prove completion

Keep this contract brief for a mechanical low-risk change. Ask for direction when a semantic ambiguity would materially change the result.

Apply the matching workflow:

- **Defect or incident:** Reproduce or directly observe the failure, use the root-cause workflow, and enforce the loop limit.
- **Feature:** Implement the acceptance contract without inventing a root cause. Apply the loop limit only when corrective attempts repeatedly fail the same acceptance criterion.
- **Refactor:** Preserve observable behavior. Establish a passing behavioral baseline, make small transformations, and re-run the baseline after each meaningful step.
- **Review:** Compare the artifact with its requirements, contracts, and verified behavior. Report evidence and uncertainty; do not mutate it unless the user also requests changes.
- **Mixed task:** Separate behavior changes, defect correction, and refactoring into explicit phases with their own checks.

## Fix the root cause for defects

1. State the expected behavior, actual behavior, and exact failure evidence.
2. Reproduce the problem or establish a reliable failing check. If reproduction is impossible, say what is missing and do not invent a cause.
3. Trace the relevant path through inputs, state, code, configuration, dependencies, and runtime behavior.
4. State a falsifiable root-cause hypothesis and the evidence supporting it.
5. Test the hypothesis with the smallest safe diagnostic that can distinguish it from alternatives.
6. Change the causal defect at its owning boundary. Remove obsolete compensating logic made unnecessary by the correction.
7. Re-run the original failure check, relevant regression tests, and nearby static or runtime checks.

Treat a cause as verified only when the evidence connects it to the failure and the correction removes the failure without a symptom-specific bypass. If the evidence supports only a hypothesis, label it as unverified and continue investigating within the loop limit.

Identify multiple contributing causes when the evidence shows them rather than forcing one simplistic cause.

Distinguish an external cause from a defect in owned resilience behavior:

- If an external dependency behaves according to its contract but the owned system fails to handle a documented failure mode, missing timeout, retry, idempotency, or degradation behavior may be the owned root cause. Implement it only when the acceptance contract requires it, and keep it bounded, observable, and tested.
- If the verified cause is inaccessible or outside the authorized scope and the owned contract does not require handling it, report the causal evidence and ask for direction. Do not create a local bypass and call it a fix.

### Handle emergencies without disguising mitigation as a fix

If an active incident threatens data, security, availability, or uncontrolled cost, first use only a containment or recovery action whose trigger, scope, and authority are already defined in the accepted contract or an established operational policy. Otherwise preserve evidence and ask the human whether to authorize temporary containment. Do not invent an ad hoc containment action or present containment as the final correction.

When containment is pre-authorized or the human authorizes it:

- Label it `TEMPORARY MITIGATION`.
- Record its scope, risk, rollback condition, and removal trigger.
- Keep the root-cause correction as unresolved work.
- Do not claim the underlying problem is fixed unless the cause is corrected and verified or the human explicitly changes the task scope.

## Enforce the three-loop limit

Define one loop as a completed corrective cycle on the same unresolved acceptance criterion:

`hypothesis -> corrective action -> verification -> acceptance criterion remains unmet`

Do not count a new read-only observation whose purpose is to gather missing evidence. Count a diagnostic cycle when it repeats a prior check, returns to the same blocked state without materially narrowing the cause, or substitutes for a corrective attempt.

Treat failures as the same problem while the same acceptance criterion remains unmet. Changing the command, tool, wording, file, process, or agent does not create a new problem by itself.

Maintain a loop log from the first failed cycle:

- Loop number
- Hypothesis tested
- Action or diagnostic performed
- Evidence obtained
- Outcome
- Why the problem remains unresolved

After three unsuccessful loops, stop before beginning a fourth loop on that problem. Red-flag the repeated pattern, stop further mutations and repeated executions on the affected track, and wait for human direction. Continue unrelated work only when it cannot alter or conceal the blocked problem.

Use this handoff format:

```text
RED FLAG - REPEATED-PROBLEM LOOP LIMIT REACHED
Loop count: 3 unsuccessful cycles; loop 4 was not started.
Problem: <unmet acceptance criterion and exact failure>
Attempts: <three hypotheses, actions, and outcomes>
Why the loop is occurring: <evidence-backed mechanism, or clearly labeled unknown>
Current evidence: <logs, tests, traces, or state>
Decision needed: <specific human choice, access, information, or proposed direction>
```

Do not reset the count because an attempt uses a different surface technique. Reset it only after evidence proves that the underlying state or causal condition materially changed and the new failure is distinct. After human direction, continue the existing count unless the direction changes the causal track or scope.

## Protect contracts and invariants

- Inventory affected observable contracts before changing behavior: public APIs, data and database schemas, serialized formats, events, configuration and environment inputs, machine-consumed CLI output, error behavior, side effects, and known consumers.
- Preserve compatibility unless the accepted scope explicitly changes the contract.
- For an approved breaking change, define versioning or deprecation, consumer and data migration, verification, and rollback or fix-forward behavior.
- Test old, new, and mixed-version states when staged deployment or persisted data makes them possible.
- Keep each invariant authoritative at its owning boundary. Do not scatter conflicting validation or transition rules across callers.
- Do not call a locally correct change complete when it silently breaks an observable consumer contract.

## Validate trust boundaries and preserve error integrity

- Validate data when it enters from a less-trusted source, crosses an ownership boundary, or is decoded under a changed contract. Validate before state changes, code execution, path construction, queries, or other dangerous use.
- Validate both structure and business meaning when relevant: types, required fields, allowed values, size and range limits, relationships between fields, and owned invariants.
- Keep trusted-side validation authoritative. Treat browser or other client-side validation as user experience, not as the security boundary.
- Keep each validation rule at the boundary that owns the rule. Do not scatter copies across callers, and do not mistake input validation for authorization, parameterized queries, contextual output encoding, or other required controls.
- Catch an error only to recover, compensate or clean up, translate it at a contract boundary, or add actionable context. Otherwise let it propagate to the accountable handler.
- Preserve the original cause and diagnostic chain when translating or rethrowing. Do not replace a useful failure with a vague exception, success value, empty result, or silent log-only path.
- Expose stable, contract-appropriate failures without secrets, stack traces, internal paths, queries, or unnecessary implementation detail.
- Record enough sanitized context at the accountable boundary to investigate the failure. Exclude credentials, tokens, secrets, and sensitive data; neutralize attacker-controlled log fields; avoid duplicate logging at every layer.

## Treat tests as behavior evidence

- Choose the narrowest test that proves the accepted behavior, then add integration or contract coverage when the behavior crosses a real boundary.
- For a defect, add or update a regression test that fails for the pre-fix behavior and passes after the correction when practicable.
- Test observable behavior and relevant edge and failure paths. Avoid assertions coupled only to implementation details unless that detail is itself contractual.
- Verify that a test would fail if the protected behavior broke. A passing test that cannot detect the defect is not evidence.
- Keep tests deterministic, readable, and actionable enough to identify what behavior failed.
- Use coverage to locate untested risk, not as proof of correctness or a universal completion score.

## Make state and side effects safe

- Identify every state-changing operation and external side effect affected by the change.
- Define the atomic unit, preconditions, postconditions, and invariants for each mutation.
- Define duplicate-request, ordering, concurrency, retry, cancellation, and partial-failure behavior when relevant.
- Ensure failure and cancellation restore a known valid state or leave enough durable evidence to reconcile it safely.
- Ensure resources are released on every exit path.
- Test interruption, duplicate delivery, concurrent execution, and partial failure when the risk exists.

## Keep documentation authoritative

- Update affected API or reference documentation, source comments, configuration examples, setup and runbook instructions, and migration notes in the same change as the behavior they describe.
- Remove false or obsolete material, or explicitly mark it as superseded when history must be retained. Do not leave contradictory instructions in place.
- Prefer names, types, schemas, and tests for facts they can express. Use comments for non-obvious intent, constraints, trade-offs, and safety reasoning rather than narrating mechanics. Remove commented-out code.
- Keep each fact in one authoritative location and link to it instead of copying it. Verify changed commands and examples when practicable.
- Create or update a decision record only for a durable, consequential choice whose context and trade-offs would otherwise be lost. Follow the project's convention, keep the record short, and supersede prior decisions explicitly rather than silently rewriting history.

## Optimize for change locality

- Keep code that changes for the same reason together and let unrelated responsibilities change independently.
- Make required collaborators and configuration explicit. Avoid hidden service locators, mutable global state, and circular dependencies.
- Isolate volatile external systems behind an owned boundary when they genuinely need to change or be tested independently.
- Introduce an interface, layer, or dependency inversion only for an observed substitution, testing, or independent-change boundary.
- Do not create an interface per class, a wrapper per dependency, or another layer merely to appear decoupled.
- Keep every subtype or implementation behaviorally substitutable for its advertised abstraction. Do not strengthen preconditions, weaken promised results, violate invariants, or introduce incompatible errors or side effects outside the contract. Add shared contract tests when multiple implementations create material risk.
- Shape interfaces around capabilities their actual consumers use. Do not force consumers or implementations to depend on unused operations; split an interface only when distinct consumers, permissions, or change patterns demonstrate a real boundary.

## Apply DRY to knowledge, not visual similarity

- Identify duplicated knowledge, business rules, intent, schemas, or invariants whose copies must change together.
- Use the test: "Would one conceptual change require coordinated edits in these places?" If not, do not force them behind one abstraction merely because the lines look similar.
- Put one authoritative representation in the module, function, type, schema, or configuration layer that owns the concept.
- Prefer a small function, module, or composed collaborator when it expresses the shared rule with low coupling.
- Use inheritance only for a genuine substitutable `is-a` relationship, not as a generic reuse mechanism.
- Use interfaces primarily to define a contract or capability. Use shared/default interface implementation only when the language supports it and the behavior is genuinely common.
- Remove the old copies after callers use the authoritative implementation, then test every affected path.

Do not create a premature or condition-heavy abstraction to satisfy DRY. A little independent code can be safer than coupling concepts that only happen to look alike. Abstract once the shared knowledge and ownership are clear.

## Apply KISS to the complete solution

- Choose the simplest design that fully meets the acceptance contract and existing constraints.
- Follow established project conventions unless they are the cause of the problem.
- Prefer direct control flow, clear names, narrow responsibilities, and explicit data movement.
- Remove dead paths, needless layers, clever indirection, and configuration with no current purpose.
- Keep required validation, error handling, security, observability, migration work, and tests. Do not mislabel necessary correctness as complexity.
- Optimize for comprehension and change safety, not minimum line count.

## Apply YAGNI to speculative work

- Implement the current acceptance contract and the support it demonstrably needs now.
- Do not add hypothetical extension points, generic frameworks, future modes, unused configuration, speculative caching, or extra dependencies without a current consumer or measured need.
- Do not preserve unused scaffolding on the claim that it may become useful.
- Keep refactoring and tests required to make the current change safe; YAGNI is not permission to leave fragile code.
- Record future ideas outside the implementation when they are not part of the accepted scope.

## Measure performance and bound resource growth when risk triggers it

Apply this section when performance is contractual or the change affects a hot path, large or untrusted inputs, persistent growth, external I/O, queues, caches, retries, batching, fan-out, or concurrency. Do not impose it on an unrelated low-risk edit.

- Define the representative workload, current baseline, relevant metric, and accepted budget before optimizing. If a performance claim cannot be measured in the available environment, label it unverified.
- Do not claim that a change is faster, more efficient, or scalable without repeatable before-and-after evidence under a representative workload.
- Do not add caching, concurrency, pooling, batching, lower-level code, or architectural complexity without an explicit requirement or an evidenced bottleneck.
- Measure the dimensions that can decide the acceptance criterion, such as latency distribution, throughput, CPU, memory and allocations, I/O, query count, storage growth, or cost. Do not hide tail behavior behind an irrelevant average or rely on a microbenchmark that omits the real bottleneck.
- Bound queues, caches, retries, batch sizes, fan-out, concurrency, retained temporary state, and other growth. Define applicable backpressure, eviction, overflow, timeout, cancellation, and degradation behavior.
- Test expected limits and credible beyond-limit behavior while preserving correctness, contract behavior, and data integrity.

## Plan safe rollout and recovery when deployment is in scope

Apply this section only when a change can reach a shared or deployed environment, infrastructure, configuration, persistent data, external state, or overlapping software versions.

- Define the blast radius, rollout stages proportional to risk, health signals, observation window, stop criteria, and authorized recovery actions.
- Choose rollback, traffic reversal, feature disablement, restoration or reconciliation, or fix-forward based on state safety. Do not assume a code revert reverses schema, data, configuration, or external side effects.
- Preserve old-and-new compatibility until mixed versions and old persisted data can no longer occur. Test mixed-version behavior when the rollout can create it.
- For high-risk changes, verify the recovery path before production. If reversal is impossible, state that before mutation and use smaller stages, checkpoints, backups, reconciliation, or a tested fix-forward path.
- Treat an automatic halt or rollback as authorized only when an accepted plan or established policy defines its trigger and scope. Treat the action as containment, not as proof that the underlying defect is corrected.
- Remove temporary flags, compatibility paths, and migration machinery after their documented exit conditions are met.

## Resolve principle conflicts

Apply this priority order:

1. Protect correctness, data, security, accepted contracts, and verified repair of defects.
2. Meet the current accepted requirement completely.
3. Preserve safe state transitions and side effects.
4. Preserve trust-boundary, error-integrity, and resource-safety requirements.
5. Keep authoritative operational and contract documentation accurate.
6. Prefer the simplest maintainable design with local change impact.
7. Remove proven duplication of knowledge without speculative abstraction.

Never use DRY to justify an abstraction that violates KISS or YAGNI. Never use KISS or YAGNI to omit work required for a correct, safe, verified solution.

## Pass the completion gate

For every task, report and verify:

- The task type and acceptance contract
- The implemented or reviewed behavior and supporting evidence
- Relevant behavioral, regression, integration, static, and runtime checks
- Affected contracts, compatibility, and migration status
- Relevant state-transition and side-effect behavior
- Relevant trust-boundary validation, error behavior, and sanitized diagnostics
- Affected authoritative documentation and verified examples
- Any remaining unverified claim, risk, or blocked work

Add the task-specific evidence:

- **Defect or incident:** Report the verified cause, correction at the owning layer, obsolete workaround removed, final same-problem loop count, and original failure check now passing.
- **Feature:** Map each acceptance criterion to implementation and verification. Do not report a root cause.
- **Refactor:** Show the passing before-and-after behavioral baseline and confirm preserved observable contracts.
- **Review:** State the inspected scope, findings, checked evidence, and what remains unverified.

Add these checks only when their trigger applies:

- **Trust boundary or failure handling:** Show rejected-input behavior, preserved diagnostic cause, safe outward errors, and sanitized logs.
- **Performance or resource risk:** Report the workload, baseline, budget, before-and-after measurements, and verified resource bounds.
- **Deployment or recovery:** Report rollout stages, observed health signals, mixed-version compatibility, stop criteria, and the verified recovery or fix-forward path.

Do not report success when only a symptom changed, verification was skipped, an acceptance criterion remains unmet, or the problem hit the loop limit.
