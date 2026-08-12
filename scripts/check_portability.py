#!/usr/bin/env python3
"""Reject source-vault and personal identifiers in distributable files."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator


DISTRIBUTION_ROOTS = ("src", "instance-template", "vault_os", "bin")
MANIFEST_PATH_KEYS = {"manifest", "source", "target"}
TEXT_SUFFIXES = {".md", ".py", ".sh", ".json", ".yaml", ".yml", ".toml", ".txt"}
FORBIDDEN = {
    "source vault name": re.compile(r"\bMindOS\b", re.IGNORECASE),
    "personal name": re.compile(r"\bJ(?:ü|u\N{COMBINING DIAERESIS})rgen\s+Schadek\b", re.IGNORECASE),
    "private platform name": re.compile(r"\bJSNexus\b", re.IGNORECASE),
    "organization context": re.compile(r"\b(?:AVAL|ALLRENTA)\b", re.IGNORECASE),
    "personal macOS path": re.compile(r"/Users/jschadek(?:/|\b)"),
    "private server path": re.compile(r"/opt/git/jsnexus(?:/|\b)"),
}


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    rule: str


def distribution_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for relative_root in DISTRIBUTION_ROOTS:
        candidate = root / relative_root
        if not candidate.exists():
            continue
        files.extend(
            path
            for path in candidate.rglob("*")
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES
        )
    return sorted(files)


def manifest_files(root: Path) -> list[Path]:
    directory = root / "manifests"
    if not directory.exists():
        return []
    return sorted(path for path in directory.rglob("*.json") if path.is_file())


def manifest_path_values(
    value: Any, parent_key: str | None = None
) -> Iterator[tuple[str, str]]:
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "origins":
                continue
            if isinstance(item, str) and (
                key in MANIFEST_PATH_KEYS or parent_key == "manifests"
            ):
                yield key, item
            else:
                yield from manifest_path_values(item, key)
    elif isinstance(value, list):
        for item in value:
            yield from manifest_path_values(item, parent_key)


def json_field_line(path: Path, key: str, value: str) -> int:
    key_literal = json.dumps(key, ensure_ascii=False)
    value_literal = json.dumps(value, ensure_ascii=False)
    lines = path.read_text(encoding="utf-8").splitlines()
    for number, line in enumerate(lines, 1):
        if key_literal in line and value_literal in line:
            return number
    for number, line in enumerate(lines, 1):
        if value_literal in line:
            return number
    return 1


def manifest_findings(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in manifest_files(root):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        for key, manifest_value in manifest_path_values(value):
            for rule, pattern in FORBIDDEN.items():
                if pattern.search(manifest_value):
                    findings.append(
                        Finding(
                            path.relative_to(root),
                            json_field_line(path, key, manifest_value),
                            rule,
                        )
                    )
    return findings


def scan(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in distribution_files(root):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for rule, pattern in FORBIDDEN.items():
                if pattern.search(line):
                    findings.append(Finding(path.relative_to(root), number, rule))
    findings.extend(manifest_findings(root))
    return sorted(findings, key=lambda item: (item.path, item.line, item.rule))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    args = parser.parse_args()

    root = args.root.resolve()
    findings = scan(root)
    if findings:
        for finding in findings:
            print(f"{finding.path}:{finding.line}: {finding.rule}")
        return 1

    print(
        "Portability check passed for "
        f"{len(distribution_files(root))} distributable files and "
        f"{len(manifest_files(root))} manifests."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
