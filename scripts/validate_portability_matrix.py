#!/usr/bin/env python3
"""Validate the structure and optional live coverage of a portability matrix."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import argparse
import csv
import subprocess
from collections import Counter
from pathlib import Path


EXPECTED_COLUMNS = ("source_path", "decision", "target", "action", "effort", "rationale")
DECISIONS = {"core", "module", "instance", "runtime", "split"}
ACTIONS = {"extract", "neutralize", "split", "seed", "retain", "exclude"}
EFFORTS = {"S", "M", "L"}
EXPECTED_ROWS = 119


def load_matrix(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != EXPECTED_COLUMNS:
            raise ValueError(f"Unexpected columns: {reader.fieldnames}")
        return list(reader)


def validate_rows(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    if len(rows) != EXPECTED_ROWS:
        errors.append(f"expected {EXPECTED_ROWS} rows, found {len(rows)}")

    paths = [row["source_path"] for row in rows]
    duplicates = sorted(path for path, count in Counter(paths).items() if count > 1)
    if duplicates:
        errors.append("duplicate source paths: " + ", ".join(duplicates))

    for number, row in enumerate(rows, 2):
        if not row["source_path"].startswith("99 System/"):
            errors.append(f"line {number}: source path is outside 99 System")
        if row["decision"] not in DECISIONS:
            errors.append(f"line {number}: invalid decision {row['decision']!r}")
        if row["action"] not in ACTIONS:
            errors.append(f"line {number}: invalid action {row['action']!r}")
        if row["effort"] not in EFFORTS:
            errors.append(f"line {number}: invalid effort {row['effort']!r}")
        if not row["target"] or not row["rationale"]:
            errors.append(f"line {number}: target and rationale are required")

        expected_action = {
            "instance": {"seed", "retain"},
            "runtime": {"exclude"},
            "split": {"split"},
        }.get(row["decision"])
        if expected_action and row["action"] not in expected_action:
            errors.append(
                f"line {number}: {row['decision']} decision cannot use {row['action']} action"
            )

    return errors


def tracked_system_files(source: Path) -> set[str]:
    output = subprocess.check_output(
        [
            "git",
            "-C",
            str(source),
            "-c",
            "core.quotepath=false",
            "ls-files",
            "99 System/**",
        ],
        text=True,
    )
    return set(output.splitlines())


def validate_source_coverage(rows: list[dict[str, str]], source: Path) -> list[str]:
    matrix_paths = {row["source_path"] for row in rows}
    source_paths = tracked_system_files(source)
    errors: list[str] = []
    missing = sorted(source_paths - matrix_paths)
    extra = sorted(matrix_paths - source_paths)
    if missing:
        errors.append("missing source paths: " + ", ".join(missing))
    if extra:
        errors.append("paths absent from source: " + ", ".join(extra))
    return errors


def main() -> int:
    repository = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--matrix",
        type=Path,
        default=repository / "analysis/mindos-portability-matrix.tsv",
    )
    parser.add_argument("--source", type=Path)
    args = parser.parse_args()

    try:
        rows = load_matrix(args.matrix)
        errors = validate_rows(rows)
        if args.source:
            errors.extend(validate_source_coverage(rows, args.source.resolve()))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"matrix validation failed: {error}")
        return 1

    if errors:
        for error in errors:
            print(f"matrix validation failed: {error}")
        return 1

    decisions = Counter(row["decision"] for row in rows)
    actions = Counter(row["action"] for row in rows)
    print(f"Portability matrix is valid for {len(rows)} source files.")
    print("Decisions: " + ", ".join(f"{key}={decisions[key]}" for key in sorted(decisions)))
    print("Actions: " + ", ".join(f"{key}={actions[key]}" for key in sorted(actions)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
