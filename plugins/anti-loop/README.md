# Anti Loop

Anti Loop is an installable Codex plugin that keeps implementation work tied to the requested outcome and warns before edits expand permanent agent or workflow controls.

The first release is deliberately narrow:

- The skill tells the agent to derive a task-local outcome, acceptance check, non-goals, expected change surface, and stop condition.
- A `SessionStart` hook injects a concise scope reminder.
- A `PreToolUse` hook shows a visible advisory, but never blocks, when an edit touches persistent agent or workflow control files.
- When the three-attempt stop rule fires, the skill requires a short user-facing receipt with the reason, evidence, and next step.
- The hook is stateless and uses only the Python standard library. It does not read transcripts, source files, Git state, or the network.

Package files:

- `.codex-plugin/plugin.json` — plugin metadata.
- `skills/anti-loop/SKILL.md` — agent behavior.
- `hooks/hooks.json` and `hooks/anti_loop.py` — lifecycle configuration and advisory logic.
- `tests/` — package and hook behavior tests.

Research files:

- `report-source.md` — anonymized diagnosis and recommendations.
- `evidence-ledger.md` — claim-by-claim evidence strength and limitations.
- `future-skill-brief.md` — the broader design considered before reducing the first release.

The source project used for the research was inspected read-only. Nothing from it is stored here, and nothing in it was edited.

## Install

Anti Loop is distributed through the `speshul-skills` marketplace. Add the marketplace once, then install the plugin:

```text
codex plugin marketplace add MTEnt/speshul-skills
codex plugin add anti-loop@speshul-skills
```

Start a new Codex conversation after installation so the bundled skill and hooks are discovered.

Open `/hooks` in Codex and review the two Anti Loop hook definitions:

- `SessionStart` injects the task-scope reminder.
- `PreToolUse` displays an advisory before edits to persistent agent or workflow controls.

Trust both definitions if you want the complete behavior. Codex records trust against the current hook hash, so an updated hook may require review again.

Verify the package is installed and enabled:

```text
codex plugin list
```

Then use `/hooks` to confirm both Anti Loop hooks are active. The hook is advisory: it can warn and add context, but it does not block edits.

## Run the tests

From this plugin folder:

```text
python -m unittest discover -s tests -v
```
