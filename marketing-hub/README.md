# Marketing Hub

An original, provider-neutral marketing skill collection for agent runtimes. The hub keeps the marketing release separate from the repository's standalone skills, MCP servers, and plugins.

The collection contains 64 independently usable skills: one `marketing-os` orchestrator, thirteen broad domain routers, and fifty specialist skills. Each package has its own `SKILL.md`; shared behavior is routed by skill name rather than copied into a second implementation.

## Domain routers

| Router | Scope |
| --- | --- |
| [`marketing-os`](./skills/marketing-os/) | Coordinates broad or connected marketing work. |
| [`marketing-context`](./skills/marketing-context/) | Product, audience, customer, competitor, proof, objection, and voice context. |
| [`marketing-strategy`](./skills/marketing-strategy/) | Plans, positioning, offers, pricing, ideas, behavioral analysis, budgets, and team execution. |
| [`conversion-optimization`](./skills/conversion-optimization/) | Pages, forms, signup, onboarding, activation, paywalls, cancellation, and churn. |
| [`copy-content`](./skills/copy-content/) | Marketing copy, editing, content systems, lead magnets, and free tools. |
| [`search-discovery`](./skills/search-discovery/) | Technical SEO, site structure, schema, AI discovery, ASO, comparisons, and directories. |
| [`paid-growth`](./skills/paid-growth/) | Paid media, creative, experiments, analytics, tracking, and attribution. |
| [`social-community`](./skills/social-community/) | Organic social, communities, creators, partnerships, referrals, and events. |
| [`lifecycle-messaging`](./skills/lifecycle-messaging/) | Lifecycle email, outbound email, and permissioned SMS. |
| [`sales-revenue`](./skills/sales-revenue/) | Prospecting, RevOps, routing, pipeline, and sales enablement. |
| [`launch-pr`](./skills/launch-pr/) | Product launches, announcements, press, and earned media. |
| [`marketing-media`](./skills/marketing-media/) | Marketing images, graphics, product captures, and video. |
| [`marketing-automation`](./skills/marketing-automation/) | Bounded recurring and trigger-driven marketing operations. |
| [`marketing-integrations`](./skills/marketing-integrations/) | Marketing APIs, MCPs, CLIs, connectors, and data exchange. |

## Specialist skills

| Domain | Skills |
| --- | --- |
| Context | [`product-marketing`](./skills/product-marketing/), [`customer-research`](./skills/customer-research/), [`competitor-profiling`](./skills/competitor-profiling/) |
| Strategy | [`marketing-plan`](./skills/marketing-plan/), [`offers`](./skills/offers/), [`pricing`](./skills/pricing/), [`marketing-ideas`](./skills/marketing-ideas/), [`marketing-psychology`](./skills/marketing-psychology/), [`marketing-council`](./skills/marketing-council/) |
| Conversion | [`cro`](./skills/cro/), [`signup`](./skills/signup/), [`onboarding`](./skills/onboarding/), [`popups`](./skills/popups/), [`paywalls`](./skills/paywalls/), [`churn-prevention`](./skills/churn-prevention/) |
| Copy and content | [`copywriting`](./skills/copywriting/), [`copy-editing`](./skills/copy-editing/), [`content-strategy`](./skills/content-strategy/), [`lead-magnets`](./skills/lead-magnets/), [`free-tools`](./skills/free-tools/) |
| Search and discovery | [`seo-audit`](./skills/seo-audit/), [`site-architecture`](./skills/site-architecture/), [`schema`](./skills/schema/), [`ai-seo`](./skills/ai-seo/), [`programmatic-seo`](./skills/programmatic-seo/), [`aso`](./skills/aso/), [`competitors`](./skills/competitors/), [`directory-submissions`](./skills/directory-submissions/) |
| Paid growth | [`ads`](./skills/ads/), [`ad-creative`](./skills/ad-creative/), [`ab-testing`](./skills/ab-testing/), [`analytics`](./skills/analytics/), [`attribution`](./skills/attribution/) |
| Social and community | [`social`](./skills/social/), [`community-marketing`](./skills/community-marketing/), [`influencer-marketing`](./skills/influencer-marketing/), [`co-marketing`](./skills/co-marketing/), [`referrals`](./skills/referrals/), [`events`](./skills/events/) |
| Lifecycle | [`emails`](./skills/emails/), [`cold-email`](./skills/cold-email/), [`sms`](./skills/sms/) |
| Sales and revenue | [`prospecting`](./skills/prospecting/), [`revops`](./skills/revops/), [`sales-enablement`](./skills/sales-enablement/) |
| Launch and PR | [`launch`](./skills/launch/), [`public-relations`](./skills/public-relations/) |
| Media | [`image`](./skills/image/), [`video`](./skills/video/) |
| Automation | [`marketing-loops`](./skills/marketing-loops/) |

## Install

List or install the hub through the direct repository path:

```text
npx skills add https://github.com/MTEnt/speshul-skills/tree/main/marketing-hub --list
npx skills add https://github.com/MTEnt/speshul-skills/tree/main/marketing-hub --skill marketing-os
```

Claude Code can install the complete collection through the repository marketplace:

```text
/plugin marketplace add MTEnt/speshul-skills
/plugin install speshul-marketing-os
```

The plugin points to the same canonical skill folders under `skills/`; it does not contain copied implementations.
