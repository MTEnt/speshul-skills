# Repeated-attempt stop rule

Embed the block below verbatim, markers included.

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
