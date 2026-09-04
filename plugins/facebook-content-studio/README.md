# Facebook Content Studio

Researches, plans, continuity-checks, packages, previews, and publishes Facebook Page content with explicit routing to Higgsfield media workflows and the companion `facebook-pages-mcp` publisher. The skill is a production director and safety gate: it never bypasses the approval step before anything reaches a Page.

## Package contents

| Path | Purpose |
| --- | --- |
| `skills/facebook-content-studio/SKILL.md` | Trigger, workflow, routing, and approval rules. |
| `skills/facebook-content-studio/references/` | Content strategy, continuity system, Higgsfield routing, Meta publishing. |
| `skills/facebook-content-studio/templates/` | Creative interview, campaign brief, continuity bible, asset registry, shot list, post-package schema. |
| `skills/facebook-content-studio/scripts/` | `validate-skill.mjs` (package structure) and `validate-post-package.mjs` (post package JSON). |
| `skills/facebook-content-studio/examples/` | A valid post package. |

## Install

Claude Code: `/plugin marketplace add MTEnt/speshul-skills` then `/plugin install facebook-content-studio@speshul-skills`.

Codex: `codex plugin marketplace add MTEnt/speshul-skills` then `codex plugin add facebook-content-studio@speshul-skills`.

Publishing requires the separately installed `facebook-pages-mcp` server from this repository with its own credentials. Video publication remains a documented manual handoff.

## Verify

```text
cd skills/facebook-content-studio
node scripts/validate-skill.mjs
node scripts/validate-post-package.mjs examples/post-package.example.json
```
