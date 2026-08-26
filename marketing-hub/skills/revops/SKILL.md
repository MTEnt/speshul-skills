---
name: revops
description: Design, audit, and improve revenue operations, including lifecycle definitions, MQL and SQL criteria, lead and account scoring, routing, SLAs, pipeline stages, CRM automation, deal desk, data hygiene, enrichment, forecasting inputs, and marketing-to-sales handoffs.
---

# Revops

Make commercial states observable, owned, and recoverable. A score or stage name cannot resolve organizational disagreement by itself.

If `.agents/marketing-context.md` exists, read it first. Read [revenue-operations-system.md](references/revenue-operations-system.md) for lifecycle, scoring, routing, automation, deal desk, hygiene, and reporting.

## Operating contract

1. Define the revenue process, systems, identities, owners, capacity, contracts, reporting decisions, and current failure evidence.
2. Give every lifecycle and pipeline stage observable entry, exit, ownership, timing, and recycle behavior.
3. Separate fit, intent, behavior, relationship, readiness, and negative evidence.
4. Specify automation with source of truth, mutation, idempotency, permissions, failure, reconciliation, and audit.
5. Test duplicates, missing fields, stale owners, capacity, out-of-office, conflicting account ownership, opt-out, retries, and partial failure.

Require authorization before changing CRM records, routing, assignments, scoring, automations, or dashboards used for compensation or forecasting.
