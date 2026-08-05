# Speshul Skills

A growing collection of reusable skills for Codex and other agent runtimes that support the `SKILL.md` convention.

Each top-level folder is a self-contained skill. Skills may include concise operating instructions, UI metadata, detailed references, deterministic scripts, or reusable assets. The exact contents depend on what the skill needs; `SKILL.md` is the entry point.

## Skills

| Skill | What it does |
| --- | --- |
| [`cleancoding`](./cleancoding/) | Enforces root-cause fixes, a three-loop stop rule, explicit acceptance contracts, safe boundaries and state, authoritative documentation, measured performance, deployment recovery, and DRY, KISS, and YAGNI. |
| [`graph-engineering`](./graph-engineering/) | Designs, simplifies, and audits AI-assisted workflow graphs. It selects the smallest useful topology and defines node contracts, state, evidence checks, bounded retries, approval gates, safe execution, and evaluation. |

## Typical structure

```text
skill-name/
├── SKILL.md              # Trigger description and core operating instructions
├── agents/
│   └── openai.yaml       # Optional UI metadata
├── references/           # Detailed material loaded only when needed
├── scripts/              # Optional deterministic utilities
└── assets/               # Optional reusable output resources
```

Not every skill needs every directory. Keep the main instructions concise and move detailed material into references.

## Using a skill

Copy the required skill folder into the skill location used by your agent runtime, or point the runtime directly at the folder. Invoke it by its frontmatter name when explicit skill invocation is supported.

Always inspect a skill before using it with sensitive data, credentials, external messaging, destructive operations, or production systems.

## Adding skills

- Use a lowercase, hyphen-separated folder name.
- Include a valid `SKILL.md` with `name` and `description` frontmatter.
- Keep each folder self-contained and avoid dependencies on unrelated skills.
- Put long documentation in `references/` and load it progressively.
- Test included scripts and validate local links before committing.
- Do not commit credentials, tokens, private data, generated run artifacts, or machine-specific configuration.
