# Hooks and evals

## When a rule needs a hook

Prose instructs; hooks enforce. Promote a rule to a hook when all of these hold:

- the rule is one a model plausibly skips under pressure (skipping verification, editing a test to make it pass, retrying the same failing command);
- the violation is observable from tool names, tool input, tool output, or the final message without reading source files;
- the hook can fail open without harming the task.

Prefer advisory hooks (`additionalContext`, `systemMessage`) over blocking ones. Block only on `Stop`, only once per response, and only for a condition the agent can resolve in one step. Never block `PostToolUse` in a way that replaces the tool result the agent needs.

## Hook discipline

- Standard library only. Timeouts of a few seconds.
- Store hashes, counters, and timestamps; never prompts, commands, output, or file contents. Delete state at `SessionEnd`; expire it after 24 hours.
- Fail open on malformed input, missing fields, or state errors. Exit 0 with no output is the safe default.
- Test the hook as a module and as a CLI: valid events, malformed input, session isolation, and that persisted state contains none of the raw strings from the event.

## When a behavior needs an eval

Write an eval scenario for any behavior the skill claims to change. A scenario is a fixture directory, a `TASK.md`, and a list of deterministic checks. The agent works in a disposable copy; the grader inspects files, runs the fixture's tests, and reads the final message. Model-graded rubrics are a last resort and must have an abstain outcome.

Good checks:

- protected files byte-identical (tests were not edited to pass);
- the fixture's test command exits 0;
- no forbidden constructs added (`sleep`, broad `except` returning success, new dependency files);
- only allowed files changed;
- the final message contains the required receipt, or the required stop receipt when the task is unreachable.

Record results with the runner version and a digest of the skill text so a later regression can be attributed. Do not commit raw transcripts.

## Routing evals

For a hub with many skills, keep a `routing-scenarios.json` of prompts and the single skill each should trigger. Grade the router's choice, not the work. Pair it with the description overlap check so both the static and the observed signal are covered.
