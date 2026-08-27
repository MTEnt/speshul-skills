# Graph Engineering Foundations

**Status:** practitioner guidance for an emerging term
**Reviewed:** 2026-08-27

## What the term means here

Graph engineering is the engineering of explicit, executable, inspectable, and evolvable prompt/workflow/agent graphs. The 2026 paper *What makes prompts a graph* proposes four constitutive conditions: explicit structure, separation of structure from prompt content, executable semantics, and first-class artifact status. The 2026 survey uses a broader taxonomy spanning task, agent, system-state, and evolution graphs. These are useful proposals, not settled standards.

A graph artifact must answer:

- What nodes and edges exist in this version?
- What data, control, error, interrupt, and compensation semantics do edges carry?
- What state and permissions can each node read or change?
- How does the runtime schedule, bound, stop, resume, and observe execution?
- How can a reviewer validate, diff, evaluate, promote, or roll back it?

## Exclusions

Do not conflate this practice with:

- knowledge graphs or graph databases;
- GraphRAG or knowledge-graph retrieval;
- prompting models to solve graph-theory or graph-ML tasks;
- model-internal Chain-, Tree-, or Graph-of-Thought reasoning;
- a Mermaid picture without executable semantics;
- a trace reconstructed after execution;
- an informal multi-agent chat with no versioned contracts;
- ordinary code whose effective topology cannot be extracted or inspected.

RAG can appear as an ordinary retrieval node. A code-first harness qualifies only if its topology and contracts can be deterministically extracted into a reviewable representation.

## Neighboring engineering boundaries

| Practice | Primary boundary |
| --- | --- |
| Prompt engineering | One model interaction and its instructions/examples |
| Context engineering | What information and capabilities are exposed for a call |
| Harness engineering | The surrounding runtime, tools, persistence, and product behavior |
| Loop engineering | One controller's repeated observe-decide-act cycle |
| Graph engineering | Explicit relationships among multiple executable components and their lifecycle |

These boundaries can nest. A graph node may contain a prompt, context projection, deterministic harness function, or bounded loop.

## Representation classes

- `declarative`: JSON is the source of truth and a runtime/compiler consumes it.
- `code-first`: code is authoritative, but topology and contracts are deterministically extractable.
- `static`: nodes and edges are fixed for the graph version.
- `conditional`: fixed nodes with declarative route selection.
- `runtime-expanded`: the runtime instantiates nodes/edges from validated data within declared bounds.
- `bounded agent-selected`: a model chooses among a declared finite action/edge set; the model may not mint new privileges or remove bounds.

Dynamic execution is not the same as persistent evolution. Runtime expansion disappears with the run unless separately proposed, evaluated, and promoted as a new graph version.

## The adversarial default

Graphs add coordination latency, state complexity, handoffs, and failure surfaces. Parallel agents can share framing, sources, model errors, or infrastructure failures; separate branches are not automatically independent. A rigid graph can also block useful adaptation.

Therefore:

- require a policy need or evaluated advantage over a simpler baseline;
- prefer a bounded loop when one controller can safely own the action space;
- describe isolation precisely rather than claiming independence;
- remove optional nodes or edges that do not earn their cost;
- allow `no_graph` as a successful selection result.

## Five distinct graph views

1. **Task graph:** prerequisites and deliverables.
2. **Capability graph:** which agent, model, human, code, or tool may perform work.
3. **Communication graph:** permitted messages, delegation, and handoffs.
4. **Runtime-state graph:** state transitions, evidence lineage, checkpoints, failures, and recovery.
5. **Evolution graph:** baseline, candidates, experiments, promotions, rollbacks, and archival relations.

Never overload a task edge to imply capability, communication, state write, or authorization.

## References

- Macedo, [What makes prompts a graph](https://arxiv.org/abs/2607.27578), v1, 2026-07-30.
- Feng et al., [Graph Engineering in the Era of LLM Agents](https://arxiv.org/abs/2608.21156), v1, 2026-08-21.
- Anthropic, [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents).
- LangGraph, [Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api).
