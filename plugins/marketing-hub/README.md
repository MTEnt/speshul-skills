# Marketing Hub

An evidence-to-artifact marketing operating system for agent runtimes: one orchestrator and 43 specialist skills organized by the decision each one answers, sharing a truth file, evidence states, a claim ledger, and deliverable contracts.

## How it is organized

Marketing work moves through eight stages. Each skill owns one question in one stage; the orchestrator routes between them and carries the same evidence, claim limits, and metric definitions across every handoff.

| Stage | Skills |
| --- | --- |
| **Orchestrate** | [`marketing-os`](./skills/marketing-os/) |
| **Evidence** | [`truth-file`](./skills/truth-file/), [`customer-evidence`](./skills/customer-evidence/), [`alternatives-map`](./skills/alternatives-map/) |
| **Decision** | [`constraint-diagnosis`](./skills/constraint-diagnosis/), [`growth-plan`](./skills/growth-plan/), [`positioning-and-offer`](./skills/positioning-and-offer/), [`pricing-and-packaging`](./skills/pricing-and-packaging/), [`tactic-portfolio`](./skills/tactic-portfolio/), [`decision-lenses`](./skills/decision-lenses/), [`behavior-design`](./skills/behavior-design/) |
| **Make** | [`page-copy`](./skills/page-copy/), [`copy-review`](./skills/copy-review/), [`content-engine`](./skills/content-engine/), [`capture-assets`](./skills/capture-assets/), [`visual-assets`](./skills/visual-assets/), [`video-assets`](./skills/video-assets/), [`ad-units`](./skills/ad-units/), [`sales-kit`](./skills/sales-kit/), [`press-kit`](./skills/press-kit/) |
| **Convert** | [`page-conversion`](./skills/page-conversion/), [`activation-path`](./skills/activation-path/), [`upgrade-moments`](./skills/upgrade-moments/), [`retention-recovery`](./skills/retention-recovery/) |
| **Reach** | [`paid-media`](./skills/paid-media/), [`organic-social`](./skills/organic-social/), [`community-programs`](./skills/community-programs/), [`creator-partnerships`](./skills/creator-partnerships/), [`advocacy-loops`](./skills/advocacy-loops/), [`field-events`](./skills/field-events/), [`lifecycle-messaging`](./skills/lifecycle-messaging/), [`outbound-prospecting`](./skills/outbound-prospecting/) |
| **Discover** | [`search-health`](./skills/search-health/), [`structured-data`](./skills/structured-data/), [`answer-engine-visibility`](./skills/answer-engine-visibility/), [`template-pages`](./skills/template-pages/), [`third-party-listings`](./skills/third-party-listings/) |
| **Measure** | [`tracking-plan`](./skills/tracking-plan/), [`credit-and-lift`](./skills/credit-and-lift/), [`experiment-design`](./skills/experiment-design/) |
| **Operate** | [`launch-runbook`](./skills/launch-runbook/), [`revenue-handoff`](./skills/revenue-handoff/), [`recurring-loops`](./skills/recurring-loops/), [`tool-connectors`](./skills/tool-connectors/) |

Design commitments that every skill honors:

- **One truth file.** `.agents/marketing-context.md`, built by `truth-file`, is read first by every skill and updated in place; evidence states (verified, user-provided, analysis, hypothesis, unknown) travel with each fact.
- **Constraint before channel.** `constraint-diagnosis` locates the weakest evidenced journey transition; plans and tactics follow it.
- **Contracts, not templates.** Each skill has a fixed operating contract, a named return, and a prohibition line. `marketing-os` picks the smallest deliverable contract that fits.
- **Authorization for side effects.** No skill publishes, spends, contacts people, imports data, or changes a live account without task-specific authorization.
- **Routing is tested.** `evals/routing-scenarios.json` pairs prompts with the single skill that should fire; the repository validator fails when two descriptions overlap enough to make that ambiguous.

## Install

Claude Code:

```text
/plugin marketplace add MTEnt/speshul-skills
/plugin install marketing-hub@speshul-skills
```

Codex:

```text
codex plugin marketplace add MTEnt/speshul-skills
codex plugin add marketing-hub@speshul-skills
```

Individual skills can be copied from `skills/<name>/`; each is self-contained apart from the shared truth file convention.

## Scripts

- `skills/experiment-design/scripts/sample_size.py`: equal-allocation sample-size estimates for proportions and means.
- `skills/tool-connectors/scripts/api_request.py`: bounded, provider-neutral HTTPS client with dry run, credential-from-environment, and an explicit write gate. Tests in the same directory.

## Upgrading from version 1

Version 1 had 64 skills named by channel with 13 routers. Version 2 merges and renames them into the stage layout above; `CHANGELOG.md` lists every old name and its new owner. The truth file path is unchanged.
