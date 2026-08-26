---
name: analytics
description: Design, implement, audit, debug, and document marketing analytics, event tracking, GA4, Google Tag Manager, product analytics, conversion events, UTM governance, metric definitions, identity, consent, and reporting QA. Use when measurement must be established or tracking appears wrong.
---

# Analytics

Start from decisions the data must support. Code presence is not evidence that events arrive correctly or mean what reports claim.

If `.agents/marketing-context.md` exists, read it first. Read [measurement-implementation.md](references/measurement-implementation.md) for metric definitions, event design, GA4/GTM mapping, UTMs, privacy, and validation.

## Operating contract

1. Define business and customer decisions, metric tree, systems, identities, consent, environments, and data consumers.
2. Create a provider-neutral event contract before mapping tools.
3. Verify current official implementation guidance for the actual platforms.
4. Test representative journeys in debug, collection, processing, and reporting layers.
5. Document discrepancies, latency, ownership, and known bias.

Do not send secrets, unnecessary personal data, raw sensitive text, or unbounded values. Do not mark work complete because a tag fired once.
