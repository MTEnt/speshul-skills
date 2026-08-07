# Higgsfield routing

This file summarizes routing decisions. The downstream Higgsfield skill remains authoritative for commands and live model contracts.

## Route by deliverable

| Deliverable | Route | Continuity method |
|---|---|---|
| General static image, graphic, typography | Higgsfield Generate, GPT Image 2 default | approved image references and style key |
| Fictional or stylized character references | Higgsfield Generate, Nano Banana 2 family | canonical character sheet and per-shot subset |
| Consenting real person's identity | Soul ID, then Soul-powered generation | trained Soul plus approved wardrobe/location anchors |
| Product-led static social creative | Product Photoshoot | product reference images; backend-enhanced prompt |
| Product ad, UGC, unboxing, presenter | Marketing Studio through Higgsfield Generate | product entity, optional avatar, approved hook or ad reference |
| Serious cinematic or motion-heavy video | Higgsfield Generate, Seedance 2.0 default | approved start image; optional end/reference media after live validation |
| Multi-reference video shot | Gemini Omni when its live reference limits fit | smallest set of identity, scene, and product references |
| Narrated non-photoreal explainer | Video Explainer | one universal style key across fixed blocks |
| Finished creative analysis | Virality Predictor | analyze final clip; do not treat score as outcome guarantee |

## Required live checks

Before generation, follow the downstream skill's bootstrap and authentication rules. Then inspect the preferred model's current schema instead of relying on this file for volatile limits:

```bash
higgsfield model get <job_set_type> --json
```

For feature discovery, first inspect the unfiltered model list. Workflows are listed separately.

## Reference-generation rules

- Generate references before motion.
- Generate alternatives for approval, then select one canonical anchor.
- Keep reference-generation prompts under roughly two hundred tokens.
- For reference edits, describe what changes instead of re-describing the source.
- Reuse completed Higgsfield image job IDs when the target model accepts them.
- Use a start image as a composition and identity anchor. Video prompt text should describe motion.
- Validate how many images and which roles the selected model currently accepts.

## Soul consent gate

Before Soul training, record:

- the depicted person explicitly consented
- the user has the right to use all training photos
- intended use and publication channel
- whether the person approved synthetic speech or action, when applicable

If any answer is missing, stop before upload or training.

## Ads and UGC

Marketing Studio has two mutually exclusive setup routes:

- reference-driven ad video
- composed hook and setting blocks

Never combine both. Products and avatars are structured entities, not bare IDs pasted into a prompt. Follow the Marketing Studio workflow for live schemas and valid modes.

## Explainers

Do not approximate the explainer workflow with generic video generation. Route the complete job to the explainer skill, which owns style selection, narrator selection, ten-second block pairing, and assembly.

## Failure recovery

- Rejoin a timed-out job by ID; do not submit a duplicate.
- Regenerate only the failed or rejected shot.
- Two identical failures require a changed prompt, reference subset, or parameters.
- Never silently fall back to an older or weaker model just because its schema is easier.
