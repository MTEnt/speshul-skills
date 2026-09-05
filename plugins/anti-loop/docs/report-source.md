# Anti-loop: behavioral failure analysis

Status: research source, not an installed skill
Review mode: read-only and anonymized
Research date: 2026-08-26

## Direct diagnosis

**[Inference]** The central failure is not merely “AI writes too much code.” It is **recursive governance**: when an agent encounters ambiguity, friction, or a prior agent mistake, it converts that local problem into permanent process. The new rule, checker, template, skill, evidence format, or workflow state becomes additional context for every later agent. Those agents then encounter conflicts and edge cases created by the enlarged control system and respond by adding still more controls.

Another useful name is **control-plane capture**. The machinery for controlling work begins to consume more attention than the product outcome the machinery is supposed to protect.

The loop is:

```text
uncertainty or failure
        ↓
add a permanent instruction, artifact, gate, or workflow step
        ↓
increase context, coupling, and state transitions
        ↓
create new conflicts, stale state, and coordination failures
        ↓
file repair work for the control system
        ↓
add more permanent machinery
        ↺
```

The trap is that each addition can be locally defensible. The failure appears only at system level.

## What was observed

The following are verified observations from the private project review, stated without identifying or exact internal data.

### The workflow became a product of its own

The project contains extensive work whose observable result is a better agent workflow, better evidence handling, better routing, better synchronization, or better enforcement. Some of this is necessary. The problem is the recurrence: workflow machinery repeatedly generates its own maintenance work.

**[Inference]** A control system has crossed the line into control-plane capture when it routinely needs product-style roadmaps, migrations, compatibility work, incident fixes, and future architecture merely to govern the actual product work.

### Process defects are answered with more process

The record contains failures caused by interactions among workflow tools, gates, state machines, shared working state, generated guidance, and agent handoffs. The normal response is another issue, helper, schema, test, instruction, or gate.

This is the clearest recursive signature:

```text
workflow defect → workflow repair → larger workflow surface → new workflow defect
```

The repair may be correct while still worsening the system-level risk.

### Instructions accumulate exceptions

The agent-facing contract mixes safety boundaries, product direction, Git rules, environment rules, evidence rules, task routing, test selection, human authority, multi-agent coordination, lifecycle transitions, and recovery procedures.

**[Inference]** When critical safety rules and ordinary process preferences share one expanding instruction surface, salience is diluted. A model has more opportunities to miss a critical rule, follow a stale exception, or satisfy the wording while missing the purpose.

Research on long-context instruction following reports that instruction adherence becomes challenging in extended conversations. A recent configuration-smell study also identifies context bloat, rules copied from linters or tools, leaked skill procedures, and conflicting instructions as recurring problems in coding-agent configuration files. The configuration-smell work is a recent preprint and should be treated as suggestive, not settled consensus. ([EACL Findings paper](https://aclanthology.org/2026.findings-eacl.254/), [configuration-smell preprint](https://arxiv.org/abs/2606.15828))

### Evidence can become a substitute for outcome

The project strongly values pinned observations, checklists, receipts, exact-state verification, and falsifiers. These are good practices when tied to a real risk. They become harmful when producing the evidence packet is treated as delivery, or when evidence volume obscures whether a user-visible or operator-runnable result improved.

**[Inference]** This is **evidence laundering**: a large amount of precise process evidence creates confidence that the right thing was built, even though the evidence mostly proves that the prescribed process ran.

The distinction matters because automatic checks can disagree with maintainers’ holistic judgment. METR reported that agents sometimes produced functionally correct work that was still not readily usable due to broader quality problems. Its earlier randomized study also found that experienced maintainers’ perception of AI speedup diverged from measured completion time in that study’s narrow setting. Those findings do not establish a universal AI slowdown; they show why self-reported progress and machine-green status are insufficient outcome measures. ([holistic evaluation study](https://metr.org/blog/2025-08-12-research-update-towards-reconciling-slowdown-with-time-horizons/), [developer productivity RCT](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/))

### Deferred scope still creates present complexity

Future systems are extensively specified, decomposed, and represented in current workflow state even when implementation is explicitly blocked.

**[Inference]** “Deferred” prevents execution but does not prevent cognitive load, backlog growth, dependency growth, or architectural anchoring. A fully elaborated future plan can pull current decisions toward a speculative design and give agents more material to reconcile.

### The system optimizes for a zero-context agent

The workflow tries to make every handoff reconstructable by a fresh agent. That goal encourages every nuance to become durable text, structured state, or a machine-enforced transition.

**[Inference]** A zero-context agent cannot be made reliable by externalizing the entire project into instructions. Past a point, adding context recreates the same comprehension problem in a larger prompt. The safer target is a minimal stable contract plus task-specific evidence, with a human responsible for exceptions.

### Safety and bureaucracy are not the same thing

The reviewed system contains real, useful safeguards: read-only production boundaries, explicit authority for consequential actions, non-destructive Git rules, scoped worktrees, and attempts to prevent duplicate work. It also uses shared links rather than physically duplicating every harness-specific skill copy.

These facts weaken the lazy conclusion that “all the process is useless.” They do not remove the recursive loop. They show that the future safeguard must distinguish high-consequence safety controls from convenience, formatting, routing, and evidence preferences.

## Behavioral flaw taxonomy

| Flaw | Observable signature | Why it compounds |
|---|---|---|
| Recursive governance | A process failure produces another permanent process artifact | The repair enlarges the surface that can fail |
| Control-plane capture | Internal workflow outcomes compete with customer or operator outcomes | Progress becomes easier to demonstrate on machinery than on the product |
| Instruction debt | Rules and exceptions are added faster than they are consolidated or removed | Every task pays the context and conflict cost |
| Scope ratcheting | New work is easy to add; removal or de-scoping requires special justification | Complexity moves in one direction |
| Evidence laundering | Checklists and receipts prove procedure more strongly than usefulness | A green process can hide a wrong or unnecessary outcome |
| Speculative elaboration | Deferred ideas receive detailed present-day architecture and task graphs | Future guesses constrain current work and occupy attention |
| State fragmentation | Authority is spread across issues, documents, fields, scripts, comments, and agent context | No reader can cheaply determine the actual current contract |
| Repair-generated work | The tools that coordinate agents create defects requiring more agent work | Capacity is consumed maintaining the coordinator |
| Human bottleneck amplification | Agents generate many small decisions that require explicit human authority | The human becomes a queue processor for agent-created ambiguity |
| Completion inversion | Finishing the task requires satisfying a growing lifecycle around the task | “Done” becomes harder to reach than the product change itself |

## Root cause versus symptoms

The root cause is an authority rule:

> Agents are allowed to convert local uncertainty into permanent shared governance without proving that the new mechanism replaces or removes more complexity than it adds.

Long instruction files, large boards, duplicate tasks, elaborate evidence, brittle gates, and project creep are symptoms of that rule.

The missing constraints are:

- a hard distinction between product work and control-system work;
- a deletion or consolidation requirement for new governance;
- a complexity budget tied to the user’s acceptance outcome;
- a stopping rule;
- a rule that a plan is a hypothesis, not authority;
- measured proof that a proposed control addresses a recurring failure rather than one uncomfortable event.

## Adversarial assessment

The project record cannot prove that AI alone caused the bloat. It shows an AI-heavy workflow consuming substantial effort and generating self-referential maintenance, but the causal attribution is **[Inference]**. A human team could build the same bureaucracy.

Plausible alternative explanations:

- The reviewed repository is intentionally a documentation and workflow hub, so process-heavy contents are expected.
- A period of migration or consolidation can temporarily produce dense issue traffic and rapid rule changes.
- A regulated or safety-sensitive product can justify more evidence and authority boundaries than an ordinary application.
- The board records work items, not time spent or business value. A large process backlog does not prove that most engineering time went there.
- Some apparent cross-harness repetition is shared through links rather than maintained as separate content.
- Controlled research has not consistently found that AI-assisted code is less maintainable. One controlled study found no systematic downstream maintainability difference in its task setting. ([maintainability experiment](https://arxiv.org/abs/2507.00788))

The critique survives these alternatives because it does not depend on raw volume alone. It depends on the repeated causal shape visible in the work record: controls interact, create friction, and receive additional controls as the preferred repair.

## Recommendation

Do not begin by adding another blocking governance layer. That would reproduce the flaw.

Build the future anti-loop mechanism in this order:

1. **Shadow mode:** observe proposed changes and emit a short complexity receipt. Do not block.
2. **Advisory mode:** warn once when scope, instruction surface, dependency surface, or workflow machinery grows without a direct acceptance link.
3. **Targeted enforcement:** block only deterministic, narrow cases with measured low false-positive rates, such as creating a new permanent agent instruction file when the user did not authorize governance work.
4. **Retirement:** every promoted rule must name what it replaces, when it expires, and how it will be removed.

The hook should measure. The skill should reason. The human should retain authority over whether extra complexity is justified.

## Hook feasibility

Official OpenAI documentation currently supports lifecycle events suitable for a bounded prototype:

- `SessionStart` can establish a small task baseline.
- `UserPromptSubmit` can add concise developer context or block a prompt.
- `PreToolUse` can inspect, deny, or rewrite supported local tool calls.
- `PostToolUse` can report on a completed supported call but cannot undo its side effects.
- `Stop` can request one more agent pass before the turn ends.

The same documentation warns that tool hooks are not a complete enforcement boundary, that hosted tools are outside the local tool hook path, that multiple matching hooks may run, and that transcript format is not stable. The design therefore must not depend on complete interception or parsing the transcript as a durable API. ([official OpenAI Hooks documentation](https://learn.chatgpt.com/docs/hooks))

## Bottom line

**[Inference]** The nightmare is best described as **recursive governance under asymmetric growth**: adding a rule is cheap and feels safe; deleting a rule feels risky and requires proof. Coding agents intensify that asymmetry because they can generate polished process artifacts faster than humans can evaluate whether those artifacts should exist.

Anti-loop should reverse the burden of proof. A new permanent instruction, workflow step, checker, schema, or coordination artifact should be presumed unnecessary until it demonstrates a direct acceptance benefit, reuses an existing mechanism where possible, and retires equivalent complexity.
