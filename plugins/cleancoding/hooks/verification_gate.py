#!/usr/bin/env python3
"""Completion gate for the cleancoding plugin.

Tracks, per session, whether the agent changed files and whether a verification
command ran after the last change. On ``Stop`` it returns the turn to the agent
once when the final response changed files but carries no receipt. It never runs
commands, never reads transcripts or source files, and fails open on any error.

State is a small JSON file under the operating system's temporary directory keyed
by a hashed session id. Persisted fields are timestamps only.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

MUTATING_TOOLS = {"edit", "write", "multiedit", "notebookedit", "apply_patch", "applypatch"}
SHELL_TOOL_HINTS = ("bash", "shell", "exec", "command", "terminal")
MUTATING_COMMAND_PATTERNS = (
    re.compile(r"(^|[^<>])>{1,2}\s*[^&|\s]"),          # output redirection into a file
    re.compile(r"\bsed\s+(-[a-zA-Z]*i|--in-place)\b"),
    re.compile(r"\b(mv|cp|rm|rmdir|mkdir|touch|tee|ln|chmod|chown|patch)\b"),
    re.compile(r"\bgit\s+(commit|merge|rebase|checkout|switch|reset|revert|cherry-pick|apply|stash|mv|rm|push)\b"),
    re.compile(r"\b(npm|pnpm|yarn|pip|pip3|uv|poetry|cargo|go)\s+(install|add|remove|uninstall|update|upgrade)\b"),
)
VERIFICATION_COMMAND_PATTERNS = (
    re.compile(r"\b(pytest|unittest|nose2|tox|nox)\b"),
    re.compile(r"\bpython3?\s+(-m\s+\S+\s+)?\S*(test|check|validate|verify|lint)\S*"),
    re.compile(r"\b(npm|pnpm|yarn|bun)\s+(run\s+)?(test|verify|lint|check|typecheck|build)\b"),
    re.compile(r"\b(npx\s+)?(jest|vitest|mocha|eslint|tsc|prettier\s+--check|biome)\b"),
    re.compile(r"\b(go|cargo|dotnet|mvn|gradle|make|just|bazel)\s+(test|check|clippy|vet|build|lint)\b"),
    re.compile(r"\b(ruff|mypy|pyright|flake8|black\s+--check|shellcheck|golangci-lint)\b"),
    re.compile(r"\bnode\s+--test\b"),
    re.compile(r"\bcurl\b.*\b(localhost|127\.0\.0\.1)\b"),
)
TTL_SECONDS = 24 * 60 * 60
SESSION_CONTEXT = (
    "Clean-coding gate: derive a task contract before editing, fix causes not symptoms, "
    "stop after three failed loops with the LOOP LIMIT REACHED receipt, run the acceptance "
    "checks after the last change, and end mutating work with the RECEIPT block (Outcome, "
    "Changed, Verified, Unverified, Open). The Stop hook returns the turn once when files "
    "changed but no receipt was written."
)


def _state_dir(override: str | os.PathLike[str] | None) -> Path:
    if override is not None:
        return Path(override)
    configured = os.environ.get("CLEANCODING_STATE_DIR")
    return Path(configured) if configured else Path(tempfile.gettempdir()) / "speshul-cleancoding"


def _state_path(session_id: str, override: str | os.PathLike[str] | None) -> Path:
    digest = hashlib.sha256(f"cleancoding-v1:{session_id}".encode("utf-8")).hexdigest()
    return _state_dir(override) / f"{digest}.json"


def _load_state(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _save_state(path: Path, state: dict[str, Any], now: float) -> None:
    state["updated_at"] = now
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, separators=(",", ":")), encoding="utf-8")
    os.replace(temporary, path)


def _cleanup_expired(directory: Path, now: float) -> None:
    if not directory.is_dir():
        return
    for candidate in directory.glob("*.json"):
        try:
            if now - candidate.stat().st_mtime > TTL_SECONDS:
                candidate.unlink()
        except OSError:
            continue


def _command_text(tool_input: Any) -> str:
    if not isinstance(tool_input, dict):
        return ""
    command = tool_input.get("command", tool_input.get("cmd"))
    if isinstance(command, list):
        return " ".join(str(part) for part in command)
    return command if isinstance(command, str) else ""


def classify_tool(tool_name: str, tool_input: Any) -> str:
    """Return 'mutation', 'verification', or 'neutral' for one completed tool call."""
    lowered = tool_name.lower()
    if lowered in MUTATING_TOOLS:
        return "mutation"
    if any(hint in lowered for hint in SHELL_TOOL_HINTS):
        command = _command_text(tool_input)
        if not command:
            return "neutral"
        if any(pattern.search(command) for pattern in VERIFICATION_COMMAND_PATTERNS):
            return "verification"
        if any(pattern.search(command) for pattern in MUTATING_COMMAND_PATTERNS):
            return "mutation"
    return "neutral"


def has_receipt(message: str) -> bool:
    return ("RECEIPT" in message and "Verified:" in message) or "LOOP LIMIT REACHED" in message


def handle_event(
    event: Any,
    *,
    now: float | None = None,
    state_dir: str | os.PathLike[str] | None = None,
) -> dict[str, Any] | None:
    """Handle one lifecycle event; return hook JSON output or None."""
    if not isinstance(event, dict):
        return None
    event_name = event.get("hook_event_name")
    timestamp = float(now) if now is not None else time.time()
    if event_name == "SessionStart":
        return {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": SESSION_CONTEXT}}
    session_id = event.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        return None
    path = _state_path(session_id, state_dir)
    try:
        if event_name == "PostToolUse":
            tool_name = event.get("tool_name")
            if not isinstance(tool_name, str):
                return None
            kind = classify_tool(tool_name, event.get("tool_input"))
            if kind == "neutral":
                return None
            state = _load_state(path)
            state[f"{kind}_at"] = timestamp
            _save_state(path, state, timestamp)
            return None
        if event_name == "Stop":
            state = _load_state(path)
            mutated_at = state.get("mutation_at")
            if not mutated_at or event.get("stop_hook_active"):
                return None
            message = event.get("last_assistant_message")
            message = message if isinstance(message, str) else ""
            if has_receipt(message):
                _save_state(path, {"mutation_at": None, "verification_at": None}, timestamp)
                return None
            verified_at = state.get("verification_at")
            unverified = not verified_at or float(verified_at) < float(mutated_at)
            reason = (
                "Completion gate: this session changed files but the final response has no receipt. "
                + ("No verification command has run since the last file change; run the acceptance checks now. "
                   if unverified else "")
                + "Then end with the RECEIPT block (Outcome, Changed, Verified, Unverified, Open), "
                "or with LOOP LIMIT REACHED if the stop rule applies. If verification is genuinely "
                "impossible, say so under Unverified with the reason."
            )
            return {"decision": "block", "reason": reason}
        if event_name == "SessionEnd":
            try:
                path.unlink()
            except OSError:
                pass
            _cleanup_expired(path.parent, timestamp)
            return None
    except OSError:
        return None
    return None


def main() -> int:
    try:
        event = json.load(sys.stdin)
        output = handle_event(event)
        if output is not None:
            json.dump(output, sys.stdout, separators=(",", ":"))
            sys.stdout.write("\n")
    except (OSError, TypeError, ValueError):
        # Fail open: the gate must never interrupt the user's task because of its own error.
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
