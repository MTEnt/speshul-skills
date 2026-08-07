---
name: video-to-particle-field
description: |
  Turn video, images, and short scene clips into a dense live particle or ASCII
  field in a web interface. Use when asked for video-to-particles, pixelated
  video, ASCII video, point-cloud video, image-to-particle morphing, particle
  disintegration and reassembly, reactive cursor fields, or scroll-synchronized
  particle scenes. Builds a hidden-video sampling pipeline, stable particle
  identities, coherent scene morphs, responsive performance budgets, and
  reduced-motion behavior without exposing the ordinary source footage.
---

# Video to Particle Field

Build a continuous visual material in which videos and images are visible only
through a dense particle, pixel, or ASCII field. Preserve particle identity
across scene changes so the field can disintegrate and reassemble instead of
crossfading between unrelated layers.

## Files to read

Read each selected file completely before implementation:

- Always: `references/canvas-pipeline.md` and
  `references/performance-and-accessibility.md`.
- For any transition between sources or scroll-controlled sequence:
  `references/morph-and-scroll.md`.
- Before changing code: `references/implementation-brief.md`. Fill it mentally
  from supplied context and ask only about unknowns that materially change the
  architecture.

For React work, copy and adapt the implementation under
`assets/react-video-particle-field/` instead of recreating the sampling engine.
Inspect source media before planning:

```bash
python3 scripts/inspect_media.py /absolute/path/to/source.mp4
```

## Non-negotiable visual contract

1. The source `<video>` is a decoder and timing source, not a visible layer.
   Keep it mounted and playing or seekable, but set its visual opacity to zero.
   Do not use `display: none`, which can stop decoding in some browsers.
2. The visible canvas begins in the particle material on the first frame. Never
   solve the entrance with ordinary footage that later crossfades to particles.
3. Reuse one stable particle population. Each particle keeps its identity,
   depth, phase, glyph seed, and one target per scene.
4. A scene transition has three legible states: coherent source, controlled
   disintegration, and coherent destination. Do not fade the source away and
   independently fade the destination in.
5. Keep headings, controls, descriptions, and accessibility content in semantic
   DOM elements. Canvas is atmosphere and imagery, never essential copy.
6. Match the project's existing visual system. Derive palette, typography,
   density, and motion language from the target product instead of applying a
   generic neon particle effect.

## Small progressive interview

Infer what is already present. Ask one compact question only when the answer
changes implementation materially:

- What is the source media, aspect ratio, duration, and ownership status?
- Is the target a React component, another framework, or framework-free canvas?
- Should the result preserve source RGB, quantize to a brand palette, or render
  monochrome glyphs?
- Are later scenes images, videos, geometry, or procedural layouts?
- Is scroll controlling a morph, scrubbing clip time, or triggering playback?
- What is the lowest device class that must remain smooth?

Do not conduct an interview when the repository and supplied assets already
answer these questions.

## Workflow

### 1. Inspect the incumbent surface

Read the target component, styling, design tokens, and motion preferences.
Inspect source media dimensions and duration. Identify the exact stacking
context so the canvas is visible behind DOM content without escaping the page.

### 2. Establish a performance budget

Choose particle count, sample resolution, frame-sampling cadence, and maximum
device-pixel ratio before coding. Start with the defaults in
`references/performance-and-accessibility.md`, then measure rather than assuming.

### 3. Build the live video sampler

Mount a muted, `playsInline` video at zero opacity. Draw its current frame to a
small offscreen canvas using the same `object-fit: cover` crop as the viewport.
Read that reduced pixel buffer and update each particle's visible scene color,
opacity, and size. The visible canvas renders the particle field every animation
frame while the expensive video sample updates less frequently.

### 4. Stylize without losing structure

Preserve luminance and edges because they carry faces, silhouettes, furniture,
and camera movement. Map sampled colors to the project's semantic palette when
the intended style is graphic. Use a stable mixture of micro-pixels and glyphs;
do not randomize glyph identity every frame.

### 5. Add coherent morph targets

Sample every destination image or video frame into the same normalized target
space. Assign each particle a destination using a stable spatial mapping. Apply
disintegration displacement only during the middle of the transition, while
interpolating the source and destination targets throughout. Follow
`references/morph-and-scroll.md`.

### 6. Connect motion to scroll

Translate scroll into a normalized scene value. Separate narrative state from
render state when the hero must remain coherent before breakup begins. Keep one
bounded horizontal or depth sequence if the concept requires it; do not hijack
ordinary page scroll for the entire document.

### 7. Handle interaction and lifecycle

Pointer influence may repel, focus, or locally increase particle coherence, but
must not replace the live video with an unrelated static image. Pause video and
animation work when the document is hidden or the field is no longer used.
Provide a static first-frame particle composition for reduced motion.

### 8. Verify in bounded passes

Run one desktop and mobile visual pass together. Check:

- ordinary source footage is never visible
- recognizable forms and motion survive particle reconstruction
- disintegration reads as the same particles leaving the source
- the destination becomes coherent before its chapter copy needs it
- scrolling backward reverses the transition cleanly
- resize preserves the correct crop and target layout
- browser console is clean
- reduced motion, semantic content, and controls remain usable

Fix the complete defect batch once, confirm once, and stop.

## Acceptance contract

The work is complete only when:

- the video element is visually hidden while continuing to decode
- the canvas is visible from the initial frame
- sampled frames visibly change over time
- one particle population carries every source and transition
- desktop and mobile use explicit budgets
- device-pixel ratio is clamped
- hidden-tab and reduced-motion behavior are implemented
- scroll transitions are reversible and free of ordinary crossfades
- local lint, type, build, and browser checks appropriate to the project pass

## Final response

Report the target route, source assets, particle budgets, transition model,
performance safeguards, verification performed, and any remaining media that
must be generated. Distinguish local proof from deployment or publication.
