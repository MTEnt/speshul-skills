from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PackageTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        required = (
            ".codex-plugin/plugin.json",
            "skills/anti-loop/SKILL.md",
            "skills/anti-loop/agents/openai.yaml",
            "hooks/hooks.json",
            "hooks/anti_loop.py",
        )
        for relative in required:
            with self.subTest(relative=relative):
                self.assertTrue((ROOT / relative).is_file())

    def test_manifest_identity_and_component_path(self) -> None:
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
        self.assertEqual(manifest["name"], "anti-loop")
        self.assertEqual(manifest["version"].split("+", 1)[0], "0.2.0")
        self.assertEqual(manifest["author"]["name"], "MTEnt")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertNotIn("hooks", manifest)

    def test_hook_surface_is_deliberately_small(self) -> None:
        config = json.loads((ROOT / "hooks" / "hooks.json").read_text())
        self.assertEqual(set(config["hooks"]), {"SessionStart", "PreToolUse"})
        matcher = config["hooks"]["PreToolUse"][0]["matcher"]
        self.assertIn("apply_patch", matcher)
        self.assertNotIn("Bash", matcher)


if __name__ == "__main__":
    unittest.main()
