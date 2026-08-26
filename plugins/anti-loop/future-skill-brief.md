# Future anti-loop skill and hook brief

Status: design brief only
Working name: `anti-loop`

## Purpose

Prevent coding agents from turning local uncertainty into permanent project complexity without an explicit acceptance benefit and a stopping rule.

This is not a generic “write less code” rule. Necessary code can be large. The target is unjustified growth in scope, instructions, dependencies, workflow machinery, evidence artifacts, and coordination state.

## Operating principle

Before adding a permanent mechanism, the agent must answer:

1. Which user-visible, operator-runnable, correctness, or safety acceptance condition does this serve?
2. Is the failure recurring and measured, or did it happen once?
3. Can an existing mechanism handle it?
4. What will this addition replace, consolidate, or delete?
5. What is the smallest falsifier that proves the mechanism works?
6. What stops the work after that falsifier passes?

If the agent cannot answer those questions, it should not create the mechanism without asking the user.

## Start-of-task contract

The skill should derive a compact contract, preferably from the user’s own words:

```yaml
outcome: one sentence
acceptance: one observable test or result
non_goals: explicit exclusions
allowed_surface: expected files or subsystem
complexity_budget:
  new_dependencies: 0 unless justified
  new_instruction_files: 0 unless explicitly requested
  new_workflow_steps: 0 unless replacing an existing step
stop_when: acceptance is met and relevant checks pass
```

This contract is task-local. It must not automatically become another repository document.

## Change classification

Every material proposed change falls into one class:

- **Required:** directly necessary for acceptance.
- **Risk control:** directly mitigates a named correctness, security, data-loss, or operational risk.
- **Repair:** fixes behavior broken by an existing mechanism.
- **Opportunistic:** useful but not required now.
- **Governance expansion:** adds instructions, gates, schemas, routing, evidence requirements, or lifecycle states.

The skill proceeds with required work and justified risk controls. It reports repairs as control-system cost. It defers opportunistic work. Governance expansion requires explicit user authorization unless it replaces or removes an existing mechanism.

## Complexity receipt

Before completion, produce a short machine-readable receipt:

```json
{
  "acceptance_progress": "met|partial|none",
  "scope_drift": [],
  "new_files": [],
  "new_dependencies": [],
  "instruction_delta": "none|net_reduction|net_growth",
  "workflow_delta": "none|simplified|expanded",
  "retired_mechanisms": [],
  "open_questions": []
}
```

The receipt is ephemeral by default. Do not commit it unless the user requests durable evidence.

## Warning signals

The first implementation should detect only signals that can be measured cheaply:

- edits outside the declared task surface;
- creation of a new instruction, policy, workflow, schema, or agent-skill file;
- new dependency or new package;
- a process-only change with no stated acceptance link;
- multiple new artifacts created to repair one workflow defect;
- repeated edits to the same governance surface during one task;
- net instruction growth with no deletion or consolidation;
- a final answer claiming completion while acceptance is partial or absent;
- the agent proposing follow-up issues for residual work created by its own change.

Do not use raw line count as a verdict. Generated files, migrations, tests, and necessary protocol definitions can be large.

## Skill behavior

The skill should be concise. Its job is to make the agent perform four checks:

1. **Anchor:** restate the outcome and stop condition.
2. **Constrain:** name non-goals and the expected change surface.
3. **Challenge:** identify additions that do not directly serve acceptance.
4. **Close:** verify acceptance, report complexity introduced, and stop.

The skill must contain its own anti-bloat rule: do not create planning artifacts, issue taxonomies, or permanent policy merely to demonstrate compliance with anti-loop.

## Hook architecture

### Phase 1: shadow mode

- `SessionStart`: create a small session-local baseline outside the repository.
- `UserPromptSubmit`: inject one concise anti-loop reminder only for implementation or planning requests.
- `PreToolUse`: inspect supported edits and shell commands for deterministic growth signals; add context but do not block.
- `PostToolUse`: update ephemeral change-surface statistics.
- `Stop`: compare the final state with the task contract and request at most one corrective pass.

The `Stop` handler must check `stop_hook_active` and enforce a one-intervention budget. An anti-loop hook that repeatedly continues the agent would itself be a loop.

### Phase 2: advisory mode

Emit one short warning when the score crosses a measured threshold. The warning must name the concrete delta, not lecture the agent.

Example:

> Scope warning: this task added a workflow step and two permanent instruction surfaces but has not advanced the stated acceptance result. Reuse or remove an existing mechanism, or ask for explicit scope expansion.

### Phase 3: narrow enforcement

Only after shadow data establishes a low false-positive rate, deny deterministic cases such as:

- creating a new permanent agent instruction or workflow-policy file when the user did not authorize governance changes;
- adding a dependency outside the declared task surface with no acceptance link;
- attempting a second recursive `Stop` continuation.

Do not claim complete enforcement. Official OpenAI documentation states that local tool-hook coverage has exceptions and hosted tools are not covered by the same path.

## Scoring model

Use a small explainable score, not an LLM judgment hidden inside the hook:

```text
+3 new permanent instruction or policy surface
+3 new workflow state, gate, or lifecycle step
+2 new dependency
+2 edit outside declared surface
+2 process-only artifact without acceptance link
+1 net instruction growth
-2 existing mechanism removed
-2 duplicate path consolidated
-3 direct acceptance condition demonstrably met
```

Scores are prompts for review, not proof of wrongdoing. Safety-critical work may legitimately score high.

## Required safeguards

- Never store raw prompts, tool output, secrets, or source contents.
- Keep state session-local and bounded.
- Do not parse the transcript as a stable API.
- Ignore generated and vendored paths through explicit configuration.
- Separate safety controls from workflow preferences.
- Let the user override a warning explicitly.
- Never create issues, comments, commits, or project records automatically.
- Never broaden repository write scope.
- Prefer warning over denial until measured evidence justifies enforcement.

## Evaluation cases

The future package should include tests for:

1. A narrow bug fix with focused tests: no warning.
2. A requested new feature that legitimately adds files: no warning based on size alone.
3. A one-line defect answered with a new policy file, checker, schema, and workflow step: warn.
4. An agent adding instructions that restate an existing linter: warn and recommend deletion.
5. A security boundary that requires a new guard and falsifier: allow, but record the justified complexity.
6. A refactor that removes two obsolete mechanisms while adding one replacement: recognize net simplification.
7. A generated-file expansion: exclude generated output from the decision.
8. A `Stop` event after an earlier anti-loop continuation: do not continue again.
9. A hosted tool call: record that it was outside enforcement coverage rather than claiming it was checked.

## Success criteria for the anti-loop package

The package is successful only if it reduces unnecessary permanent artifacts without blocking ordinary product work or legitimate safety controls. Its own code, instructions, configuration, and outputs must remain small enough for a human to audit in one sitting.
