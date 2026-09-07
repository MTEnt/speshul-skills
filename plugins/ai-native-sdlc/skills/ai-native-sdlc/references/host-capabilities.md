# Host capabilities

Map the required operation to something the current host actually exposes. A model
name or subscription does not establish filesystem access, tool execution,
permissions, persistent jobs, or skill discovery.

| Needed operation | Capability to verify | If absent |
| --- | --- | --- |
| Read the source of truth | File access or an authorized connector | Work from supplied excerpts and mark freshness/completeness unknown; request the specific missing evidence. |
| Edit and exercise code | Workspace writes plus command/test execution | Produce an applicable patch or implementation guidance; label it unexecuted. |
| Inspect a UI | Browser interaction or image input plus suitable evidence | Use available structural checks and leave visual/interaction acceptance unresolved. |
| Coordinate concurrent work | Isolated workspaces and a supported coordination mechanism | Work sequentially; do not invent subagent tools or assume separate branches isolate shared databases. |
| Enforce a protected operation | Tool/server permissions, CI policy, sandbox, or a verified host hook | Prepare the proposal only. A prompt saying to ask first is not equivalent enforcement. |
| Resume unattended work | Scheduler/event delivery, durable state, scoped identity, logs | Keep the workflow interactive; do not promise future monitoring or continuation. |

The core distribution is the complete `ai-native-sdlc/` skill folder with its
relative references. An Agent Skills-compatible host can discover `SKILL.md`;
other hosts can load its text and relevant references as instructions. Packaging
metadata for an individual product is optional to the reasoning workflow.

Do not rewrite the portable core as vendor command aliases. When implementation
needs a specific CLI, API, permission setting, or hook event, verify that host's
current official documentation and installed version, then keep the mapping in
the user's existing integration configuration. Report unsupported semantics.

Select a model by the task's required context, modalities, tool reliability, data
handling constraints, and observed evaluation results. The same instructions can
be reused across providers; equal capability or equal outcomes are not implied.

At a model/host handoff, supply source identifiers and revisions, accepted
decisions, actual check results, changed paths, and pending actions. Recheck
revision, credentials/authority, and environment before resuming. Do not export
private chain-of-thought, credentials, or a full conversation when a bounded
operational handoff suffices.
