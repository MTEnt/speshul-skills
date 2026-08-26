from __future__ import annotations

import importlib.util
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK_PATH = ROOT / "hooks" / "task_clock.py"
SPEC = importlib.util.spec_from_file_location("task_clock", HOOK_PATH)
assert SPEC and SPEC.loader
TASK_CLOCK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TASK_CLOCK)


class TaskClockTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.db_path = Path(self.temporary.name) / "clock.sqlite3"

    def event(self, name: str, *, session: str = "session-a", turn: str = "turn-a", **extra):
        return {
            "hook_event_name": name,
            "session_id": session,
            "turn_id": turn,
            **extra,
        }

    def start(self, at: float = 0, *, session: str = "session-a", turn: str = "turn-a"):
        return TASK_CLOCK.handle_event(
            self.event(
                "UserPromptSubmit",
                session=session,
                turn=turn,
                prompt="raw prompt must not persist",
            ),
            now=at,
            db_path=self.db_path,
        )

    def pre(
        self,
        tool_use_id: str,
        at: float,
        *,
        session: str = "session-a",
        turn: str = "turn-a",
        tool_input=None,
        tool_name: str = "Bash",
    ):
        return TASK_CLOCK.handle_event(
            self.event(
                "PreToolUse",
                session=session,
                turn=turn,
                tool_name=tool_name,
                tool_use_id=tool_use_id,
                tool_input=tool_input if tool_input is not None else {"command": "echo safe"},
            ),
            now=at,
            db_path=self.db_path,
        )

    def post(
        self,
        tool_use_id: str,
        at: float,
        *,
        session: str = "session-a",
        turn: str = "turn-a",
        tool_input=None,
        tool_response=None,
        tool_name: str = "Bash",
    ):
        return TASK_CLOCK.handle_event(
            self.event(
                "PostToolUse",
                session=session,
                turn=turn,
                tool_name=tool_name,
                tool_use_id=tool_use_id,
                tool_input=tool_input if tool_input is not None else {"command": "echo safe"},
                tool_response=(
                    tool_response if tool_response is not None else {"output": "safe result"}
                ),
            ),
            now=at,
            db_path=self.db_path,
        )

    def test_turn_initialization_injects_utc_start(self) -> None:
        output = self.start(at=1_700_000_000)
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(output["hookSpecificOutput"]["hookEventName"], "UserPromptSubmit")
        self.assertIn("2023-11-14T22:13:20Z UTC", context)
        self.assertIn("Task budget: SCORE/10", context)
        self.assertIn("1-2=1-5m/3m", context)
        self.assertIn("TASK CLOCK REASSESSMENT; Elapsed:; Evidence gained:;", context)
        self.assertIn("Delay cause:; Re-score:; Decision:", context)
        self.assertIn("cannot by themselves trigger the anti-loop hard stop", context)

        with closing(sqlite3.connect(self.db_path)) as connection:
            row = connection.execute(
                "SELECT started_at, completed_calls FROM turns"
            ).fetchone()
        self.assertEqual(row, (1_700_000_000.0, 0))

    def test_threshold_crossing_reports_elapsed_long_tool_and_call_count(self) -> None:
        self.start(at=1_000)
        self.pre("tool-1", at=1_001)
        output = self.post("tool-1", at=1_301)
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Elapsed: 5m 1s", context)
        self.assertIn("last tool: Bash (5m 0s)", context)
        self.assertIn("completed calls: 1", context)
        self.assertIn("3m, 5m", context)
        self.assertNotIn("permissionDecision", output["hookSpecificOutput"])

        self.pre("tool-2", at=1_302)
        self.assertIsNone(self.post("tool-2", at=1_303))

    def test_hourly_thresholds_continue_after_eight_hours(self) -> None:
        self.start(at=0)
        self.pre("tool-1", at=0)
        output = self.post("tool-1", at=600 * 60)
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("480m, 540m, 600m", context)

    def test_three_exact_repeats_signal_immediately(self) -> None:
        self.start()
        outputs = []
        for index in range(1, 4):
            self.pre(f"tool-{index}", at=index)
            outputs.append(self.post(f"tool-{index}", at=index + 0.1))
        self.assertIsNone(outputs[0])
        self.assertIsNone(outputs[1])
        context = outputs[2]["hookSpecificOutput"]["additionalContext"]
        self.assertIn("three consecutive identical input/result fingerprints", context)
        self.assertIn("begin with TASK CLOCK REASSESSMENT", context)
        self.assertIn("do not prove failed attempts", context)

    def test_different_pair_resets_repeat_streak(self) -> None:
        self.start()
        for index in range(1, 3):
            self.pre(f"same-{index}", at=index)
            self.assertIsNone(self.post(f"same-{index}", at=index + 0.1))
        self.pre("different", at=3, tool_input={"command": "different"})
        self.assertIsNone(
            self.post("different", at=3.1, tool_input={"command": "different"})
        )
        self.pre("same-again", at=4)
        self.assertIsNone(self.post("same-again", at=4.1))

    def test_parallel_post_updates_have_no_lost_counts(self) -> None:
        self.start()
        call_total = 12
        for index in range(call_total):
            self.pre(f"parallel-{index}", at=1)

        def finish(index: int):
            return self.post(f"parallel-{index}", at=2)

        with ThreadPoolExecutor(max_workers=6) as executor:
            outputs = list(executor.map(finish, range(call_total)))

        with closing(sqlite3.connect(self.db_path)) as connection:
            count, streak = connection.execute(
                "SELECT completed_calls, repeat_streak FROM turns"
            ).fetchone()
        self.assertEqual(count, call_total)
        self.assertEqual(streak, call_total)
        self.assertEqual(sum(output is not None for output in outputs), 1)

    def test_sessions_are_isolated_and_session_end_removes_only_target(self) -> None:
        for session in ("session-a", "session-b"):
            self.start(session=session)
            for index in range(2):
                tool_id = f"{session}-{index}"
                self.pre(tool_id, at=index + 1, session=session)
                self.assertIsNone(self.post(tool_id, at=index + 1.1, session=session))

        TASK_CLOCK.handle_event(
            {"hook_event_name": "SessionEnd", "session_id": "session-a"},
            now=10,
            db_path=self.db_path,
        )
        with closing(sqlite3.connect(self.db_path)) as connection:
            turns = connection.execute("SELECT COUNT(*) FROM turns").fetchone()[0]
            calls = connection.execute("SELECT COUNT(*) FROM tool_calls").fetchone()[0]
        self.assertEqual(turns, 1)
        self.assertEqual(calls, 2)

    def test_abandoned_records_expire_after_24_hours(self) -> None:
        self.start(at=0, session="stale")
        self.pre("stale-tool", at=1, session="stale")
        self.start(at=TASK_CLOCK.TTL_SECONDS + 1, session="current")
        with closing(sqlite3.connect(self.db_path)) as connection:
            turns = connection.execute("SELECT COUNT(*) FROM turns").fetchone()[0]
            calls = connection.execute("SELECT COUNT(*) FROM tool_calls").fetchone()[0]
        self.assertEqual(turns, 1)
        self.assertEqual(calls, 0)

    def test_persisted_state_contains_no_raw_sensitive_content(self) -> None:
        prompt = "TOP_SECRET_PROMPT_9381"
        command = "TOP_SECRET_COMMAND_4827"
        result = "TOP_SECRET_RESULT_1740"
        TASK_CLOCK.handle_event(
            self.event("UserPromptSubmit", prompt=prompt), now=0, db_path=self.db_path
        )
        self.pre("secret-tool-id", at=1, tool_input={"command": command})
        self.post(
            "secret-tool-id",
            at=2,
            tool_input={"command": command},
            tool_response={"output": result},
        )
        persisted = self.db_path.read_bytes()
        for raw in (prompt, command, result, "secret-tool-id", "session-a", "turn-a"):
            with self.subTest(raw=raw):
                self.assertNotIn(raw.encode(), persisted)

    def test_duplicate_post_is_idempotent(self) -> None:
        self.start()
        self.pre("tool-1", at=1)
        self.post("tool-1", at=2)
        self.assertIsNone(self.post("tool-1", at=3))
        with closing(sqlite3.connect(self.db_path)) as connection:
            count = connection.execute("SELECT completed_calls FROM turns").fetchone()[0]
        self.assertEqual(count, 1)

    def test_malformed_input_and_database_failure_fail_open(self) -> None:
        self.assertIsNone(TASK_CLOCK.handle_event("not-an-object", db_path=self.db_path))
        self.assertIsNone(
            TASK_CLOCK.handle_event(
                {"hook_event_name": "UserPromptSubmit"}, db_path=self.db_path
            )
        )
        failing_path = Path(self.temporary.name) / "is-a-directory"
        failing_path.mkdir()
        self.assertIsNone(
            TASK_CLOCK.handle_event(
                self.event("UserPromptSubmit", prompt="safe"), db_path=failing_path
            )
        )

    def test_cli_emits_valid_event_specific_output_and_malformed_input_is_safe(self) -> None:
        env = os.environ.copy()
        env["TASK_CLOCK_DB_PATH"] = str(self.db_path)
        completed = subprocess.run(
            [sys.executable, str(HOOK_PATH)],
            input=json.dumps(self.event("UserPromptSubmit", prompt="representative")),
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )
        self.assertEqual(completed.returncode, 0)
        output = json.loads(completed.stdout)
        self.assertEqual(
            output["hookSpecificOutput"]["hookEventName"], "UserPromptSubmit"
        )

        malformed = subprocess.run(
            [sys.executable, str(HOOK_PATH)],
            input="not-json",
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )
        self.assertEqual(malformed.returncode, 0)
        self.assertEqual(malformed.stdout, "")


if __name__ == "__main__":
    unittest.main()
