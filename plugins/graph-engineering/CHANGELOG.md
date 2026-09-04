# Changelog

## 2.1.0 - 2026-09-05

- Moved to the plugin layout (`skills/graph-engineering/`) and listed in both marketplaces.
- Added a compile target for the Claude Code `Workflow` tool to `references/framework-mappings.md`.
- Clarified routing for run traces: a trace that names its graph id and version routes to `diagnose`; `no_graph_artifact` is reserved for material that is asked to be classified or that carries no graph identity. The inline-prompt eval exposed this ambiguity, which the earlier file-blocked runs had masked.
- The behavior suite now embeds the skill and fixture text in the routing prompt instead of asking the model to read files, so results no longer depend on the runner's sandbox file policy (Codex on Windows rejected the shell reads and produced an unverified misroute). `behavior-results.json` regenerated.
- Added `metadata.version` to the skill frontmatter and this changelog.

## 2.0.0 - 2026-08-27

- Seven explicit modes with public JSON Schemas, assurance profiles, deterministic `graph_tool.py` validation and rendering, behavior eval suite, and regression record.

## 1.0.0 - 2026-08-05

- Initial skill.
