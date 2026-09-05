# Measurement implementation

## Metric dictionary

For every material metric define name, decision, meaning, numerator, denominator, eligible population, exclusions, event source, identity, deduplication, time zone, cohort and attribution window, latency, owner, validation, and known bias.

Build a tree from business outcome to customer outcome, key behavior, journey transitions, diagnostics, and guardrails.

## Event contract

```text
Event name:
Object and action:
Exact trigger and source of truth:
Required properties and allowed values:
Identity state:
Consent and sensitive-data treatment:
Duplicate, retry, offline, and ordering behavior:
Environments:
Validation:
Downstream consumers:
Owner and version:
```

Use stable behavior names, not tool names. Define page or screen view, lead, signup, activation, purchase, subscription, retention, referral, sales, and error events only where the product and decision need them.

## Identity

Define anonymous, session, user, account, device, lead, and contact IDs; when they are created; permitted stitching; logout; account switch; shared devices; cross-domain behavior; deletion; and downstream mapping. Avoid silently merging people from weak identifiers.

## GA4 mapping

Map neutral events to current recommended or custom GA4 events, parameters, user properties only when appropriate, key-event configuration, ecommerce objects, consent behavior, cross-domain settings, internal traffic, referral exclusions, retention, and BigQuery export where used. Verify current limits and names in official documentation.

## Google Tag Manager

Define data-layer contract, trigger, variables, tags, environments, consent initialization, sequencing, error behavior, version naming, review, preview tests, and publication approval. Keep business logic in the application or data layer where it is authoritative rather than reconstructing it from fragile DOM selectors.

## Campaign parameters

Govern source, medium, campaign, content or creative, term where useful, geography or business unit if needed, casing, separators, controlled vocabulary, owner, redirects, persistence, invalid values, and raw capture. Do not overwrite newer valid touchpoints unintentionally.

## Validation

Test consent states, expected count, absence of duplicates, property types and values, identity, cross-domain or app transitions, blockers, offline behavior, refunds, delayed events, receiving tools, warehouse, reports, and conversion configuration. Record time, environment, test identity, expected result, observed result, and evidence.

## Output

Return decision questions, metric dictionary, event plan, platform mappings, implementation instructions, UTM governance, consent and privacy constraints, QA evidence, discrepancies, dashboard requirements, and ownership.
