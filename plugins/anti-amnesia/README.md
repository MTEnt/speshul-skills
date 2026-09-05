# Anti Amnesia

Anti Amnesia answers "what did you just do?" from the recorded session instead of re-running checks, keeps present-state questions honest, and closes tool-using work with the repository's shared handoff receipt.

## What it does

- The skill separates retrospective questions (answer from tool results, the last response, and the last receipt) from current-state questions (verify with tools).
- `hooks/session_start.py` injects the same policy at `SessionStart`, including after resume, clear, and compaction, so the behavior survives context loss.
- The receipt block in `skills/anti-amnesia/SKILL.md` is a verbatim copy of `contracts/handoff-receipt.md`, validated by the repository validator. `cleancoding` writes the same block and its Stop hook requires it after file changes.

## Install

Claude Code:

```text
/plugin marketplace add MTEnt/speshul-skills
/plugin install anti-amnesia@speshul-skills
```

Codex:

```text
codex plugin marketplace add MTEnt/speshul-skills
codex plugin add anti-amnesia@speshul-skills
```

The hook is stateless, reads nothing from disk, and fails open on malformed input.

## Run the tests

```text
python -m unittest discover -s tests -v
```
