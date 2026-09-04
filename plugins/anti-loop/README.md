# Anti Loop

Anti Loop keeps implementation work tied to the requested outcome, warns before edits expand permanent agent or workflow controls, and enforces the repository's shared three-loop stop rule.

## What it does

- The skill tells the agent to derive a task contract (outcome, acceptance checks, non-goals, surface, stop condition), make the smallest sufficient change, and stop when acceptance is met.
- `hooks/anti_loop.py` (stateless) injects a concise scope reminder at `SessionStart` and shows a visible, non-blocking advisory at `PreToolUse` when an edit touches persistent control files such as `AGENTS.md`, `CLAUDE.md`, `SKILL.md`, `hooks.json`, `plugin.json`, `marketplace.json`, `.codex/config.toml`, or `.github/workflows/*`.
- `hooks/loop_limit.py` (stateful) watches `PostToolUse`. When the same verification command fails again after a corrective change, it counts one loop. The second loop gets a reminder to change the hypothesis; the third injects the `LOOP LIMIT REACHED` receipt requirement. A passing run resets the count. Repeated failures with no change in between count once.
- The stop rule text in `skills/anti-loop/SKILL.md` is a verbatim copy of `contracts/loop-limit.md`, checked by the repository validator, so `cleancoding` and Anti Loop never disagree about what a loop is.

Package files:

- `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` — manifests for both runtimes.
- `skills/anti-loop/SKILL.md` — agent behavior.
- `hooks/hooks.json`, `hooks/anti_loop.py`, `hooks/loop_limit.py` — lifecycle configuration and logic.
- `tests/` — package and hook behavior tests.
- `docs/` — the anonymized research that motivated the first release.

## Install

Claude Code:

```text
/plugin marketplace add MTEnt/speshul-skills
/plugin install anti-loop@speshul-skills
```

Codex:

```text
codex plugin marketplace add MTEnt/speshul-skills
codex plugin add anti-loop@speshul-skills
```

Start a new conversation after installation. Review the hook definitions before trusting them (`/hooks` in Codex). Both hooks are advisory: they add context and visible warnings but never block a tool.

## Privacy and state

`loop_limit.py` stores hashed session ids, hashed normalized commands, counters, and timestamps in a SQLite file under the OS temporary directory (override with `ANTI_LOOP_DB_PATH`). It stores no command text, output, prompts, or file contents. Session rows are removed at `SessionEnd`; abandoned rows expire after 24 hours. Both hooks fail open.

## Run the tests

```text
python -m unittest discover -s tests -v
```
