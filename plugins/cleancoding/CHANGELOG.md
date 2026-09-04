# Changelog

## 1.0.0 - 2026-09-05

- Moved to the plugin layout (`skills/cleancoding/`) so both Claude Code and Codex install it from the repository marketplace.
- Split the 22 KB single-file skill into a concise `SKILL.md` plus six references loaded by risk trigger.
- Embedded the shared repeated-attempt stop rule and handoff receipt from `contracts/`; the stop receipt is now `LOOP LIMIT REACHED` in every package.
- Added the `verification_gate.py` Stop hook: a final response that changed files must carry a receipt, and the agent is told when no verification ran after the last change.
- Added a behavior eval suite (`evals/`) with deterministic fixture grading for defect, flaky-retry, scope, refactor, review, and loop-limit scenarios, plus a recorded run (`evals/behavior-results.json`). The Claude runner sends the prompt through stdin and allowlists tools explicitly: on Windows the npm `claude.CMD` shim mangles multi-line arguments and drops the flags after them, and `--dangerously-skip-permissions` is refused when the runner is launched from inside a Claude Code session. Permission denials are surfaced as run errors rather than graded as agent failures.

## 0.1.0 - 2026-08-05

- Initial standalone skill.
