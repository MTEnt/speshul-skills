---
name: upgrade-moments
description: Design, audit, or optimize the in-product moments where an existing user is asked to begin or increase a paid commitment: paywalls, upgrade screens, feature gates, trial-expiry prompts, usage-limit messages, add-ons, and the purchase flow behind them. Use for free-to-paid and expansion conversion inside the product; use pricing-and-packaging to decide the plans and page-conversion for public pricing pages.
license: MIT
metadata:
  version: "2.0.0"
  author: MTEnt
---

# Upgrade Moments

Ask for payment where the user can understand experienced value, added capability, total commitment, and the safe path back to work.

If `.agents/marketing-context.md` exists, read it first; it is the truth file every skill in this hub shares, and its evidence states are constraints. Read [paywall-workflow.md](references/paywall-workflow.md) for trigger types, screen components, patterns, the upgrade flow, timing, and experiments.

## Operating contract

1. Define user state, value already experienced, entitlement, blocked or expanded capability, plan choices, price, terms, and baseline.
2. Verify actual billing, trial, renewal, cancellation, refund, tax, and access behavior.
3. Choose a paywall type and timing that matches user intent; define what remains available on decline.
4. Specify complete screen copy, plan comparison, billing states, failures, reconciliation, and return path.
5. Protect trust, accessibility, refunds, support load, retained value, and long-term conversion.

Do not degrade already-promised value, hide total cost, preselect an unwanted commitment, repeat prompts after dismissal, or manufacture urgency.

## Return

Current-state evidence, paywall type and trigger, screen hierarchy and copy, entitlement and billing state diagram, analytics events, experiment or rollout, policy dependencies, QA, and stop conditions.
