from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
HOOK_PATH = PLUGIN_ROOT / "hooks" / "session_start.py"


def load_hook_module():
    spec = importlib.util.spec_from_file_location("anti_amnesia_session_start", HOOK_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load session_start.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SessionStartHookTests(unittest.TestCase):
    def test_build_output_adds_bounded_policy(self) -> None:
        module = load_hook_module()
        output = module.build_output({"hook_event_name": "SessionStart"})

        self.assertEqual(
            output["hookSpecificOutput"]["hookEventName"], "SessionStart"
        )
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("retrospective questions", context)
        self.assertIn("present state", context)
        self.assertLess(len(context), 1800)

    def test_non_session_event_produces_no_context(self) -> None:
        module = load_hook_module()
        self.assertIsNone(module.build_output({"hook_event_name": "Stop"}))

    def test_cli_emits_valid_hook_json(self) -> None:
        event = {
            "session_id": "test-session",
            "cwd": str(PLUGIN_ROOT),
            "hook_event_name": "SessionStart",
            "source": "startup",
        }
        completed = subprocess.run(
            [sys.executable, str(HOOK_PATH)],
            input=json.dumps(event),
            text=True,
            capture_output=True,
            check=True,
        )

        output = json.loads(completed.stdout)
        self.assertEqual(
            output["hookSpecificOutput"]["hookEventName"], "SessionStart"
        )

    def test_malformed_input_fails_open_without_output(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(HOOK_PATH)],
            input="not-json",
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertEqual(completed.stdout, "")


if __name__ == "__main__":
    unittest.main()
