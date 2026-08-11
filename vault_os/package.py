"""Load and validate a Vault-OS release package and instance configuration."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

import yaml


SCHEMA_VERSION = 1
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")
RUNTIME_LOCK_TARGET = ".vault-os/lock.json"
BOOTSTRAP_DEFAULTS = {
    "profileFile": "Profile.md",
    "readmeFile": "README.md",
    "dashboardFile": "Dashboard.md",
    "overviewFile": "README.md",
}


class VaultOSError(Exception):
    """Expected package, configuration, or installation error."""

    exit_code = 1


class ConflictError(VaultOSError):
    """A protected target would be overwritten or removed."""

    exit_code = 2


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_relative(value: object, label: str, *, protect_obsidian: bool = False) -> str:
    if not isinstance(value, str) or not value:
        raise VaultOSError(f"{label}: expected a non-empty relative path")
    if "\\" in value:
        raise VaultOSError(f"{label}: use POSIX path separators")
    path = PurePosixPath(value)
    parts = value.split("/")
    if path.is_absolute() or any(part in {"", ".", ".."} for part in parts):
        raise VaultOSError(f"{label}: path must be relative and cannot traverse parents")
    if protect_obsidian and path.parts[0].casefold() == ".obsidian":
        raise VaultOSError(f"{label}: .obsidian is outside Vault-OS ownership")
    return value


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise VaultOSError(f"{label}: cannot load {path}: {error}") from error
    if not isinstance(value, dict):
        raise VaultOSError(f"{label}: expected a JSON object")
    return value


@dataclass(frozen=True)
class FileSpec:
    source: str
    target: str
    sha256: str
    owner: str
    target_root: str
    install_mode: str

    def source_path(self, package_root: Path) -> Path:
        return package_root / self.source


@dataclass(frozen=True)
class InstanceConfig:
    data: dict[str, Any]
    system_root: str
    modules: tuple[str, ...]

    def to_yaml(self) -> bytes:
        rendered = yaml.safe_dump(
            self.data,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        )
        return rendered.encode("utf-8")


@dataclass(frozen=True)
class Package:
    root: Path
    version: str
    fingerprint: str
    repository: dict[str, Any]
    core: tuple[FileSpec, ...]
    modules: dict[str, tuple[FileSpec, ...]]
    module_order: tuple[str, ...]
    instance: tuple[FileSpec, ...]
    runtime_target: str

    @classmethod
    def load(cls, root: Path) -> "Package":
        root = root.resolve()
        repository = load_json(root / "manifests/repository.json", "repository")
        if repository.get("schemaVersion") != SCHEMA_VERSION:
            raise VaultOSError("repository: unsupported schemaVersion")
        if repository.get("product") != "vault-os":
            raise VaultOSError("repository: product must be 'vault-os'")
        version = repository.get("version")
        if not isinstance(version, str) or not VERSION_PATTERN.fullmatch(version):
            raise VaultOSError("repository: version must be a semantic version")

        references = repository.get("manifests")
        if not isinstance(references, dict) or set(references) != {
            "core",
            "modules",
            "instance",
            "runtime",
        }:
            raise VaultOSError("repository: incomplete manifest references")

        def referenced(name: str) -> dict[str, Any]:
            relative = safe_relative(references[name], f"repository.manifests.{name}")
            return load_json(root / relative, name)

        core_manifest = referenced("core")
        catalog = referenced("modules")
        instance_manifest = referenced("instance")
        runtime_manifest = referenced("runtime")

        core = cls._load_files(root, core_manifest, "core")
        instance = cls._load_files(root, instance_manifest, "instance")

        catalog_entries = catalog.get("modules")
        if not isinstance(catalog_entries, list):
            raise VaultOSError("modules: catalog must contain an array")
        modules: dict[str, tuple[FileSpec, ...]] = {}
        module_manifests: dict[str, dict[str, Any]] = {}
        module_order: list[str] = []
        for index, item in enumerate(catalog_entries):
            if not isinstance(item, dict):
                raise VaultOSError(f"modules[{index}]: expected an object")
            identifier = item.get("id")
            if not isinstance(identifier, str) or not identifier:
                raise VaultOSError(f"modules[{index}]: invalid id")
            if identifier in modules:
                raise VaultOSError(f"modules: duplicate module {identifier}")
            manifest_path = safe_relative(
                item.get("manifest"), f"modules[{index}].manifest"
            )
            manifest = load_json(root / manifest_path, f"module {identifier}")
            if manifest.get("id") != identifier:
                raise VaultOSError(f"module {identifier}: manifest id mismatch")
            modules[identifier] = cls._load_files(root, manifest, identifier)
            module_manifests[identifier] = manifest
            module_order.append(identifier)

        runtime_files = runtime_manifest.get("files")
        if (
            runtime_manifest.get("schemaVersion") != SCHEMA_VERSION
            or runtime_manifest.get("id") != "runtime"
            or runtime_manifest.get("kind") != "runtime"
            or runtime_manifest.get("owner") != "runtime"
            or runtime_manifest.get("targetRoot") != "vault"
        ):
            raise VaultOSError("runtime: invalid manifest contract")
        if not isinstance(runtime_files, list) or len(runtime_files) != 1:
            raise VaultOSError("runtime: exactly one lock artifact is required")
        runtime_entry = runtime_files[0]
        if (
            not isinstance(runtime_entry, dict)
            or runtime_entry.get("installMode") != "generated"
            or not isinstance(runtime_entry.get("generator"), str)
            or not runtime_entry["generator"]
            or "source" in runtime_entry
            or "sha256" in runtime_entry
        ):
            raise VaultOSError("runtime: lock artifact must be generated")
        runtime_target = safe_relative(
            runtime_entry.get("target"), "runtime target", protect_obsidian=True
        )
        if runtime_target != RUNTIME_LOCK_TARGET:
            raise VaultOSError(
                f"runtime: lock artifact target must be {RUNTIME_LOCK_TARGET}"
            )

        fingerprint_data = {
            "repository": repository,
            "core": core_manifest,
            "catalog": catalog,
            "modules": module_manifests,
            "instance": instance_manifest,
            "runtime": runtime_manifest,
        }
        canonical = json.dumps(
            fingerprint_data,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        fingerprint = sha256_bytes(canonical)
        return cls(
            root=root,
            version=version,
            fingerprint=fingerprint,
            repository=repository,
            core=core,
            modules=modules,
            module_order=tuple(module_order),
            instance=instance,
            runtime_target=runtime_target,
        )

    @staticmethod
    def _load_files(
        root: Path, manifest: dict[str, Any], owner: str
    ) -> tuple[FileSpec, ...]:
        target_root = manifest.get("targetRoot")
        if target_root not in {"system", "vault"}:
            raise VaultOSError(f"{owner}: invalid targetRoot")
        entries = manifest.get("files")
        if not isinstance(entries, list) or not entries:
            raise VaultOSError(f"{owner}: files must be a non-empty array")
        result: list[FileSpec] = []
        targets: set[str] = set()
        for index, entry in enumerate(entries):
            label = f"{owner}.files[{index}]"
            if not isinstance(entry, dict):
                raise VaultOSError(f"{label}: expected an object")
            source = safe_relative(entry.get("source"), f"{label}.source")
            target = safe_relative(
                entry.get("target"), f"{label}.target", protect_obsidian=True
            )
            if owner == "instance" and PurePosixPath(target).parts[0].startswith("."):
                raise VaultOSError(
                    f"{label}: instance targets must be visible for synchronization"
                )
            if owner == "instance" and PurePosixPath(target).parts[0] != "Vault-OS":
                raise VaultOSError(
                    f"{label}: instance targets must use the Vault-OS/ root"
                )
            if target in targets:
                raise VaultOSError(f"{label}: duplicate target {target}")
            targets.add(target)
            checksum = entry.get("sha256")
            if not isinstance(checksum, str) or not re.fullmatch(r"[0-9a-f]{64}", checksum):
                raise VaultOSError(f"{label}: invalid sha256")
            source_path = root / source
            if not source_path.is_file() or source_path.is_symlink():
                raise VaultOSError(f"{label}: invalid source {source}")
            if sha256_file(source_path) != checksum:
                raise VaultOSError(f"{label}: package checksum mismatch for {source}")
            install_mode = entry.get("installMode")
            if install_mode not in {"managed", "create-only"}:
                raise VaultOSError(f"{label}: invalid installMode")
            result.append(
                FileSpec(
                    source=source,
                    target=target,
                    sha256=checksum,
                    owner=owner,
                    target_root=target_root,
                    install_mode=install_mode,
                )
            )
        return tuple(result)

    def parse_config(self, content: bytes) -> InstanceConfig:
        try:
            value = yaml.safe_load(content.decode("utf-8"))
        except (UnicodeDecodeError, yaml.YAMLError) as error:
            raise VaultOSError(f"configuration: invalid YAML: {error}") from error
        if not isinstance(value, dict) or value.get("schema") != SCHEMA_VERSION:
            raise VaultOSError("configuration: schema must be 1")
        vault = value.get("vault")
        if not isinstance(vault, dict):
            raise VaultOSError("configuration: vault must be an object")
        for field in ("name", "language"):
            if not isinstance(vault.get(field), str) or not vault[field].strip():
                raise VaultOSError(f"configuration: vault.{field} must be non-empty")
        paths = value.get("paths")
        if not isinstance(paths, dict) or not paths:
            raise VaultOSError("configuration: paths must be an object")
        for key, path in paths.items():
            safe_relative(path, f"configuration.paths.{key}", protect_obsidian=True)
            if PurePosixPath(path).parts[0].casefold() == ".vault-os":
                raise VaultOSError(
                    f"configuration.paths.{key}: .vault-os is reserved for instance state"
                )
        system_root = paths.get("system")
        if not isinstance(system_root, str):
            raise VaultOSError("configuration: paths.system is required")
        bootstrap = value.get("bootstrap", {})
        if not isinstance(bootstrap, dict):
            raise VaultOSError("configuration: bootstrap must be an object")
        unknown_bootstrap = sorted(set(bootstrap) - set(BOOTSTRAP_DEFAULTS))
        if unknown_bootstrap:
            raise VaultOSError(
                "configuration: unknown bootstrap fields: "
                + ", ".join(unknown_bootstrap)
            )
        normalized_bootstrap: dict[str, str] = {}
        for field, default in BOOTSTRAP_DEFAULTS.items():
            filename = bootstrap.get(field, default)
            safe_relative(
                filename,
                f"configuration.bootstrap.{field}",
                protect_obsidian=True,
            )
            candidate = PurePosixPath(filename)
            if len(candidate.parts) != 1 or candidate.suffix.casefold() != ".md":
                raise VaultOSError(
                    f"configuration.bootstrap.{field} must be one Markdown filename"
                )
            if any(character in candidate.name for character in "[]#|"):
                raise VaultOSError(
                    f"configuration.bootstrap.{field} contains unsafe link syntax"
                )
            if candidate.name.casefold() in {"agents.md", "claude.md"}:
                raise VaultOSError(
                    f"configuration.bootstrap.{field} is reserved for agent integration"
                )
            normalized_bootstrap[field] = candidate.name
        root_files = (
            normalized_bootstrap["profileFile"],
            normalized_bootstrap["readmeFile"],
            normalized_bootstrap["dashboardFile"],
        )
        if len({item.casefold() for item in root_files}) != len(root_files):
            raise VaultOSError("configuration: bootstrap root filenames must be unique")
        value["bootstrap"] = normalized_bootstrap
        modules = value.get("modules")
        if not isinstance(modules, list) or any(not isinstance(item, str) for item in modules):
            raise VaultOSError("configuration: modules must be a string array")
        if len(set(modules)) != len(modules):
            raise VaultOSError("configuration: modules must not contain duplicates")
        unknown = sorted(set(modules) - set(self.modules))
        if unknown:
            raise VaultOSError("configuration: unknown modules: " + ", ".join(unknown))
        normalized = tuple(sorted(modules))
        value["modules"] = list(normalized)
        return InstanceConfig(value, system_root, normalized)

    def managed_files(self, config: InstanceConfig) -> dict[str, FileSpec]:
        files: dict[str, FileSpec] = {}
        for spec in self.core:
            files[self.resolve_target(spec, config)] = spec
        for identifier in config.modules:
            for spec in self.modules[identifier]:
                target = self.resolve_target(spec, config)
                if target in files:
                    raise VaultOSError(f"managed target collision: {target}")
                files[target] = spec
        return files

    def instance_files(self, config: InstanceConfig) -> dict[str, FileSpec]:
        files: dict[str, FileSpec] = {}
        for spec in self.instance:
            parts = PurePosixPath(spec.source).parts
            if len(parts) >= 4 and parts[:2] == ("instance-template", "modules"):
                if parts[2] not in config.modules:
                    continue
            target = self.resolve_target(spec, config)
            if target in files:
                raise VaultOSError(f"instance target collision: {target}")
            files[target] = spec
        return files

    @staticmethod
    def resolve_target(spec: FileSpec, config: InstanceConfig) -> str:
        target = spec.target
        if spec.target_root == "system":
            target = f"{config.system_root}/{target}"
        return safe_relative(target, "resolved target", protect_obsidian=True)
