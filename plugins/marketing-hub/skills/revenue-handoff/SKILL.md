---
name: revenue-handoff
description: Make the marketing-to-sales system observable and recoverable: lifecycle stage definitions, qualification criteria, lead and account scoring, routing and SLAs, pipeline stages, CRM automation contracts, deal desk rules, data hygiene, and forecasting inputs. Use for revenue operations and handoff failures; use outbound-prospecting for list building and sales-kit for seller-facing assets.
license: MIT
metadata:
  version: "2.0.0"
  author: MTEnt
---

# Revenue Handoff

Make commercial states observable, owned, and recoverable. A score or stage name cannot resolve organizational disagreement by itself.

If `.agents/marketing-context.md` exists, read it first; it is the truth file every skill in this hub shares, and its evidence states are constraints. Read [revenue-operations-system.md](references/revenue-operations-system.md) for lifecycle, scoring, routing, pipeline, automations, deal desk, hygiene, and the dashboard.

## Operating contract

1. Define the revenue process, systems, identities, owners, capacity, contracts, reporting decisions, and current failure evidence.
2. Give every lifecycle and pipeline stage observable entry, exit, ownership, timing, and recycle behavior.
3. Separate fit, intent, behavior, relationship, readiness, and negative evidence instead of one unexplained score.
4. Specify automation with source of truth, mutation, idempotency, permissions, failure, reconciliation, and audit.
5. Test duplicates, missing fields, stale owners, capacity, out-of-office, conflicting ownership, opt-out, retries, and partial failure.

Do not change CRM records, routing, assignments, scoring, automations, or dashboards used for compensation or forecasting without authorization.

## Return

Lifecycle table, scoring model, routing and SLA, pipeline definitions, automation contracts, deal-desk rules, hygiene controls, metric dictionary, migration and recovery, and unresolved ownership decisions.
