---
version: 0.1.0
name: facebook-content-studio
description: |
  Research, plan, generate, continuity-check, package, preview, and publish
  Facebook Page content. Use for social post ideation, campaigns, captions,
  generated images, consistent-character video, Higgsfield production,
  thumbnails, captions, accessibility text, post scheduling, and approval-led
  Facebook Page publishing. Orchestrates Higgsfield Generate, Soul ID, Product
  Photoshoot, and Video Explainer, then uses the Workshop AI Facebook Pages MCP
  for supported text, link, and photo posts. Video publication remains a
  documented manual handoff until the publisher has the separate Meta upload
  credentials and video tools required by the Video API.
argument-hint: "[brand or campaign] [objective] [Facebook Page] [text|image|video|explainer|ad]"
---

# Facebook Content Studio

Create coherent Facebook Page content from brief through verified publication. The skill is a production director and safety gate. It does not replace the underlying media-generation skills or the Facebook publisher.

## Required downstream capabilities

Use the available implementation of each capability and follow its current instructions:

- `higgsfield-generate`: generic images, serious video, Marketing Studio, audio, and Virality Predictor.
- `higgsfield-soul-id`: reusable identity for a consenting real person.
- `higgsfield-product-photoshoot`: product-led social images and static ad packs.
- `higgsfield-video-explainer`: complete non-photoreal narrated explainers.
- The Workshop AI Facebook Pages MCP tools:
  - `facebook_connection_status`
  - `facebook_page_get`
  - `facebook_post_preview`
  - `facebook_post_publish`
  - `facebook_post_get`
  - `facebook_post_list_recent`

Do not copy another skill's commands into this skill when that skill owns the workflow. Route to it and preserve its interview, model-selection, and delivery rules.

## Files to read

Read only the references required by the request, but read each selected file completely:

- Always: `references/content-strategy.md`, `references/continuity-system.md`, and `references/meta-publishing.md`.
- For any generated media: `references/higgsfield-routing.md`.
- For a new campaign: `templates/creative-interview.md` and `templates/campaign-brief.md`.
- For recurring subjects, characters, products, or locations: `templates/continuity-bible.md`, `templates/asset-registry.schema.md`, and `templates/shot-list.md`.
- Before delivery or publication: `templates/post-package.schema.md`.
- For a named brand: load the matching file under `brand-profiles/`. Treat `null`, `TBD`, and `needs_interview` values as unknown; never invent them.

## Non-negotiable boundaries

1. Never request, display, store in campaign files, or pass a Facebook access token as a tool argument.
2. Never publish without showing the exact Page, final copy, media, link, time, and the MCP approval phrase to the user.
3. Never call `facebook_post_publish` until the user explicitly approves that exact preview.
4. Never represent a generated asset, quote, testimonial, statistic, event detail, or product claim as factual without evidence.
5. Never create a Soul or photorealistic synthetic depiction of a real person without explicit confirmation that the person consented and the user has the right to use the supplied photos.
6. Do not generate public figures, deceptive impersonation, or a real person appearing to say or do something they did not approve.
7. Keep political, election, regulated-product, medical, legal, financial, or crisis content out of automatic publication. Produce a draft package and require qualified human review.
8. Do not claim that a format, posting time, hashtag, or creative technique guarantees reach.
9. Do not use a raw Higgsfield job URL as a durable publication URL until it is confirmed public and sufficiently stable for Meta to fetch. Prefer user-controlled storage for final media delivery.
10. Do not call unsupported publication tools. The current publisher supports text, links, and one public-HTTPS photo. Video is a manual handoff.
11. A local path passed to a Higgsfield media flag is uploaded to Higgsfield. Upload only files the user supplied or specifically authorized for that production, and only after identity and usage rights are resolved.

## Campaign workspace

For durable work, create or reuse:

```text
campaigns/<campaign-slug>/
├── campaign-brief.md
├── continuity-bible.md
├── asset-registry.json
├── shot-list.md
├── research.md
├── drafts/
├── references/
├── outputs/
├── qa/
└── post-package.json
```

Do not overwrite an approved asset. Add a new version and update the registry. Use absolute local paths when handing media to a generation tool and stable URLs only when handing media to Facebook.

## Phase 0: orient and check capabilities

1. Identify the brand profile. Use the reusable template when no profile exists.
2. Inspect what the user already supplied: goal, Page, audience, source material, product, people, media, deadline, and format.
3. If publication is in scope, call `facebook_connection_status` and then `facebook_page_get` before creative production. A missing token does not block drafting, but it blocks live verification and publication.
4. Determine the route:
   - text or link post
   - single generated photo
   - product photo or carousel
   - photoreal or cinematic video
   - ad or UGC video
   - narrated non-photoreal explainer
5. State any unsupported final step early. For current video output, say that production is automated but Facebook upload is a manual handoff.
6. If a required downstream skill or Higgsfield capability is unavailable, stop that production branch and report the missing capability. Do not imitate it with an unreviewed command.

## Phase 1: small progressive interview

Use `templates/creative-interview.md`. Infer answers already present and ask only what materially changes the result.

- Ask one compact question per turn unless the user asks for a one-message form.
- Resolve the desired audience action before discussing visual style.
- Resolve audience and offer before writing copy.
- Resolve identity ownership and consent before Soul training or realistic human generation.
- If the request is a product photoshoot, obey that skill's maximum four-question interview.
- If the request is an explainer, obey its mandatory two-turn style-first interview. Do not merge style selection with production settings.

Stop the interview when the remaining unknowns can safely use defaults recorded in the brief. Do not conduct a performative interview whose answers will not affect production.

## Phase 2: research and brief

1. For factual content, research current primary or authoritative sources. Record URLs, access dates, supported claims, and exclusions in `research.md`.
2. Separate three evidence classes:
   - verified fact
   - brand-provided claim awaiting verification
   - creative framing or opinion
3. Write `campaign-brief.md` using the template.
4. Pick one primary objective and one primary CTA. Secondary objectives may be noted but must not compete in the final post.
5. Present a concise brief checkpoint. Continue only when the user approves it or explicitly delegates the decision.

## Phase 3: continuity system

Use `references/continuity-system.md` and the continuity template.

1. Create canonical entries for every recurring person, character, product, location, prop, wardrobe set, and visual style.
2. Mark attributes as `LOCKED`, `FLEXIBLE`, or `FORBIDDEN`.
3. Create a style key and the minimum useful reference set:
   - person or character: front, three-quarter, profile, and expression reference
   - product: front, side, back, label/detail, and scale reference as needed
   - location: establishing, medium, detail, palette, and lighting references
   - wardrobe and props: isolated approved views
4. Generate variants for selection, not simultaneous use. The user approves one canonical version of each anchor.
5. Hash or otherwise identify approved assets in `asset-registry.json`. Downstream prompts must reference registry IDs, not vague descriptions.

Multiple references can conflict. Attach only the smallest per-shot subset needed to lock identity, wardrobe, product, scene, start frame, or end frame.

## Phase 4: reference generation

Use `references/higgsfield-routing.md`.

- Consenting real person: train or reuse Soul ID before final reference stills.
- Fictional or stylized character: use Higgsfield Generate with Nano Banana 2 family and approved references.
- Product-led static content: use Product Photoshoot. Do not bypass its backend prompt enhancer.
- General design, typography, or high-fidelity still: use GPT Image 2 through Higgsfield Generate.
- Environment-only style/location work: use the appropriate location or general image route.

Generate two to four useful alternatives unless the downstream skill has a different required count. Do not generate volume without an explicit comparison criterion.

Checkpoint: show labeled contact sheets or clearly labeled assets. Ask the user to approve canonical anchors before video generation.

## Phase 5: production

### Text, link, or static image

1. Write the copy against the approved brief.
2. Generate or select the final asset.
3. Create alt text that describes the meaningful visual content without marketing filler.
4. Check link destination, claim evidence, spelling, brand voice, and the single CTA.

### General or cinematic video

1. Break the idea into shots. One shot gets one primary action.
2. Create and approve a start keyframe for every shot. Add an end keyframe only when the transition needs it.
3. Create a per-shot reference manifest from the approved asset registry.
4. Use Seedance 2.0 as the default serious-video route after validating the live model contract. Use Gemini Omni when the shot genuinely needs multiple image references within its current limits. Use Marketing Studio for ads, UGC, unboxing, presenter, and product-demo formats.
5. The video prompt describes motion, camera, timing, and sound. It does not re-describe a static start image.
6. Keep the prompt concrete and compact. Preserve identical locked continuity tokens across shots.
7. Regenerate only failed shots. Never replace approved anchors silently.

### Narrated explainer

Route the complete job to `higgsfield-video-explainer`. Preserve its style-first interview, universal style key, fixed ten-second blocks, voice-first barrier, clip generation, and immediate server-side assembly.

### Finished-video analysis

When useful, run Higgsfield Virality Predictor on the final clip. Treat its scores as comparative creative evidence, not a guarantee of reach or sales. Record the report URL and the specific revision decision it supports.

## Phase 6: QA

Run four gates and record results under `qa/`:

1. **Continuity QA**: identity, face, body, wardrobe, product geometry, label, prop count, location, palette, lighting, and screen direction.
2. **Creative QA**: the opening communicates quickly, the story remains coherent, the asset works without sound, captions are legible when used, and the CTA is clear.
3. **Truth and policy QA**: every factual claim is supported, synthetic humans are consented, disclosure is considered, and no prohibited or high-risk claim slipped in.
4. **Technical QA**: aspect, duration, file integrity, thumbnail, captions/transcript, delivery URL, and Facebook transport capability.

Reject the asset if a locked continuity attribute changes. Do not explain away visible drift.

## Phase 7: package

Create `post-package.json` from the schema documentation and validate it:

```bash
node /absolute/path/to/facebook-content-studio/scripts/validate-post-package.mjs \
  campaigns/<campaign-slug>/post-package.json
```

The package includes the final copy, CTA, Page ID, media manifest, accessibility text, evidence, AI-disclosure decision, QA results, approval state, publication transport, and schedule. It must not contain credentials or an MCP approval phrase.

## Phase 8: preview, approve, publish, verify

### Supported MCP publication

For text, link, and one public-HTTPS photo:

1. Call `facebook_page_get` again if the Page identity has not been shown in the current approval turn.
2. Call `facebook_post_preview` with the exact package content.
3. Show the full preview, Page, media, link, schedule, expiry, content hash, and approval phrase.
4. Stop and wait for explicit approval.
5. Call `facebook_post_publish` once.
6. Report the post ID, permalink when available, and verification status.
7. Save only the post ID, permalink, content hash, and result. Do not save the approval phrase.

### Video publication

The current MCP has no video uploader. Set:

```json
{
  "transport": "manual_meta_business_suite",
  "action": "manual_handoff"
}
```

Deliver the MP4, thumbnail, title, description, caption, transcript or SRT, AI-disclosure decision, and Page ID. Do not claim it was posted. A future automated video transport must implement Meta's current resumable upload flow with separate User-token and App-ID handling before this gate changes.

## Recovery and stopping rules

- Preserve completed job IDs and approved assets so a timeout can be rejoined instead of duplicated.
- Two identical generation failures mean the prompt, reference set, or parameters must change.
- If a publish call is ambiguous, inspect recent Page posts before creating a new preview. Never blindly retry.
- Stop when the approved artifact has been packaged and the authorized publication or handoff is complete. Do not start optional revision waves after acceptance criteria are met.

## Final response

Report:

- what was created
- the approved Page and format
- final asset locations or URLs
- whether publication was verified, scheduled, or handed off manually
- post ID and permalink when available
- material limitations or pending human reviews
- the sources used for factual content
