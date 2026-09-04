---
name: anti-amnesia
description: Answer retrospective questions about immediately preceding work from the current conversation and tool record without needless re-execution, and close tool-using work with the shared handoff receipt. Use when the user asks what you just did, changed, ran, found, tested, or concluded. Do not use for requests to verify present state or investigate new changes.
license: MIT
metadata:
  version: "0.2.0"
  author: MTEnt
---

# Anti-Amnesia

Treat a question about your immediately preceding work as retrospective unless the user asks whether that state remains true now.

## Recall recent work

1. Use the available record in this order: tool results from the relevant turn, the completed assistant response, the most recent receipt, then any compacted conversation summary.
2. Answer directly from that record. Do not call tools merely to rediscover actions already recorded.
3. Distinguish actions performed, checks and observed results, and anything left unresolved. Keep the answer proportional to the question.
4. Do not claim that recorded state is current unless it was verified in the present turn.

If the record is missing, ambiguous, or contradictory, say exactly what cannot be recovered. Do not silently reconstruct it by inspecting the workspace. Inspect only when the user requests current-state verification or asks you to reconstruct the missing record.

## Preserve verification

Use tools normally when the user asks what exists now, whether something still works, or for a fresh check. A retrospective answer and a present-state verification are different tasks; state which one you are providing when that distinction matters.

<!-- contract:handoff-receipt:start -->
## Close with a receipt

After tool-using or mutating work, end the response with a compact factual receipt. Omit it when no work was performed. Every line comes from the recorded actions of this session, not from memory of what was intended.

```text
RECEIPT
Outcome: <what was delivered or decided>
Changed: <files, systems, or state touched; "none" when read-only>
Verified: <checks run and their observed results>
Unverified: <claims, risks, or checks that were skipped, with the reason>
Open: <blocked or deferred items and who decides>
```
<!-- contract:handoff-receipt:end -->

The receipt is the record a later retrospective question is answered from. Write it so a reader who sees nothing else knows what happened, what was proven, and what was not.
