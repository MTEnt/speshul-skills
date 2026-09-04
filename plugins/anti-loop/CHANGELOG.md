# Changelog

## 0.3.0 - 2026-09-05

- Replaced the package-specific three-attempt rule and `ANTI LOOP STOPPED THIS ATTEMPT` receipt with the shared repeated-attempt stop rule from `contracts/loop-limit.md`; the receipt is now `LOOP LIMIT REACHED` everywhere.
- Added `hooks/loop_limit.py`: a stateful `PostToolUse` hook that counts the same verification command failing again after a corrective change, reminds at the second failure, and requires the receipt at the third.
- Added a Claude Code manifest so the plugin installs from the repository marketplace on both runtimes; hook commands resolve `python` or `python3`.
- The `PreToolUse` advisory now also covers `MultiEdit`, `plugin.json`, and `marketplace.json`.
- Moved the research notes into `docs/`.

## 0.2.0 - 2026-08-26

- First marketplace release: scope anchor, growth constraints, stateless `SessionStart` and `PreToolUse` advisory hook.
