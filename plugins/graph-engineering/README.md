# Graph Engineering

Selects, designs, compiles, audits, diagnoses, optimizes, and evolves executable prompt, workflow, and agent graphs as explicit, versioned artifacts with typed state, bounded runtime semantics, security controls, and evaluation.

## Package contents

| Path | Purpose |
| --- | --- |
| `skills/graph-engineering/SKILL.md` | Boundary, mode and profile selection, shared invariants, reference routing. |
| `skills/graph-engineering/references/` | Philosophy, playbook, topologies, runtime and recovery, coordination, optimization and evolution, security, evaluation, framework mappings (including the Claude Code `Workflow` tool), high-assurance profile. |
| `skills/graph-engineering/schemas/` | Seven public JSON Schemas: GraphSpec, GraphDecision, GraphAudit, RunDiagnosis, OptimizationPlan, EvolutionProposal, ImplementationMapping. |
| `skills/graph-engineering/scripts/graph_tool.py` | Deterministic validator and renderer. It never executes workflows, models, or network calls. |
| `skills/graph-engineering/templates/`, `tests/`, `evals/` | Templates, fixtures, golden files, unit tests, and the fresh-session behavior suite with its recorded results. |

## Install

Claude Code: `/plugin marketplace add MTEnt/speshul-skills` then `/plugin install graph-engineering@speshul-skills`.

Codex: `codex plugin marketplace add MTEnt/speshul-skills` then `codex plugin add graph-engineering@speshul-skills`.

## Verify

```text
cd skills/graph-engineering
python -m unittest discover -s tests -v
python scripts/graph_tool.py validate templates/graph-spec.json
python evals/run_behavior_suite.py --output evals/behavior-results.json   # needs codex
```
