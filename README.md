# Speshul Skills

**Odd name. Serious tools for AI-assisted work.**

Speshul Skills is a maintained collection of reusable agent skills, installable plugins, focused MCP tools, and larger skill hubs. The packages here are built for real workflows: each one should make agent behavior more reliable, bounded, inspectable, or repeatable.

The repository supports more than one agent runtime. Standalone skills use `SKILL.md` as a portable entry point. Codex plugins can bundle skills with lifecycle hooks. MCP servers document their external access, permissions, and side effects inside their own package.

## Repository standards

Packages in this repository should have:

- a clear purpose and trigger
- self-contained instructions, dependencies, and installation notes
- explicit permissions, side effects, failure behavior, and safety limits
- deterministic scripts or tests when prompt instructions alone are not enough
- verification claims limited to checks that were actually run
- no committed credentials, private data, generated run artifacts, or machine-specific configuration

Not every package needs the same structure. It does need to be understandable and auditable without relying on undocumented context.

## Installable plugins

Plugins combine agent instructions with runtime components such as lifecycle hooks.

| Plugin | What it does |
| --- | --- |
| [`anti-amnesia`](./plugins/anti-amnesia/) | Answers questions about immediately preceding work from the existing conversation and tool record without needless reinspection, while preserving fresh verification for current-state questions. |
| [`anti-loop`](./plugins/anti-loop/) | Keeps coding work tied to the requested outcome, warns before permanent control surfaces expand, and stops repeated materially similar failed attempts. |
| [`temporal-tasks`](./plugins/temporal-tasks/) | Estimates substantive task difficulty and active-work budgets, then uses privacy-preserving lifecycle signals to trigger evidence-aware reassessment. |

Add this repository as a Codex plugin marketplace once:

```text
codex plugin marketplace add MTEnt/speshul-skills
```

Then install the plugin you want:

```text
codex plugin add anti-amnesia@speshul-skills
codex plugin add anti-loop@speshul-skills
codex plugin add temporal-tasks@speshul-skills
```

Start a new conversation after installation. These plugins include lifecycle hooks, so open `/hooks`, inspect each installed definition, and trust only the hooks you intend to run. Each plugin README contains its own installation, behavior, and verification details.

## Standalone skills

| Skill | What it does |
| --- | --- |
| [`cleancoding`](./cleancoding/) | Enforces root-cause fixes, a three-loop stop rule, explicit acceptance contracts, safe boundaries and state, authoritative documentation, measured performance, deployment recovery, and DRY, KISS, and YAGNI. |
| [`facebook-content-studio`](./facebook-content-studio/) | Researches, plans, continuity-checks, packages, and approval-gates Facebook content, with explicit routing to Higgsfield media workflows and the companion Page publisher. |
| [`graph-engineering`](./graph-engineering/) | Selects, designs, compiles, audits, diagnoses, optimizes, and evolves executable prompt, workflow, and agent graphs with typed state, bounded runtime semantics, security controls, and evaluation. |
| [`video-to-particle-field`](./video-to-particle-field/) | Reconstructs videos and images as dense live particle or ASCII fields, then preserves particle identity through scroll-controlled disintegration, reassembly, and multi-clip scene transitions. |

Copy a skill folder into the skill location used by your agent runtime, or point the runtime directly at that folder. Invoke the skill by its frontmatter name when explicit skill invocation is supported.

## Skill hubs

| Hub | What it contains |
| --- | --- |
| [`marketing-hub`](./marketing-hub/) | A separate collection of 64 original marketing skills: one orchestrator, domain routers, specialist skills, and provider-neutral integration guidance. |

## MCP tools

| Tool | What it does |
| --- | --- |
| [`facebook-pages-mcp`](./facebook-pages-mcp/) | Provides a local stdio MCP server for safely previewing, publishing, scheduling, and verifying allowlisted Facebook Page posts. |

MCP tool folders include their own installation, configuration, security, and verification instructions. They remain independently installable and do not rely on sibling skills at runtime.

## Typical skill structure

```text
skill-name/
├── SKILL.md              # Trigger description and core operating instructions
├── agents/
│   └── openai.yaml       # Optional runtime-specific metadata
├── references/           # Detailed material loaded only when needed
├── scripts/              # Optional deterministic utilities
└── assets/               # Optional reusable output resources
```

Keep the entry point concise. Put detailed procedures and conditional material in references, and include scripts only when deterministic execution materially improves reliability.

## Contributing

- Use lowercase, hyphen-separated package names.
- Give each skill a valid `SKILL.md` with `name` and `description` frontmatter.
- Keep packages self-contained and avoid undocumented dependencies on sibling folders.
- Document every external side effect and deliberately unsupported operation.
- Test executable code without calling live production APIs.
- Validate local links and the packed or installed artifact when packaging can change behavior.
- Never commit credentials, tokens, private data, or machine-specific state.

Before using any package with sensitive data, credentials, external messaging, destructive operations, or production systems, inspect its instructions and executable components yourself.
