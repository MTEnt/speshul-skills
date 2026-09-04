# Completion gate

Report and verify these for every task before writing the receipt:

- The task type and task contract.
- The implemented or reviewed behavior and its supporting evidence.
- Relevant behavioral, regression, integration, static, and runtime checks, with observed results.
- Affected contracts, compatibility, and migration status.
- Relevant state-transition and side-effect behavior.
- Relevant trust-boundary validation, error behavior, and sanitized diagnostics.
- Affected authoritative documentation and verified examples.
- Any remaining unverified claim, risk, or blocked work.

Add the task-specific evidence:

- **Defect or incident:** the verified cause, correction at the owning layer, obsolete workaround removed, final same-problem loop count, and the original failure check now passing.
- **Feature:** each acceptance check mapped to implementation and verification. Do not report a root cause.
- **Refactor:** the passing before-and-after behavioral baseline and confirmation that observable contracts are preserved.
- **Review:** the inspected scope, findings, checked evidence, and what remains unverified.

Add these only when their trigger applies:

- **Trust boundary or failure handling:** rejected-input behavior, preserved diagnostic cause, safe outward errors, and sanitized logs.
- **Performance or resource risk:** workload, baseline, budget, before-and-after measurements, and verified resource bounds.
- **Deployment or recovery:** rollout stages, observed health signals, mixed-version compatibility, stop criteria, and the verified recovery or fix-forward path.

## What the bundled hook enforces

The `Stop` hook in `hooks/verification_gate.py` tracks whether the session changed files and whether a verification command ran after the last change. When the final response lacks a `RECEIPT` block after file changes, the hook returns the turn to the agent once with the reason. It never blocks a second time for the same stop, and it never runs commands itself. Everything above the receipt remains the agent's responsibility.
