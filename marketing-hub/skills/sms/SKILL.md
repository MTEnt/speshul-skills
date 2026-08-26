---
name: sms
description: Plan, write, audit, and optimize permissioned SMS or MMS marketing and service journeys, including welcome, abandoned action, post-purchase, reminders, promotion, support, verification, and win-back. Use for consent, sender setup, A2P requirements, phone-number types, quiet hours, STOP handling, providers, copy, frequency, and delivery measurement.
---

# Sms

SMS is an intimate and regulated channel. Possessing a phone number or email consent does not prove permission for promotional texts.

If `.agents/marketing-context.md` exists, read it first. Read [mobile-messaging-system.md](references/mobile-messaging-system.md) for consent, sender choice, flows, copy, providers, QA, and measurement.

## Operating contract

1. Define jurisdiction, message category, sender identity, number type, consent source and wording, expected frequency, quiet hours, HELP and STOP, evidence retention, and restrictions.
2. Verify current law, carrier, registry, provider, and platform requirements for the actual situation.
3. Use SMS only when urgency, intimacy, or requested service value justifies it over email or in-product messaging.
4. Specify every flow's trigger, eligibility, exclusion, delay, cap, success event, stop state, fallback, and failure response.
5. Require authorization before registration, contact import, activation, or sending.

Do not obscure sender or destination, manufacture urgency, bypass opt-out, or use link behavior that creates phishing risk.
