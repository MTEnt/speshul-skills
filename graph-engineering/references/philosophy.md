# Graph Engineering for AI Workflows

> A practical philosophy of explicit topology, state, evidence, and control

**Status:** Practitioner guidance  
**Last reviewed:** 2026-08-05  
**Companion document:** [Prompt-to-Graph Operational Playbook](./playbook.md)

## Contents

- [Scope](#scope)
- [Core thesis](#core-thesis)
- [1. Choose the smallest sufficient workflow](#1-choose-the-smallest-sufficient-workflow)
- [2. Give every node a contract](#2-give-every-node-a-contract)
- [3. Let edges encode real policy](#3-let-edges-encode-real-policy)
- [4. Treat state as a governed record](#4-treat-state-as-a-governed-record)
- [5. Use isolation carefully](#5-use-isolation-carefully)
- [6. Separate collection, verification, criticism, and synthesis](#6-separate-collection-verification-criticism-and-synthesis)
- [7. Put human approval before the exact action](#7-put-human-approval-before-the-exact-action)
- [8. Design failures before the happy path](#8-design-failures-before-the-happy-path)
- [9. Turn records into governed knowledge](#9-turn-records-into-governed-knowledge)
- [10. Evaluate the system, not the diagram](#10-evaluate-the-system-not-the-diagram)
- [11. Treat tools and retrieved content as security boundaries](#11-treat-tools-and-retrieved-content-as-security-boundaries)
- [Design maxims](#design-maxims)
- [References](#references)

## Scope

In this guide, **graph engineering** means designing an AI-assisted workflow as an explicit graph:

- **Nodes** perform bounded work.
- **Edges** define permitted transitions and dependencies.
- **State** records the information required to continue, inspect, recover, and evaluate a run.
- **Policies** determine when the workflow may proceed, retry, stop, escalate, or act.

The term describes workflow topology and runtime control. It is distinct from graph theory, graph databases, knowledge graphs, and GraphRAG.

A graph is not automatically multi-agent. A node may be deterministic code, a tool call, one model call, a human decision, or an agent with its own internal loop. A linear sequence is also a graph. The useful question is not whether a task can be drawn as a graph; it is whether making the structure explicit improves the result enough to justify the added cost and coordination.

## Core thesis

Graph structure is a **control mechanism**, not a source of truth.

An explicit workflow can make dependencies visible, limit tool access, isolate context, preserve provenance, introduce checkpoints, and place approval before protected actions. None of those properties proves that a generated claim is correct. Reliability still depends on source quality, deterministic checks, qualified human judgment, evaluation, and the behavior of the models and tools used in each node.

Research supports a bounded position. Multi-agent debate has improved results on some reasoning and factuality tasks, while other work has found correlated errors and recurring failures in multi-agent specification, coordination, and verification. The design therefore treats additional agents as a hypothesis to test, not a quality guarantee.

## 1. Choose the smallest sufficient workflow

Start from the simplest design that could meet the run success criteria:

1. Deterministic code or a direct lookup.
2. One model call with the required context, retrieval, or tools.
3. A short sequence of verifiable model or tool calls.
4. Conditional routing for meaningfully different input classes.
5. Parallel branches for genuinely separable work.
6. An evaluator and repair loop when objective node acceptance or run success criteria are explicit.
7. A bounded agent or multi-agent graph when dynamic tool selection is necessary, its permissions and stop conditions can be constrained, and evaluation shows an advantage over simpler or human-led exploration.

Move down this list when evaluation shows a material benefit or when a documented policy, security, or compliance requirement mandates a control. Evaluate mandatory controls for effectiveness and cost even when they cannot be removed. Extra nodes consume tokens, time, engineering effort, and review attention. They also create more handoffs and failure surfaces.

Keep three kinds of criteria distinct: **run success criteria** define the requested outcome, **node acceptance criteria** define when one node has completed its contract, and **partial-sufficiency criteria** define when a run may return a useful partial result after a branch or dependency fails.

### When a graph helps

Use explicit graph control when at least one of these is material:

- Tasks have prerequisites, branches, joins, retries, or stop conditions.
- Different steps need different tools, permissions, models, or context.
- Work can be parallelized without hiding important dependencies.
- A protected action requires approval before execution.
- Runs must survive failure, pause, resume, or generate the records required for later audit.
- The workflow will be evaluated repeatedly against stable criteria.

### When to stay simple

A direct call or short linear chain is usually preferable when:

- The task is narrow and low risk.
- The answer can be checked cheaply.
- The required context fits cleanly in one call.
- Branching would mainly duplicate the same reasoning.
- The task is still exploratory and a person needs to discover the useful path before it can be bounded safely.
- Coordination cost is larger than the measured quality gain.

## 2. Give every node a contract

A role name is not a node contract. Calling a model an “expert,” “skeptic,” or “executive” describes a style; it does not define reliable behavior.

Every node should declare:

- its purpose and owner;
- required inputs and the state fields it may read;
- allowed tools, sources, and permissions;
- forbidden actions and data boundaries;
- output schema and fields it may update;
- acceptance criteria;
- timeout, retry limit, and failure route;
- cost or token budget where relevant;
- whether it performs an external side effect;
- the evidence required to claim completion.

Use deterministic nodes for work that code can check more reliably, such as schema validation, arithmetic, deduplication, policy enforcement, file comparison, tests, and permission checks. Reserve model judgment for work that needs interpretation or synthesis.

## 3. Let edges encode real policy

Edges should express why another node is allowed to run. Common edge types include:

- fixed prerequisite transitions;
- conditional routes based on validated state;
- fan-out to parallelizable branches;
- fan-in with an explicit merge rule;
- targeted repair routes;
- bounded retry loops;
- escalation to a human or specialist;
- terminal success, partial, blocked, failed, and cancelled states.

“Run these in separate chats” is an execution suggestion, not an edge definition. A useful graph states the trigger, the state passed forward, and what happens when a prerequisite is missing.

Production graphs often contain cycles. Every cycle needs a maximum attempt count, an escalation route, and a terminal condition. “Try again until good” is not a safe stopping rule.

## 4. Treat state as a governed record

State is the current, inspectable record of a run. It should be structured around decisions and artifacts rather than an ever-growing transcript.

A minimum state normally includes:

- run identifier, objective, run success criteria, partial-sufficiency criteria, and constraints;
- risk and data-sensitivity classification;
- selected topology and node status;
- immutable input references;
- artifact identifiers and versions;
- claim and evidence identifiers;
- unresolved questions and conflicts;
- errors, retries, total-run deadlines, cancellation events, budgets, and timestamps;
- approval records and proposed actions;
- final outcome and verification result.
- graph, prompt, model, tool, schema, security-policy, and approval-policy versions required to interpret or resume the state.

Parallel branches should receive only the state they need. Give them branch-local working state and define how their outputs join. Append-only evidence records are safer than allowing several workers to overwrite the same summary.

Keep four concepts separate:

1. **Conversation history:** a stored transcript in a product or application.
2. **Working context:** information supplied to the model for the current call.
3. **Checkpoint state:** the data required to pause and resume one workflow run.
4. **Organizational knowledge:** curated information intended for reuse across runs.

These are not interchangeable. A chat may remain stored without being supplied to a later call. A checkpoint may resume a run without being suitable as long-term knowledge.

## 5. Use isolation carefully

Separate branches can reduce direct anchoring on one another’s intermediate conclusions. They do not guarantee independent evidence or independent errors.

Branches can still share:

- the same upstream framing;
- the same model family or provider;
- overlapping training data;
- the same search results or source pool;
- the same missing assumption;
- correlated evaluation errors.

Describe such branches as **context-isolated** or **separately scoped**, not “unpolluted” or “truly independent.” Where independence matters, vary the evidence assignment, require disconfirming searches, preserve branch-local assumptions, and use external checks. Even different models may make correlated mistakes.

Parallel collection also has a tradeoff. Some questions are coupled: customer pain affects competitor analysis, and distribution constraints affect willingness to pay. Give each branch primary ownership while requiring it to report cross-branch dependencies and conflicts.

## 6. Separate collection, verification, criticism, and synthesis

These are different jobs:

- **Collection** finds candidate facts, observations, and hypotheses.
- **Source verification** checks whether cited material exists and supports the claim within the stated scope.
- **Criticism** tests logic, assumptions, omissions, counterexamples, and decision relevance.
- **Synthesis** produces a conclusion while preserving provenance, disagreement, and uncertainty.

A factual claim is material when its falsity could change a run success check, decision, stated risk, or protected action. Those claims need claim-level evidence and verification; incidental details may use lighter treatment defined by policy.

A skeptical tone does not create an audit. A verifier should reopen sources, check dates and locators, recalculate material numbers where possible, and record whether each claim is supported, partially supported, unsupported, contradicted, or unverifiable. A critic should work from that verified ledger rather than from prose confidence.

Prompt-only self-correction has shown mixed and task-dependent results. External feedback, tools, reference answers, tests, and primary evidence provide stronger correction signals than asking a model to reconsider its own text.

The final synthesis must preserve valid stop outcomes. For decision work with sufficient evidence, allowed results should include:

- proceed;
- proceed only if named conditions hold;
- run a specified test;
- defer;
- stop.

Keep evidence sufficiency separate from run status. Record evidence as sufficient, limited, insufficient, or not applicable. Record the run as success, partial, blocked, failed, or cancelled according to its declared success and partial-sufficiency criteria. For non-decision work, the artifact continues to use its own output schema.

Retain `unsupported`, `contradicted`, and `unverifiable` claims, conflicting evidence, and unresolved challenges with their reasons. A later reviewer must be able to see what failed verification and why.

## 7. Put human approval before the exact action

Review quality depends on reviewer authority, expertise, time, and access to evidence. A protected-action gate should assign all four explicitly.

Require approval based on policy and risk, including:

- magnitude and probability of harm;
- reversibility and rollback difficulty;
- customer, financial, legal, safety, or production impact;
- external visibility;
- data sensitivity;
- model uncertainty and unresolved evidence;
- organizational rules and delegated authority.

A **protected action** is an external side effect matched by the workflow's approval policy. Low-risk, non-executing work may bypass approval. A protected action should pause immediately before execution. Handling sensitive data is governed by data policy; its exposure or egress is a protected action when the approval policy says so.

The approval packet should contain:

- the exact proposed action or change;
- affected people and systems;
- supporting evidence and unresolved risks;
- expected outcome and verification method;
- cost, permissions, and blast radius;
- rollback or cancellation path;
- allowed decisions: approve the exact proposal, edit and resubmit, reject, or request evidence, with a revocation path before execution;
- approval identity, time, scope, and expiry.

Approval is not execution. Keep the proposal, authorization, execution attempt, and outcome verification as separate records. Bind approval to a stable hash and version of the exact payload. Retried or resumed workflows must not repeat a side effect accidentally. Use idempotency controls that the receiving system actually enforces. If they are unavailable or expired, retry only when an authoritative operation-status check confirms that the earlier attempt failed without producing the protected effect, or when a newly reviewed compensating action is approved.

## 8. Design failures before the happy path

Different failures require different responses:

- **Transient tool failure:** retry with backoff within a fixed limit.
- **Invalid model output:** return schema errors to the responsible node.
- **Missing user information:** pause and request the missing input.
- **Evidence conflict:** preserve both claims and route to targeted verification.
- **Partial branch failure:** continue only if declared partial-sufficiency criteria still hold.
- **Policy or security failure:** stop or escalate without improvising a workaround.
- **Budget exhaustion:** return a partial result with explicit gaps.
- **Partial side effect:** reconcile the real external state, then run an approved compensation or escalation path.
- **Unexpected failure:** preserve the last known-good checkpoint and diagnostic record; do not promote uncertain writes to valid state.

Feedback should return to the node that can fix the problem. Restarting the entire graph wastes work and can erase useful state.

Every run also needs a total deadline and cancellation path. Before resuming an old checkpoint after a graph, prompt, model, tool, schema, security-policy, or approval-policy change, verify compatibility and current authorization or perform a deliberate migration. When compatibility cannot be established, abandon the old execution path while preserving its audit record.

## 9. Turn records into governed knowledge

A Markdown file can be one audit artifact. The surrounding system must provide identity, provenance, integrity, access, retention, and traceable links to inputs and actions appropriate to the risk. A file by itself is merely stored output.

Reusable knowledge needs:

- provenance and claim-level source links;
- validation status and promotion criteria;
- creation, verification, and expiry dates;
- scope and applicability;
- owner and review responsibility;
- versioning, supersession, and contradiction history;
- access control, retention, and deletion rules;
- redaction of secrets and sensitive personal data;
- retrieval rules and freshness checks;
- explicit deprecation or revocation rules;
- measurement of whether retrieval improves later work.

Later runs should retrieve only relevant, current records. Retrieved material remains untrusted until its freshness and scope are checked. Stale conclusions must not silently become premises for new decisions.

## 10. Evaluate the system, not the diagram

Define success before choosing the graph. Compare the proposed workflow with a simpler baseline on representative tasks.

Measure separately:

- task success and acceptance-criteria coverage;
- supported, unsupported, and contradicted claim rates;
- citation correctness and source quality;
- critic false alarms and missed errors;
- human corrections and approval overrides;
- cost, latency, and token use;
- retry, timeout, and terminal-failure rates;
- recovery after interruption;
- unintended actions or policy violations.

Use repeated trials when model variability could change the conclusion. Retain an added node when its measured benefit justifies its cost and failure surface or when it implements a documented mandatory control whose effectiveness is tested. If an optional graph does not beat the simpler baseline, simplify it.

Match the grader to the property: deterministic tests for deterministic properties, authoritative post-state observations for side effects, authoritative references for factual claims, qualified humans for judgment, and calibrated model graders only as proxies where stronger checks are unavailable or too costly. Test model graders for missed errors, false alarms, and style or position bias.

Version the evaluation set and rerun regressions after changes to the graph, prompts, models, tools, schemas, or source policy. Production monitoring should compare intended and observed outcomes, capture human overrides and incidents, and feed confirmed failures back into the regression set.

## 11. Treat tools and retrieved content as security boundaries

External text, model output, inter-agent messages, tool responses, checkpoints, and stored memory can contain errors or malicious instructions. The system must treat them as data and must not allow them to redefine policy or authorize an action. Enforce this boundary with code, permissions, validation, and isolation outside the model wherever practical.

Use:

- least-privilege tool access and explicit allowlists;
- separate read, propose, approve, execute, and verify permissions;
- input and structured-output validation;
- data minimization and redaction;
- secret handles instead of raw secrets in model prompts, logs, and reusable artifacts, with any required secret values held in a separate access-controlled execution store;
- scoped network, filesystem, messaging, payment, and deployment access;
- audit logs for actions and approvals;
- controls for memory or context poisoning, insecure inter-agent communication, and cascading failures;
- safe terminal behavior when security checks fail.

## Design maxims

1. Start with a baseline, not a swarm.
2. A node is a contract, not a persona.
3. An edge is a policy, not an arrow drawn after the fact.
4. State should be structured, minimal, and inspectable.
5. Context separation reduces contamination; it does not prove independence.
6. Verification needs evidence or an external signal.
7. Preserve disagreement and uncertainty through synthesis.
8. Gate the exact action according to risk.
9. Every loop needs a limit and a terminal route.
10. Persisted output becomes knowledge only through governance and tested retrieval.
11. Keep a node when evaluation shows that it earns its cost or when it implements a documented mandatory control that has been tested for effectiveness.

## References

- Anthropic, [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — workflow and agent distinctions, composable patterns, and the simplest-sufficient-system principle.
- Anthropic, [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — evaluation of multi-turn, tool-using systems.
- LangChain, [3 Years of Graph Engineering with LangGraph](https://www.langchain.com/blog/3-years-of-graph-engineering-with-langgraph) — graph terminology, node types, dynamic transitions, cycles, and limits of fixed graphs.
- LangGraph, [Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api) — state, nodes, edges, reducers, and routing.
- LangGraph, [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) and [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) — checkpointing, recovery, and human-in-the-loop mechanics.
- LangGraph, [Fault tolerance](https://docs.langchain.com/oss/python/langgraph/fault-tolerance) — retries, timeouts, recovery handlers, and compensation routes.
- NIST, [AI Risk Management Framework Core](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/) — governance, human oversight, roles, and risk-based controls.
- OWASP, [Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) — memory poisoning, insecure inter-agent communication, privilege abuse, and cascading failures.
- Liu et al., [Lost in the Middle](https://aclanthology.org/2024.tacl-1.9/) — position-sensitive degradation in tested long-context tasks.
- Kamoi et al., [When Can LLMs Actually Correct Their Own Mistakes?](https://arxiv.org/abs/2406.01297) — conditions and limitations of model self-correction.
- Du et al., [Improving Factuality and Reasoning in Language Models through Multiagent Debate](https://proceedings.mlr.press/v235/du24e.html) — measured gains on selected tasks.
- Kim et al., [Correlated Errors in Large Language Models](https://proceedings.mlr.press/v267/kim25e.html) — correlated mistakes across models and providers.
- Cemri et al., [Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657) — failure modes in specification, coordination, and verification.
- OpenAI, [Chat and file retention policies in ChatGPT](https://help.openai.com/en/articles/8983778-chat-and-file-retention-policies-in-chatgpt-97) — an example of why stored conversation history and current model context must be distinguished.
