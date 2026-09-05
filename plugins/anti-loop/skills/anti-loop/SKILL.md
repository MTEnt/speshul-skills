---
name: anti-loop
description: Keep coding and planning tasks scoped to the requested outcome, prevent unrequested architecture or process growth, and stop repeated failed attempts with the shared three-loop rule. Use when implementing, refactoring, debugging, planning repository changes, or modifying agent workflows. Do not use to reject complexity the user explicitly requested or that a demonstrated safety or correctness risk requires.
license: MIT
metadata:
  version: "0.3.0"
  author: MTEnt
---

# Anti Loop

Deliver the smallest sufficient change that meets the user's actual acceptance condition.

## Anchor the task

Before expanding the implementation, derive a task contract from the request and inspected evidence (field names follow the repository's shared `contracts/task-contract.schema.json`):

- outcome: the observable result the user asked for;
- acceptance checks: the smallest checks that demonstrate that result;
- non-goals: adjacent work the user did not request;
- surface: the files or subsystem likely to require change;
- stop condition: acceptance is met and proportionate checks pass.

Keep this contract in working context. Do not create a planning, policy, receipt, or tracking file merely to record it.

If the request has multiple materially different interpretations, ask one focused question. Otherwise choose the narrowest interpretation that fully satisfies it and state any consequential assumption.

## Constrain growth

Treat a change as in scope only when it is directly required for acceptance or mitigates a demonstrated correctness, security, data-loss, or operational risk.

Before adding a dependency, abstraction, schema, workflow step, agent instruction, hook, skill, policy, or tracking artifact, ask:

1. Which acceptance check or demonstrated risk requires it?
2. Can an existing mechanism handle it?
3. Can something obsolete be consolidated or removed instead?
4. What bounded check will prove the addition works?

If those questions do not have concrete answers, omit the addition or ask the user to authorize the scope expansion. An adjacent improvement is not part of the task merely because it was noticed.

Do not turn a single failure into permanent governance. Prefer repairing the immediate defect and collecting evidence before adding a lasting control. The bundled `PreToolUse` hook warns, without blocking, when an edit touches persistent agent or workflow control files.

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

The bundled `PostToolUse` hook counts the same verification command failing again after a corrective change and injects a reminder at the second failure and the receipt requirement at the third. A plan is a hypothesis, not an obligation: after each failed attempt, use the new evidence to change the hypothesis. Distinct failures discovered while making real progress are not the same loop.

## Close and stop

Verify in proportion to the change. Do not add evidence artifacts or extra workflow just to demonstrate compliance with this skill.

When acceptance is met, stop. Report the result, the relevant verification, and any material limitation. Do not manufacture follow-up work from optional improvements or residual complexity introduced by the task itself.
