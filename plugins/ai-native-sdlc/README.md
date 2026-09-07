# AI Native SDLC

Status: experimental. Provider-neutral instructions for carrying software work
between product decisions, implementation, verification, release, and operations.
Uses existing project records and scales the process to the requested task.

## Use

Load `skills/ai-native-sdlc/SKILL.md` and the references it selects. Example requests:

- "Carry this approved design through implementation and local verification."
- "Audit the handoff between our agent-written patches and human release review."
- "Help us adopt AI-assisted delivery without replacing our issue tracker."

The portable unit is the complete `skills/ai-native-sdlc/` directory. Copy it to
the skill directory supported by your agent host. In a host without skill discovery,
provide the entrypoint and requested references as instruction context. Tool-free
chat can prepare proposals; execution requires a host with the relevant tools.

The repository marketplace entries package this same core for Claude Code and
Codex. Once this revision is published to the configured marketplace, install
`ai-native-sdlc@speshul-skills` using that host's plugin installer. A local checkout
is not evidence that the published marketplace already contains this package.

## Permissions and limits

No hooks, scripts, network calls, credentials, or model dependencies ship in this
package. The skill guides an agent that may edit files, run checks, or prepare
release actions when the user authorizes them. It grants no permissions and adds
no sandbox. Enforced review gates, protected actions, and unattended jobs require
actual host or application controls.

Missing tools produce an explicit capability gap and a reviewable partial result.
Blocked decisions and exhausted work bounds stop the affected operation. The
skill does not authorize sending messages, merging, deploying, or publishing
merely because an earlier delivery stage was authorized.

Graph Engineering is an optional companion for executable workflow design; there
is no runtime dependency on another package. Model-neutral instructions do not
establish behavioral compatibility with every model or host.

## Verify

From the repository root:

```text
python scripts/validate_repo.py --strict-overlap
python plugins/skill-authoring/skills/skill-authoring/scripts/skill_lint.py plugins/ai-native-sdlc/skills/ai-native-sdlc
```

The supplied [behavior scenarios](evals/scenarios.json) describe acceptance checks
for disposable evaluations. They are not recorded passing results. Static lint
checks packaging and instructions, not model behavior or runtime enforcement.

## Provenance

Inspired by Anthropic's AI-Native SDLC playbook, independently written with
provider-neutral capability handling and proportional process. See
[sources and adaptation](skills/ai-native-sdlc/references/sources.md).
