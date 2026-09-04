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
HOOK_PATH = ROOT / "hooks" / "verification_gate.py"
SPEC = importlib.util.spec_from_file_location("verification_gate", HOOK_PATH)
assert SPEC and SPEC.loader
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)

RECEIPT = "Done.\n\nRECEIPT\nOutcome: fixed\nChanged: a.py\nVerified: pytest passed\nUnverified: none\nOpen: none\n"


class ClassificationTests(unittest.TestCase):
    def test_editor_tools_are_mutations(self) -> None:
        for tool in ("Edit", "Write", "MultiEdit", "NotebookEdit", "apply_patch"):
            with self.subTest(tool=tool):
                self.assertEqual(GATE.classify_tool(tool, {}), "mutation")

    def test_shell_commands_are_classified(self) -> None:
        cases = {
            "pytest -q": "verification",
            "python -m unittest discover -s tests": "verification",
            "npm run test": "verification",
            "npm test": "verification",
            "cargo test": "verification",
            "python scripts/validate_repo.py": "verification",
            "sed -i 's/a/b/' file.py": "mutation",
            "echo hi > out.txt": "mutation",
            "git commit -m x": "mutation",
            "pip install requests": "mutation",
            "cat file.py": "neutral",
            "git status": "neutral",
            "ls -la": "neutral",
            "grep -rn foo src": "neutral",
        }
        for command, expected in cases.items():
            with self.subTest(command=command):
                self.assertEqual(GATE.classify_tool("Bash", {"command": command}), expected)

    def test_codex_shell_tool_with_list_command(self) -> None:
        self.assertEqual(GATE.classify_tool("local_shell", {"command": ["bash", "-lc", "pytest"]}), "verification")

    def test_unknown_tools_are_neutral(self) -> None:
        self.assertEqual(GATE.classify_tool("Read", {"file_path": "x"}), "neutral")
        self.assertEqual(GATE.classify_tool("WebFetch", {"url": "https://example.test"}), "neutral")


class GateBehaviorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.state_dir = Path(self.temporary.name)

    def event(self, name: str, **extra):
        return {"hook_event_name": name, "session_id": "session-a", **extra}

    def handle(self, event, at: float = 0):
        return GATE.handle_event(event, now=at, state_dir=self.state_dir)

    def post(self, tool: str, command: str | None = None, at: float = 0):
        tool_input = {"command": command} if command else {"file_path": "a.py"}
        return self.handle(self.event("PostToolUse", tool_name=tool, tool_input=tool_input), at)

    def test_session_start_injects_short_context(self) -> None:
        output = self.handle(self.event("SessionStart", source="startup"))
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertLess(len(context), 500)
        self.assertIn("RECEIPT", context)
        self.assertIn("LOOP LIMIT REACHED", context)

    def test_read_only_session_never_blocks(self) -> None:
        self.post("Read")
        self.post("Bash", "git status")
        self.assertIsNone(self.handle(self.event("Stop", last_assistant_message="looked around")))

    def test_mutation_without_receipt_blocks_once(self) -> None:
        self.post("Edit", at=1)
        output = self.handle(self.event("Stop", last_assistant_message="all done", stop_hook_active=False), at=2)
        self.assertEqual(output["decision"], "block")
        self.assertIn("no receipt", output["reason"])
        self.assertIn("No verification command has run", output["reason"])
        again = self.handle(self.event("Stop", last_assistant_message="all done", stop_hook_active=True), at=3)
        self.assertIsNone(again)

    def test_mutation_then_verification_still_requires_receipt(self) -> None:
        self.post("Edit", at=1)
        self.post("Bash", "pytest -q", at=2)
        output = self.handle(self.event("Stop", last_assistant_message="tests pass", stop_hook_active=False), at=3)
        self.assertEqual(output["decision"], "block")
        self.assertNotIn("No verification command has run", output["reason"])

    def test_verification_before_last_mutation_counts_as_unverified(self) -> None:
        self.post("Bash", "pytest -q", at=1)
        self.post("Write", at=2)
        output = self.handle(self.event("Stop", last_assistant_message="done", stop_hook_active=False), at=3)
        self.assertIn("No verification command has run", output["reason"])

    def test_receipt_allows_stop_and_resets_state(self) -> None:
        self.post("Edit", at=1)
        self.post("Bash", "pytest -q", at=2)
        self.assertIsNone(self.handle(self.event("Stop", last_assistant_message=RECEIPT, stop_hook_active=False), at=3))
        self.assertIsNone(self.handle(self.event("Stop", last_assistant_message="follow-up chat", stop_hook_active=False), at=4))

    def test_loop_limit_receipt_allows_stop(self) -> None:
        self.post("Edit", at=1)
        message = "LOOP LIMIT REACHED\nLoops: 3 unsuccessful cycles; loop 4 not started.\nProblem: x\n"
        self.assertIsNone(self.handle(self.event("Stop", last_assistant_message=message, stop_hook_active=False), at=2))

    def test_sessions_are_isolated_and_session_end_cleans_up(self) -> None:
        self.post("Edit", at=1)
        other = {"hook_event_name": "Stop", "session_id": "session-b", "last_assistant_message": "hi", "stop_hook_active": False}
        self.assertIsNone(GATE.handle_event(other, now=2, state_dir=self.state_dir))
        self.handle(self.event("SessionEnd", reason="other"), at=3)
        self.assertEqual(list(self.state_dir.glob("*.json")), [])
        self.assertIsNone(self.handle(self.event("Stop", last_assistant_message="x", stop_hook_active=False), at=4))

    def test_state_contains_only_timestamps(self) -> None:
        self.post("Bash", "echo TOP_SECRET > file.txt", at=1)
        persisted = b"".join(p.read_bytes() for p in self.state_dir.glob("*.json"))
        self.assertNotIn(b"TOP_SECRET", persisted)
        self.assertNotIn(b"session-a", persisted)

    def test_malformed_input_fails_open(self) -> None:
        self.assertIsNone(GATE.handle_event("not-a-dict", state_dir=self.state_dir))
        self.assertIsNone(GATE.handle_event({"hook_event_name": "Stop"}, state_dir=self.state_dir))
        completed = subprocess.run([sys.executable, str(HOOK_PATH)], input="not-json", text=True, capture_output=True, check=False)
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "")

    def test_cli_round_trip(self) -> None:
        env = os.environ.copy()
        env["CLEANCODING_STATE_DIR"] = str(self.state_dir)
        for payload in (
            self.event("PostToolUse", tool_name="Edit", tool_input={"file_path": "a.py"}),
            self.event("Stop", last_assistant_message="done", stop_hook_active=False),
        ):
            completed = subprocess.run([sys.executable, str(HOOK_PATH)], input=json.dumps(payload), text=True, capture_output=True, check=False, env=env)
            self.assertEqual(completed.returncode, 0)
        self.assertEqual(json.loads(completed.stdout)["decision"], "block")


if __name__ == "__main__":
    unittest.main()
