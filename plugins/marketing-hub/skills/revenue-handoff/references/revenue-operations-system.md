# Revenue-operations system

## Lifecycle

For every state define purpose, observable entry event, required fields, identity scope, owner, allowed actions, exit event, maximum age or review, recycle, disqualification, suppression, and reporting definition.

Possible states include anonymous audience, known person, engaged account, captured lead, qualified for marketing, sales-accepted, active opportunity, customer, expansion, recycled, disqualified, and churned. Use only states the operating model needs.

Do not use MQL or SQL until required evidence and accountable action are agreed.

## Scoring

Separate fit, behavior, declared intent, product signal, relationship, and negative evidence. For each rule specify source event, value, decay, cap, duplicates, missing-data handling, exclusion, threshold, owner, and recalibration. Validate relationship to actual qualification and retained outcomes where data permits.

Protect against bots, internal traffic, inflated activity, shared accounts, sensitive proxies, and gaming.

## Routing and SLA

Define route key, priority, territory or segment, account ownership, capacity, round robin where used, conflicts, duplicates, out-of-office, acceptance deadline, failed assignment, escalation, recycle, and audit trail. Reconcile state before retrying notifications or assignments.

## Pipeline

Every stage needs customer evidence, exit criteria, amount and date rules, next action, owner, age expectation, probability only when empirically grounded, and closed-lost taxonomy. Prevent stage changes made solely to improve reports.

## CRM automations

For each workflow record trigger, conditions, source of truth, state read, mutation, owner, permissions, idempotency key, duplicate handling, timeout, retry bounds, partial failure, reconciliation, monitoring, rollback or correction, and retirement.

Common workflows include intake, enrichment, matching, scoring, assignment, alerts, SLA escalation, opportunity creation, stage validation, nurture eligibility, stale-record review, customer handoff, renewal, and suppression.

## Deal desk

Define when approval is required for price, discount, terms, security, legal, implementation, billing, and nonstandard commitments; required evidence; approvers; SLA; conflict; expiration; order form; and audit trail. Do not let informal chat approval become the system of record.

## Data hygiene

Define account and person identity, duplicate matching, merge authority, field ownership, required fields by state, source and freshness, invalid values, enrichment, consent and suppression, retention, deletion, access, audit cadence, and remediation owner.

## Dashboard

Specify volume and conversion by lifecycle transition, time in state, acceptance and response, pipeline and revenue by cohort and source, quality and disqualification, aging, data completeness, forecast inputs, and attribution definitions. Preserve reporting limitations.

## Output

Return lifecycle table, scoring model, routing and SLA, pipeline definitions, automation contracts, deal-desk rules, hygiene controls, metric dictionary, migration and recovery, and unresolved ownership decisions.
