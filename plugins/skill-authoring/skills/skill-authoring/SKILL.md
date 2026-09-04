---
name: skill-authoring
description: Write, restructure, or audit an agent skill or plugin so it is concise, correctly triggered, self-contained, versioned, and installable on Claude Code and Codex. Use when creating a SKILL.md, tightening a skill description, splitting an oversized skill into references, adding hooks or evals to a plugin, packaging a marketplace, or checking why a skill misroutes or fails validation.
license: MIT
metadata:
  version: "1.0.0"
  author: MTEnt
---

# Skill Authoring

A skill is a contract with a router and a reader. The router sees only `name` and `description`; the reader loads `SKILL.md` and then only the references it needs. Write for both.

## Operating contract

1. Define the skill's job in one sentence, the requests that must trigger it, and the nearby requests that must not. If the second list is empty, the skill is too broad.
2. Write the description last, from the trigger lists, following [description-writing.md](references/description-writing.md).
3. Keep `SKILL.md` under 10 KB and 500 lines: operating contract, workflow selection, and routing to references. Move procedures, catalogs, templates, and rarely needed rules into `references/` with a one-line trigger for each.
4. Make the package self-contained: no links outside the skill directory, no dependence on sibling packages at runtime, every script standard-library or clearly documented.
5. Declare version, license, side effects, permissions, and failure behavior in the package. Follow [package-standards.md](references/package-standards.md) for layout, manifests, and marketplaces.
6. Enforce behavior in code when it matters: a rule that must hold under pressure belongs in a hook or a deterministic script, not only in prose. See [hooks-and-evals.md](references/hooks-and-evals.md).
7. Run `python scripts/skill_lint.py <skill-dir>` before presenting the skill. Fix errors; treat warnings as review items.

## Audit an existing skill

Read the description first and predict the requests it will capture. Then read the body and answer:

- Does the body do what the description promises, and nothing the description hides?
- Which sentences would change agent behavior if deleted? Keep those; move or cut the rest.
- Where does the skill repeat a rule that another package owns? Embed the shared block verbatim or reference it; do not paraphrase.
- Which rules could a model silently skip? Those are hook or eval candidates.
- What evidence exists that the skill works? If none, write the two or three scenarios that would show it.

Report findings as: trigger defects, body defects, packaging defects, enforcement gaps, and evidence gaps, each with the exact file and line.

## Do not

- Do not write a description that is a summary of the body; it is a routing key.
- Do not add sections because a template has them.
- Do not create a plugin for a rule that a hook cannot enforce and an eval cannot observe; a sentence in an existing skill is cheaper.
- Do not claim a skill was tested unless the lint passed and a scenario ran.
