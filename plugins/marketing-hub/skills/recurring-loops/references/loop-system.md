# Marketing-loop system

## Qualify the loop

A loop is appropriate when a decision repeats, inputs and output are defined, cadence follows real change, no-action can be distinguished, state can be stored safely, success and harm are observable, and a human can pause or retire it.

Keep rare judgment, unstable platform behavior, one-off strategy, unbounded creative generation, and unauthorized external action outside autonomous scheduling.

## Specification

```yaml
name:
purpose:
trigger:
minimum_interval:
inputs:
source_freshness:
state_owner:
decision_rules:
outputs:
approval_required:
authorized_actions:
limits:
deduplication_key:
timeout:
retry_policy:
partial_failure:
metrics:
guardrails:
pause_conditions:
stop_conditions:
retention:
```

## State

Store last successful run, input watermark, decisions, drafted and executed artifacts, external identifiers, approvals, errors, next eligibility, and metrics required for comparison. Protect secrets and personal data. Bound history and define deletion.

Use idempotency based on the real side effect. Reconcile external state after ambiguous failure before retrying.

## Cadence

Set cadence from source change, cost of staleness, time to signal, operational capacity, and review need. Prefer events when reliable and timely. Use minimum intervals, quiet periods, and backpressure to prevent bursts.

## Approval layers

1. read and analyze;
2. recommend or draft;
3. approve;
4. mutate external state;
5. verify and reconcile.

Authorization for one run does not imply permanent authority. Bind account, action, audience, spend, volume, and time window.

## Catalog

### Acquisition and discovery

Search ranking and index anomaly review, programmatic-page quality sample, directory or listing freshness, competitor change monitor, AI-answer observation, content-decay review, and broken campaign-destination audit.

### Paid and creative

Campaign-health review, tracking discrepancy check, budget-risk alert, search-term and exclusion review, creative-fatigue evidence, concept-performance synthesis, policy or disapproval review, and experiment decision checkpoint.

### Conversion and lifecycle

Page or form error review, signup failure monitor, onboarding-stall synthesis, paywall and refund review, churn-risk evidence, payment-recovery state review, email collision and suppression audit, and messaging deliverability review.

### Customer and market

Support and research synthesis, review-theme change, win/loss update, competitor profile refresh, pricing and claim freshness, customer-proof permission audit, and product-context contradiction check.

### Social, partners, and events

Approved-source distribution queue, social-listening triage, community health review, creator deliverable and rights check, partner commitment tracker, referral-fraud review, and event-readiness checkpoint.

### Sales and revenue

Lead routing and SLA monitor, stale-owner escalation, prospect-data freshness, lifecycle-state hygiene, pipeline aging review, enablement asset expiry, and attribution reconciliation.

These are patterns, not preauthorized automations.

## Orchestration

For multi-skill loops, define each node's input, output, owner, state, failure, and approval. Carry the same marketing context, evidence labels, claim limits, audience identity, and metric definitions through every handoff. Avoid circular triggers and duplicate communications.

## Failure handling

Cover missing or stale input, invalid data, source outage, rejected approval, duplicate trigger, concurrent run, external timeout, ambiguous mutation, partial batch, policy change, metric regression, and unavailable owner. Fail closed for external action when authority or state is unclear.

Use bounded retries only for evidenced transient failures and safe idempotent operations. Escalate with evidence after the limit.

## Dry run and activation

Run against a fixed snapshot. Verify decision logic, no-action path, output usefulness, limits, logs, and one failure. Then use recommendation-only mode before external mutation unless risk is trivial and scope explicit.

## Loop report

Record trigger, input period, changes, decision, evidence, artifact, approval, action, external identifier, verification, measures, exceptions, and next eligibility. Retire the loop when its decision no longer creates value or the underlying process changes.
