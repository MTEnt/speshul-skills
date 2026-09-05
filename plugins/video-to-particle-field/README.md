# Video to Particle Field

Turns video, images, and short scene clips into a dense live particle or ASCII field in a web interface, with stable particle identities, coherent scene morphs, scroll-synchronized disintegration and reassembly, responsive performance budgets, and reduced-motion behavior.

## Package contents

| Path | Purpose |
| --- | --- |
| `skills/video-to-particle-field/SKILL.md` | Trigger and operating instructions. |
| `skills/video-to-particle-field/references/` | Canvas pipeline, morph and scroll choreography, performance and accessibility, implementation brief. |
| `skills/video-to-particle-field/scripts/inspect_media.py` | Deterministic media inspection helper. |
| `skills/video-to-particle-field/assets/react-video-particle-field/` | Reusable React component and stylesheet. |

## Install

Claude Code: `/plugin marketplace add MTEnt/speshul-skills` then `/plugin install video-to-particle-field@speshul-skills`.

Codex: `codex plugin marketplace add MTEnt/speshul-skills` then `codex plugin add video-to-particle-field@speshul-skills`.

Standalone: copy `skills/video-to-particle-field/` into your runtime's skills directory.

The skill has no hooks and makes no network calls. It reads the media files you point it at.
