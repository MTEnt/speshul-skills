from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("skill_lint", HERE / "scripts" / "skill_lint.py")
assert SPEC and SPEC.loader
LINT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LINT)

GOOD = """---
name: {name}
description: {description}
metadata:
  version: "1.0.0"
---

# Title

See [ref](references/ref.md).
"""


def make_skill(root: Path, name: str, description: str, *, body: str | None = None, yaml: bool = True, ref: bool = True) -> Path:
    skill = root / name
    (skill / "agents").mkdir(parents=True)
    if yaml:
        (skill / "agents" / "openai.yaml").write_text("interface: {}\n", encoding="utf-8")
    if ref:
        (skill / "references").mkdir()
        (skill / "references" / "ref.md").write_text("# ref\n", encoding="utf-8")
    (skill / "SKILL.md").write_text(body if body is not None else GOOD.format(name=name, description=description), encoding="utf-8")
    return skill


class FrontmatterTests(unittest.TestCase):
    def test_parses_scalars_blocks_and_nested(self) -> None:
        meta, error = LINT.parse_frontmatter('---\nname: x\ndescription: |\n  one\n  two\nmetadata:\n  version: "1.2.3"\n  author: me\n---\nbody')
        self.assertEqual(error, "")
        self.assertEqual(meta["name"], "x")
        self.assertEqual(meta["description"], "one two")
        self.assertEqual(meta["metadata"], {"version": "1.2.3", "author": "me"})

    def test_rejects_missing_or_unclosed_frontmatter(self) -> None:
        self.assertIsNone(LINT.parse_frontmatter("# no frontmatter")[0])
        self.assertIsNone(LINT.parse_frontmatter("---\nname: x\n")[0])


class SkillChecksTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def lint(self, skill: Path) -> LINT.Report:
        report = LINT.Report()
        LINT.check_skill(skill, report)
        return report

    def test_valid_skill_has_no_errors(self) -> None:
        report = self.lint(make_skill(self.root, "good-skill", "Do a thing. Use when asked."))
        self.assertEqual(report.errors, [])

    def test_name_must_match_directory_and_pattern(self) -> None:
        skill = make_skill(self.root, "dir-name", "x", body=GOOD.format(name="other", description="x"))
        self.assertTrue(any("does not match directory" in e for e in self.lint(skill).errors))
        skill = make_skill(self.root, "Bad_Name", "x", body=GOOD.format(name="Bad_Name", description="x"))
        self.assertTrue(any("invalid skill name" in e for e in self.lint(skill).errors))

    def test_version_rules(self) -> None:
        body = "---\nname: no-version\ndescription: x\n---\n\nbody\n"
        skill = make_skill(self.root, "no-version", "x", body=body)
        self.assertTrue(any("metadata.version" in e for e in self.lint(skill).errors))
        body = "---\nname: top-version\nversion: 1.0.0\ndescription: x\nmetadata:\n  version: \"1.0.0\"\n---\n\nbody\n"
        skill = make_skill(self.root, "top-version", "x", body=body)
        self.assertTrue(any("top-level version" in e for e in self.lint(skill).errors))

    def test_description_limit_and_size_budget(self) -> None:
        skill = make_skill(self.root, "long-desc", "x" * 1100)
        self.assertTrue(any("limit is 1024" in e for e in self.lint(skill).errors))
        big = GOOD.format(name="big-skill", description="x") + ("filler line\n" * 600)
        skill = make_skill(self.root, "big-skill", "x", body=big)
        errors = self.lint(skill).errors
        self.assertTrue(any("lines" in e for e in errors))

    def test_broken_links_and_missing_yaml(self) -> None:
        skill = make_skill(self.root, "no-ref", "x", ref=False, yaml=False)
        errors = self.lint(skill).errors
        self.assertTrue(any("broken link" in e for e in errors))
        self.assertTrue(any("openai.yaml" in e for e in errors))

    def test_sibling_overlap_is_reported(self) -> None:
        make_skill(self.root, "paid-ads", "Plan, build, audit, and optimize paid search and social campaigns, budgets, bidding, and conversion tracking.")
        make_skill(self.root, "ad-campaigns", "Plan, build, audit, and optimize paid search and social campaigns, budgets, bidding, and tracking.")
        make_skill(self.root, "press-kit", "Write press releases, media kits, and journalist pitches for earned media.")
        report = LINT.Report()
        LINT.lint_siblings(self.root, report, 0.35, strict=True)
        self.assertTrue(any("ad-campaigns and paid-ads overlap" in e for e in report.errors), report.errors)
        self.assertFalse(any("press-kit" in e for e in report.errors))


if __name__ == "__main__":
    unittest.main()
