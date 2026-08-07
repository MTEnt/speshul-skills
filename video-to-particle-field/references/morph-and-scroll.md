# Morph and scroll continuity

## Contents

- Preserve particle identity
- Three-stage transition
- Make disintegration feel physical
- Scroll mapping
- Image destinations
- Video destinations
- Clip handoff

## Preserve particle identity

Each particle owns one target per scene:

```ts
type Particle = {
  depth: number
  phase: number
  glyphSeed: number
  targets: Array<{ x: number; y: number }>
  colors: string[]
  opacities: number[]
  sizes: number[]
}
```

Interpolate those properties between adjacent scenes. Do not allocate a second
particle system for the destination.

## Three-stage transition

For normalized transition progress `p`:

1. `0.00-0.25`: source stays coherent while motion energy accumulates.
2. `0.25-0.75`: particles separate, travel, and progressively inherit the
   destination palette and target.
3. `0.75-1.00`: displacement collapses and the destination locks into focus.

Use a smooth interpolation for target travel and a middle-weighted breakup:

```ts
const travel = smoothstep(p)
const breakup = Math.sin(Math.PI * p)

let x = mix(source.x, destination.x, travel)
let y = mix(source.y, destination.y, travel)

x += radialX * breakup * depthStrength
y += radialY * breakup * depthStrength * 0.66
x += Math.cos(phase) * viewportWidth * 0.05 * breakup * depth
y += Math.sin(phase * 1.37) * viewportHeight * 0.06 * breakup * depth
```

Breakup must peak in the middle and return to zero. A permanent random offset
prevents the destination from becoming coherent.

## Make disintegration feel physical

Combine a small number of motivated forces:

- radial expansion from a meaningful focal point
- depth-scaled camera translation or zoom
- stable phase-based turbulence
- temporary opacity reduction for deep particles
- size compression during travel, restored during reassembly

Avoid fresh random scatter, uniform explosions, and excessive blur. The viewer
should be able to follow the material even when individual particles cannot be
tracked consciously.

## Scroll mapping

Keep narrative scene progress separate from render progress. A hero can remain
coherent during initial scroll before its morph begins:

```ts
const heroProgress = clamp((viewportCenter - heroCenter) / handoffDistance)
const renderProgress = clamp((heroProgress - 0.28) / 0.72)
```

Use document geometry rather than hardcoded page pixels. Recalculate after
resize and content changes. Backward scrolling must produce the exact reverse
state without resetting media or particle identity.

## Image destinations

Sample a destination image into normalized coordinates with the same coverage
strategy as the video grid. Assign particles by a stable spatial order such as
serpentine rows, Hilbert-like locality, or nearest-region buckets. Pure random
assignment creates a noisy teleport rather than legible reassembly.

Define destination coordinates separately from source coordinates even when
both sources fill the viewport. A destination placement rectangle is a useful
minimum contract:

```ts
destination.x = placement.left + sample.x * placement.width
destination.y = placement.top + sample.y * placement.height
```

This allows the source to occupy the full viewport while the same particles
reassemble into an inset, shifted, or differently scaled image. The bundled
React asset exposes `destinationPlacement` for this purpose.

## Video destinations

For multiple short clips, give each clip its own hidden decoder but keep one
visible particle population.

Two control modes are valid:

### Scroll-scrubbed clip

Map chapter-local scroll progress to media time:

```ts
targetTime = clipDuration * chapterProgress
```

Do not assign `currentTime` on every raw scroll event. Store `targetTime`, then
approach it from `requestAnimationFrame` or a bounded scheduler. Seek only when
the difference exceeds a small threshold. Scrubbing works best with short,
frequent-keyframe clips encoded for seeking.

### Triggered playback

Start the clip when its chapter becomes active, then let it play while scroll
controls only the particle morph and camera. Pause inactive clips and preserve
their last frame for reverse transitions.

Choose one mode deliberately. Scrubbing gives direct control but is sensitive
to codec and keyframe spacing. Triggered playback is smoother but less tightly
coupled to user movement.

## Clip handoff

At the boundary between clip A and clip B:

1. sample the current visible frame of A into scene target A
2. prepare the chosen start or scrubbed frame of B in target B
3. morph the stable particles from A to B
4. switch the live sampling source only after B has enough coherence

Do not show both videos as independent visible layers. The particle field is the
only visual output.
