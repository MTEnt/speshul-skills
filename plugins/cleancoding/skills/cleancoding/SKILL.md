---
name: cleancoding
description: Evidence-backed engineering for implementing, debugging, refactoring, and reviewing code or configuration. Use when changing code; defining acceptance criteria; fixing a defect at its root cause instead of a symptom; protecting contracts, trust boundaries, state, or error integrity; or deciding how much design, testing, documentation, performance work, or rollout care a change needs. Applies DRY, KISS, and YAGNI, the shared three-loop stop rule, and a receipt-based completion gate.
license: MIT
metadata:
  version: "1.0.0"
  author: MTEnt
---

# Clean Coding

## Operating contract

- Protect correctness, data integrity, security, accepted contracts, and explicit user requirements before style heuristics.
- Fix a defect at the verified cause in the layer that owns the violated behavior. A workaround, band-aid, symptom suppression, or temporary mitigation is not a completed solution.
- Do not hide failures with arbitrary retries or delays, swallowed exceptions, hard-coded special cases, duplicated branches, disabled tests, weakened types, ignored lint rules, or bypassed security checks.
- Add a fallback or retry only when the accepted contract requires it, the failure mode is evidenced, and the behavior is bounded, observable, idempotent, and tested.
- Keep work scoped to the current requirement while completing everything correctness, safety, and maintainability need.
- Verify behavior with evidence. Plausible-looking code is not complete.

## Select the workflow and write the task contract

Before editing, classify the task and derive a proportional task contract in working context (field names follow the shared `contracts/task-contract.schema.json` in the repository): task type, required observable outcome, acceptance checks, baseline or exact failure evidence, non-goals, expected change surface, constraints and known consumers, and the stop condition. Keep it brief for a mechanical low-risk change. Ask for direction only when a semantic ambiguity would materially change the result.

| Task type | Workflow |
| --- | --- |
| Defect or incident | Reproduce or directly observe the failure, then follow [root-cause.md](references/root-cause.md). The loop limit applies from the first failed fix. |
| Feature | Implement the acceptance checks without inventing a root cause. The loop limit applies only when corrective attempts repeatedly fail the same check. |
| Refactor | Establish a passing behavioral baseline, make small transformations, and re-run the baseline after each meaningful step. Observable behavior is preserved. |
| Review | Compare the artifact with its requirements, contracts, and verified behavior. Report evidence and uncertainty. Do not mutate unless the user also requests changes. |
| Mixed | Separate behavior change, defect correction, and refactoring into explicit phases with their own checks. |

## Apply the discipline that the change needs

Read the reference that matches the risk in the task contract; skip the rest.

- Contracts, trust boundaries, error integrity, state, and side effects: [contracts-and-boundaries.md](references/contracts-and-boundaries.md). Read it whenever a change touches a public API, schema, serialized format, event, input from a less-trusted source, or a state-changing operation.
- Tests as evidence and authoritative documentation: [tests-and-docs.md](references/tests-and-docs.md). Read it for any defect fix, any change that adds or alters behavior, and any change that makes existing docs or examples false.
- Change locality, DRY, KISS, YAGNI, and how to resolve conflicts between them: [design-principles.md](references/design-principles.md). Read it before introducing an abstraction, layer, dependency, or shared helper, and when removing duplication.
- Performance budgets, resource bounds, rollout, and recovery: [performance-and-rollout.md](references/performance-and-rollout.md). Read it only when the change affects a hot path, large or untrusted inputs, persistent growth, external I/O, concurrency, or anything that reaches a shared or deployed environment.

<!-- contract:loop-limit:start -->
## Stop after three failed loops

One loop is a completed corrective cycle on the same unmet acceptance criterion: hypothesis, corrective action, verification, criterion still unmet. Read-only evidence gathering is not a loop. Changing the tool, wording, file, or agent does not create a new problem; reset the count only when evidence shows the causal condition materially changed.

Keep a loop log from the first failed cycle: loop number, hypothesis, action, evidence, outcome, and why the criterion remains unmet.

After three unsuccessful loops, do not start a fourth. Stop mutations and repeated executions on that track and begin the next user-visible response with this receipt:

```text
LOOP LIMIT REACHED
Loops: 3 unsuccessful cycles; loop 4 not started.
Problem: <unmet acceptance criterion and exact failure>
Attempts: <three hypotheses, actions, and outcomes>
Mechanism: <evidence-backed cause, or labeled unknown>
Evidence: <logs, tests, traces, or state>
Decision needed: <specific choice, access, or information>
Next step: Waiting for user direction.
```

Continue unrelated work only when it cannot alter or conceal the blocked problem. After direction, keep the existing count unless the direction changes the causal track or scope. Use the receipt only when work actually stops under this rule; a warning that allowed an action is not a stop.
<!-- contract:loop-limit:end -->

## Pass the completion gate

Before reporting completion, confirm every item in [completion-gate.md](references/completion-gate.md) that applies to the task type. Do not report success when only a symptom changed, verification was skipped, an acceptance check remains unmet, or the loop limit was reached. The bundled Stop hook blocks a final response that changed files but carries no receipt.

<!-- contract:handoff-receipt:start -->
## Close with a receipt

After tool-using or mutating work, end the response with a compact factual receipt. Omit it when no work was performed. Every line comes from the recorded actions of this session, not from memory of what was intended.

```text
RECEIPT
Outcome: <what was delivered or decided>
Changed: <files, systems, or state touched; "none" when read-only>
Verified: <checks run and their observed results>
Unverified: <claims, risks, or checks that were skipped, with the reason>
Open: <blocked or deferred items and who decides>
```
<!-- contract:handoff-receipt:end -->
