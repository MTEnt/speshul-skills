# Framework Mappings

**Verified against official documentation:** 2026-08-27. APIs are unstable; verify again immediately before implementation. GraphSpec semantics remain authoritative.

## LangGraph (Graph API)

Map nodes to `StateGraph` nodes, state channels to the declared state schema/reducers, fixed and conditional edges to graph edges, runtime fan-out to `Send`, combined state/routing updates to `Command`, checkpoints to a checkpointer, and human pause/resume to interrupts. LangGraph uses message-passing supersteps and can run activated nodes in parallel. Application code must still enforce GraphSpec permissions, approval bindings, protected execution, global budgets, and any semantics not native to the runtime.

The Functional API is a code-first mapping when decorators/tasks and control flow can be extracted into the same GraphSpec contract. Record where native Python control flow hides topology.

Official docs: [Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api), [Functional API](https://docs.langchain.com/oss/python/langgraph/functional-api), [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence), [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts).

## Google ADK Graph Workflows

ADK 2 graph workflows define execution nodes and edges combining code, tools, humans, and LLM capabilities, with graph routes, data handling, human input, and dynamic workflows. Map GraphSpec node/edge/data contracts explicitly and record language/version support. Keep approval binding, security policy, migration, and promotion logic application-owned unless current docs demonstrate native equivalence.

Official docs: [Graph-based agent workflows](https://adk.dev/graphs/). The page observed on 2026-08-27 listed Python and Go v2.0.0 support; recheck before use.

## Microsoft Agent Framework

The graph API maps nodes to typed executors and edges/conditions to workflow routes, with fan-out/fan-in groups, events, state, checkpoints, and sub-workflows. Python also exposes an experimental Functional Workflow API using native control flow and `@step`; .NET and Go use graph builders. Map GraphSpec interrupts to the documented human-input primitive and test checkpoint boundaries.

Official docs: [Workflow concepts](https://learn.microsoft.com/en-us/agent-framework/concepts/workflows/). The page was last updated 2026-08-25 when checked.

## AutoGen GraphFlow

Map agent nodes and routes to `DiGraphBuilder`/`GraphFlow`; current docs cover sequential, parallel, conditional, and looping behavior with safe exit conditions. GraphFlow is explicitly experimental, so pin version, write conformance tests, and expect API/behavior changes. Non-agent deterministic nodes may need adapters, and GraphSpec state, controls, and durability must be mapped or owned by the application.

Official docs: [GraphFlow](https://microsoft.github.io/autogen/dev/user-guide/agentchat-user-guide/graph-flow.html).

## OpenAI Agents SDK

The SDK is code-first rather than a general declarative graph runtime. Map model/agent nodes to `Agent`; manager-style bounded calls to agents-as-tools; responsibility transfer to handoffs; deterministic orchestration to application code around `Runner`; structured outputs and guardrails to SDK contracts; and observability to traces/spans. Handoffs and tool calls have different guardrail semantics, so map them explicitly.

Current `Runner` contracts include resumable `RunState`, function-tool approval pause/resume, a local function-tool concurrency limit, and pre-approval tool-input guardrail control. Sessions provide conversation persistence, but do not by themselves implement GraphSpec graph scheduling, joins, checkpoint compatibility, or compensation. Official docs also list Dapr, Temporal, Restate, and DBOS integrations for durable, long-running orchestration; record the selected integration as a separate runtime dependency and test its checkpoint, retry, human-input, and recovery semantics instead of attributing them to the core SDK. Application code or the selected integration still owns any GraphSpec semantic that has no demonstrated native equivalent.

Official docs: [Agents](https://openai.github.io/openai-agents-python/agents/), [Running agents](https://openai.github.io/openai-agents-python/running_agents/), [Orchestration](https://openai.github.io/openai-agents-python/multi_agent/), [Handoffs](https://openai.github.io/openai-agents-python/handoffs/), [Tracing](https://openai.github.io/openai-agents-python/tracing/), [Testing](https://openai.github.io/openai-agents-python/testing/).

Do not target Agent Builder as a durable backend. OpenAI's 2026-06-03 update says Agent Builder and Evals are winding down and will be unavailable on the platform from 2026-11-30, recommending Agents SDK for code workflows: [AgentKit update](https://openai.com/index/introducing-agentkit/).

## Claude Code Workflow tool

**Verified against the in-product authoring reference:** 2026-09-05. The `Workflow` tool runs a plain-JavaScript orchestration script inside a Claude Code session; the runtime spawns subagents, caps concurrency, journals every `agent()` return value, and can resume a run from the longest unchanged prefix of calls.

Map GraphSpec semantics as follows:

| GraphSpec element | Workflow tool construct | Notes |
| --- | --- | --- |
| Model or agent node | `agent(prompt, {label, phase, schema, model, effort, agentType})` | `schema` enforces the node's output contract at the tool-call layer; a node without a schema returns free text and needs an application-side validator. |
| Deterministic node | Plain JavaScript inside the script or a stage callback | No filesystem or Node.js API access; `Date.now()`, `Math.random()`, and argless `new Date()` throw. Pass timestamps through `args`. |
| Sequential edge chain per item | `pipeline(items, stage1, stage2, ...)` | No barrier between stages; a throwing stage drops that item to `null` and skips its remaining stages. Record that as the item's `failed` terminal. |
| Fan-out with join | `parallel(thunks)` | A barrier: every thunk resolves before it returns; failed thunks resolve to `null`. Use only when the join genuinely needs all inputs. Declare `join_behavior` explicitly in the mapping. |
| Bounded cycle | `while` loop with a counter or `budget.remaining()` guard | The runtime caps lifetime agents at 1000 and concurrent agents at min(16, CPUs-2); your GraphSpec `iteration_guard` must still be encoded in script logic. |
| Runtime expansion | `pipeline` or `parallel` over a discovered list | Max 4096 items per call. Expansion cannot raise permissions; the subagent inherits session permissions regardless of the graph. |
| Sub-graph | `workflow(nameOrRef, args)` | One level of nesting only; shares the parent's concurrency cap, abort signal, and token budget. |
| Budgets | `budget.total`, `budget.spent()`, `budget.remaining()` | A user-set token target is a hard ceiling: `agent()` throws once it is exhausted. Cost budgets in GraphSpec map here; latency budgets do not exist natively. |
| Checkpoint and resume | `resumeFromRunId` with an unchanged script prefix | Cached results are keyed by `(prompt, opts)` equality; a changed prompt invalidates every later call. Record this as checkpoint granularity = agent call. |
| Trace and evidence | `journal.jsonl` and per-agent transcripts in the run directory | Sufficient for run and node identity and return values; latency and cost per node must be derived from the transcripts. |
| Isolation for parallel mutation | `isolation: 'worktree'` per agent | Expensive; use only when agents write files concurrently. |
| Human approval, protected actions, `ApprovalBinding` | Not native | Approval, least privilege, idempotency checks, authoritative post-state verification, and compensation remain application-owned: put them in deterministic script code before and after the acting `agent()`, or route the protected action outside the workflow. A subagent's claim that it acted is not post-state evidence. |
| Interrupt and cancellation | Session abort only | There is no per-node interrupt primitive; the cancel route is the run terminal. Name it in `runtime.cancellation.cancel_route`. |
| State channels and reducers | Script variables and return values | State lives in the script's memory for the run; persistence beyond the run is the caller's responsibility. Reducers are ordinary JavaScript over `parallel` results. |

Conformance tests for this target should assert: the script's `meta.phases` match the GraphSpec's declared phases; every node with an output contract passes a `schema`; every cycle has an explicit counter or budget guard; every `parallel` join has a documented behavior for `null` entries; and every protected action is bracketed by deterministic pre-check and post-state verification code. A mapping that relies on prompt text to enforce a bound is incomplete.

Authoring reference: the `workflow-authoring` skill bundled with Claude Code; recheck it before implementation because the runtime API is not versioned separately.

## Code-first harness

Map nodes to typed functions/services, edges to an inspectable scheduler/router, state to a versioned store, and events to a documented schema. Provide a deterministic extractor that emits normalized GraphSpec from code/config. Dynamic dispatch, decorators, reflection, or model-selected tools do not excuse hidden topology or permissions. Conformance tests must compare extracted semantics, not source formatting.

## Mapping deliverable

For every target, return framework/version/date checked, semantic mapping, adapters, unsupported gaps, code locations, and conformance tests. A mapping is incomplete if a GraphSpec invariant is silently dropped.
