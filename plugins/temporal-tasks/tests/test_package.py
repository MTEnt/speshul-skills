from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PackageTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        required = (
            ".codex-plugin/plugin.json",
            "skills/task-clock/SKILL.md",
            "skills/task-clock/agents/openai.yaml",
            "hooks/hooks.json",
            "hooks/task_clock.py",
        )
        for relative in required:
            with self.subTest(relative=relative):
                self.assertTrue((ROOT / relative).is_file())

    def test_manifest_identity_and_component_path(self) -> None:
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
        self.assertEqual(manifest["name"], "temporal-tasks")
        self.assertEqual(manifest["version"].split("+", 1)[0], "0.1.0")
        self.assertEqual(manifest["author"]["name"], "MTEnt")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertNotIn("hooks", manifest)

    def test_only_clock_events_are_registered(self) -> None:
        config = json.loads((ROOT / "hooks" / "hooks.json").read_text())
        self.assertEqual(
            set(config["hooks"]),
            {"UserPromptSubmit", "PreToolUse", "PostToolUse", "SessionEnd"},
        )
        self.assertEqual(config["hooks"]["PreToolUse"][0]["matcher"], ".*")
        self.assertEqual(config["hooks"]["PostToolUse"][0]["matcher"], ".*")
        self.assertNotIn("anti_loop.py", json.dumps(config))

    def test_task_clock_skill_is_implicitly_invoked(self) -> None:
        skill = (ROOT / "skills" / "task-clock" / "SKILL.md").read_text()
        metadata = (ROOT / "skills" / "task-clock" / "agents" / "openai.yaml").read_text()
        self.assertIn("allow_implicit_invocation: true", metadata)
        self.assertIn("begin with `TASK CLOCK REASSESSMENT`", skill)
        self.assertIn("does not prove that the attempt failed", skill)

    def test_anti_loop_capability_is_not_bundled(self) -> None:
        self.assertFalse((ROOT / "skills" / "anti-loop").exists())
        self.assertFalse((ROOT / "hooks" / "anti_loop.py").exists())

    def test_user_level_hooks_are_outside_package(self) -> None:
        self.assertFalse((ROOT / ".codex" / "hooks.json").exists())


if __name__ == "__main__":
    unittest.main()
