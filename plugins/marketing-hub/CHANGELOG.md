# Changelog

## 2.0.0 - 2026-09-05

- Redesigned the taxonomy from 64 channel-named skills and 13 routers into one orchestrator plus 43 specialists organized by the decision each answers (Evidence, Decision, Make, Convert, Reach, Discover, Measure, Operate).
- Added `constraint-diagnosis` as the explicit entry point before any channel work, with the journey diagnostic and diagnosis record.
- Merged skills that answered the same question (for example signup and onboarding into `activation-path`; email and SMS into `lifecycle-messaging`; competitor dossiers and comparison pages into `alternatives-map`).
- Rewrote every description with a boundary sentence naming the sibling that takes adjacent requests; the repository validator enforces a description-overlap limit.
- Added `evals/routing-scenarios.json` with one expected skill per prompt.
- Replaced the version 1 capability map (organized around an external reference list) with a stage-based map, and replaced the provenance note with a design-provenance note.
- Plugin name changed from `speshul-marketing-os` to `marketing-hub`; the Claude Code marketplace carries a rename entry.

### Old name to new owner

| Version 1 skill | Version 2 owner |
| --- | --- |
| `ab-testing` | `experiment-design` |
| `ad-creative` | `ad-units` |
| `ads` | `paid-media` |
| `ai-seo` | `answer-engine-visibility` |
| `analytics` | `tracking-plan` |
| `aso` | `third-party-listings` |
| `attribution` | `credit-and-lift` |
| `churn-prevention` | `retention-recovery` |
| `co-marketing` | `creator-partnerships` |
| `cold-email` | `outbound-prospecting` |
| `community-marketing` | `community-programs` |
| `competitor-profiling` | `alternatives-map` |
| `competitors` | `alternatives-map` |
| `content-strategy` | `content-engine` |
| `conversion-optimization` | `page-conversion` |
| `copy-content` | `page-copy` |
| `copy-editing` | `copy-review` |
| `copywriting` | `page-copy` |
| `cro` | `page-conversion` |
| `customer-research` | `customer-evidence` |
| `directory-submissions` | `third-party-listings` |
| `emails` | `lifecycle-messaging` |
| `events` | `field-events` |
| `free-tools` | `capture-assets` |
| `image` | `visual-assets` |
| `influencer-marketing` | `creator-partnerships` |
| `launch` | `launch-runbook` |
| `launch-pr` | `launch-runbook` |
| `lead-magnets` | `capture-assets` |
| `marketing-automation` | `recurring-loops` |
| `marketing-context` | `truth-file` |
| `marketing-council` | `decision-lenses` |
| `marketing-ideas` | `tactic-portfolio` |
| `marketing-integrations` | `tool-connectors` |
| `marketing-loops` | `recurring-loops` |
| `marketing-media` | `visual-assets` |
| `marketing-plan` | `growth-plan` |
| `marketing-psychology` | `behavior-design` |
| `marketing-strategy` | `growth-plan` |
| `offers` | `positioning-and-offer` |
| `onboarding` | `activation-path` |
| `paid-growth` | `paid-media` |
| `paywalls` | `upgrade-moments` |
| `popups` | `page-conversion` |
| `pricing` | `pricing-and-packaging` |
| `product-marketing` | `truth-file` |
| `programmatic-seo` | `template-pages` |
| `prospecting` | `outbound-prospecting` |
| `public-relations` | `press-kit` |
| `referrals` | `advocacy-loops` |
| `revops` | `revenue-handoff` |
| `sales-enablement` | `sales-kit` |
| `sales-revenue` | `revenue-handoff` |
| `schema` | `structured-data` |
| `search-discovery` | `search-health` |
| `seo-audit` | `search-health` |
| `signup` | `activation-path` |
| `site-architecture` | `search-health` |
| `sms` | `lifecycle-messaging` |
| `social` | `organic-social` |
| `social-community` | `organic-social` |
| `video` | `video-assets` |

## 1.0.0 - 2026-08-26

- Initial hub: 64 skills, 13 routers, and `marketing-os`.
