#!/usr/bin/env python3
"""Stateless advisory hook for the Anti Loop plugin."""

from __future__ import annotations

import json
import re
import sys
from pathlib import PurePosixPath
from typing import Any


SESSION_CONTEXT = (
    "Anti-loop guard: derive outcome, acceptance checks, non-goals, change surface, "
    "and stop condition. Make the smallest sufficient change. Do not turn one failure "
    "or an adjacent idea into permanent instructions, dependencies, workflows, schemas, "
    "or tracking unless requested or required by a demonstrated safety or correctness "
    "risk. Reuse, consolidate, or remove first. "
    "After three failed corrective loops on the same acceptance criterion, do not start a "
    "fourth: begin the next user-visible response with the LOOP LIMIT REACHED receipt (Loops, "
    "Problem, Attempts, Mechanism, Evidence, Decision needed, Next step: Waiting for user "
    "direction). Stop when acceptance is met; create no compliance artifacts."
)

CONTROL_BASENAMES = {
    "agents.md",
    "claude.md",
    "hooks.json",
    "skill.md",
    "marketplace.json",
    "plugin.json",
}

PATCH_PATH_PATTERN = re.compile(
    r"^\*\*\*\s+(?:Add|Update|Delete)\s+File:\s*(.+?)\s*$",
    re.MULTILINE,
)


def _normalize_path(value: str) -> str:
    normalized = value.strip().strip('"\'').replace("\\", "/").lower()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _extract_paths(tool_input: Any) -> list[str]:
    if not isinstance(tool_input, dict):
        return []

    found: list[str] = []
    command = tool_input.get("command")
    if isinstance(command, str):
        found.extend(PATCH_PATH_PATTERN.findall(command))

    for key in ("file_path", "path"):
        value = tool_input.get(key)
        if isinstance(value, str):
            found.append(value)

    result: list[str] = []
    seen: set[str] = set()
    for value in found:
        normalized = _normalize_path(value)
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def _is_control_surface(path: str) -> bool:
    pure = PurePosixPath(path)
    basename = pure.name.lower()
    parts = tuple(part.lower() for part in pure.parts)

    if basename in CONTROL_BASENAMES:
        return True
    if len(parts) >= 2 and parts[-2:] == (".codex", "config.toml"):
        return True
    if len(parts) >= 2 and parts[-2:] == (".codex-plugin", "plugin.json"):
        return True
    if len(parts) >= 3 and parts[-3:] == (".agents", "plugins", "marketplace.json"):
        return True
    return any(
        parts[index : index + 2] == (".github", "workflows")
        for index in range(max(0, len(parts) - 1))
    )


def handle_event(event: Any) -> dict[str, Any] | None:
    if not isinstance(event, dict):
        return None

    event_name = event.get("hook_event_name")
    if event_name == "SessionStart":
        return {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": SESSION_CONTEXT,
            }
        }

    if event_name != "PreToolUse":
        return None

    touched = [
        path for path in _extract_paths(event.get("tool_input")) if _is_control_surface(path)
    ]
    if not touched:
        return None

    shown = ", ".join(touched[:3])
    if len(touched) > 3:
        shown += f", and {len(touched) - 3} more"

    context = (
        f"Anti-loop advisory: this edit touches persistent agent or workflow control "
        f"surface(s): {shown}. Continue only if this directly serves the requested "
        "acceptance condition and is in scope. Otherwise reuse, consolidate, or remove "
        "an existing mechanism. This advisory did not block the edit, so do not tell "
        "the user that Anti Loop stopped it."
    )
    system_message = (
        "ANTI LOOP WARNING\n"
        f"Reason: This edit touches persistent agent or workflow control surface(s): {shown}.\n"
        "Action: The edit was allowed."
    )
    return {
        "systemMessage": system_message,
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": context,
        }
    }


def main() -> int:
    try:
        event = json.load(sys.stdin)
        output = handle_event(event)
        if output is not None:
            json.dump(output, sys.stdout, separators=(",", ":"))
            sys.stdout.write("\n")
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        # Fail open: a malformed advisory event must never interrupt the user's task.
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
