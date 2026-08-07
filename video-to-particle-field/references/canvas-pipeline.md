# Canvas pipeline

## Contents

- Architecture
- Source video
- Exact cover crop
- Stable particle layout
- Frame sampling
- Palette mapping
- Rendering
- Media safety

## Architecture

Use two media surfaces with only one visible result:

```text
hidden video decoder
        |
        v
small offscreen sampling canvas
        |
        v
stable particle state
        |
        v
visible full-viewport canvas
```

The offscreen canvas controls sampling cost. The visible canvas controls output
resolution. Do not read pixels from a full-resolution video frame on every
animation frame.

## Source video

Use a mounted video element with:

- `muted`
- `playsInline`
- `preload="auto"` when the hero depends on immediate playback
- `opacity: 0`
- a real width and height or full-cover positioning

Do not use `display: none` or remove it after load. Browsers may throttle or stop
decoding media that is removed from layout.

Autoplay can fail. Catch the returned promise and keep a poster or first decoded
frame available. Do not add sound merely to force an interaction requirement.

## Exact cover crop

The sampling crop must match the visible viewport composition. For source size
`videoWidth x videoHeight` and viewport aspect `viewportWidth / viewportHeight`:

```ts
const sourceAspect = videoWidth / videoHeight
const viewportAspect = viewportWidth / viewportHeight

let sx = 0
let sy = 0
let sw = videoWidth
let sh = videoHeight

if (sourceAspect > viewportAspect) {
  sw = videoHeight * viewportAspect
  sx = (videoWidth - sw) * 0.5
} else {
  sh = videoWidth / viewportAspect
  sy = (videoHeight - sh) * 0.5
}

samplingContext.drawImage(video, sx, sy, sw, sh, 0, 0, sampleWidth, sampleHeight)
```

Repeat this calculation after viewport changes.

## Stable particle layout

Create particles once per budget or resize. A dense grid with deterministic
jitter preserves the whole frame:

```ts
const columns = Math.ceil(Math.sqrt(count * viewportAspect))
const rows = Math.ceil(count / columns)

for (let index = 0; index < count; index += 1) {
  const column = index % columns
  const row = Math.floor(index / columns)
  particle.target.x = (column + 0.5 + jitterX(index)) / columns
  particle.target.y = (row + 0.5 + jitterY(index)) / rows
}
```

Hash the index for jitter, glyph choice, depth, and phase. Never use fresh
`Math.random()` values during rendering because that creates visual noise rather
than material continuity.

## Frame sampling

At each sampling tick:

1. Draw the current video frame to the offscreen canvas.
2. Read one reduced pixel buffer.
3. For every particle, sample the pixel under its normalized target.
4. Compute luminance and a small local edge estimate.
5. Update color, opacity, and size for the live scene target.

Luminance:

```ts
const luminance = (red * 0.2126 + green * 0.7152 + blue * 0.0722) / 255
```

Edge energy can use absolute differences between left/right and top/bottom
luminance. Boosting edge opacity and size helps silhouettes, faces, typography,
and furniture survive reduction.

## Palette mapping

Choose one of three explicit modes:

- `source`: preserve sampled RGB.
- `brand`: quantize pixels into semantic project colors based on luminance,
  warmth, coolness, and edge energy.
- `mono`: use one foreground color with luminance-driven opacity and size.

Brand quantization should preserve meaning. A cool signal color may represent
screens and system activity. A warm-pixel heuristic only identifies warm
material; it cannot distinguish people from wood, leather, or lamps. If a color
token is semantically reserved for humans, use an authored mask, segmentation,
or a strict region/allocation rule instead of color alone. Do not apply
arbitrary rainbow hues or claim semantic detection the sampler does not perform.

## Rendering

Render at animation-frame cadence, independent from media sampling cadence.
Mix mostly small rectangles with a smaller set of stable glyph particles. Apply
subtle phase-based drift after the target position is resolved. Reset
`globalAlpha` after the loop.

The canvas should be fixed or isolated in the intended section, with semantic
DOM content above it in the same stacking context. A negative `z-index` often
places the canvas behind an opaque page background; verify the actual render.

## Media safety

Pixel reads fail when a remote video lacks compatible CORS headers. Prefer local
public assets or same-origin delivery. When remote media is necessary, set
`crossOrigin="anonymous"` before assigning the source and verify the response
headers before promising client-side sampling.
