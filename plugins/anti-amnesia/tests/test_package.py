from __future__ import annotations

import json
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]


class PackageTests(unittest.TestCase):
    def test_manifest_points_to_bundled_skill(self) -> None:
        manifest = json.loads(
            (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(manifest["name"], "anti-amnesia")
        self.assertEqual(manifest["author"]["name"], "MTEnt")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertTrue(
            (PLUGIN_ROOT / "skills" / "anti-amnesia" / "SKILL.md").is_file()
        )

    def test_default_hook_covers_session_continuity_sources(self) -> None:
        config = json.loads(
            (PLUGIN_ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8")
        )
        session_start = config["hooks"]["SessionStart"]

        self.assertEqual(len(session_start), 1)
        matcher = set(session_start[0]["matcher"].split("|"))
        self.assertEqual(matcher, {"startup", "resume", "clear", "compact"})

        handler = session_start[0]["hooks"][0]
        self.assertIn("${PLUGIN_ROOT}/hooks/session_start.py", handler["command"])
        self.assertIn(
            "${PLUGIN_ROOT}/hooks/session_start.py", handler["commandWindows"]
        )
        self.assertTrue((PLUGIN_ROOT / "hooks" / "session_start.py").is_file())


if __name__ == "__main__":
    unittest.main()
