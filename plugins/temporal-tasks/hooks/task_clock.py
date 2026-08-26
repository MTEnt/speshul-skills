#!/usr/bin/env python3
"""Stateful, privacy-preserving clock for the standalone Temporal Tasks plugin."""

from __future__ import annotations

import hashlib
import json
import math
import os
import sqlite3
import sys
import tempfile
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FIXED_THRESHOLDS_MINUTES = (3, 5, 7, 15, 20, 30, 45, 60, 120, 180, 480)
TTL_SECONDS = 24 * 60 * 60
DEFAULT_DB_PATH = Path(tempfile.gettempdir()) / "codex-task-clock" / "state.sqlite3"


SCHEMA = """
CREATE TABLE IF NOT EXISTS turns (
    session_hash TEXT NOT NULL,
    turn_hash TEXT NOT NULL,
    started_at REAL NOT NULL,
    updated_at REAL NOT NULL,
    completed_calls INTEGER NOT NULL DEFAULT 0,
    last_elapsed REAL NOT NULL DEFAULT 0,
    last_threshold REAL NOT NULL DEFAULT 0,
    last_pair_fp TEXT,
    repeat_streak INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (session_hash, turn_hash)
);

CREATE TABLE IF NOT EXISTS tool_calls (
    session_hash TEXT NOT NULL,
    turn_hash TEXT NOT NULL,
    tool_use_hash TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    started_at REAL NOT NULL,
    completed_at REAL,
    duration_seconds REAL,
    input_fp TEXT NOT NULL,
    result_fp TEXT,
    pair_fp TEXT,
    PRIMARY KEY (session_hash, turn_hash, tool_use_hash)
);

CREATE INDEX IF NOT EXISTS idx_turns_updated_at ON turns(updated_at);
CREATE INDEX IF NOT EXISTS idx_tool_calls_turn ON tool_calls(session_hash, turn_hash);
"""


def _hash_identifier(kind: str, value: str) -> str:
    payload = f"task-clock-v1:{kind}:{value}".encode("utf-8", errors="strict")
    return hashlib.sha256(payload).hexdigest()


def _canonical_json(value: Any) -> str:
    """Return a stable JSON representation without relying on object repr output."""

    def normalize(item: Any) -> Any:
        if item is None or isinstance(item, (bool, int, float, str)):
            return item
        if isinstance(item, dict):
            return {
                str(key): normalize(item[key])
                for key in sorted(item, key=lambda candidate: str(candidate))
            }
        if isinstance(item, (list, tuple)):
            return [normalize(child) for child in item]
        return {"unsupported_type": type(item).__name__}

    return json.dumps(
        normalize(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _tool_input_fingerprint(tool_name: str, tool_input: Any) -> str:
    return _fingerprint({"tool_name": tool_name, "tool_input": tool_input})


def _pair_fingerprint(input_fp: str, result_fp: str) -> str:
    return hashlib.sha256(f"{input_fp}:{result_fp}".encode("ascii")).hexdigest()


def _utc_text(timestamp: float) -> str:
    return (
        datetime.fromtimestamp(timestamp, tz=timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )


def _format_duration(seconds: float) -> str:
    total = max(0, int(round(seconds)))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}h {minutes}m {secs}s"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def _thresholds_crossed(previous_seconds: float, elapsed_seconds: float) -> list[int]:
    previous_minutes = max(0.0, previous_seconds / 60.0)
    elapsed_minutes = max(0.0, elapsed_seconds / 60.0)
    crossed = [
        threshold
        for threshold in FIXED_THRESHOLDS_MINUTES
        if previous_minutes < threshold <= elapsed_minutes
    ]
    if elapsed_minutes > 480:
        first_hourly = max(540, int(math.floor(previous_minutes / 60.0) + 1) * 60)
        crossed.extend(range(first_hourly, int(math.floor(elapsed_minutes / 60.0)) * 60 + 1, 60))
    return crossed


def _resolve_db_path(db_path: str | os.PathLike[str] | None) -> Path:
    if db_path is not None:
        return Path(db_path)
    configured = os.environ.get("TASK_CLOCK_DB_PATH")
    return Path(configured) if configured else DEFAULT_DB_PATH


def _connect(db_path: str | os.PathLike[str] | None) -> sqlite3.Connection:
    path = _resolve_db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=2.0, isolation_level=None)
    connection.execute("PRAGMA busy_timeout = 2000")
    connection.execute("PRAGMA journal_mode = WAL")
    connection.executescript(SCHEMA)
    return connection


def _event_keys(event: dict[str, Any]) -> tuple[str, str] | None:
    session_id = event.get("session_id")
    turn_id = event.get("turn_id")
    if not isinstance(session_id, str) or not session_id:
        return None
    if not isinstance(turn_id, str) or not turn_id:
        return None
    return (
        _hash_identifier("session", session_id),
        _hash_identifier("turn", turn_id),
    )


def _cleanup_expired(connection: sqlite3.Connection, now: float) -> None:
    cutoff = now - TTL_SECONDS
    stale = connection.execute(
        "SELECT session_hash, turn_hash FROM turns WHERE updated_at <= ?", (cutoff,)
    ).fetchall()
    for session_hash, turn_hash in stale:
        connection.execute(
            "DELETE FROM tool_calls WHERE session_hash = ? AND turn_hash = ?",
            (session_hash, turn_hash),
        )
    connection.execute("DELETE FROM turns WHERE updated_at <= ?", (cutoff,))


def _initialize_turn(
    connection: sqlite3.Connection, session_hash: str, turn_hash: str, now: float
) -> None:
    connection.execute(
        """
        INSERT INTO turns (session_hash, turn_hash, started_at, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(session_hash, turn_hash) DO UPDATE SET updated_at = excluded.updated_at
        """,
        (session_hash, turn_hash, now, now),
    )


def _user_prompt_submit(
    connection: sqlite3.Connection,
    event: dict[str, Any],
    now: float,
) -> dict[str, Any] | None:
    keys = _event_keys(event)
    if keys is None:
        return None
    session_hash, turn_hash = keys
    connection.execute("BEGIN IMMEDIATE")
    try:
        _cleanup_expired(connection, now)
        _initialize_turn(connection, session_hash, turn_hash, now)
        started_at = connection.execute(
            "SELECT started_at FROM turns WHERE session_hash = ? AND turn_hash = ?",
            (session_hash, turn_hash),
        ).fetchone()[0]
        connection.execute("COMMIT")
    except BaseException:
        connection.execute("ROLLBACK")
        raise

    context = (
        f"Task clock: this active user turn started at {_utc_text(started_at)} UTC. "
        "For substantive work, use: Task budget: SCORE/10 (CONFIDENCE confidence) · "
        "expected RANGE · reassess after CHECKPOINT without progress. Defaults are "
        "1-2=1-5m/3m; 3-4=5-20m/7m; 5-6=20-60m/15m; 7-8=1-3h/30m; "
        "9=3-8h/45m; 10=decompose per stage. Omit the budget for casual or trivial work. "
        "Use this timestamp only for elapsed-work accounting. When a later clock threshold "
        "or repeat signal requires action, pause and output these exact labels in order: "
        "TASK CLOCK REASSESSMENT; Elapsed:; Evidence gained:; Delay cause:; Re-score:; "
        "Decision:. Elapsed time and identical fingerprints do not prove failed attempts or "
        "an unchanged blocker and cannot by themselves trigger the anti-loop hard stop."
    )
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }


def _pre_tool_use(
    connection: sqlite3.Connection,
    event: dict[str, Any],
    now: float,
) -> None:
    keys = _event_keys(event)
    tool_name = event.get("tool_name")
    tool_use_id = event.get("tool_use_id")
    if keys is None or not isinstance(tool_name, str) or not tool_name:
        return None
    if not isinstance(tool_use_id, str) or not tool_use_id:
        return None

    session_hash, turn_hash = keys
    tool_use_hash = _hash_identifier("tool", tool_use_id)
    input_fp = _tool_input_fingerprint(tool_name, event.get("tool_input"))
    connection.execute("BEGIN IMMEDIATE")
    try:
        _initialize_turn(connection, session_hash, turn_hash, now)
        connection.execute(
            """
            INSERT INTO tool_calls (
                session_hash, turn_hash, tool_use_hash, tool_name, started_at, input_fp
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_hash, turn_hash, tool_use_hash) DO NOTHING
            """,
            (session_hash, turn_hash, tool_use_hash, tool_name, now, input_fp),
        )
        connection.execute("COMMIT")
    except BaseException:
        connection.execute("ROLLBACK")
        raise
    return None


def _clock_signal(
    *,
    elapsed: float,
    duration: float,
    tool_name: str,
    call_count: int,
    crossed: list[int],
    repeated: bool,
) -> dict[str, Any]:
    triggers: list[str] = []
    if crossed:
        labels = ", ".join(f"{threshold}m" for threshold in crossed)
        triggers.append(f"elapsed threshold crossed: {labels}")
    if repeated:
        triggers.append("three consecutive identical input/result fingerprints")

    context = (
        "TASK CLOCK SIGNAL\n"
        f"Elapsed: {_format_duration(elapsed)} · last tool: {tool_name} "
        f"({_format_duration(duration)}) · completed calls: {call_count}\n"
        f"Trigger: {'; '.join(triggers)}.\n"
        "Before the next action, compare this signal with the current completion ceiling, "
        "no-progress checkpoint, and concrete evidence. If a clock reassessment condition "
        "is met, pause and begin with TASK CLOCK REASSESSMENT. Identical fingerprints prove "
        "only that recorded calls repeated; they do not prove failed attempts or an unchanged "
        "blocker. Do not use the anti-loop hard-stop receipt without separate concrete evidence "
        "for its three-materially-similar-failures rule."
    )
    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": context,
        }
    }


def _post_tool_use(
    connection: sqlite3.Connection,
    event: dict[str, Any],
    now: float,
) -> dict[str, Any] | None:
    keys = _event_keys(event)
    tool_name = event.get("tool_name")
    tool_use_id = event.get("tool_use_id")
    if keys is None or not isinstance(tool_name, str) or not tool_name:
        return None
    if not isinstance(tool_use_id, str) or not tool_use_id:
        return None

    session_hash, turn_hash = keys
    tool_use_hash = _hash_identifier("tool", tool_use_id)
    result_fp = _fingerprint(event.get("tool_response"))
    fallback_input_fp = _tool_input_fingerprint(tool_name, event.get("tool_input"))

    connection.execute("BEGIN IMMEDIATE")
    try:
        _initialize_turn(connection, session_hash, turn_hash, now)
        call = connection.execute(
            """
            SELECT started_at, input_fp, completed_at
            FROM tool_calls
            WHERE session_hash = ? AND turn_hash = ? AND tool_use_hash = ?
            """,
            (session_hash, turn_hash, tool_use_hash),
        ).fetchone()
        if call is None:
            connection.execute(
                """
                INSERT INTO tool_calls (
                    session_hash, turn_hash, tool_use_hash, tool_name, started_at, input_fp
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (session_hash, turn_hash, tool_use_hash, tool_name, now, fallback_input_fp),
            )
            started_at, input_fp, completed_at = now, fallback_input_fp, None
        else:
            started_at, input_fp, completed_at = call

        if completed_at is not None:
            connection.execute("COMMIT")
            return None

        turn = connection.execute(
            """
            SELECT started_at, completed_calls, last_elapsed, last_pair_fp, repeat_streak
            FROM turns WHERE session_hash = ? AND turn_hash = ?
            """,
            (session_hash, turn_hash),
        ).fetchone()
        turn_started, completed_calls, last_elapsed, last_pair_fp, repeat_streak = turn
        duration = max(0.0, now - float(started_at))
        elapsed = max(0.0, now - float(turn_started))
        pair_fp = _pair_fingerprint(input_fp, result_fp)
        next_streak = repeat_streak + 1 if pair_fp == last_pair_fp else 1
        repeated = next_streak == 3
        crossed = _thresholds_crossed(float(last_elapsed), elapsed)
        next_threshold = max(crossed, default=0)
        next_call_count = int(completed_calls) + 1

        connection.execute(
            """
            UPDATE tool_calls
            SET completed_at = ?, duration_seconds = ?, result_fp = ?, pair_fp = ?
            WHERE session_hash = ? AND turn_hash = ? AND tool_use_hash = ?
            """,
            (
                now,
                duration,
                result_fp,
                pair_fp,
                session_hash,
                turn_hash,
                tool_use_hash,
            ),
        )
        connection.execute(
            """
            UPDATE turns
            SET updated_at = ?, completed_calls = ?, last_elapsed = ?,
                last_threshold = CASE WHEN ? > last_threshold THEN ? ELSE last_threshold END,
                last_pair_fp = ?, repeat_streak = ?
            WHERE session_hash = ? AND turn_hash = ?
            """,
            (
                now,
                next_call_count,
                elapsed,
                next_threshold,
                next_threshold,
                pair_fp,
                next_streak,
                session_hash,
                turn_hash,
            ),
        )
        connection.execute("COMMIT")
    except BaseException:
        connection.execute("ROLLBACK")
        raise

    if not crossed and not repeated:
        return None
    return _clock_signal(
        elapsed=elapsed,
        duration=duration,
        tool_name=tool_name,
        call_count=next_call_count,
        crossed=crossed,
        repeated=repeated,
    )


def _session_end(
    connection: sqlite3.Connection, event: dict[str, Any], now: float
) -> None:
    session_id = event.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        return None
    session_hash = _hash_identifier("session", session_id)
    connection.execute("BEGIN IMMEDIATE")
    try:
        connection.execute("DELETE FROM tool_calls WHERE session_hash = ?", (session_hash,))
        connection.execute("DELETE FROM turns WHERE session_hash = ?", (session_hash,))
        _cleanup_expired(connection, now)
        connection.execute("COMMIT")
    except BaseException:
        connection.execute("ROLLBACK")
        raise
    return None


def handle_event(
    event: Any,
    *,
    now: float | None = None,
    db_path: str | os.PathLike[str] | None = None,
) -> dict[str, Any] | None:
    """Handle one lifecycle event and fail open on malformed input or state errors."""

    if not isinstance(event, dict):
        return None
    event_name = event.get("hook_event_name")
    if event_name not in {"UserPromptSubmit", "PreToolUse", "PostToolUse", "SessionEnd"}:
        return None
    timestamp = float(now) if now is not None else datetime.now(tz=timezone.utc).timestamp()

    try:
        with closing(_connect(db_path)) as connection:
            if event_name == "UserPromptSubmit":
                return _user_prompt_submit(connection, event, timestamp)
            if event_name == "PreToolUse":
                return _pre_tool_use(connection, event, timestamp)
            if event_name == "PostToolUse":
                return _post_tool_use(connection, event, timestamp)
            return _session_end(connection, event, timestamp)
    except (OSError, TypeError, ValueError, sqlite3.Error):
        return None


def main() -> int:
    try:
        event = json.load(sys.stdin)
        output = handle_event(event)
        if output is not None:
            json.dump(output, sys.stdout, separators=(",", ":"))
            sys.stdout.write("\n")
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        # Fail open: clock state must never interrupt the user's task.
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
