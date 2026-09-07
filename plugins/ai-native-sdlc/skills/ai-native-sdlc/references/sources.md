# Sources and adaptation

Reviewed 2026-09-07. These links provide provenance, not runtime dependencies.

- Anthropic, [The AI-Native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook):
  motivation for connecting software-delivery stages through reviewable records,
  feedback, and accountable human decisions. This package is an independently
  written, provider-neutral application of those ideas. It does not reproduce
  the article, its prompts, diagrams, or vendor configurations, and is not an
  official Anthropic product or endorsed adaptation.
- [Agent Skills specification](https://agentskills.io/specification): the portable
  folder/frontmatter format and on-demand references. Product-specific plugin
  manifests supplement the skill; they are not requirements on the model.
- Anthropic, [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents):
  choose simpler implementations where they meet the need. Its tooling examples
  are dated; this package does not copy them as current integration instructions.
- MTEnt, [Graph Engineering v2.1.0](https://github.com/MTEnt/speshul-skills/tree/8c5e725a94fd6d0cb1d1e44f8ffe05cff7d9f35f/plugins/graph-engineering):
  scope boundaries, capability-aware coordination, evaluation, and recovery
  inform the optional relationship with executable workflows.

## Deliberate choices in this package

The process scales to the requested change and reuses its source of truth. It
does not require new intent/spec/plan files, approval at every stage, a particular
model, parallel agents, or a graph. Mandatory controls belong to the host or
application. Checks support bounded claims; neither a passing regression test
nor a second model establishes universal correctness. Monitoring and promotion
criteria must be selected and evaluated for the actual workload.

The repository's MIT license covers the original package materials. Referenced
third-party articles and specifications retain their own terms.
