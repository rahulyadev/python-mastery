#!/usr/bin/env python3
"""Validate the Python Mastery repository using only the Python standard library."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import zipfile
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Iterable
from urllib.parse import unquote

UNIT_ID_RE = re.compile(r"PY-[A-Z]{3}-\d{3}")
PROJECT_ID_RE = re.compile(r"PY-PRJ-\d{3}")
EXPECTED_PROJECT_IDS = [f"PY-PRJ-{number:03d}" for number in range(10, 70, 10)]
EXPECTED_PATHS = [
    ("complete-python-mastery", "Complete Python mastery"),
    ("absolute-beginner", "Absolute beginner to confident Python programmer"),
    ("python-interview-preparation", "Senior Python interview preparation"),
    ("backend-python-engineer", "Backend Python engineer"),
    ("standard-library-mastery", "Standard-library mastery"),
    ("async-concurrency-performance", "Async, concurrency, and performance"),
    ("cpython-deep-internals", "CPython and deep internals"),
]
REQUIRED_FILES = [
    ".gitignore",
    ".python-version",
    "AGENTS.md",
    "BUNDLE_MANIFEST.md",
    "CURRICULUM.md",
    "LEARNING_PATHS.md",
    "NOTEBOOKLM.md",
    "PROGRESS.md",
    "PROJECTS.md",
    "README.md",
    "START_HERE.md",
    "pyproject.toml",
    "uv.lock",
    "docs/COPYRIGHT_AND_LICENSE.md",
    "docs/NOTEBOOKLM.md",
    "docs/SOURCE_AND_VERSION_POLICY.md",
    "docs/WORKFLOW.md",
    "scripts/validate_repo.py",
    "templates/experiment.md",
    "templates/practice.md",
    "templates/project.md",
    "templates/review.md",
    "templates/unit.md",
]
FORBIDDEN_COMPONENTS = {
    ".venv",
    "venv",
    "env",
    "ENV",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".hypothesis",
    "secrets",
    "credentials",
    "transcripts",
    "chat-exports",
}
FORBIDDEN_ARCHIVE_PREFIXES = (".git/", "units/", "projects/")
FORBIDDEN_LICENSE_NAMES = {"LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"}
SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
ALLOWED_ANGLE_PLACEHOLDERS = {
    "<DOMAIN>",
    "<THREE-DIGIT-SEQUENCE>",
    "<TOPIC-ID>",
    "<PROJECT-ID>",
    "<question or concept>",
    "<topic or question>",
    "<domain-slug>",
    "<topic-slug>",
    "<project-slug>",
}


@dataclass
class Report:
    root: Path
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    statistics: dict[str, object] = field(default_factory=dict)
    checks: dict[str, str] = field(default_factory=dict)
    archive: dict[str, object] | None = None

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)

    def mark(self, name: str, passed: bool) -> None:
        self.checks[name] = "passed" if passed else "failed"

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "status": "passed" if not self.errors else "failed",
            "repository_root": str(self.root),
            "checks": self.checks,
            "statistics": self.statistics,
            "archive": self.archive,
            "errors": self.errors,
            "warnings": self.warnings,
        }


@dataclass(frozen=True)
class Unit:
    unit_id: str
    title: str
    outcome: str
    prerequisites: tuple[str, ...]
    anchor: str


@dataclass(frozen=True)
class Project:
    project_id: str
    title: str
    anchor: str


def read_text(path: Path, report: Report) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        report.error(f"Cannot read UTF-8 text file {path.relative_to(report.root)}: {exc}")
        return ""


def split_table_row(line: str) -> list[str]:
    text = line.strip()
    if not text.startswith("|"):
        return []
    text = text[1:]
    if text.endswith("|") and not text.endswith(r"\|"):
        text = text[:-1]

    cells: list[str] = []
    current: list[str] = []
    escaped = False
    code_delimiter = 0
    index = 0
    while index < len(text):
        char = text[index]
        if escaped:
            current.append(char)
            escaped = False
            index += 1
            continue
        if char == "\\":
            current.append(char)
            escaped = True
            index += 1
            continue
        if char == "`":
            run = 1
            while index + run < len(text) and text[index + run] == "`":
                run += 1
            current.extend("`" * run)
            if code_delimiter == 0:
                code_delimiter = run
            elif run == code_delimiter:
                code_delimiter = 0
            index += run
            continue
        if char == "|" and code_delimiter == 0:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        index += 1
    cells.append("".join(current).strip())
    return cells


def is_separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def lines_outside_fences(text: str, relative_path: str, report: Report) -> tuple[list[tuple[int, str]], int]:
    visible: list[tuple[int, str]] = []
    open_fence: tuple[str, int, int] | None = None
    blocks = 0
    for line_number, line in enumerate(text.splitlines(), 1):
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if match:
            marker = match.group(1)
            char = marker[0]
            length = len(marker)
            if open_fence is None:
                open_fence = (char, length, line_number)
                blocks += 1
            elif char == open_fence[0] and length >= open_fence[1]:
                open_fence = None
            continue
        if open_fence is None:
            visible.append((line_number, line))
    if open_fence is not None:
        report.error(
            f"Unclosed code fence in {relative_path}, opened at line {open_fence[2]}"
        )
    return visible, blocks


def github_slug(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[`*_~]", "", text).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")


def anchors_for_markdown(path: Path, report: Report) -> set[str]:
    text = read_text(path, report)
    anchors = set(re.findall(r'<a\s+id="([^"]+)"\s*></a>', text))
    visible, _ = lines_outside_fences(text, str(path.relative_to(report.root)), report)
    counts: defaultdict[str, int] = defaultdict(int)
    for _, line in visible:
        match = re.match(r"^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        base = github_slug(match.group(1))
        if not base:
            continue
        count = counts[base]
        anchor = base if count == 0 else f"{base}-{count}"
        counts[base] += 1
        anchors.add(anchor)
    return anchors


def markdown_links(text: str, relative_path: str, report: Report) -> list[tuple[int, str]]:
    visible, _ = lines_outside_fences(text, relative_path, report)
    links: list[tuple[int, str]] = []
    pattern = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
    for line_number, line in visible:
        for match in pattern.finditer(line):
            target = match.group(1).strip()
            if " " in target and not target.startswith("<"):
                target = target.split(" ", 1)[0]
            target = target.strip("<>")
            links.append((line_number, target))
    return links


def validate_required_files(report: Report) -> None:
    missing = [path for path in REQUIRED_FILES if not (report.root / path).is_file()]
    for path in missing:
        report.error(f"Required file is missing: {path}")
    report.statistics["required_files"] = len(REQUIRED_FILES)
    report.statistics["required_files_present"] = len(REQUIRED_FILES) - len(missing)
    report.mark("required_files", not missing)


def parse_curriculum(report: Report) -> tuple[list[Unit], dict[str, Unit]]:
    path = report.root / "CURRICULUM.md"
    text = read_text(path, report)
    units: list[Unit] = []
    row_pattern = re.compile(
        r'^<a id="(?P<anchor>py-[a-z]{3}-\d{3})"></a>`(?P<id>PY-[A-Z]{3}-\d{3})`\s+—\s+\*\*(?P<title>.+?)\*\*$'
    )
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.startswith('| <a id="py-'):
            continue
        cells = split_table_row(line)
        if len(cells) != 7:
            report.error(f"Curriculum row at line {line_number} does not have 7 columns")
            continue
        match = row_pattern.fullmatch(cells[0])
        if not match:
            report.error(f"Malformed curriculum ID/title cell at line {line_number}: {cells[0]}")
            continue
        unit_id = match.group("id")
        anchor = match.group("anchor")
        expected_anchor = unit_id.lower()
        if anchor != expected_anchor:
            report.error(f"Anchor {anchor} does not match {unit_id} at line {line_number}")
        prerequisites = tuple(UNIT_ID_RE.findall(cells[2]))
        units.append(Unit(unit_id, match.group("title"), cells[1], prerequisites, anchor))

    ids = [unit.unit_id for unit in units]
    duplicates = sorted({unit_id for unit_id in ids if ids.count(unit_id) > 1})
    if len(units) != 121:
        report.error(f"Expected 121 curriculum units, found {len(units)}")
    if duplicates:
        report.error(f"Duplicate curriculum unit IDs: {', '.join(duplicates)}")

    unit_map = {unit.unit_id: unit for unit in units}
    for unit in units:
        for prerequisite in unit.prerequisites:
            if prerequisite not in unit_map:
                report.error(f"{unit.unit_id} has unknown prerequisite {prerequisite}")

    state: dict[str, int] = {unit_id: 0 for unit_id in unit_map}
    stack: list[str] = []

    def visit(unit_id: str) -> None:
        state[unit_id] = 1
        stack.append(unit_id)
        for prerequisite in unit_map[unit_id].prerequisites:
            if prerequisite not in unit_map:
                continue
            if state[prerequisite] == 0:
                visit(prerequisite)
            elif state[prerequisite] == 1:
                cycle_start = stack.index(prerequisite)
                cycle = stack[cycle_start:] + [prerequisite]
                report.error(f"Curriculum prerequisite cycle: {' -> '.join(cycle)}")
        stack.pop()
        state[unit_id] = 2

    for unit_id in unit_map:
        if state[unit_id] == 0:
            visit(unit_id)

    report.statistics["curriculum_units"] = len(units)
    report.statistics["unique_curriculum_ids"] = len(set(ids))
    report.statistics["prerequisite_edges"] = sum(len(unit.prerequisites) for unit in units)
    report.mark(
        "curriculum",
        len(units) == 121
        and len(set(ids)) == 121
        and all(p in unit_map for unit in units for p in unit.prerequisites)
        and not any("prerequisite cycle" in error for error in report.errors),
    )
    return units, unit_map


def validate_progress(report: Report, units: list[Unit], unit_map: dict[str, Unit]) -> None:
    path = report.root / "PROGRESS.md"
    text = read_text(path, report)
    rows: list[tuple[str, str, str]] = []
    pattern = re.compile(
        r'^\| `(?P<id>PY-[A-Z]{3}-\d{3})` \| \[(?P<title>[^\]]+)\]\(CURRICULUM\.md#(?P<anchor>py-[a-z]{3}-\d{3})\) \|'
    )
    for line in text.splitlines():
        match = pattern.match(line)
        if match:
            rows.append((match.group("id"), match.group("title"), match.group("anchor")))
    row_ids = [row[0] for row in rows]
    if len(rows) != 121:
        report.error(f"Expected 121 curriculum progress rows, found {len(rows)}")
    if row_ids != [unit.unit_id for unit in units]:
        report.error("Curriculum progress rows do not match canonical curriculum order")
    for unit_id, title, anchor in rows:
        unit = unit_map.get(unit_id)
        if unit and (title != unit.title or anchor != unit.anchor):
            report.error(f"Progress row metadata mismatch for {unit_id}")
    report.statistics["progress_unit_rows"] = len(rows)
    report.mark("progress_units", len(rows) == 121 and row_ids == [u.unit_id for u in units])


def validate_learning_paths(report: Report, units: list[Unit], unit_map: dict[str, Unit]) -> None:
    path = report.root / "LEARNING_PATHS.md"
    text = read_text(path, report)
    section_pattern = re.compile(r'(?m)^<a id="([^"]+)"></a>\n## (.+)$')
    matches = list(section_pattern.finditer(text))
    actual = [(match.group(1), match.group(2)) for match in matches]
    if actual != EXPECTED_PATHS:
        report.error(f"Learning-path anchors or titles differ from the seven expected paths: {actual}")

    selector_end = matches[0].start() if matches else len(text)
    selector = text[:selector_end]
    for anchor, title in EXPECTED_PATHS:
        if f"[{title}](#{anchor})" not in selector:
            report.error(f"Learning-path selector is missing {title} -> #{anchor}")

    total_topic_links = 0
    total_project_callouts = 0
    for index, match in enumerate(matches):
        section_end = matches[index + 1].start() if index + 1 < len(matches) else text.find("\n## Find a unit", match.end())
        if section_end < 0:
            section_end = len(text)
        section = text[match.end():section_end]
        entries: list[tuple[int, str, str, str]] = []
        entry_pattern = re.compile(
            r'(?m)^(\d+)\. \[(PY-[A-Z]{3}-\d{3}) — (.+?)\]\(CURRICULUM\.md#(py-[a-z]{3}-\d{3})\)$'
        )
        for item in entry_pattern.finditer(section):
            entries.append((int(item.group(1)), item.group(2), item.group(3), item.group(4)))
        numbers = [entry[0] for entry in entries]
        expected_numbers = list(range(1, len(entries) + 1))
        if numbers != expected_numbers:
            report.error(f"Learning path '{match.group(2)}' has non-sequential numbering")
        ids = [entry[1] for entry in entries]
        duplicates = sorted({unit_id for unit_id in ids if ids.count(unit_id) > 1})
        if duplicates:
            report.error(f"Learning path '{match.group(2)}' repeats: {', '.join(duplicates)}")
        positions = {unit_id: position for position, unit_id in enumerate(ids)}
        omitted_edges = 0
        for _, unit_id, title, anchor in entries:
            unit = unit_map.get(unit_id)
            if unit is None:
                report.error(f"Learning path '{match.group(2)}' uses unknown unit {unit_id}")
                continue
            if title != unit.title or anchor != unit.anchor:
                report.error(f"Learning path metadata mismatch for {unit_id} in '{match.group(2)}'")
            for prerequisite in unit.prerequisites:
                if prerequisite in positions:
                    if positions[prerequisite] > positions[unit_id]:
                        report.error(
                            f"Learning path '{match.group(2)}' puts {unit_id} before included prerequisite {prerequisite}"
                        )
                else:
                    omitted_edges += 1
        if omitted_edges:
            required_phrases = (
                "**Omitted-prerequisite policy:**",
                "assumed prior knowledge",
                "prerequisite bridge",
            )
            if not all(phrase in section for phrase in required_phrases):
                report.error(
                    f"Learning path '{match.group(2)}' omits prerequisites without the required policy label"
                )
        if match.group(1) == "complete-python-mastery":
            if ids != [unit.unit_id for unit in units] and set(ids) != set(unit_map):
                report.error("Complete Python mastery path does not contain all 121 canonical units")
            if len(ids) != 121 or len(set(ids)) != 121:
                report.error("Complete Python mastery path must contain 121 unique units")
        project_callouts = set(PROJECT_ID_RE.findall(section))
        for project_id in project_callouts:
            if project_id not in EXPECTED_PROJECT_IDS:
                report.error(f"Unknown project callout {project_id} in '{match.group(2)}'")
        total_topic_links += len(entries)
        total_project_callouts += len(project_callouts)

    report.statistics["learning_paths"] = len(matches)
    report.statistics["learning_path_topic_links"] = total_topic_links
    report.statistics["learning_path_project_callouts"] = total_project_callouts
    report.mark(
        "learning_paths",
        actual == EXPECTED_PATHS
        and not any("Learning path" in error or "Complete Python mastery path" in error for error in report.errors),
    )


def parse_projects(report: Report) -> dict[str, Project]:
    text = read_text(report.root / "PROJECTS.md", report)
    details_pattern = re.compile(
        r'(?m)^<a id="(?P<anchor>py-prj-\d{3})"></a>\n## (?P<id>PY-PRJ-\d{3}) — (?P<title>.+)$'
    )
    projects: dict[str, Project] = {}
    for match in details_pattern.finditer(text):
        project = Project(match.group("id"), match.group("title"), match.group("anchor"))
        if project.project_id in projects:
            report.error(f"Duplicate detailed project ID {project.project_id}")
        projects[project.project_id] = project
        if project.anchor != project.project_id.lower():
            report.error(f"Project anchor {project.anchor} does not match {project.project_id}")

    overview_pattern = re.compile(
        r'(?m)^\| \[(PY-PRJ-\d{3})\]\(#(py-prj-\d{3})\) \| \[(.+?)\]\(#(py-prj-\d{3})\) \|'
    )
    overview = list(overview_pattern.finditer(text))
    overview_ids = [match.group(1) for match in overview]
    if overview_ids != EXPECTED_PROJECT_IDS:
        report.error(f"Project overview IDs are invalid or out of order: {overview_ids}")
    for match in overview:
        project_id, id_anchor, title, title_anchor = match.groups()
        project = projects.get(project_id)
        if project is None:
            report.error(f"Project overview links to missing detail section {project_id}")
        elif id_anchor != project.anchor or title_anchor != project.anchor or title != project.title:
            report.error(f"Project overview metadata mismatch for {project_id}")

    if list(projects) != EXPECTED_PROJECT_IDS:
        report.error(f"Detailed project IDs are invalid or out of order: {list(projects)}")

    progress = read_text(report.root / "PROGRESS.md", report)
    tracker_pattern = re.compile(
        r'(?m)^\| \[`(PY-PRJ-\d{3})`\]\(PROJECTS\.md#(py-prj-\d{3})\) \| \[([^\]]+)\]\(PROJECTS\.md#(py-prj-\d{3})\) \| (Planned|Active|Complete) \| `project/(PY-PRJ-\d{3})` \|'
    )
    tracker = list(tracker_pattern.finditer(progress))
    tracker_ids = [match.group(1) for match in tracker]
    if tracker_ids != EXPECTED_PROJECT_IDS:
        report.error(f"Project tracker IDs are invalid or out of order: {tracker_ids}")
    for match in tracker:
        project_id, id_anchor, title, title_anchor, _state, branch_id = match.groups()
        project = projects.get(project_id)
        if project is None:
            continue
        if (
            id_anchor != project.anchor
            or title_anchor != project.anchor
            or title != project.title
            or branch_id != project_id
        ):
            report.error(f"Project tracker metadata mismatch for {project_id}")

    unit_text = read_text(report.root / "CURRICULUM.md", report)
    for project_id in EXPECTED_PROJECT_IDS:
        if re.search(rf'`{re.escape(project_id)}`\s+—', unit_text):
            report.error(f"Project ID {project_id} was incorrectly added as a curriculum unit")

    report.statistics["projects"] = len(projects)
    report.statistics["project_tracker_rows"] = len(tracker)
    report.mark(
        "projects",
        list(projects) == EXPECTED_PROJECT_IDS
        and overview_ids == EXPECTED_PROJECT_IDS
        and tracker_ids == EXPECTED_PROJECT_IDS,
    )
    return projects


def validate_markdown(report: Report) -> None:
    markdown_files = sorted(
        path for path in report.root.rglob("*.md")
        if ".git" not in path.parts and not any(part in FORBIDDEN_COMPONENTS for part in path.parts)
    )
    table_count = 0
    fence_blocks = 0
    link_count = 0
    anchor_cache: dict[Path, set[str]] = {}

    for path in markdown_files:
        relative = str(path.relative_to(report.root))
        text = read_text(path, report)
        visible, blocks = lines_outside_fences(text, relative, report)
        fence_blocks += blocks
        visible_lines = [line for _, line in visible]
        visible_numbers = [number for number, _ in visible]

        index = 0
        while index + 1 < len(visible_lines):
            header_cells = split_table_row(visible_lines[index])
            separator_cells = split_table_row(visible_lines[index + 1])
            if header_cells and is_separator_row(separator_cells):
                table_count += 1
                expected_columns = len(header_cells)
                if len(separator_cells) != expected_columns:
                    report.error(
                        f"Table separator column mismatch in {relative} at line {visible_numbers[index + 1]}"
                    )
                row_index = index + 2
                while row_index < len(visible_lines) and visible_lines[row_index].strip().startswith("|"):
                    cells = split_table_row(visible_lines[row_index])
                    if len(cells) != expected_columns:
                        report.error(
                            f"Table row column mismatch in {relative} at line {visible_numbers[row_index]}: "
                            f"expected {expected_columns}, found {len(cells)}"
                        )
                    row_index += 1
                index = row_index
            else:
                index += 1

        if "templates" not in path.parts:
            if re.search(r"\{\{[A-Z0-9_]+\}\}", text):
                report.error(f"Unexpected template placeholder outside templates/: {relative}")
            for placeholder in re.findall(r"<[^>\n]{1,80}>", text):
                if placeholder.startswith("<a ") or placeholder.startswith("</"):
                    continue
                if placeholder not in ALLOWED_ANGLE_PLACEHOLDERS:
                    report.error(f"Unexpected angle placeholder {placeholder} in {relative}")

        links = markdown_links(text, relative, report)
        link_count += len(links)
        if "templates" in path.parts:
            continue
        for line_number, target in links:
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", target) or target.startswith("mailto:"):
                continue
            target = unquote(target)
            file_part, separator, anchor = target.partition("#")
            resolved = path if file_part == "" else (path.parent / file_part).resolve()
            try:
                resolved.relative_to(report.root.resolve())
            except ValueError:
                report.error(f"Internal link escapes repository in {relative}:{line_number}: {target}")
                continue
            if not resolved.exists():
                report.error(f"Broken internal link in {relative}:{line_number}: {target}")
                continue
            if separator and anchor and resolved.is_file() and resolved.suffix.lower() == ".md":
                if resolved not in anchor_cache:
                    anchor_cache[resolved] = anchors_for_markdown(resolved, report)
                if anchor not in anchor_cache[resolved]:
                    report.error(f"Missing anchor #{anchor} for link in {relative}:{line_number}: {target}")

    report.statistics["markdown_files"] = len(markdown_files)
    report.statistics["markdown_tables"] = table_count
    report.statistics["code_fence_blocks"] = fence_blocks
    report.statistics["markdown_links"] = link_count
    report.mark(
        "markdown",
        not any(
            phrase in error
            for error in report.errors
            for phrase in (
                "code fence",
                "Table ",
                "Broken internal link",
                "Missing anchor",
                "escapes repository",
                "placeholder",
            )
        ),
    )


def validate_template_links(report: Report) -> None:
    substitutions = {
        "{{TOPIC_ID}}": "PY-FND-010",
        "{{TOPIC_ANCHOR}}": "py-fnd-010",
        "{{PROJECT_ID}}": "PY-PRJ-010",
        "{{PROJECT_ANCHOR}}": "py-prj-010",
        "{{DOMAIN_SLUG}}": "foundations",
        "{{TOPIC_SLUG}}": "python-syntax-and-execution",
        "{{PROJECT_SLUG}}": "streaming-log-investigator-cli",
    }
    intended_locations = {
        "templates/unit.md": Path("units/foundations/PY-FND-010-python-syntax-and-execution/README.md"),
        "templates/practice.md": Path("units/foundations/PY-FND-010-python-syntax-and-execution/practice/README.md"),
        "templates/experiment.md": Path("units/foundations/PY-FND-010-python-syntax-and-execution/experiments/EXP-01-example/README.md"),
        "templates/review.md": Path("units/foundations/PY-FND-010-python-syntax-and-execution/REVIEW.md"),
        "templates/project.md": Path("projects/PY-PRJ-010-streaming-log-investigator-cli/README.md"),
    }
    virtual_files = set(intended_locations.values())
    virtual_files.update(
        {
            Path("units/foundations/PY-FND-010-python-syntax-and-execution/README.md"),
            Path("projects/PY-PRJ-010-streaming-log-investigator-cli/README.md"),
        }
    )
    anchor_cache: dict[Path, set[str]] = {}
    checked = 0
    for template_path, intended in intended_locations.items():
        text = read_text(report.root / template_path, report)
        for source, replacement in substitutions.items():
            text = text.replace(source, replacement)
        for line_number, target in markdown_links(text, template_path, report):
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", target):
                continue
            checked += 1
            file_part, separator, anchor = unquote(target).partition("#")
            resolved_relative = intended if file_part == "" else Path(os.path.normpath(str(intended.parent / file_part)))
            actual = report.root / resolved_relative
            if resolved_relative not in virtual_files and not actual.exists():
                report.error(
                    f"Template-relative link from {template_path}:{line_number} resolves to missing {resolved_relative}"
                )
                continue
            if separator and anchor and actual.exists() and actual.suffix == ".md":
                if actual not in anchor_cache:
                    anchor_cache[actual] = anchors_for_markdown(actual, report)
                if anchor not in anchor_cache[actual]:
                    report.error(
                        f"Template-relative link from {template_path}:{line_number} targets missing #{anchor}"
                    )
    report.statistics["template_relative_links"] = checked
    report.mark(
        "template_links",
        not any("Template-relative link" in error for error in report.errors),
    )


def validate_repository_paths(report: Report) -> None:
    scanned_files = 0
    violations = 0
    for path in report.root.rglob("*"):
        relative = path.relative_to(report.root)
        if relative.parts and relative.parts[0] == ".git":
            continue
        if path.is_file():
            scanned_files += 1
        parts = set(relative.parts)
        if parts & FORBIDDEN_COMPONENTS:
            report.error(f"Forbidden generated or privacy-sensitive path: {relative}")
            violations += 1
        if path.name in FORBIDDEN_LICENSE_NAMES:
            report.error(f"License file exists before an explicit license decision: {relative}")
            violations += 1
        if path.is_file() and (path.suffix.lower() in SENSITIVE_SUFFIXES or path.name == ".env"):
            report.error(f"Potential credential or secret file: {relative}")
            violations += 1
    report.statistics["repository_files_scanned"] = scanned_files
    report.statistics["forbidden_path_violations"] = violations
    report.mark("repository_hygiene", violations == 0)


def validate_short_ids(report: Report) -> None:
    domains = "FND|BLT|FIT|OBJ|ERR|MOD|TYP|LIB|IOP|TST|CON|MPR|SEC|CPY|INT"
    pattern = re.compile(rf"(?<!PY-)(?<![A-Z0-9-])(?:{domains})-\d{{3}}")
    matches: list[str] = []
    for path in report.root.rglob("*.md"):
        if "templates" in path.parts or ".git" in path.parts:
            continue
        text = read_text(path, report)
        for match in pattern.finditer(text):
            matches.append(f"{path.relative_to(report.root)}:{match.group(0)}")
    if matches:
        report.error(f"Shortened curriculum IDs found: {', '.join(matches[:10])}")
    report.statistics["shortened_unit_id_references"] = len(matches)
    report.mark("canonical_id_format", not matches)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_archive(report: Report, archive_path: Path) -> None:
    archive_errors_before = len(report.errors)
    archive_info: dict[str, object] = {
        "path": str(archive_path),
        "exists": archive_path.is_file(),
    }
    if not archive_path.is_file():
        report.error(f"Archive does not exist: {archive_path}")
        report.archive = archive_info
        report.mark("archive", False)
        return

    archive_info["sha256"] = sha256_file(archive_path)
    archive_info["size_bytes"] = archive_path.stat().st_size
    try:
        with zipfile.ZipFile(archive_path) as archive:
            names = [info.filename for info in archive.infolist() if not info.is_dir()]
            archive_info["entry_count"] = len(names)
            archive_info["corrupt_entry"] = archive.testzip()
            if len(names) != len(set(names)):
                report.error("Archive contains duplicate paths")
            if "README.md" not in names or "AGENTS.md" not in names:
                report.error("Archive has an unnecessary wrapper directory or lacks root bootstrap files")
            for required in REQUIRED_FILES:
                if required not in names:
                    report.error(f"Archive is missing required file: {required}")
            for info in archive.infolist():
                name = info.filename
                pure = PurePosixPath(name)
                if pure.is_absolute() or ".." in pure.parts:
                    report.error(f"Unsafe archive path: {name}")
                if name.startswith(FORBIDDEN_ARCHIVE_PREFIXES):
                    report.error(f"Forbidden archive path: {name}")
                if any(part in FORBIDDEN_COMPONENTS for part in pure.parts):
                    report.error(f"Forbidden generated or privacy-sensitive archive path: {name}")
                if pure.name in FORBIDDEN_LICENSE_NAMES:
                    report.error(f"Archive contains a license before explicit selection: {name}")
                if pure.suffix.lower() in SENSITIVE_SUFFIXES or pure.name == ".env":
                    report.error(f"Archive may contain credentials or secrets: {name}")
                mode = (info.external_attr >> 16) & 0o170000
                if mode == 0o120000:
                    report.error(f"Archive contains a symbolic link: {name}")
            if archive.testzip() is not None:
                report.error(f"Archive contains a corrupt entry: {archive.testzip()}")
    except (OSError, zipfile.BadZipFile) as exc:
        report.error(f"Cannot validate archive {archive_path}: {exc}")
    report.archive = archive_info
    report.mark("archive", len(report.errors) == archive_errors_before)


def build_report(root: Path, archive: Path | None = None) -> Report:
    report = Report(root=root.resolve())
    validate_required_files(report)
    units, unit_map = parse_curriculum(report)
    validate_progress(report, units, unit_map)
    validate_learning_paths(report, units, unit_map)
    parse_projects(report)
    validate_markdown(report)
    validate_template_links(report)
    validate_repository_paths(report)
    validate_short_ids(report)
    if archive is not None:
        validate_archive(report, archive.resolve())
    return report


def print_report(report: Report) -> None:
    status = "PASSED" if not report.errors else "FAILED"
    print(f"Python Mastery repository validation: {status}")
    print()
    for name, result in sorted(report.checks.items()):
        print(f"- {name}: {result}")
    print()
    for name, value in sorted(report.statistics.items()):
        print(f"- {name}: {value}")
    if report.archive:
        print()
        for name, value in sorted(report.archive.items()):
            print(f"- archive.{name}: {value}")
    if report.warnings:
        print("\nWarnings:")
        for warning in report.warnings:
            print(f"- {warning}")
    if report.errors:
        print("\nErrors:")
        for error in report.errors:
            print(f"- {error}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root; defaults to the parent of scripts/.",
    )
    parser.add_argument("--archive", type=Path, help="Optional ZIP archive to validate.")
    parser.add_argument("--json", type=Path, help="Write a machine-readable JSON report.")
    arguments = parser.parse_args()

    report = build_report(arguments.root, arguments.archive)
    print_report(report)
    if arguments.json:
        arguments.json.parent.mkdir(parents=True, exist_ok=True)
        arguments.json.write_text(
            json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return 0 if not report.errors else 1


if __name__ == "__main__":
    sys.exit(main())
