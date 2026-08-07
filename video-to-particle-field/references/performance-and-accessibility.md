# Performance and accessibility

## Starting budgets

These are starting points, not guarantees:

| Target | Particles | Sampling width | Sample cadence | DPR cap |
| --- | ---: | ---: | ---: | ---: |
| Desktop | 24,000 | 384 px | 70-100 ms | 1.5 |
| Mobile | 7,000 | 216 px | 90-140 ms | 1.25-1.5 |

Increase density only after measuring the target machine. A denser offscreen
sample does not help if the visible particle grid is much coarser.

## Web video derivatives

Inspect source size and codec with `scripts/inspect_media.py`. A large production
master should not automatically become the mobile web source. Create a local web
derivative when file size, resolution, or bitrate exceeds the delivery budget.

Example H.264 derivatives:

```bash
# Desktop, maximum 1920 px wide
ffmpeg -i master.mp4 -vf "scale='min(1920,iw)':-2" \
  -c:v libx264 -preset slow -crf 22 -pix_fmt yuv420p -movflags +faststart \
  -an hero-desktop.mp4

# Mobile, maximum 960 px wide
ffmpeg -i master.mp4 -vf "scale='min(960,iw)':-2" \
  -c:v libx264 -preset slow -crf 25 -pix_fmt yuv420p -movflags +faststart \
  -an hero-mobile.mp4
```

Use `<source media>` queries or select the source before playback. Preserve the
master separately. Confirm the derivative visually because particles still
depend on silhouette and edge detail. For scroll-scrubbed clips, encode frequent
keyframes and test seeking on the target browser; normal streaming optimization
alone does not guarantee smooth scrubbing.

## Separate work rates

- Render inexpensive particle positions at animation-frame cadence.
- Sample and read video pixels at a slower fixed cadence.
- Rebuild particle arrays only when the budget or viewport changes.
- Decode and sample only the active or incoming clip.
- Load static destination samples once, then reuse them.

Avoid object allocation inside the particle draw loop. Reuse canvases, contexts,
arrays, and particle records.

## Lifecycle

Pause or throttle when:

- `document.hidden` is true
- the visual field is outside its useful story range
- another route replaces the component
- reduced motion is active

Cancel animation frames and remove every event listener during cleanup. Avoid
starting a second animation loop when visibility returns.

## Resize

Clamp device-pixel ratio before sizing the visible canvas. Recompute cover crop,
particle count, target layouts, static image placements, and scroll geometry.
Debounce expensive image re-sampling when resize events fire rapidly.

## Reduced motion

`prefers-reduced-motion: reduce` should:

- pause source videos on a representative decoded frame
- render a stable particle composition
- replace continuous interpolation with discrete scene states
- remove ambient particle drift and breakup turbulence
- preserve all semantic page content and navigation

Do not remove the visual entirely unless the user asks for a plain fallback.

## Readability

Particle imagery sits behind DOM text. Maintain text contrast with a real dark
surface, localized solid backing, or source-aware placement. Do not rely on a
decorative gradient. Test real frames because average contrast is not enough.

## Verification

Measure or inspect:

- frame stability while video is playing
- scroll responsiveness during the breakup peak
- resize behavior at desktop and narrow mobile widths
- clip seeking on the actual encoded files
- memory after repeated route entry and exit
- console warnings and media errors
- autoplay failure behavior
- same-origin or CORS-safe pixel access

Local browser proof does not establish production CDN headers, remote autoplay,
or low-end device performance. State those boundaries explicitly.
