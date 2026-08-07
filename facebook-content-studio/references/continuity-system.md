# Continuity system

Consistency comes from approved production assets and constrained per-shot references, not from repeating a long prose prompt.

## Canonical asset types

| Asset | Minimum useful views | Lock |
|---|---|---|
| Real person or character | front, three-quarter, profile, expressions | face, body, hair, distinguishing features |
| Wardrobe | front, back, material/detail | color, cut, accessories, logos |
| Product | front, side, back, label/detail, scale | geometry, packaging, label, color |
| Location | establishing, medium, detail | architecture, layout, palette, lighting |
| Prop | isolated neutral view and in-scene scale | shape, count, material |
| Style key | one canonical swatch or hero frame | medium, palette, line/texture, finish |

For a real person, Soul training requires explicit consent and five to twenty suitable photos. Eight to twelve varied, sharp images are preferred by the downstream Soul workflow.

## Attribute states

- `LOCKED`: must remain identical across every asset and shot.
- `FLEXIBLE`: may change within recorded limits.
- `FORBIDDEN`: must never appear.
- `UNKNOWN`: unresolved; production cannot silently fill it when it affects identity, claims, or brand.

## Asset registry entry

```json
{
  "asset_id": "character-host-v1-front",
  "entity_id": "character-host-v1",
  "role": "identity_anchor",
  "version": 1,
  "source": "higgsfield_job",
  "path_or_url": "<job-id-or-absolute-path>",
  "approval": "approved",
  "locked_attributes": ["face", "hair", "jacket", "glasses"],
  "notes": "Canonical front view"
}
```

Never store Facebook tokens, Higgsfield session credentials, or private OAuth material in the registry.

## Reference selection per shot

Build a manifest before generating the shot:

```json
{
  "shot_id": "S03",
  "references": {
    "start_frame": "shot-S03-start-v2",
    "identity": "character-host-v1-three-quarter",
    "wardrobe": "wardrobe-host-blue-v1",
    "location": "location-workshop-wide-v1",
    "product": "product-device-front-v1"
  },
  "locked_tokens": [
    "same short black hair",
    "same cobalt work jacket",
    "same brushed aluminum device"
  ]
}
```

Do not attach every campaign image to every shot. Extra references can conflict, dilute the hierarchy, or exceed the model contract. Validate accepted media roles and limits before submission.

## Prompt separation

Image prompt:

- establish the canonical subject, setting, composition, lens, light, and style
- keep concrete and compact
- use reference-driven prompts to describe changes, not re-describe the input

Image-to-video prompt:

- describe motion, timing, camera, physical behavior, and sound
- do not re-describe the static start frame
- one primary action per shot
- preserve the same short locked-token block across related shots

## Continuity QA matrix

Score every final shot as pass, revise, or reject:

| Dimension | Check |
|---|---|
| Identity | facial proportions, hair, skin or surface, body, age presentation |
| Wardrobe | garment, color, fit, accessories, logo placement |
| Product | geometry, label spelling, controls, color, scale |
| Location | floor plan, background objects, palette, time and lighting |
| Motion | body mechanics, object physics, camera direction, screen direction |
| Text | spelling, legibility, no invented labels |
| Style | medium, render finish, contrast, grain, realism level |
| Safety | consent, no public-figure impersonation, no deceptive event |

A visible change to a `LOCKED` attribute is a rejection, not a minor note.
