#!/usr/bin/env python3
"""Stateful loop-limit hook for the Anti Loop plugin.

Counts, per session, how many times the same verification command has failed
again after a corrective change. The second failure gets a reminder; the third
gets the shared LOOP LIMIT REACHED receipt requirement. The hook never blocks
the tool result, never runs commands, and stores only hashes and counters in a
SQLite file under the operating system's temporary directory.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import sys
import tempfile
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LOOP_LIMIT = 3
TTL_SECONDS = 24 * 60 * 60
DEFAULT_DB_PATH = Path(tempfile.gettempdir()) / "speshul-anti-loop" / "state.sqlite3"
MUTATING_TOOLS = {"edit", "write", "multiedit", "notebookedit", "apply_patch", "applypatch"}
SHELL_TOOL_HINTS = ("bash", "shell", "exec", "command", "terminal")
VERIFICATION_PATTERNS = (
    re.compile(r"\b(pytest|unittest|nose2|tox|nox|jest|vitest|mocha|tsc|eslint|ruff|mypy|pyright|flake8)\b"),
    re.compile(r"\b(npm|pnpm|yarn|bun)\s+(run\s+)?(test|verify|lint|check|typecheck|build)\b"),
    re.compile(r"\b(go|cargo|dotnet|mvn|gradle|make|just|bazel)\s+(test|check|build|vet|clippy|lint)\b"),
    re.compile(r"\bpython3?\s+(-m\s+\S+\s+)?\S*(test|check|validate|verify|lint)\S*"),
    re.compile(r"\bnode\s+--test\b"),
)
MUTATING_COMMAND_PATTERNS = (
    re.compile(r"(^|[^<>])>{1,2}\s*[^&|\s]"),
    re.compile(r"\bsed\s+(-[a-zA-Z]*i|--in-place)\b"),
    re.compile(r"\b(mv|cp|rm|tee|patch)\b"),
    re.compile(r"\bgit\s+(commit|checkout|switch|reset|revert|apply|stash)\b"),
)
FAILURE_COUNT_PATTERN = re.compile(r"\b([1-9]\d*) (failed|errors?|failures?)\b", re.IGNORECASE)
FAILURE_MARKERS = re.compile(
    r"(^FAILED\b|Traceback \(most recent call last\)|^E\s{2,}|^ERROR\b|npm ERR!|error TS\d+|\berror\[E\d+\]|"
    r"exit code:? [1-9]|exit status [1-9]|command failed|AssertionError|panicked at|FAIL\b)",
    re.IGNORECASE | re.MULTILINE,
)
SUCCESS_MARKERS = re.compile(r"(^OK\b|\b\d+ passed\b(?![^\n]*\bfailed\b)|all tests passed|0 failed|exit code:? 0\b)", re.IGNORECASE | re.MULTILINE)

SCHEMA = """
CREATE TABLE IF NOT EXISTS loops (
    session_hash TEXT NOT NULL,
    command_hash TEXT NOT NULL,
    failures INTEGER NOT NULL DEFAULT 0,
    mutation_pending INTEGER NOT NULL DEFAULT 1,
    updated_at REAL NOT NULL,
    PRIMARY KEY (session_hash, command_hash)
);
CREATE INDEX IF NOT EXISTS idx_loops_updated_at ON loops(updated_at);
"""


def _hash(kind: str, value: str) -> str:
    return hashlib.sha256(f"anti-loop-v1:{kind}:{value}".encode("utf-8")).hexdigest()


def _command_text(tool_input: Any) -> str:
    if not isinstance(tool_input, dict):
        return ""
    command = tool_input.get("command", tool_input.get("cmd"))
    if isinstance(command, list):
        command = " ".join(str(part) for part in command)
    if not isinstance(command, str):
        return ""
    command = re.sub(r"^\s*cd\s+\S+\s*(&&|;)\s*", "", command)
    return re.sub(r"\s+", " ", command).strip()


def classify(tool_name: str, tool_input: Any) -> tuple[str, str]:
    """Return (kind, normalized command) where kind is mutation, verification, or neutral."""
    lowered = tool_name.lower()
    if lowered in MUTATING_TOOLS:
        return "mutation", ""
    if any(hint in lowered for hint in SHELL_TOOL_HINTS):
        command = _command_text(tool_input)
        if command and any(pattern.search(command) for pattern in VERIFICATION_PATTERNS):
            return "verification", command
        if command and any(pattern.search(command) for pattern in MUTATING_COMMAND_PATTERNS):
            return "mutation", command
    return "neutral", ""


def _response_text(tool_response: Any) -> str:
    if isinstance(tool_response, str):
        return tool_response
    if isinstance(tool_response, dict):
        parts = []
        for value in tool_response.values():
            if isinstance(value, str):
                parts.append(value)
            elif isinstance(value, (dict, list)):
                parts.append(_response_text(value))
        return "\n".join(parts)
    if isinstance(tool_response, list):
        return "\n".join(_response_text(item) for item in tool_response)
    return ""


def looks_failed(tool_response: Any) -> bool:
    """Best-effort failure detection from structured fields, then output text."""
    if isinstance(tool_response, dict):
        for key in ("exit_code", "exitCode", "returncode", "return_code", "status_code"):
            value = tool_response.get(key)
            if isinstance(value, int):
                return value != 0
        if tool_response.get("error") or tool_response.get("is_error") or tool_response.get("isError"):
            return True
    text = _response_text(tool_response)
    if not text:
        return False
    counted = FAILURE_COUNT_PATTERN.search(text)
    if counted:
        return True
    if FAILURE_MARKERS.search(text):
        return not SUCCESS_MARKERS.search(text) or "Traceback" in text
    return False


def _connect(db_path: str | os.PathLike[str] | None) -> sqlite3.Connection:
    path = Path(db_path) if db_path is not None else Path(os.environ.get("ANTI_LOOP_DB_PATH") or DEFAULT_DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=2.0, isolation_level=None)
    connection.execute("PRAGMA busy_timeout = 2000")
    connection.executescript(SCHEMA)
    return connection


def _message(command: str, failures: int) -> dict[str, Any]:
    shown = command if len(command) <= 120 else command[:117] + "..."
    if failures < LOOP_LIMIT:
        context = (
            f"Anti-loop: `{shown}` has now failed {failures} times after corrective changes. One more failed "
            "loop on this criterion reaches the limit. Change the hypothesis using the new evidence; do not "
            "retry a variant of the same fix."
        )
        return {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": context}}
    started = failures - LOOP_LIMIT
    context = (
        f"Anti-loop: `{shown}` has failed {failures} times after corrective changes; the three-loop limit is "
        "reached. Do not start another corrective attempt on this criterion. Begin the next user-visible "
        "response with the LOOP LIMIT REACHED receipt (Loops, Problem, Attempts, Mechanism, Evidence, "
        "Decision needed, Next step: Waiting for user direction) and stop mutations on this track."
        + (f" Loop {LOOP_LIMIT + started} was started despite the limit; report that." if started > 0 else "")
    )
    system_message = f"ANTI LOOP LIMIT\nReason: the same verification failed {failures} times after corrective changes.\nAction: stop and report with LOOP LIMIT REACHED."
    return {"systemMessage": system_message, "hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": context}}


def handle_event(event: Any, *, now: float | None = None, db_path: str | os.PathLike[str] | None = None) -> dict[str, Any] | None:
    if not isinstance(event, dict):
        return None
    event_name = event.get("hook_event_name")
    if event_name not in {"PostToolUse", "SessionEnd"}:
        return None
    session_id = event.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        return None
    timestamp = float(now) if now is not None else datetime.now(tz=timezone.utc).timestamp()
    session_hash = _hash("session", session_id)
    try:
        with closing(_connect(db_path)) as connection:
            connection.execute("DELETE FROM loops WHERE updated_at <= ?", (timestamp - TTL_SECONDS,))
            if event_name == "SessionEnd":
                connection.execute("DELETE FROM loops WHERE session_hash = ?", (session_hash,))
                return None
            tool_name = event.get("tool_name")
            if not isinstance(tool_name, str):
                return None
            kind, command = classify(tool_name, event.get("tool_input"))
            if kind == "mutation":
                connection.execute("UPDATE loops SET mutation_pending = 1, updated_at = ? WHERE session_hash = ?", (timestamp, session_hash))
                return None
            if kind != "verification":
                return None
            command_hash = _hash("command", command)
            failed = looks_failed(event.get("tool_response"))
            connection.execute("BEGIN IMMEDIATE")
            try:
                row = connection.execute(
                    "SELECT failures, mutation_pending FROM loops WHERE session_hash = ? AND command_hash = ?",
                    (session_hash, command_hash),
                ).fetchone()
                failures, pending = (row[0], row[1]) if row else (0, 1)
                if not failed:
                    connection.execute(
                        "INSERT INTO loops (session_hash, command_hash, failures, mutation_pending, updated_at) VALUES (?, ?, 0, 1, ?) "
                        "ON CONFLICT(session_hash, command_hash) DO UPDATE SET failures = 0, mutation_pending = 1, updated_at = excluded.updated_at",
                        (session_hash, command_hash, timestamp),
                    )
                    connection.execute("COMMIT")
                    return None
                if pending or failures == 0:
                    failures += 1
                connection.execute(
                    "INSERT INTO loops (session_hash, command_hash, failures, mutation_pending, updated_at) VALUES (?, ?, ?, 0, ?) "
                    "ON CONFLICT(session_hash, command_hash) DO UPDATE SET failures = excluded.failures, mutation_pending = 0, updated_at = excluded.updated_at",
                    (session_hash, command_hash, failures, timestamp),
                )
                connection.execute("COMMIT")
            except BaseException:
                connection.execute("ROLLBACK")
                raise
            if failures >= 2 and (pending or failures == 1):
                return _message(command, failures)
            return None
    except (OSError, TypeError, ValueError, sqlite3.Error):
        return None


def main() -> int:
    try:
        event = json.load(sys.stdin)
        output = handle_event(event)
        if output is not None:
            json.dump(output, sys.stdout, separators=(",", ":"))
            sys.stdout.write("\n")
    except (OSError, TypeError, ValueError):
        # Fail open: loop accounting must never interrupt the user's task.
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
