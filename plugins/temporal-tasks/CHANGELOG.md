# Changelog

## 0.2.0 - 2026-09-05

- Runs on Claude Code as well as Codex: `prompt_id` is accepted as the turn identifier, a session without one is tracked as a single turn, and hook commands resolve `python` or `python3` through `${CLAUDE_PLUGIN_ROOT}`.
- Reassessment text now refers to the shared `LOOP LIMIT REACHED` stop rule instead of the retired Anti Loop receipt.
- The budget line is documented as the `budget` object of the shared task contract.
- Added a Claude Code manifest, `metadata.version`, and this changelog.

## 0.1.0 - 2026-08-26

- First marketplace release: five-factor difficulty score, budget line, SQLite-backed elapsed-time and repeated-call signals.
