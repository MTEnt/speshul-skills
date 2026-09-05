# Root-cause workflow for defects and incidents

1. State the expected behavior, actual behavior, and exact failure evidence.
2. Reproduce the problem or establish a reliable failing check. If reproduction is impossible, say what is missing and do not invent a cause.
3. Trace the relevant path through inputs, state, code, configuration, dependencies, and runtime behavior.
4. State a falsifiable root-cause hypothesis and the evidence supporting it.
5. Test the hypothesis with the smallest safe diagnostic that can distinguish it from alternatives.
6. Change the causal defect at its owning boundary. Remove obsolete compensating logic made unnecessary by the correction.
7. Re-run the original failure check, relevant regression tests, and nearby static or runtime checks.

Treat a cause as verified only when the evidence connects it to the failure and the correction removes the failure without a symptom-specific bypass. If the evidence supports only a hypothesis, label it unverified and continue investigating within the loop limit.

Identify multiple contributing causes when the evidence shows them rather than forcing one simplistic cause.

## External causes versus owned resilience

- If an external dependency behaves according to its contract but the owned system fails to handle a documented failure mode, the missing timeout, retry, idempotency, or degradation behavior may be the owned root cause. Implement it only when the acceptance contract requires it, and keep it bounded, observable, and tested.
- If the verified cause is inaccessible or outside the authorized scope and the owned contract does not require handling it, report the causal evidence and ask for direction. Do not create a local bypass and call it a fix.

## Emergencies

If an active incident threatens data, security, availability, or uncontrolled cost, first use only a containment or recovery action whose trigger, scope, and authority are already defined in the accepted contract or an established operational policy. Otherwise preserve evidence and ask the human whether to authorize temporary containment. Do not invent an ad hoc containment action or present containment as the final correction.

When containment is pre-authorized or the human authorizes it:

- Label it `TEMPORARY MITIGATION`.
- Record its scope, risk, rollback condition, and removal trigger.
- Keep the root-cause correction as unresolved work.
- Do not claim the underlying problem is fixed unless the cause is corrected and verified or the human explicitly changes the task scope.

## Loop log entry

Record each failed corrective cycle in this shape so the stop rule in `SKILL.md` can be applied without reconstruction:

```text
Loop <n>
Hypothesis: <cause under test>
Action: <corrective change or diagnostic>
Evidence: <observed output, test, trace, or state>
Outcome: <criterion still unmet because ...>
```
