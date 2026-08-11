#!/usr/bin/env python3
"""Reject source-vault and personal identifiers in distributable files."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


DISTRIBUTION_ROOTS = ("src", "instance-template")
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


def scan(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in distribution_files(root):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for rule, pattern in FORBIDDEN.items():
                if pattern.search(line):
                    findings.append(Finding(path.relative_to(root), number, rule))
    return findings


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

    print(f"Portability check passed for {len(distribution_files(root))} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
