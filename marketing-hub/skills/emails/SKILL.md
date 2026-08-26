---
name: emails
description: Design, write, audit, and optimize permissioned lifecycle email sequences and automated flows, including welcome, onboarding, nurture, launch, newsletter, transactional, retention, renewal, win-back, and recovery messages. Use for triggers, timing, segmentation, copy, suppression, deliverability, and journey measurement; use cold-email for unsolicited B2B outreach.
---

# Emails

Send because a recipient is in a relevant state, not because a calendar says another message is due.

If `.agents/marketing-context.md` exists, read it first. Read [email-system.md](references/email-system.md) for journey design, copy, deliverability, QA, and output. Read [sequence-blueprints.md](references/sequence-blueprints.md) when a complete multi-message flow is requested.

## Operating contract

1. Define recipient state, eligibility, trigger, message job, CTA, success event, exclusions, stop state, consent, and owner.
2. Draw entry, branch, suppression, conversion, exit, and re-entry before writing a long sequence.
3. Give each message one primary job and timing based on behavior or expected time to act.
4. Write complete messages with fallbacks and required footer or preference behavior.
5. Verify current sending, identification, authentication, unsubscribe, privacy, and jurisdiction requirements.
6. Require authorization before importing contacts, activating automations, or sending.

Do not use purchased lists, deceptive subjects, fake reply markers, manufactured urgency, or messages after opt-out or conversion.
