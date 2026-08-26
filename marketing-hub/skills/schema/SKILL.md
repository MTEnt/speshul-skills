---
name: schema
description: Select, generate, implement, audit, and validate schema.org structured data and search-feature markup, usually as JSON-LD. Use for Organization, Product, SoftwareApplication, Article, BreadcrumbList, LocalBusiness, Event, VideoObject, FAQ, or other supported types backed by visible page content.
---

# Schema

Structured data describes truthful visible content; it does not create eligibility through markup alone.

If `.agents/marketing-context.md` exists, read it first. Read [structured-data-workflow.md](references/structured-data-workflow.md) for type selection, graph design, generation, validation, and deployment. Read [schema-patterns.md](references/schema-patterns.md) when the task needs a concrete JSON-LD shape or page-to-entity mapping.

## Operating contract

1. Inspect the rendered page, entity model, authoritative values, and existing markup.
2. Verify currently supported search features and required properties from official documentation.
3. Choose the narrowest accurate types and stable identifiers.
4. Generate valid markup only from visible, supportable content.
5. Validate syntax, type semantics, search-feature eligibility where relevant, and rendered deployment.
6. State warnings, unsupported fields, and that valid markup does not guarantee a rich result.

Never mark up hidden reviews, invented ratings, unavailable products, fake FAQs, or misleading organization relationships.
