---
name: tracking-plan
description: Design, implement, audit, and debug marketing measurement: metric dictionary, provider-neutral event contract, identity model, consent handling, GA4 and tag-manager mapping, campaign-parameter governance, and validation across debug, collection, processing, and reporting layers. Use when measurement must be established or tracking looks wrong; use credit-and-lift when the question is which marketing deserves the credit.
license: MIT
metadata:
  version: "2.0.0"
  author: MTEnt
---

# Tracking Plan

Start from the decisions the data must support. Code presence is not evidence that events arrive correctly or mean what reports claim.

If `.agents/marketing-context.md` exists, read it first; it is the truth file every skill in this hub shares, and its evidence states are constraints. Read [measurement-implementation.md](references/measurement-implementation.md) for the metric dictionary, event contract, identity, GA4 and tag-manager mapping, campaign parameters, and validation.

## Operating contract

1. Define business and customer decisions, metric tree, systems, identities, consent, environments, and data consumers.
2. Create a provider-neutral event contract before mapping tools.
3. Verify current official implementation guidance for the actual platforms.
4. Test representative journeys in debug, collection, processing, and reporting layers, recording expected and observed results.
5. Document discrepancies, latency, ownership, and known bias.

Do not send secrets, unnecessary personal data, raw sensitive text, or unbounded values, and do not mark work complete because a tag fired once.

## Return

Decision questions, metric dictionary, event plan, platform mappings, implementation instructions, parameter governance, consent and privacy constraints, QA evidence, discrepancies, dashboard requirements, and ownership.
