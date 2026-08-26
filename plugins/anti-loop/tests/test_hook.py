from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK_PATH = ROOT / "hooks" / "anti_loop.py"
SPEC = importlib.util.spec_from_file_location("anti_loop", HOOK_PATH)
assert SPEC and SPEC.loader
ANTI_LOOP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ANTI_LOOP)


class HookBehaviorTests(unittest.TestCase):
    def test_session_start_adds_concise_context(self) -> None:
        result = ANTI_LOOP.handle_event({"hook_event_name": "SessionStart"})
        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertLess(len(context), 700)
        self.assertIn("smallest sufficient change", context)
        self.assertIn("three materially similar attempts", context)
        self.assertIn("ANTI LOOP STOPPED THIS ATTEMPT", context)
        self.assertIn("Waiting for user direction", context)

    def test_normal_source_patch_has_no_warning(self) -> None:
        result = ANTI_LOOP.handle_event(
            {
                "hook_event_name": "PreToolUse",
                "tool_input": {
                    "command": "*** Begin Patch\n*** Update File: src/widget.py\n*** End Patch"
                },
            }
        )
        self.assertIsNone(result)

    def test_agent_instruction_patch_is_advisory(self) -> None:
        result = ANTI_LOOP.handle_event(
            {
                "hook_event_name": "PreToolUse",
                "tool_input": {
                    "command": "*** Begin Patch\n*** Add File: AGENTS.md\n*** End Patch"
                },
            }
        )
        output = result["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "PreToolUse")
        self.assertIn("did not block", output["additionalContext"])
        self.assertNotIn("permissionDecision", output)
        self.assertEqual(
            result["systemMessage"],
            "ANTI LOOP WARNING\n"
            "Reason: This edit touches persistent agent or workflow control surface(s): agents.md.\n"
            "Action: The edit was allowed.",
        )

    def test_skill_and_workflow_paths_warn(self) -> None:
        for path in (
            "skills/example/SKILL.md",
            ".github/workflows/check.yml",
            ".codex/config.toml",
            ".codex-plugin/plugin.json",
        ):
            with self.subTest(path=path):
                result = ANTI_LOOP.handle_event(
                    {
                        "hook_event_name": "PreToolUse",
                        "tool_input": {
                            "command": f"*** Begin Patch\n*** Update File: {path}\n*** End Patch"
                        },
                    }
                )
                self.assertIsNotNone(result)

    def test_direct_path_input_is_supported(self) -> None:
        result = ANTI_LOOP.handle_event(
            {
                "hook_event_name": "PreToolUse",
                "tool_input": {"file_path": "nested/CLAUDE.md"},
            }
        )
        self.assertIsNotNone(result)

    def test_unrelated_or_malformed_event_fails_open(self) -> None:
        self.assertIsNone(ANTI_LOOP.handle_event({"hook_event_name": "PostToolUse"}))
        completed = subprocess.run(
            [sys.executable, str(HOOK_PATH)],
            input="not-json",
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "")

    def test_cli_emits_valid_json(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(HOOK_PATH)],
            input=json.dumps({"hook_event_name": "SessionStart"}),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(
            json.loads(completed.stdout)["hookSpecificOutput"]["hookEventName"],
            "SessionStart",
        )


if __name__ == "__main__":
    unittest.main()
