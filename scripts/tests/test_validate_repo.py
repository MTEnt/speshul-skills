from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("validate_repo", REPO / "scripts" / "validate_repo.py")
assert SPEC and SPEC.loader
VALIDATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATE)

SKILL = """---
name: {name}
description: {description}
metadata:
  version: "1.0.0"
---

# {name}

Body.
"""


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def make_repo(root: Path) -> None:
    (root / "contracts").mkdir()
    (root / "contracts" / "loop-limit.md").write_text("# x\n\n<!-- contract:loop-limit:start -->\n## Rule\n\nStop after three.\n<!-- contract:loop-limit:end -->\n", encoding="utf-8")
    (root / "README.md").write_text("# repo\n", encoding="utf-8")
    add_plugin(root, "alpha", "Alpha does one thing. Use for alpha requests.")
    write_json(root / ".claude-plugin" / "marketplace.json", {"name": "m", "owner": {"name": "o"}, "plugins": [{"name": "alpha", "source": "./plugins/alpha"}]})
    write_json(root / ".agents" / "plugins" / "marketplace.json", {"name": "m", "plugins": [{"name": "alpha", "source": {"source": "local", "path": "./plugins/alpha"}}]})


def add_plugin(root: Path, name: str, description: str, *, embed: bool = True) -> Path:
    plugin = root / "plugins" / name
    skill = plugin / "skills" / name
    (skill / "agents").mkdir(parents=True)
    (skill / "agents" / "openai.yaml").write_text("interface: {}\n", encoding="utf-8")
    body = SKILL.format(name=name, description=description)
    if embed:
        body += "\n<!-- contract:loop-limit:start -->\n## Rule\n\nStop after three.\n<!-- contract:loop-limit:end -->\n"
    (skill / "SKILL.md").write_text(body, encoding="utf-8")
    write_json(plugin / ".claude-plugin" / "plugin.json", {"name": name, "version": "1.0.0"})
    write_json(plugin / ".codex-plugin" / "plugin.json", {"name": name, "version": "1.0.0", "description": description, "skills": "./skills/"})
    (plugin / "README.md").write_text("# r\n", encoding="utf-8")
    (plugin / "CHANGELOG.md").write_text("# c\n", encoding="utf-8")
    return plugin


class ValidateRepoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        make_repo(self.root)

    def errors(self, **kwargs) -> list[str]:
        return VALIDATE.validate(self.root, **kwargs).errors

    def test_minimal_repo_is_valid(self) -> None:
        self.assertEqual(self.errors(), [])

    def test_unlisted_plugin_is_reported_for_both_marketplaces(self) -> None:
        add_plugin(self.root, "beta", "Beta does another thing. Use for beta requests.")
        errors = self.errors()
        self.assertEqual(sum("plugin directory not listed: ./plugins/beta" in e for e in errors), 2)

    def test_manifest_version_mismatch(self) -> None:
        write_json(self.root / "plugins" / "alpha" / ".codex-plugin" / "plugin.json", {"name": "alpha", "version": "1.1.0", "description": "d", "skills": "./skills/"})
        self.assertTrue(any("differs from the other manifest" in e for e in self.errors()))

    def test_drifted_contract_block_is_reported(self) -> None:
        skill = self.root / "plugins" / "alpha" / "skills" / "alpha" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8").replace("Stop after three.", "Stop after four."), encoding="utf-8")
        self.assertTrue(any("differs from contracts/loop-limit.md" in e for e in self.errors()))

    def test_hook_script_must_exist(self) -> None:
        hooks = self.root / "plugins" / "alpha" / "hooks" / "hooks.json"
        write_json(hooks, {"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "python \"${CLAUDE_PLUGIN_ROOT}/hooks/missing.py\""}]}]}})
        self.assertTrue(any("hook script does not exist: hooks/missing.py" in e for e in self.errors()))

    def test_generated_directories_are_rejected(self) -> None:
        (self.root / "plugins" / "alpha" / "__pycache__").mkdir()
        self.assertTrue(any("generated directory" in e for e in self.errors()))

    def test_overlap_is_warning_unless_strict(self) -> None:
        plugin = self.root / "plugins" / "alpha"
        for index in range(6):
            name = f"twin-{index}"
            skill = plugin / "skills" / name
            (skill / "agents").mkdir(parents=True)
            (skill / "agents" / "openai.yaml").write_text("interface: {}\n", encoding="utf-8")
            (skill / "SKILL.md").write_text(SKILL.format(name=name, description="Plan build audit optimize paid search social campaigns budgets bidding tracking."), encoding="utf-8")
        report = VALIDATE.validate(self.root)
        self.assertTrue(any("overlap" in w for w in report.warnings))
        self.assertFalse(any("overlap" in e for e in report.errors))
        self.assertTrue(any("overlap" in e for e in self.errors(strict_overlap=True)))

    def test_real_repository_validates(self) -> None:
        report = VALIDATE.validate(REPO)
        self.assertEqual(report.errors, [], "\n".join(report.errors))


if __name__ == "__main__":
    unittest.main()
