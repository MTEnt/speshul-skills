---
name: lifecycle-messaging
description: Design and write lifecycle email, newsletters, onboarding and nurture sequences, launch and transactional messages, cold email and follow-ups, and compliant SMS or MMS journeys. Use for automated flows, drip campaigns, outbound copy, subject lines, deliverability, segmentation, messaging triggers, or mobile lifecycle communication.
---

# Lifecycle Messaging

Send the right message because a person is in a relevant state, not because a calendar says it is time. Every message needs a legitimate trigger, one job, and a stop condition.

If `.agents/marketing-context.md` exists, read it before asking foundational product, audience, proof, or voice questions. Preserve its evidence states and surface stale or contradictory entries.

## Route the task

- Use `$emails` for permissioned lifecycle, newsletter, launch, transactional, renewal, retention, and recovery email.
- Use `$cold-email` for qualified B2B outbound, personalization, follow-ups, replies, and suppression.
- Use `$sms` for permissioned SMS or MMS consent, sender setup, flows, copy, provider choice, and delivery behavior.

## Messaging contract

1. Define audience state, eligibility, trigger, exclusion, message job, CTA, success event, and stop condition.
2. Inspect product, offer, prior messages, consent state, customer language, and deliverability evidence.
3. Verify current applicable law, carrier or platform rules, and sender requirements for the actual jurisdiction and channel.
4. Write the full sequence with timing rationale and dynamic inputs clearly marked.
5. Suppress messages after conversion, opt-out, invalid contact, or another defined stop state.
6. Test links, rendering, variables, tracking, reply path, unsubscribe, and failure handling before activation.
7. Require explicit authorization before importing contacts or sending.

No purchased-list assumptions, invented personalization, deceptive subjects, hidden commercial intent, manufactured urgency, or continued contact after opt-out.
