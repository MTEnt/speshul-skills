---
name: anti-loop
description: Keep coding and planning tasks scoped to the requested outcome, prevent unrequested architecture or process growth, and stop repeated materially similar failed attempts. Use when implementing, refactoring, debugging, planning repository changes, or modifying agent workflows. Do not use to reject complexity explicitly requested by the user or required by a demonstrated safety or correctness risk.
---

# Anti Loop

Deliver the smallest sufficient change that meets the user's actual acceptance condition.

## Anchor the task

Before expanding the implementation, derive these task-local facts from the user's request and inspected evidence:

- outcome: the observable result the user asked for;
- acceptance: the smallest check that demonstrates that result;
- non-goals: adjacent work the user did not request;
- expected surface: the files or subsystem likely to require change;
- stop condition: acceptance is met and proportionate checks pass.

Keep this contract in working context. Do not create a planning, policy, receipt, or tracking file merely to record it.

If the request has multiple materially different interpretations, ask one focused question. Otherwise choose the narrowest interpretation that fully satisfies it and state any consequential assumption.

## Constrain growth

Treat a change as in scope only when it is directly required for acceptance or mitigates a demonstrated correctness, security, data-loss, or operational risk.

Before adding a dependency, abstraction, schema, workflow step, agent instruction, hook, skill, policy, or tracking artifact, ask:

1. Which acceptance condition or demonstrated risk requires it?
2. Can an existing mechanism handle it?
3. Can something obsolete be consolidated or removed instead?
4. What bounded check will prove the addition works?

If those questions do not have concrete answers, omit the addition or ask the user to authorize the scope expansion. An adjacent improvement is not part of the task merely because it was noticed.

Do not turn a single failure into permanent governance. Prefer repairing the immediate defect and collecting evidence before adding a lasting control.

## Break repeated loops

A plan is a hypothesis, not an obligation. After each failed attempt, use the new evidence to change the hypothesis.

Count attempts as the same loop only when the intended result, approach, and blocker are materially unchanged. After three materially similar failed attempts with the same unchanged blocker:

- stop making variants of that attempt;
- report what was tried and the repeated evidence;
- identify the missing information, authority, or external state;
- ask for direction when progress cannot continue safely.

The next user-facing response must begin with this short receipt:

```text
ANTI LOOP STOPPED THIS ATTEMPT
Reason: <the unchanged blocker>
Evidence: <the materially similar attempts and repeated result>
Next step: Waiting for user direction.
```

Keep the receipt factual and specific. Use it only when work actually stops under the repeated-attempt rule. An advisory that allowed an action must not be described as a stop.

Distinct failures discovered while making real progress are not the same loop.

## Close and stop

Verify in proportion to the change. Do not add evidence artifacts or extra workflow just to demonstrate compliance with this skill.

When acceptance is met, stop. Report the result, the relevant verification, and any material limitation. Do not manufacture follow-up work from optional improvements or residual complexity introduced by the task itself.
