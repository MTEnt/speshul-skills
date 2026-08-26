---
name: task-clock
description: "Estimate difficulty and active-work budgets for substantive multi-step work. Before tools, report `Task budget: SCORE/10 (CONFIDENCE) · expected RANGE · reassess after CHECKPOINT without progress.` Reassess when deterministic elapsed-time or repeated-call signals show the route may be stale. Skip casual conversation and trivial one-step answers."
---

# Task Clock

Give substantive work a visible estimate, then use real clock signals to challenge that estimate without treating time as proof of failure.

## Score the task

Before substantive work, score each factor from 0 to 2 and sum them. Use a minimum total of 1.

- Scope: atomic / several connected steps / multiple systems.
- Uncertainty: clear path / investigation required / novel or materially ambiguous.
- Environment: none / one known environment / multiple or unstable dependencies.
- Risk: reversible / moderately consequential / destructive, external, or high-stakes.
- Verification: one direct check / several checks / cross-system or difficult proof.

Difficulty is model judgment, not an objective measurement. State low, medium, or high confidence based on how much of the route is known.

| Score | Expected active completion | No-progress checkpoint |
|---|---:|---:|
| 1–2 | 1–5 minutes | 3 minutes |
| 3–4 | 5–20 minutes | 7 minutes |
| 5–6 | 20–60 minutes | 15 minutes |
| 7–8 | 1–3 hours | 30 minutes |
| 9 | 3–8 hours | 45 minutes |
| 10 | Decompose before execution | Per-stage budget |

Active work is time spent advancing the current user turn. Do not count time after handing control back to the user.

## Show the budget

Combine the normal commentary preamble with one compact line before substantive work. Use exactly this field structure, replacing only the values:

```text
Task budget: 6/10 (medium confidence) · expected 20–60m · reassess after 15m without progress.
```

The line must begin with `Task budget:` and include the numeric score out of 10, confidence, expected-completion range, and no-progress checkpoint in that order. Do not substitute a free-form estimate such as `Task Clock — budget: 10 min`.

Omit this status for casual conversation and trivial one-step answers. A materially changed follow-up starts a new rating.

After initial inspection, visibly re-score only when the total changes by at least two points, the risk category changes, or an unknown invalidates the original route.

## React to clock signals

The bundled hook supplies UTC start metadata and deterministic signals at supported lifecycle boundaries. It cannot interrupt uninterrupted reasoning or a tool that is still running.

Pause before the next action and reassess when any of these is true:

- the assigned expected-completion ceiling has been exceeded;
- the no-progress checkpoint has elapsed without new concrete evidence;
- the hook reports three consecutive identical input/result fingerprints.

When any condition above fires, begin with `TASK CLOCK REASSESSMENT` and use the structure below. An identical fingerprint proves only that the recorded call input and result repeated. It does not prove that the attempt failed, that the intended result and approach were materially unchanged, or that the same blocker persisted. Do not emit `ANTI LOOP STOPPED THIS ATTEMPT` unless separate concrete evidence establishes all parts of that three-failure rule.

Use this exact compact structure:

```text
TASK CLOCK REASSESSMENT
Elapsed: <time> against <original budget>
Evidence gained: <concrete result or none>
Delay cause: <bad assumption, repeated blocker, legitimate long operation, or scope growth>
Re-score: <score and revised budget>
Decision: <changed route, justified continuation, or blocked>
```

Time alone never triggers the Anti Loop hard-stop receipt. The three-materially-similar-failures rule remains authoritative; repeated fingerprints and elapsed thresholds are reassessment evidence only.
