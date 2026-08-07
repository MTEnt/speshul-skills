# Speshul Skills

A growing collection of reusable skills and focused MCP tools for Codex and other agent runtimes.

Each top-level folder is a self-contained artifact. Skill folders use `SKILL.md` as their entry point. Tool folders include their own installation, configuration, security, and verification instructions.

## MCP servers

| Tool | What it does |
| --- | --- |
| [`facebook-pages-mcp`](./facebook-pages-mcp/) | Provides a local stdio MCP server for safely previewing, publishing, scheduling, and verifying allowlisted Facebook Page posts. |

## Skills

| Skill | What it does |
| --- | --- |
| [`cleancoding`](./cleancoding/) | Enforces root-cause fixes, a three-loop stop rule, explicit acceptance contracts, safe boundaries and state, authoritative documentation, measured performance, deployment recovery, and DRY, KISS, and YAGNI. |
| [`facebook-content-studio`](./facebook-content-studio/) | Researches, plans, continuity-checks, packages, and approval-gates Facebook content, with explicit routing to Higgsfield media workflows and the companion Page publisher. |
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

MCP server folders follow their own documented package structure. They must remain independently installable and must not rely on sibling skills at runtime.

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

## Adding MCP servers

- Keep the server narrowly scoped and document every external side effect.
- Keep credentials out of tool schemas, logs, fixtures, example commands, and commits.
- Include deterministic tests that do not call live production APIs.
- Document supported and deliberately unsupported operations.
- Verify the packed artifact as well as the source checkout.
