# Temporal Tasks

Temporal Tasks is a standalone plugin for Codex and Claude Code for difficulty estimates, active-work budgets, and deterministic elapsed-time reassessment signals.

It intentionally does not implement scope control or the shared three-loop stop rule. Those remain in the separate `anti-loop` plugin.

The package provides:

- `skills/task-clock/SKILL.md` — implicitly invoked guidance for scoring substantive multi-step tasks and reporting a compact active-work budget.
- `hooks/task_clock.py` — standard-library lifecycle handling for per-turn start time, tool duration, call count, elapsed thresholds, and repeated identical input/result fingerprints.
- `hooks/hooks.json` — registrations for `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, and `SessionEnd`.
- `tests/` — deterministic package and hook tests with injected timestamps.

The hook stores temporary SQLite state under the operating system's temporary directory. Persisted fields are limited to hashed session, turn, tool-use, input, and result identifiers; timestamps; tool names; counters; and fingerprints. It does not store prompts, commands, source text, tool output, transcript contents, or secrets. Session state is removed at `SessionEnd`, records expire after 24 hours, and hook failures do not block tools.

Clock signals request reassessment. They do not cancel tools and do not independently trigger the `LOOP LIMIT REACHED` receipt.

## Install

Claude Code:

```text
/plugin marketplace add MTEnt/speshul-skills
/plugin install temporal-tasks@speshul-skills
```

Codex:

```text
codex plugin marketplace add MTEnt/speshul-skills
codex plugin add temporal-tasks@speshul-skills
```

Start a new Codex conversation after installation so the bundled skill and hooks are discovered.

Open `/hooks` in Codex and review the four Temporal Tasks hook definitions:

- `UserPromptSubmit` starts the turn clock and injects the compact scoring/budget mapping.
- `PreToolUse` records a hashed input fingerprint and tool start time.
- `PostToolUse` records duration and emits elapsed-threshold or repeated-call signals.
- `SessionEnd` removes the current session state and expires abandoned state.

Trust the definitions you want to run. Codex records trust against the current hook definition, so an updated hook may require review again.

Verify the package is installed and enabled:

```text
codex plugin list
```

Then use `/hooks` to confirm all four Temporal Tasks hooks are active.

## Run the tests

From this plugin folder:

```text
python -m unittest discover -s tests -v
```
