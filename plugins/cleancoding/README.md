# Clean Coding

Evidence-backed engineering discipline for coding agents: task contracts before edits, root-cause fixes instead of symptom patches, the shared three-loop stop rule, and a receipt-based completion gate enforced by a `Stop` hook.

## What is in the package

| Path | Purpose |
| --- | --- |
| `skills/cleancoding/SKILL.md` | Operating contract, workflow selection, the embedded stop rule and receipt. Under 10 KB by design. |
| `skills/cleancoding/references/` | Root-cause workflow, contracts and boundaries, tests and docs, design principles, performance and rollout, completion gate. Loaded only when the task's risk calls for them. |
| `hooks/verification_gate.py` | Tracks file mutations and verification commands per session; returns the turn once when a final response changed files without a `RECEIPT`. |
| `evals/` | Scenario suite with real fixture repositories and deterministic grading. |
| `tests/` | Hook, grading, and package tests. |

## Install

Claude Code:

```text
/plugin marketplace add MTEnt/speshul-skills
/plugin install cleancoding@speshul-skills
```

Codex:

```text
codex plugin marketplace add MTEnt/speshul-skills
codex plugin add cleancoding@speshul-skills
```

Standalone: copy `skills/cleancoding/` into your runtime's skills directory. The stop rule and receipt still apply; only the hook enforcement is lost.

## What the hook does and does not do

- Runs on `PostToolUse`, `Stop`, `SessionStart`, and `SessionEnd`.
- Stores only timestamps under the OS temporary directory, keyed by a hashed session id, and deletes them at `SessionEnd`. Override the location with `CLEANCODING_STATE_DIR`.
- Blocks a stop at most once per response and never blocks when the last message already contains a `RECEIPT` or `LOOP LIMIT REACHED`.
- Never runs commands, reads transcripts, or inspects source files. It classifies tool names and shell command text only.
- Fails open on malformed input or state errors.

## Run the tests and evals

```text
python -m unittest discover -s tests -v
python evals/run_behavior_suite.py --runner claude --output evals/behavior-results.json
```

The eval runner needs a local `claude` or `codex` executable. Grading is deterministic: each scenario ships a fixture repository, the agent works in a disposable copy, and the grader inspects the resulting files, test results, and final message. `--keep` retains the working copies, the final messages, and the raw event streams for inspection; `--grade-only` regrades a kept copy without running an agent.

Results are model behavior, so they vary between runs. `evals/behavior-results.json` records one full run with the runner version and a digest of the skill text; a scenario that fails there is a real adherence gap to investigate, not something to tune the grader around. Two grader rules came out of that investigation and are worth knowing: protected test files may be made hermetic or extended but never weakened (`test_assertions_preserved`), and an unreachable task may stop honestly with a receipt whose `Open` line names the decision instead of fabricating three loops (`stopped_for_direction`).
