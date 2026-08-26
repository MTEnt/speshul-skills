"""Inject Anti-Amnesia's bounded recent-work policy into Codex sessions."""

from __future__ import annotations

import json
import sys
from typing import Any


POLICY = """Anti-Amnesia recent-work policy:
- Distinguish retrospective questions about your recorded actions from questions about present state.
- When asked what you just did, changed, ran, found, tested, or concluded, answer first from the current conversation, tool results, and latest completed response. Do not call tools solely to reconstruct actions already present in that record.
- If the record is missing, ambiguous, or contradictory, say what is unknown. Do not silently inspect the workspace unless the user requests verification, reconstruction, or current state.
- Use tools normally for current-state questions and fresh verification. Never present a past observation as confirmed-current without a present check.
- After tool-using or mutating work, make the final response a compact factual receipt: outcome, material files or systems changed, checks and observed results, and unresolved items. Do not add a receipt when no work was performed.
"""


def build_output(event: dict[str, Any]) -> dict[str, Any] | None:
    """Return model context only for the SessionStart event."""
    if event.get("hook_event_name") != "SessionStart":
        return None

    return {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": POLICY,
        }
    }


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    if not isinstance(event, dict):
        return 0

    output = build_output(event)
    if output is not None:
        json.dump(output, sys.stdout, ensure_ascii=True, separators=(",", ":"))
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
