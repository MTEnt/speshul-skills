# Package standards

## Layout

```text
plugin-name/
├── .claude-plugin/plugin.json     # name, version, description, hooks path when present
├── .codex-plugin/plugin.json      # name, version, description, skills: "./skills/", interface
├── README.md                      # purpose, install, side effects, verification
├── CHANGELOG.md                   # newest first, dated, one line per user-visible change
├── skills/<skill-name>/
│   ├── SKILL.md                   # frontmatter + concise body
│   ├── agents/openai.yaml         # Codex display metadata
│   ├── references/                # loaded on demand
│   ├── scripts/                   # deterministic helpers, standard library preferred
│   └── assets/                    # templates and static resources
├── hooks/hooks.json               # optional lifecycle hooks (both runtimes read this file)
├── evals/                         # optional scenarios, rubric, runner, fixtures
└── tests/                         # package and hook tests, runnable with unittest
```

A single-skill plugin keeps the skill under `skills/<name>/` too. Consistency beats the one-directory saving.

## Frontmatter

```yaml
---
name: skill-name            # equals the directory name; lowercase, digits, single hyphens; max 64
description: ...            # 1 to 1024 characters; see description-writing.md
license: MIT                # optional
metadata:
  version: "1.2.0"          # required in this repository; semantic
  author: MTEnt
---
```

Do not add a top-level `version` key; the specification puts version under `metadata`. Multi-line descriptions use `description: |`.

## Manifests

Both manifests carry the same `name` and `version`. `name` equals the directory name. The Codex manifest needs `description` and `skills: "./skills/"`. When the plugin has hooks, the Claude Code manifest points at them with `"hooks": "./hooks/hooks.json"`; Codex discovers that path by default.

## Hooks that run on both runtimes

Reference scripts through `${CLAUDE_PLUGIN_ROOT}`; Codex exposes the same variable. Provide `command` for POSIX shells and `commandWindows` for Codex on Windows. Claude Code on Windows runs `command` through Git Bash, so the POSIX form must not assume `python3` exists:

```json
"command": "if command -v python >/dev/null 2>&1; then python \"${CLAUDE_PLUGIN_ROOT}/hooks/x.py\"; else python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/x.py\"; fi",
"commandWindows": "python \"${CLAUDE_PLUGIN_ROOT}/hooks/x.py\""
```

Event input differs slightly: Codex sends `turn_id` on turn-scoped events, Claude Code sends `prompt_id`. Accept either.

## Marketplaces

- Claude Code: `.claude-plugin/marketplace.json` at the repository root with `plugins[].source` as `./plugins/<name>`. Use `renames` when a plugin changes name so installed users migrate.
- Codex: `.agents/plugins/marketplace.json` with `source: {source: "local", path: "./plugins/<name>"}` and a `policy` block.

Every plugin directory must appear in both files; the repository validator fails otherwise.

## Shared rules

When more than one package must state the same rule, the rule lives once under `contracts/` and each package embeds it between `<!-- contract:<name>:start -->` and `<!-- contract:<name>:end -->` markers. The validator compares the embedded text byte for byte. Change the contract first, then re-embed everywhere in the same commit.

## Versioning

Bump `metadata.version` and both manifests together. Record the change in `CHANGELOG.md` with the date. A behavior change to a hook or a description is user-visible and gets an entry; reformatting does not.

## Status

State one of `stable`, `experimental`, or `draft` in the README of anything that is not stable. Do not ship research notes inside the package root; put them under `docs/`.
