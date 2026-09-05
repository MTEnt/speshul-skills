# Skill Authoring

Writes and audits agent skills and plugins to the standards this repository uses: routing-grade descriptions, a concise `SKILL.md` with references loaded on demand, self-contained packages, versions in the right place, hooks where prose is not enough, and evals for claimed behavior.

## Package contents

| Path | Purpose |
| --- | --- |
| `skills/skill-authoring/SKILL.md` | Operating contract for writing and auditing skills. |
| `skills/skill-authoring/references/description-writing.md` | How to write a description that routes, with the overlap rule. |
| `skills/skill-authoring/references/package-standards.md` | Layout, frontmatter, manifests, cross-runtime hooks, marketplaces, shared contracts, versioning. |
| `skills/skill-authoring/references/hooks-and-evals.md` | When a rule needs a hook, hook discipline, when a behavior needs an eval, routing evals. |
| `skills/skill-authoring/scripts/skill_lint.py` | Deterministic linter for one skill or a directory of siblings. The repository validator imports it, so the rules exist once. |
| `skills/skill-authoring/tests/` | Linter tests. |

## Install

Claude Code: `/plugin marketplace add MTEnt/speshul-skills` then `/plugin install skill-authoring@speshul-skills`.

Codex: `codex plugin marketplace add MTEnt/speshul-skills` then `codex plugin add skill-authoring@speshul-skills`.

## Use the linter directly

```text
python skills/skill-authoring/scripts/skill_lint.py path/to/skill
python skills/skill-authoring/scripts/skill_lint.py --siblings path/to/skills --strict-overlap
```

The linter reads files only and has no dependencies beyond the Python standard library.
