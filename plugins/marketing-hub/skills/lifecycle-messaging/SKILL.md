---
name: lifecycle-messaging
description: Design, write, audit, and optimize permissioned messages triggered by a recipient's state: welcome, onboarding, nurture, launch, newsletter, transactional, renewal, win-back, and recovery email, and consented SMS or MMS journeys with sender registration, quiet hours, and STOP handling. Use for automated flows, drip campaigns, segmentation, deliverability, and mobile messaging; use outbound-prospecting for unsolicited B2B outreach.
license: MIT
metadata:
  version: "2.0.0"
  author: MTEnt
---

# Lifecycle Messaging

Send because a recipient is in a relevant state, not because a calendar says another message is due. Possessing a phone number or an email address does not prove permission.

If `.agents/marketing-context.md` exists, read it first; it is the truth file every skill in this hub shares, and its evidence states are constraints. Read [email-system.md](references/email-system.md) for the journey model, sequence families, message structure, timing, deliverability, and QA. Read [sequence-blueprints.md](references/sequence-blueprints.md) for complete multi-message flows. Read [mobile-messaging-system.md](references/mobile-messaging-system.md) for SMS and MMS consent, sender choice, flow contract, and monitoring.

## Operating contract

1. Define recipient state, eligibility, trigger, message job, CTA, success event, exclusions, stop state, consent source, jurisdiction, and owner.
2. Draw entry, branch, suppression, conversion, exit, and re-entry before writing a long sequence; give each message one job and timing based on behavior or expected time to act.
3. Use SMS only when urgency, intimacy, or requested service value justifies it over email or in-product messaging.
4. Write complete messages with fallbacks and required identity, preference, and unsubscribe or STOP behavior; verify current authentication, carrier, registry, provider, and legal requirements.
5. Test variables, eligibility, links, rendering, tracking, collisions, suppression, and failure handling; require authorization before importing contacts, registering senders, activating automations, or sending.

Do not use purchased lists, deceptive subjects, fake reply markers, manufactured urgency, phishing-like links, or messages after opt-out or conversion.

## Return

Journey diagram or table, full sequence, triggers and timing, data fields, segmentation, suppression and failure handling, deliverability and compliance requirements, provider comparison where relevant, QA, primary measure, guardrails, and activation approval.
