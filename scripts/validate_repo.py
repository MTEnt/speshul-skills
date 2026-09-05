#!/usr/bin/env python3
"""Validate every package in the speshul-skills repository.

Skill-level rules (frontmatter, name, description, metadata.version, size budget,
links, agents/openai.yaml, description overlap) are owned by the skill-authoring
package's ``skill_lint.py`` and imported from there so the two never disagree.
This script adds the repository-level rules:

- plugin layout: manifests for both runtimes, matching names and versions, README and CHANGELOG;
- marketplace files list every plugin and point at directories that exist;
- hooks.json files parse and reference scripts that exist;
- shared contract blocks embedded in packages match contracts/*.md verbatim;
- no generated or secret files are committed;
- relative links in package-level markdown resolve.

Usage: python scripts/validate_repo.py [--root PATH] [--strict-overlap] [--overlap-threshold 0.35]
Exit code 0 when there are no errors; 1 otherwise. Warnings never fail the run.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
LINT_PATH = REPO_ROOT / "plugins" / "skill-authoring" / "skills" / "skill-authoring" / "scripts" / "skill_lint.py"
_SPEC = importlib.util.spec_from_file_location("skill_lint", LINT_PATH)
assert _SPEC and _SPEC.loader, f"skill linter not found at {LINT_PATH}"
lint = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(lint)

Report = lint.Report
SEMVER_PATTERN = lint.SEMVER_PATTERN
MARKER_PATTERN = re.compile(r"<!-- contract:([a-z0-9-]+):start -->(.*?)<!-- contract:\1:end -->", re.DOTALL)
# The path ends at whitespace, a quote, or the backslash that escapes a quote inside JSON
# ("...x.py\""); including that backslash made Linux look for a file named "x.py\".
PLUGIN_ROOT_PATTERN = re.compile(r"\$\{(?:CLAUDE_)?PLUGIN_ROOT\}/([^\s\"'\\]+)")
FORBIDDEN_DIRS = {"__pycache__", "node_modules", ".eval-output"}
FORBIDDEN_FILES = {".env"}


def load_json(path: Path, report: Report) -> Any:
    try:
        return json.loads(lint.read_text(path))
    except (OSError, json.JSONDecodeError) as exc:
        report.error(path, f"invalid JSON: {exc}")
        return None


def check_manifests(plugin_dir: Path, report: Report) -> tuple[str | None, list[Path]]:
    claude = plugin_dir / ".claude-plugin" / "plugin.json"
    codex = plugin_dir / ".codex-plugin" / "plugin.json"
    version: str | None = None
    skill_roots: list[Path] = []
    for manifest in (claude, codex):
        if not manifest.is_file():
            report.error(plugin_dir, f"missing {manifest.relative_to(plugin_dir)}")
            continue
        data = load_json(manifest, report)
        if not isinstance(data, dict):
            continue
        if data.get("name") != plugin_dir.name:
            report.error(manifest, f"name {data.get('name')!r} does not match directory {plugin_dir.name!r}")
        manifest_version = data.get("version")
        if not isinstance(manifest_version, str) or not SEMVER_PATTERN.match(manifest_version):
            report.error(manifest, f"version {manifest_version!r} is not semantic")
        elif version is None:
            version = manifest_version
        elif manifest_version != version:
            report.error(manifest, f"version {manifest_version} differs from the other manifest ({version})")
        if manifest is codex and not data.get("description"):
            report.error(manifest, "Codex manifests require a description")
        skills_field = data.get("skills", "./skills/")
        entries = [skills_field] if isinstance(skills_field, str) else list(skills_field or [])
        for entry in entries:
            target = (plugin_dir / entry).resolve()
            if not target.exists():
                report.error(manifest, f"skills path does not exist: {entry}")
            elif target not in skill_roots:
                skill_roots.append(target)
        hooks_field = data.get("hooks")
        if isinstance(hooks_field, str) and not (plugin_dir / hooks_field).is_file():
            report.error(manifest, f"hooks file does not exist: {hooks_field}")
    if (plugin_dir / "hooks" / "hooks.json").is_file() and claude.is_file():
        data = load_json(claude, report)
        if isinstance(data, dict) and data.get("hooks") != "./hooks/hooks.json":
            report.error(claude, "plugin has hooks/hooks.json but the Claude Code manifest does not declare it")
    for required in ("README.md", "CHANGELOG.md"):
        if not (plugin_dir / required).is_file():
            report.error(plugin_dir, f"missing {required}")
    return version, skill_roots


def check_hooks(plugin_dir: Path, report: Report) -> None:
    for hooks_file in sorted(plugin_dir.glob("hooks/*.json")):
        data = load_json(hooks_file, report)
        if not isinstance(data, dict) or not isinstance(data.get("hooks"), dict):
            report.error(hooks_file, "hooks file must contain a top-level 'hooks' object")
            continue
        for script in PLUGIN_ROOT_PATTERN.findall(lint.read_text(hooks_file)):
            if not (plugin_dir / script).is_file():
                report.error(hooks_file, f"hook script does not exist: {script}")


def check_plugin(plugin_dir: Path, report: Report, seen_names: dict[str, Path]) -> list[dict[str, Any]]:
    version, skill_roots = check_manifests(plugin_dir, report)
    check_hooks(plugin_dir, report)
    skills: list[dict[str, Any]] = []
    for root in skill_roots:
        candidates = [root] if (root / "SKILL.md").is_file() else sorted(p for p in root.iterdir() if p.is_dir())
        for skill_dir in candidates:
            info = lint.check_skill(skill_dir, report, seen_names)
            if info:
                skills.append(info)
    if not skills:
        report.error(plugin_dir, "plugin exposes no skills")
    if version and len(skills) == 1 and skills[0]["version"] and skills[0]["version"] != version:
        report.error(skills[0]["path"], f"metadata.version {skills[0]['version']} differs from plugin version {version}")
    return skills


def check_marketplaces(root: Path, plugin_dirs: list[Path], report: Report) -> None:
    expected = {f"./plugins/{p.name}" for p in plugin_dirs}
    claude = root / ".claude-plugin" / "marketplace.json"
    data = load_json(claude, report) if claude.is_file() else None
    if data is None:
        report.error(claude, "missing or invalid Claude Code marketplace")
    else:
        listed: set[str] = set()
        for entry in data.get("plugins", []):
            source = entry.get("source")
            if isinstance(source, str):
                if not (root / source).is_dir():
                    report.error(claude, f"plugin {entry.get('name')!r} source does not exist: {source}")
                listed.add(source)
                if entry.get("name") != Path(source).name:
                    report.warn(claude, f"plugin {entry.get('name')!r} is listed under a different name than its directory")
        for missing in sorted(expected - listed):
            report.error(claude, f"plugin directory not listed: {missing}")
    codex = root / ".agents" / "plugins" / "marketplace.json"
    data = load_json(codex, report) if codex.is_file() else None
    if data is None:
        report.error(codex, "missing or invalid Codex marketplace")
    else:
        listed = set()
        for entry in data.get("plugins", []):
            source = entry.get("source", {})
            path = source.get("path") if isinstance(source, dict) else None
            if path:
                if not (root / path).is_dir():
                    report.error(codex, f"plugin {entry.get('name')!r} path does not exist: {path}")
                listed.add(path)
        for missing in sorted(expected - listed):
            report.error(codex, f"plugin directory not listed: {missing}")


def canonical_blocks(root: Path, report: Report) -> dict[str, str]:
    blocks: dict[str, str] = {}
    for path in sorted((root / "contracts").glob("*.md")):
        for match in MARKER_PATTERN.finditer(lint.read_text(path).replace("\r\n", "\n")):
            name, body = match.group(1), match.group(2)
            if name in blocks:
                report.error(path, f"contract {name!r} is defined twice")
            blocks[name] = body
    return blocks


def check_contract_blocks(root: Path, blocks: dict[str, str], report: Report) -> None:
    embedded: dict[str, int] = {name: 0 for name in blocks}
    for path in lint.iter_markdown(root / "plugins"):
        for match in MARKER_PATTERN.finditer(lint.read_text(path).replace("\r\n", "\n")):
            name, body = match.group(1), match.group(2)
            if name not in blocks:
                report.error(path, f"embeds unknown contract {name!r}")
                continue
            embedded[name] += 1
            if body != blocks[name]:
                report.error(path, f"embedded contract {name!r} differs from contracts/{name}.md")
    for name, count in embedded.items():
        if count == 0:
            report.warn(root / "contracts", f"contract {name!r} is not embedded by any package")


def tracked_files(root: Path) -> list[Path] | None:
    """Return git-tracked and staged paths, or None when git is unavailable."""
    import subprocess

    try:
        completed = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=root, capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return [root / entry for entry in completed.stdout.decode("utf-8", errors="replace").split("\0") if entry]


def check_forbidden(root: Path, report: Report) -> None:
    """Reject generated or secret files that would be committed.

    Uses git's view (tracked plus untracked-but-not-ignored) when available so local
    caches that .gitignore already excludes do not fail the run; falls back to a
    filesystem scan outside a repository.
    """
    tracked = tracked_files(root)
    if tracked is None:
        tracked = [path for path in root.rglob("*") if ".git" not in path.parts]
    flagged: set[Path] = set()
    for path in tracked:
        for parent in [path, *path.parents]:
            if parent == root:
                break
            if parent.name in FORBIDDEN_DIRS and parent not in flagged:
                flagged.add(parent)
                report.error(parent, "generated directory must not be committed")
        if path.name in FORBIDDEN_FILES:
            report.error(path, "environment files must not be committed")


def validate(root: Path, *, overlap_threshold: float = 0.35, strict_overlap: bool = False) -> Report:
    report = Report()
    plugins_root = root / "plugins"
    plugin_dirs = sorted(p for p in plugins_root.iterdir() if p.is_dir()) if plugins_root.is_dir() else []
    if not plugin_dirs:
        report.error(plugins_root, "no plugins found")
    seen_names: dict[str, Path] = {}
    for plugin_dir in plugin_dirs:
        skills = check_plugin(plugin_dir, report, seen_names)
        if len(skills) >= 6:
            for left, right, score in lint.overlap_pairs(skills, overlap_threshold):
                message = f"descriptions of {left} and {right} overlap (jaccard {score:.2f} >= {overlap_threshold})"
                (report.error if strict_overlap else report.warn)(plugin_dir, message)
    check_marketplaces(root, plugin_dirs, report)
    check_contract_blocks(root, canonical_blocks(root, report), report)
    check_forbidden(root, report)
    for path in list(lint.iter_markdown(root / "contracts")) + [root / "README.md"]:
        if path.is_file():
            lint.check_links(path, report)
    for plugin_dir in plugin_dirs:
        for path in lint.iter_markdown(plugin_dir):
            if "skills" not in path.relative_to(plugin_dir).parts:
                lint.check_links(path, report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--overlap-threshold", type=float, default=0.35)
    parser.add_argument("--strict-overlap", action="store_true", help="treat description overlap as an error")
    args = parser.parse_args(argv)
    report = validate(args.root.resolve(), overlap_threshold=args.overlap_threshold, strict_overlap=args.strict_overlap)
    for warning in report.warnings:
        print(f"warning: {warning}")
    for error in report.errors:
        print(f"error: {error}")
    print(f"{len(report.errors)} error(s), {len(report.warnings)} warning(s)")
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
