# Speshul Skills

**Odd name. Serious tools for AI-assisted work.**

Speshul Skills is a maintained collection of agent plugins for Claude Code and Codex. Every package here is built to make agent behavior more reliable, bounded, inspectable, or repeatable, and every claim of that kind is backed by something you can run: a hook, a validator, a test, or an eval.

## Install

Add the marketplace once, then install what you need.

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

Every plugin installs the same way; substitute the name from the tables below. Plugins that ship lifecycle hooks say so in their README; review a hook before trusting it (`/hooks` in Codex). Start a new conversation after installing.

## Packages

| Plugin | Status | What it does | Enforcement |
| --- | --- | --- | --- |
| [`cleancoding`](./plugins/cleancoding/) | stable | Evidence-backed engineering: task contracts, root-cause fixes, DRY/KISS/YAGNI, the shared three-loop stop rule, receipt-based completion. | `Stop` hook requires a receipt after file changes; behavior eval suite with fixture repos. |
| [`anti-loop`](./plugins/anti-loop/) | stable | Keeps work scoped to the requested outcome and stops repeated failed attempts. | `PreToolUse` advisory on control files; stateful `PostToolUse` loop counter that enforces the stop rule. |
| [`anti-amnesia`](./plugins/anti-amnesia/) | stable | Answers "what did you just do" from the record and closes work with the shared receipt. | `SessionStart` policy hook. |
| [`temporal-tasks`](./plugins/temporal-tasks/) | stable | Difficulty scores, active-work budgets, and deterministic elapsed-time and repeated-call signals. | Four lifecycle hooks with SQLite state; tests with injected clocks. |
| [`untrusted-content`](./plugins/untrusted-content/) | stable | Treats fetched, file, tool, and agent content as data, never as instructions; reports injection attempts. | Prose only, by design. |
| [`skill-authoring`](./plugins/skill-authoring/) | stable | Writes and audits skills and plugins to this repository's standards. | `skill_lint.py`, the same linter the repository CI runs. |
| [`graph-engineering`](./plugins/graph-engineering/) | stable | Selects, designs, compiles, audits, diagnoses, optimizes, and evolves executable workflow graphs. | Seven JSON Schemas, deterministic validator, unit tests, behavior suite with recorded results. |
| [`ai-native-sdlc`](./plugins/ai-native-sdlc/) | experimental | Coordinates software delivery across lifecycle stages using existing records and provider-neutral capability mapping. | Advisory instructions; package validation and behavior scenarios. No runtime enforcement. |
| [`marketing-hub`](./plugins/marketing-hub/) | stable | One orchestrator and 43 specialist marketing skills organized by the decision each answers, sharing a truth file and deliverable contracts. | Description-overlap check, routing scenarios, script tests. |
| [`facebook-content-studio`](./plugins/facebook-content-studio/) | experimental | Plans, packages, and approval-gates Facebook Page content with routing to Higgsfield media workflows and the Pages MCP. | Package and post-package validators in CI. |
| [`video-to-particle-field`](./plugins/video-to-particle-field/) | experimental | Reconstructs video and images as live particle or ASCII fields with stable particle identity and scroll-driven transitions. | Media inspection script; React asset. |

MCP server, installed separately:

| Tool | What it does |
| --- | --- |
| [`facebook-pages-mcp`](./facebook-pages-mcp/) | Local stdio MCP server for safely previewing, publishing, scheduling, and verifying allowlisted Facebook Page posts. Own README, tests, CI, and security policy. |

## Shared contracts

Rules that more than one package enforces live once under [`contracts/`](./contracts/) and are embedded verbatim, between marker comments, by each package that uses them. The repository validator fails when an embedded copy drifts.

| Contract | What it fixes | Used by |
| --- | --- | --- |
| [Task contract](./contracts/task-contract.schema.json) | One field set for the acceptance contract, task anchor, and budget line. | `cleancoding`, `anti-loop`, `temporal-tasks` |
| [Repeated-attempt stop rule](./contracts/loop-limit.md) | One definition of a loop and one `LOOP LIMIT REACHED` receipt. | `cleancoding`, `anti-loop` (hook-enforced) |
| [Handoff receipt](./contracts/handoff-receipt.md) | One `RECEIPT` block that closes work and that later recall reads from. | `cleancoding` (hook-enforced), `anti-amnesia` |

## Repository standards

Every package has:

- a `SKILL.md` under 10 KB with a description written as a routing key, and references loaded on demand;
- manifests for both runtimes with the same name and version, a README, and a dated CHANGELOG;
- explicit permissions, side effects, failure behavior, and safety limits;
- deterministic scripts or hooks where prompt text alone would not hold, and tests for them;
- no committed credentials, private data, generated artifacts, or machine-specific configuration.

The full standard, with layout and cross-runtime hook conventions, is in [`skill-authoring`](./plugins/skill-authoring/skills/skill-authoring/references/package-standards.md).

## Verify locally

```text
python scripts/validate_repo.py --strict-overlap
python -m unittest discover -s scripts/tests
for p in plugins/*/; do [ -d "$p/tests" ] && (cd "$p" && python -m unittest discover -s tests); done
```

CI runs the same commands on Linux and Windows for each pull request, plus the package-specific suites listed in [`.github/workflows/ci.yml`](./.github/workflows/ci.yml).

## Contributing

- Use lowercase, hyphen-separated package and skill names; the skill name equals its directory name.
- Keep packages self-contained; the only cross-package dependency allowed is a verbatim contract embed.
- Document every external side effect and deliberately unsupported operation.
- Test executable code without calling live production APIs.
- Run the validator and the affected test suites before opening a pull request.

Before using any package with sensitive data, credentials, external messaging, destructive operations, or production systems, inspect its instructions and executable components yourself.

## License

MIT. See [LICENSE](./LICENSE).
