# Evidence ledger

This ledger deliberately withholds all identifying and exact internal project data. “Private review” means a read-only inspection of the project board, linked work items, repository tree, current agent instructions, and recent history on 2026-08-26.

| Claim | Evidence | Confidence | Limitation or counterevidence |
|---|---|---:|---|
| Workflow machinery repeatedly creates maintenance work for itself | Private review showed multiple work items whose initiating defect arose from interactions among workflow tools, gates, shared state, generated guidance, or lifecycle rules | High | The fixes may still be individually necessary |
| The control plane competes with product delivery | Private review found workflow and hygiene work deeply embedded in the project’s active planning and recent history | High | A workflow hub is expected to contain more process work than a product repository |
| The instruction surface is broad and exception-heavy | Private review of the canonical agent instructions found safety, product, Git, environment, evidence, routing, test, authority, coordination, and recovery rules in one contract | High | Breadth alone does not show that any specific rule is wrong |
| Future scope creates present cognitive load even when blocked | Private review found deferred future work already decomposed into detailed architecture, tasks, dependencies, and gates | High | Early design work can reduce later uncertainty; the net value was not measured |
| Cross-harness directories are simple duplicate copies | Private review disproved this broad claim: most corresponding entries are shared links | Rejected | Do not use directory counts as duplication evidence |
| The project record proves AI caused the bureaucracy | It does not | Rejected | Causality is not recoverable from the board and repository alone |
| Long context can make instruction adherence harder | Peer-reviewed long-context instruction-following research reports adherence challenges in extended conversations | Medium-high | Experiments used selected models and tasks; results do not quantify this private project |
| Coding-agent configuration bloat and conflicting instructions are recognized smells | A recent repository-mining preprint proposes and detects context bloat, lint leakage, skill leakage, and conflicting instructions | Medium | Recent preprint; heuristics and sample may not generalize |
| Automated success can overstate real-world usefulness | METR compared automatic scoring with holistic review and found some functionally correct agent work was not readily usable | Medium | Small, selected task sample and earlier model generation |
| Developer perception can diverge from measured AI productivity | METR’s randomized study found a gap between expected/self-reported and measured completion effects in experienced maintainers | Medium | Narrow population, older tools, and not evidence of a universal slowdown |
| AI assistance necessarily damages maintainability | A controlled experiment did not find systematic downstream maintainability harm in its task setting | Rejected | Other settings may differ; this is useful counterevidence against overclaiming |
| A Codex hook can fully enforce anti-loop policy | Official documentation says supported local tool calls can be inspected or blocked, but hook coverage is not complete | Rejected | Hosted and specialized tool paths may not be intercepted |

## External sources

- [Official OpenAI Hooks documentation](https://learn.chatgpt.com/docs/hooks)
- [Long-context instruction-following study, EACL Findings](https://aclanthology.org/2026.findings-eacl.254/)
- [Coding-agent configuration-smell preprint](https://arxiv.org/abs/2606.15828)
- [METR: algorithmic versus holistic evaluation](https://metr.org/blog/2025-08-12-research-update-towards-reconciling-slowdown-with-time-horizons/)
- [METR: randomized developer productivity study](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)
- [Controlled downstream maintainability experiment](https://arxiv.org/abs/2507.00788)
