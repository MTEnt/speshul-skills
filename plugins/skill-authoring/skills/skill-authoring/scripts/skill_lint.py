#!/usr/bin/env python3
"""Lint one skill directory, or a directory of sibling skills, against the Agent Skills
specification and this repository's conventions.

Checks per skill: frontmatter parses; name matches the directory and the spec pattern;
description length; metadata.version present and semantic; no top-level version key;
SKILL.md under the size budget; every relative markdown link resolves; agents/openai.yaml
exists. With --siblings, also reports description pairs whose distinctive vocabulary
overlaps enough to confuse a router.

Usage:
    python skill_lint.py path/to/skill
    python skill_lint.py --siblings path/to/skills-dir [--overlap-threshold 0.35]

Standard library only. Exit 0 when there are no errors.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any, Iterable

NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
MAX_SKILL_LINES = 500
MAX_SKILL_BYTES = 16000
WARN_SKILL_BYTES = 10000
MAX_DESCRIPTION = 1024
MAX_NAME = 64
SKIP_DIRS = {"__pycache__", "node_modules", ".git", ".eval-output"}
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "do", "for", "from", "if", "in", "into", "is",
    "it", "its", "not", "of", "on", "or", "other", "that", "the", "this", "to", "use", "when",
    "with", "work", "marketing", "skill", "including", "such", "any", "one", "only", "also",
}


class Report:
    """Collected errors and warnings. A plain class so the module loads correctly
    through importlib without being registered in sys.modules."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, path: Path | str, message: str) -> None:
        self.errors.append(f"{path}: {message}")

    def warn(self, path: Path | str, message: str) -> None:
        self.warnings.append(f"{path}: {message}")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> tuple[dict[str, Any] | None, str]:
    """Parse the small YAML subset used by SKILL.md files.

    Supports `key: value`, `key: |` block scalars, and one level of nested mappings.
    Returns (mapping, error) where error is a message when parsing fails.
    """
    normalized = text.replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        return None, "must start with YAML frontmatter"
    end = normalized.find("\n---\n", 4)
    if end == -1:
        return None, "frontmatter is not closed"
    body = normalized[4:end].split("\n")
    result: dict[str, Any] = {}
    index = 0
    while index < len(body):
        line = body[index]
        if not line.strip():
            index += 1
            continue
        if line.startswith(" "):
            return None, f"unexpected indentation at frontmatter line {index + 1}"
        if ":" not in line:
            return None, f"cannot parse frontmatter line {index + 1}: {line!r}"
        key, _, raw = line.partition(":")
        key = key.strip()
        raw = raw.strip()
        if raw in {"|", ">", "|-", ">-"}:
            block: list[str] = []
            index += 1
            while index < len(body) and (body[index].startswith("  ") or not body[index].strip()):
                block.append(body[index].strip())
                index += 1
            result[key] = " ".join(part for part in block if part).strip()
            continue
        if raw == "":
            nested: dict[str, str] = {}
            index += 1
            while index < len(body) and body[index].startswith("  "):
                child = body[index].strip()
                child_key, _, child_value = child.partition(":")
                nested[child_key.strip()] = child_value.strip().strip('"').strip("'")
                index += 1
            result[key] = nested
            continue
        result[key] = raw.strip('"').strip("'")
        index += 1
    return result, ""


def iter_markdown(root: Path) -> Iterable[Path]:
    if not root.exists():
        return
    for path in sorted(root.rglob("*.md")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def check_links(path: Path, report: Report) -> None:
    for match in LINK_PATTERN.finditer(read_text(path)):
        target = match.group(1)
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        clean = target.split("#", 1)[0]
        if clean and not (path.parent / clean).resolve().exists():
            report.error(path, f"broken link: {target}")


def check_skill(skill_dir: Path, report: Report, seen_names: dict[str, Path] | None = None) -> dict[str, Any] | None:
    """Lint one skill directory; return its name, description, and version when parseable."""
    seen_names = seen_names if seen_names is not None else {}
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        report.error(skill_dir, "skill directory has no SKILL.md")
        return None
    text = read_text(skill_md)
    meta, error = parse_frontmatter(text)
    if meta is None:
        report.error(skill_md, error)
        return None
    name = str(meta.get("name", ""))
    description = str(meta.get("description", ""))
    if not name:
        report.error(skill_md, "frontmatter is missing name")
    elif not NAME_PATTERN.match(name) or len(name) > MAX_NAME:
        report.error(skill_md, f"invalid skill name {name!r}")
    elif name != skill_dir.name:
        report.error(skill_md, f"name {name!r} does not match directory {skill_dir.name!r}")
    if name in seen_names:
        report.error(skill_md, f"duplicate skill name {name!r}; also in {seen_names[name]}")
    else:
        seen_names[name] = skill_md
    if not description:
        report.error(skill_md, "frontmatter is missing description")
    elif len(description) > MAX_DESCRIPTION:
        report.error(skill_md, f"description is {len(description)} characters; limit is {MAX_DESCRIPTION}")
    metadata = meta.get("metadata")
    version = metadata.get("version") if isinstance(metadata, dict) else None
    if not version:
        report.error(skill_md, "frontmatter needs metadata.version")
    elif not SEMVER_PATTERN.match(str(version)):
        report.error(skill_md, f"metadata.version {version!r} is not semantic")
    if "version" in meta:
        report.error(skill_md, "top-level version is not part of the spec; use metadata.version")
    line_count = text.count("\n") + 1
    byte_count = len(text.encode("utf-8"))
    if line_count > MAX_SKILL_LINES:
        report.error(skill_md, f"{line_count} lines; keep SKILL.md under {MAX_SKILL_LINES}")
    if byte_count > MAX_SKILL_BYTES:
        report.error(skill_md, f"{byte_count} bytes; move detail into references/ (limit {MAX_SKILL_BYTES})")
    elif byte_count > WARN_SKILL_BYTES:
        report.warn(skill_md, f"{byte_count} bytes; consider moving detail into references/")
    if not (skill_dir / "agents" / "openai.yaml").is_file():
        report.error(skill_dir, "missing agents/openai.yaml for Codex metadata")
    for path in iter_markdown(skill_dir):
        check_links(path, report)
    return {"name": name, "description": description, "version": str(version or ""), "path": skill_md}


def tokens(description: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", description.lower())
    return {word for word in words if word not in STOPWORDS and len(word) > 2}


def overlap_pairs(skills: list[dict[str, Any]], threshold: float) -> list[tuple[str, str, float]]:
    """Return (left, right, jaccard) for description pairs at or above the threshold."""
    pairs: list[tuple[str, str, float]] = []
    for index, left in enumerate(skills):
        left_tokens = tokens(left["description"])
        for right in skills[index + 1:]:
            right_tokens = tokens(right["description"])
            if not left_tokens or not right_tokens:
                continue
            score = len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
            if score >= threshold:
                pairs.append((left["name"], right["name"], round(score, 2)))
    return sorted(pairs, key=lambda item: -item[2])


def lint_siblings(directory: Path, report: Report, threshold: float, strict: bool) -> list[dict[str, Any]]:
    seen: dict[str, Path] = {}
    skills = [info for child in sorted(p for p in directory.iterdir() if p.is_dir()) if (info := check_skill(child, report, seen))]
    for left, right, score in overlap_pairs(skills, threshold):
        message = f"descriptions of {left} and {right} overlap (jaccard {score:.2f} >= {threshold})"
        (report.error if strict else report.warn)(directory, message)
    return skills


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", type=Path)
    parser.add_argument("--siblings", action="store_true", help="treat PATH as a directory of skill directories")
    parser.add_argument("--overlap-threshold", type=float, default=0.35)
    parser.add_argument("--strict-overlap", action="store_true")
    args = parser.parse_args(argv)
    report = Report()
    if args.siblings:
        lint_siblings(args.path.resolve(), report, args.overlap_threshold, args.strict_overlap)
    else:
        check_skill(args.path.resolve(), report)
    for warning in report.warnings:
        print(f"warning: {warning}")
    for error in report.errors:
        print(f"error: {error}")
    print(f"{len(report.errors)} error(s), {len(report.warnings)} warning(s)")
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
