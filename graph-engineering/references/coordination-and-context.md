# Coordination and Context

## Separate graph views

Maintain distinct declarations for:

- task dependencies;
- capability assignment;
- communication and delegation;
- runtime state/evidence;
- persistent evolution.

An edge in one view does not imply an edge in another. In particular, dependency is not permission.

## Capability selection

Assign work from required capability, data access, consequence, latency/cost, and evaluation evidence. Record model/tool/human versions or selection rules. Role labels such as "researcher" or "critic" are not capability contracts.

For bounded agent selection, define the finite capability set, selection input schema, permission ceiling, delegation depth, and fallback when no capability fits.

## Communication and delegation

Declare allowed sender/recipient pairs, message schemas, trust labels, context projection, reply/timeout behavior, and whether control transfers. A handoff changes active responsibility; an agent-as-tool call does not necessarily do so.

Validate inter-agent messages as untrusted structured input. No message can grant privilege, approve an action, rewrite policy, or change a persistent graph version.

## Context projections

For each node, specify required channels/artifacts, excluded data, trust labels, sensitivity ceiling, freshness rule, maximum size, summarization provenance, and whether conversation history is included.

Minimize shared context. Preserve immutable source references separately from generated summaries. Do not treat a summary as the source of truth.

## Verification and correlated error

Independent verification requires an independently scoped job and evidence access, not merely a second model call. Where consequence warrants it:

- separate candidate production from verification;
- vary evidence assignment or require disconfirming searches;
- prevent the verifier from accepting the producer's unsupported claims as evidence;
- use deterministic checks or qualified human review where available;
- preserve disagreements for adjudication.

Different agents or models can still share sources, assumptions, provider failure, or evaluation bias. Describe the actual isolation achieved.

## Human participation

Distinguish human input, expert judgment, policy approval, adjudication, and operational execution. Record identity and authority only when necessary. Human approval is not evidence that a claim is true, and expert review is not authorization to perform a protected action unless the approval policy explicitly grants it.
