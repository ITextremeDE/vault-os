#!/usr/bin/env python3
"""Validate Vault-OS manifest structure, ownership, paths, and checksums."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any


SCHEMA_VERSION = 1
MANIFEST_KEYS = {"core", "modules", "instance", "runtime"}
TARGET_ROOTS = {"system", "vault"}
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")


@dataclass(frozen=True)
class Counts:
    core: int
    module_files: int
    instance: int
    runtime: int
    modules: int


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: manifest root must be an object")
    return value


def safe_relative_path(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label}: path must be a non-empty string")
    if "\\" in value:
        raise ValueError(f"{label}: path must use POSIX separators")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in value.split("/")):
        raise ValueError(f"{label}: path must be relative and cannot traverse parents")
    return value


def require(value: dict[str, Any], key: str, expected: object, label: str) -> None:
    if value.get(key) != expected:
        raise ValueError(f"{label}: {key} must be {expected!r}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_checksum(entry: dict[str, Any], root: Path, label: str) -> str:
    source = safe_relative_path(entry.get("source"), f"{label}.source")
    source_path = root / source
    if not source_path.is_file():
        raise ValueError(f"{label}: source does not exist: {source}")
    if source_path.is_symlink():
        raise ValueError(f"{label}: source cannot be a symbolic link: {source}")
    expected = entry.get("sha256")
    if not isinstance(expected, str) or len(expected) != 64:
        raise ValueError(f"{label}: sha256 must contain 64 hexadecimal characters")
    try:
        int(expected, 16)
    except ValueError as error:
        raise ValueError(f"{label}: sha256 is not hexadecimal") from error
    actual = sha256(source_path)
    if actual != expected:
        raise ValueError(f"{label}: checksum mismatch for {source}")
    return source


def validate_files(value: dict[str, Any], root: Path, owner: str) -> tuple[set[str], set[str]]:
    files = value.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError(f"{owner}: files must be a non-empty array")
    target_root = value.get("targetRoot")
    if target_root not in TARGET_ROOTS:
        raise ValueError(f"{owner}: targetRoot must be one of {sorted(TARGET_ROOTS)}")

    sources: set[str] = set()
    targets: set[str] = set()
    expected_mode = {"managed": "managed", "instance": "create-only"}[owner]
    for index, entry in enumerate(files):
        label = f"{owner}.files[{index}]"
        if not isinstance(entry, dict):
            raise ValueError(f"{label}: entry must be an object")
        if entry.get("installMode") != expected_mode:
            raise ValueError(f"{label}: installMode must be {expected_mode!r}")
        source = validate_checksum(entry, root, label)
        target = safe_relative_path(entry.get("target"), f"{label}.target")
        if source in sources:
            raise ValueError(f"{label}: duplicate source {source}")
        if target in targets:
            raise ValueError(f"{label}: duplicate target {target}")
        sources.add(source)
        targets.add(target)
    return sources, targets


def entry_origins(entry: dict[str, Any], label: str, required: bool) -> set[str]:
    value = entry.get("origins")
    if value is None and not required:
        return set()
    if not isinstance(value, list) or not value or any(
        not isinstance(item, str) or not item for item in value
    ):
        raise ValueError(f"{label}.origins: expected a non-empty string array")
    origins = {
        safe_relative_path(item, f"{label}.origins")
        for item in value
    }
    if len(origins) != len(value):
        raise ValueError(f"{label}.origins: duplicate origins")
    if any(not origin.startswith("99 System/") for origin in origins):
        raise ValueError(f"{label}.origins: every origin must be below 99 System")
    return origins


def source_tree_files(path: Path, root: Path) -> set[str]:
    return {
        candidate.relative_to(root).as_posix()
        for candidate in path.rglob("*")
        if candidate.is_file()
        and "__pycache__" not in candidate.parts
        and candidate.suffix.lower() not in {".pyc", ".pyo"}
    }


def load_matrix(root: Path) -> dict[str, dict[str, str]]:
    matrix_path = root / "analysis/mindos-portability-matrix.tsv"
    with matrix_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if not {"source_path", "decision", "target"}.issubset(reader.fieldnames or ()):
            raise ValueError("portability matrix has unexpected columns")
        rows = list(reader)
    return {row["source_path"]: row for row in rows}


def validate_core(
    value: dict[str, Any], root: Path, matrix: dict[str, dict[str, str]]
) -> tuple[int, set[str], set[str]]:
    label = "core"
    require(value, "schemaVersion", SCHEMA_VERSION, label)
    require(value, "id", "core", label)
    require(value, "kind", "core", label)
    require(value, "owner", "managed", label)
    require(value, "required", True, label)
    require(value, "targetRoot", "system", label)
    sources, targets = validate_files(value, root, "managed")
    if any(not source.startswith("src/core/") for source in sources):
        raise ValueError("core: every source must be below src/core")

    origins: set[str] = set()
    for index, entry in enumerate(value["files"]):
        origins.update(entry_origins(entry, f"core.files[{index}]", required=True))

    actual_sources = source_tree_files(root / "src/core", root)
    missing = sorted(actual_sources - sources)
    extra = sorted(sources - actual_sources)
    if missing:
        raise ValueError("core: unlisted core sources: " + ", ".join(missing))
    if extra:
        raise ValueError("core: listed sources outside core tree: " + ", ".join(extra))

    expected_origins = {
        path
        for path, row in matrix.items()
        if row["decision"] == "core"
        or (row["decision"] == "split" and "src/core" in row["target"])
    }
    missing_origins = sorted(expected_origins - origins)
    extra_origins = sorted(origins - expected_origins)
    if missing_origins:
        raise ValueError("core: missing classified origins: " + ", ".join(missing_origins))
    if extra_origins:
        raise ValueError("core: unclassified origins: " + ", ".join(extra_origins))
    return len(sources), origins, targets


def validate_module(
    value: dict[str, Any], root: Path, identifier: str
) -> tuple[int, set[str], set[str]]:
    label = f"module {identifier}"
    require(value, "schemaVersion", SCHEMA_VERSION, label)
    require(value, "id", identifier, label)
    require(value, "kind", "module", label)
    require(value, "owner", "managed", label)
    require(value, "required", False, label)
    require(value, "targetRoot", "system", label)
    sources, targets = validate_files(value, root, "managed")
    prefix = f"src/modules/{identifier}/"
    if any(not source.startswith(prefix) for source in sources):
        raise ValueError(f"{label}: every source must be below src/modules/{identifier}")
    actual_sources = source_tree_files(root / f"src/modules/{identifier}", root)
    missing = sorted(actual_sources - sources)
    extra = sorted(sources - actual_sources)
    if missing:
        raise ValueError(f"{label}: unlisted module sources: " + ", ".join(missing))
    if extra:
        raise ValueError(f"{label}: listed sources outside module tree: " + ", ".join(extra))
    origins: set[str] = set()
    for index, entry in enumerate(value["files"]):
        origins.update(entry_origins(entry, f"{label}.files[{index}]", required=True))
    return len(sources), origins, targets


def validate_modules(
    value: dict[str, Any], root: Path
) -> tuple[int, int, set[str], set[str]]:
    label = "modules"
    require(value, "schemaVersion", SCHEMA_VERSION, label)
    require(value, "id", "modules", label)
    require(value, "kind", "module-catalog", label)
    require(value, "owner", "managed", label)
    modules = value.get("modules")
    if not isinstance(modules, list):
        raise ValueError("modules: modules must be an array")

    ids: set[str] = set()
    manifests: set[str] = set()
    targets: set[str] = set()
    origins: set[str] = set()
    file_count = 0
    for index, entry in enumerate(modules):
        item_label = f"modules.modules[{index}]"
        if not isinstance(entry, dict):
            raise ValueError(f"{item_label}: entry must be an object")
        identifier = entry.get("id")
        if not isinstance(identifier, str) or not identifier:
            raise ValueError(f"{item_label}: id must be a non-empty string")
        manifest = safe_relative_path(entry.get("manifest"), f"{item_label}.manifest")
        if identifier in ids:
            raise ValueError(f"{item_label}: duplicate module id {identifier}")
        if manifest in manifests:
            raise ValueError(f"{item_label}: duplicate module manifest {manifest}")
        if not (root / manifest).is_file():
            raise ValueError(f"{item_label}: module manifest does not exist: {manifest}")
        if not isinstance(entry.get("default"), bool):
            raise ValueError(f"{item_label}: default must be boolean")
        module_files, module_origins, module_targets = validate_module(
            load_json(root / manifest), root, identifier
        )
        duplicate_targets = sorted(targets & module_targets)
        if duplicate_targets:
            raise ValueError(
                f"{item_label}: duplicate module targets: " + ", ".join(duplicate_targets)
            )
        targets.update(module_targets)
        origins.update(module_origins)
        file_count += module_files
        ids.add(identifier)
        manifests.add(manifest)
    return len(modules), file_count, origins, targets


def validate_instance(value: dict[str, Any], root: Path) -> tuple[int, set[str]]:
    label = "instance"
    require(value, "schemaVersion", SCHEMA_VERSION, label)
    require(value, "id", "instance", label)
    require(value, "kind", "instance", label)
    require(value, "owner", "instance", label)
    require(value, "targetRoot", "vault", label)
    sources, _ = validate_files(value, root, "instance")
    if any(not source.startswith("instance-template/") for source in sources):
        raise ValueError("instance: every seed must be below instance-template")
    actual_sources = source_tree_files(root / "instance-template", root)
    missing = sorted(actual_sources - sources)
    extra = sorted(sources - actual_sources)
    if missing:
        raise ValueError("instance: unlisted seed sources: " + ", ".join(missing))
    if extra:
        raise ValueError("instance: listed sources outside template tree: " + ", ".join(extra))
    origins: set[str] = set()
    for index, entry in enumerate(value["files"]):
        origins.update(entry_origins(entry, f"instance.files[{index}]", required=False))
    return len(sources), origins


def validate_runtime(value: dict[str, Any]) -> int:
    label = "runtime"
    require(value, "schemaVersion", SCHEMA_VERSION, label)
    require(value, "id", "runtime", label)
    require(value, "kind", "runtime", label)
    require(value, "owner", "runtime", label)
    require(value, "targetRoot", "vault", label)
    files = value.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("runtime: files must be a non-empty array")

    targets: set[str] = set()
    for index, entry in enumerate(files):
        item_label = f"runtime.files[{index}]"
        if not isinstance(entry, dict):
            raise ValueError(f"{item_label}: entry must be an object")
        if entry.get("installMode") != "generated":
            raise ValueError(f"{item_label}: installMode must be 'generated'")
        if "source" in entry or "sha256" in entry:
            raise ValueError(f"{item_label}: runtime artifacts cannot have release sources")
        if not isinstance(entry.get("generator"), str) or not entry["generator"]:
            raise ValueError(f"{item_label}: generator must be a non-empty string")
        target = safe_relative_path(entry.get("target"), f"{item_label}.target")
        if target in targets:
            raise ValueError(f"{item_label}: duplicate target {target}")
        targets.add(target)
    return len(files)


def validate_origin_coverage(
    matrix: dict[str, dict[str, str]],
    core_origins: set[str],
    module_origins: set[str],
    instance_origins: set[str],
) -> None:
    domains = {
        "core": ("src/core", core_origins),
        "modules": ("src/modules", module_origins),
        "instance": ("instance-template", instance_origins),
    }
    known = set(matrix)
    for name, (_, origins) in domains.items():
        unknown = sorted(origins - known)
        if unknown:
            raise ValueError(f"{name}: origins absent from portability matrix: " + ", ".join(unknown))

    direct_domains = {
        "core": "core",
        "module": "modules",
        "instance": "instance",
    }
    for path, row in matrix.items():
        decision = row["decision"]
        expected_domains: set[str] = set()
        if decision in direct_domains:
            expected_domains.add(direct_domains[decision])
        elif decision == "split":
            expected_domains = {
                name
                for name, (target_marker, _) in domains.items()
                if target_marker in row["target"]
            }
        elif decision != "runtime":
            raise ValueError(f"origin coverage: {path} has unknown decision {decision!r}")

        for name, (target_marker, origins) in domains.items():
            expected = name in expected_domains
            present = path in origins
            if expected and not present:
                raise ValueError(f"origin coverage: {path} is missing its {name} artifact")
            if present and not expected:
                raise ValueError(f"origin coverage: {path} has an unexpected {name} artifact")


def validate_repository(root: Path) -> Counts:
    entry_path = root / "manifests/repository.json"
    entry = load_json(entry_path)
    require(entry, "schemaVersion", SCHEMA_VERSION, "repository")
    require(entry, "product", "vault-os", "repository")
    version = entry.get("version")
    if not isinstance(version, str) or not VERSION_PATTERN.fullmatch(version):
        raise ValueError("repository: version must be a semantic version")
    references = entry.get("manifests")
    if not isinstance(references, dict) or set(references) != MANIFEST_KEYS:
        raise ValueError(
            "repository: manifests must contain exactly " + ", ".join(sorted(MANIFEST_KEYS))
        )

    loaded: dict[str, dict[str, Any]] = {}
    seen_paths: set[str] = set()
    for domain in sorted(MANIFEST_KEYS):
        path = safe_relative_path(references[domain], f"repository.manifests.{domain}")
        if path in seen_paths:
            raise ValueError(f"repository: duplicate manifest reference {path}")
        seen_paths.add(path)
        loaded[domain] = load_json(root / path)

    matrix = load_matrix(root)
    core_count, core_origins, core_targets = validate_core(
        loaded["core"], root, matrix
    )
    module_count, module_files, module_origins, module_targets = validate_modules(
        loaded["modules"], root
    )
    duplicate_managed_targets = sorted(core_targets & module_targets)
    if duplicate_managed_targets:
        raise ValueError(
            "managed targets collide between core and modules: "
            + ", ".join(duplicate_managed_targets)
        )
    instance_count, instance_origins = validate_instance(loaded["instance"], root)
    validate_origin_coverage(
        matrix, core_origins, module_origins, instance_origins
    )
    return Counts(
        core=core_count,
        module_files=module_files,
        instance=instance_count,
        runtime=validate_runtime(loaded["runtime"]),
        modules=module_count,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args()
    root = args.root.resolve()

    try:
        counts = validate_repository(root)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"manifest validation failed: {error}")
        return 1

    print(
        "Manifest validation passed: "
        f"{counts.core} core files, "
        f"{counts.module_files} files in {counts.modules} modules, "
        f"{counts.instance} instance seeds, "
        f"{counts.runtime} runtime artifact, "
        "all classified origins covered."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
