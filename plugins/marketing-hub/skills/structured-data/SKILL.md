---
name: structured-data
description: Select, generate, implement, audit, and validate schema.org markup as JSON-LD for organizations, articles, products and offers, software, local businesses, events, video, breadcrumbs, and other supported types backed by visible page content. Use for rich-result eligibility work and structured-data audits; use search-health for the surrounding crawl and architecture problems.
license: MIT
metadata:
  version: "2.0.0"
  author: MTEnt
---

# Structured Data

Structured data describes truthful visible content; it does not create eligibility through markup alone.

If `.agents/marketing-context.md` exists, read it first; it is the truth file every skill in this hub shares, and its evidence states are constraints. Read [structured-data-workflow.md](references/structured-data-workflow.md) for source of truth, type selection, graph design, implementation, and validation. Read [schema-patterns.md](references/schema-patterns.md) for concrete entity shapes and the graph skeleton.

## Operating contract

1. Inspect the rendered page, entity model, authoritative values, and existing markup.
2. Verify currently supported search features and required properties from official documentation.
3. Choose the narrowest accurate types and stable identifiers; generate markup only from visible, supportable content.
4. Validate syntax, type semantics, feature eligibility where relevant, and rendered deployment.
5. State warnings, unsupported fields, ownership of freshness-sensitive values, and that valid markup does not guarantee a rich result.

Never mark up hidden reviews, invented ratings, unavailable products, fake FAQs, or misleading organization relationships.

## Return

Selected types and rationale, property-source map, complete JSON-LD, implementation location, validation results, warnings, ownership, and monitoring.
