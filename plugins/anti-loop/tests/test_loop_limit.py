from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK_PATH = ROOT / "hooks" / "loop_limit.py"
SPEC = importlib.util.spec_from_file_location("loop_limit", HOOK_PATH)
assert SPEC and SPEC.loader
LOOP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LOOP)

FAIL_OUTPUT = "FAILED (failures=1)\nAssertionError: 106.0 != 116.0"
PASS_OUTPUT = "...\nOK"


class FailureDetectionTests(unittest.TestCase):
    def test_structured_exit_codes_win(self) -> None:
        self.assertTrue(LOOP.looks_failed({"exit_code": 1, "output": "OK"}))
        self.assertFalse(LOOP.looks_failed({"exit_code": 0, "output": "FAILED"}))

    def test_text_markers(self) -> None:
        self.assertTrue(LOOP.looks_failed({"type": "text", "text": FAIL_OUTPUT}))
        self.assertTrue(LOOP.looks_failed("1 failed, 4 passed in 0.2s"))
        self.assertTrue(LOOP.looks_failed("Traceback (most recent call last):\n  File x\nValueError: bad"))
        self.assertFalse(LOOP.looks_failed(PASS_OUTPUT))
        self.assertFalse(LOOP.looks_failed("5 passed in 0.1s"))
        self.assertFalse(LOOP.looks_failed("Tests: 3 passed, 0 failed"))
        self.assertFalse(LOOP.looks_failed(""))

    def test_classification(self) -> None:
        self.assertEqual(LOOP.classify("Bash", {"command": "cd repo && python -m unittest  test_x"}), ("verification", "python -m unittest test_x"))
        self.assertEqual(LOOP.classify("Edit", {"file_path": "a.py"}), ("mutation", ""))
        self.assertEqual(LOOP.classify("Bash", {"command": "cat a.py"}), ("neutral", ""))
        self.assertEqual(LOOP.classify("local_shell", {"command": ["bash", "-lc", "npm test"]})[0], "verification")


class LoopLimitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.db_path = Path(self.temporary.name) / "state.sqlite3"

    def verify(self, output: str, at: float, session: str = "s1", command: str = "pytest -q") -> dict | None:
        return LOOP.handle_event(
            {"hook_event_name": "PostToolUse", "session_id": session, "tool_name": "Bash", "tool_input": {"command": command}, "tool_response": {"type": "text", "text": output}},
            now=at,
            db_path=self.db_path,
        )

    def mutate(self, at: float, session: str = "s1") -> None:
        LOOP.handle_event({"hook_event_name": "PostToolUse", "session_id": session, "tool_name": "Edit", "tool_input": {"file_path": "a.py"}}, now=at, db_path=self.db_path)

    def test_three_failed_loops_reach_the_limit(self) -> None:
        self.assertIsNone(self.verify(FAIL_OUTPUT, 1))
        self.mutate(2)
        second = self.verify(FAIL_OUTPUT, 3)
        self.assertIn("failed 2 times", second["hookSpecificOutput"]["additionalContext"])
        self.assertNotIn("systemMessage", second)
        self.mutate(4)
        third = self.verify(FAIL_OUTPUT, 5)
        self.assertIn("LOOP LIMIT REACHED", third["hookSpecificOutput"]["additionalContext"])
        self.assertIn("ANTI LOOP LIMIT", third["systemMessage"])
        self.assertNotIn("decision", third)

    def test_repeated_failure_without_a_change_is_one_loop(self) -> None:
        self.assertIsNone(self.verify(FAIL_OUTPUT, 1))
        self.assertIsNone(self.verify(FAIL_OUTPUT, 2))
        self.assertIsNone(self.verify(FAIL_OUTPUT, 3))
        self.mutate(4)
        self.assertIn("failed 2 times", self.verify(FAIL_OUTPUT, 5)["hookSpecificOutput"]["additionalContext"])

    def test_success_resets_the_count(self) -> None:
        self.verify(FAIL_OUTPUT, 1)
        self.mutate(2)
        self.verify(FAIL_OUTPUT, 3)
        self.mutate(4)
        self.assertIsNone(self.verify(PASS_OUTPUT, 5))
        self.mutate(6)
        self.assertIsNone(self.verify(FAIL_OUTPUT, 7))

    def test_fourth_loop_is_reported(self) -> None:
        for step in range(3):
            self.verify(FAIL_OUTPUT, step * 2 + 1)
            self.mutate(step * 2 + 2)
        fourth = self.verify(FAIL_OUTPUT, 20)
        self.assertIn("Loop 4 was started despite the limit", fourth["hookSpecificOutput"]["additionalContext"])

    def test_different_commands_and_sessions_are_independent(self) -> None:
        self.verify(FAIL_OUTPUT, 1)
        self.mutate(2)
        self.assertIsNone(self.verify(FAIL_OUTPUT, 3, command="npm test"))
        self.assertIsNone(self.verify(FAIL_OUTPUT, 4, session="s2"))

    def test_session_end_clears_state_and_persists_no_raw_text(self) -> None:
        self.verify(FAIL_OUTPUT, 1, command="pytest tests/test_secret_thing.py")
        persisted = self.db_path.read_bytes()
        self.assertNotIn(b"test_secret_thing", persisted)
        self.assertNotIn(b"s1", persisted.replace(b"sqlite", b""))
        LOOP.handle_event({"hook_event_name": "SessionEnd", "session_id": "s1"}, now=2, db_path=self.db_path)
        self.mutate(3)
        self.assertIsNone(self.verify(FAIL_OUTPUT, 4))

    def test_malformed_input_fails_open(self) -> None:
        self.assertIsNone(LOOP.handle_event("nope", db_path=self.db_path))
        self.assertIsNone(LOOP.handle_event({"hook_event_name": "PostToolUse"}, db_path=self.db_path))
        completed = subprocess.run([sys.executable, str(HOOK_PATH)], input="not-json", text=True, capture_output=True, check=False)
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "")

    def test_cli_round_trip(self) -> None:
        env = os.environ.copy()
        env["ANTI_LOOP_DB_PATH"] = str(self.db_path)
        payload = {"hook_event_name": "PostToolUse", "session_id": "cli", "tool_name": "Bash", "tool_input": {"command": "pytest"}, "tool_response": {"text": FAIL_OUTPUT}}
        mutation = {"hook_event_name": "PostToolUse", "session_id": "cli", "tool_name": "Write", "tool_input": {"file_path": "x"}}
        for event in (payload, mutation, payload):
            completed = subprocess.run([sys.executable, str(HOOK_PATH)], input=json.dumps(event), text=True, capture_output=True, check=False, env=env)
            self.assertEqual(completed.returncode, 0)
        self.assertIn("failed 2 times", json.loads(completed.stdout)["hookSpecificOutput"]["additionalContext"])


if __name__ == "__main__":
    unittest.main()
