"""Install, update, diff, and diagnose Vault-OS installations."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import json
import os
import shutil
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterator

from .package import (
    ConflictError,
    FileSpec,
    InstanceConfig,
    Package,
    VaultOSError,
    safe_relative,
    sha256_bytes,
    sha256_file,
)


LOCK_SCHEMA_VERSION = 1
CONFIG_SOURCE = "instance-template/vault-os.yaml"
OPERATION_LOCK = ".vault-os/operation.lock"
TRANSACTION_ROOT = ".vault-os/.transactions"


@dataclass(frozen=True)
class Change:
    action: str
    target: str
    content: bytes | None
    category: str


@dataclass
class Plan:
    operation: str
    release_from: str | None
    release_to: str
    modules_from: tuple[str, ...]
    modules_to: tuple[str, ...]
    changes: list[Change]
    conflicts: list[str]
    unchanged: int = 0
    instance_preserved: int = 0

    def counts(self) -> dict[str, int]:
        result = {"add": 0, "update": 0, "remove": 0, "seed": 0, "lock": 0}
        for change in self.changes:
            result[change.category] = result.get(change.category, 0) + 1
        result["unchanged"] = self.unchanged
        result["instancePreserved"] = self.instance_preserved
        result["conflicts"] = len(self.conflicts)
        return result

    def as_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "release": {"from": self.release_from, "to": self.release_to},
            "modules": {"from": list(self.modules_from), "to": list(self.modules_to)},
            "counts": self.counts(),
            "changes": [
                {
                    "action": change.action,
                    "category": change.category,
                    "target": change.target,
                }
                for change in self.changes
                if change.category != "lock"
            ],
            "conflicts": list(self.conflicts),
        }


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def vault_root(path: Path, *, create: bool = False) -> Path:
    if create and not path.exists():
        path.mkdir(parents=True)
    if not path.is_dir() or path.is_symlink():
        raise VaultOSError(f"vault must be a real directory: {path}")
    resolved = path.resolve()
    if resolved == Path(resolved.anchor) or resolved == Path.home().resolve():
        raise VaultOSError(f"refusing broad vault target: {resolved}")
    return resolved


def secure_target(root: Path, relative: str) -> Path:
    root = root.resolve()
    relative = safe_relative(relative, "vault target", protect_obsidian=True)
    current = root
    parts = PurePosixPath(relative).parts
    for index, part in enumerate(parts):
        current = current / part
        if current.is_symlink():
            raise ConflictError(f"target uses a symbolic link: {relative}")
        if index < len(parts) - 1 and current.exists() and not current.is_dir():
            raise ConflictError(f"target parent is not a directory: {relative}")
    try:
        current.resolve(strict=False).relative_to(root)
    except ValueError as error:
        raise ConflictError(f"target escapes vault: {relative}") from error
    return current


def read_bytes_secure(root: Path, relative: str, label: str) -> bytes:
    path = secure_target(root, relative)
    if not path.is_file():
        raise VaultOSError(f"{label} is missing: {relative}")
    try:
        return path.read_bytes()
    except OSError as error:
        raise VaultOSError(f"cannot read {label} {relative}: {error}") from error


def source_bytes(package: Package, spec: FileSpec) -> bytes:
    path = spec.source_path(package.root)
    content = path.read_bytes()
    if sha256_bytes(content) != spec.sha256:
        raise VaultOSError(f"package checksum changed while reading {spec.source}")
    return content


def config_spec(package: Package) -> FileSpec:
    matches = [spec for spec in package.instance if spec.source == CONFIG_SOURCE]
    if len(matches) != 1:
        raise VaultOSError("instance manifest must contain exactly one configuration seed")
    return matches[0]


def prepare_install_config(
    package: Package,
    vault: Path,
    config_path: Path | None,
    name: str | None,
    system_root: str | None,
    modules: list[str] | None,
    all_modules: bool,
) -> InstanceConfig:
    if config_path is None:
        content = source_bytes(package, config_spec(package))
    else:
        try:
            content = config_path.read_bytes()
        except OSError as error:
            raise VaultOSError(f"cannot read configuration {config_path}: {error}") from error
    config = package.parse_config(content)
    data = config.data
    if name is not None:
        if not name.strip():
            raise VaultOSError("vault name must not be empty")
        data["vault"]["name"] = name.strip()
    elif config_path is None:
        data["vault"]["name"] = vault.name
    if system_root is not None:
        data["paths"]["system"] = system_root
    if all_modules:
        data["modules"] = list(package.module_order)
    elif modules is not None:
        data["modules"] = modules
    rendered = InstanceConfig(data, config.system_root, config.modules).to_yaml()
    return package.parse_config(rendered)


def config_target(package: Package) -> str:
    return package.resolve_target(
        config_spec(package),
        InstanceConfig(
            data={"vault": {}, "paths": {"system": "unused"}, "modules": []},
            system_root="unused",
            modules=(),
        ),
    )


def load_installed_config(package: Package, vault: Path) -> InstanceConfig:
    return package.parse_config(
        read_bytes_secure(vault, config_target(package), "configuration")
    )


def load_lock(package: Package, vault: Path) -> dict[str, Any]:
    content = read_bytes_secure(vault, package.runtime_target, "release lock")
    try:
        value = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise VaultOSError(f"release lock is invalid JSON: {error}") from error
    if not isinstance(value, dict):
        raise VaultOSError("release lock must be an object")
    if value.get("schemaVersion") != LOCK_SCHEMA_VERSION:
        raise VaultOSError("release lock has an unsupported schemaVersion")
    if value.get("product") != "vault-os":
        raise VaultOSError("release lock belongs to another product")
    for field in ("packageVersion", "packageFingerprint", "installedAt", "updatedAt", "systemRoot"):
        if not isinstance(value.get(field), str) or not value[field]:
            raise VaultOSError(f"release lock field {field} is invalid")
    if len(value["packageFingerprint"]) != 64:
        raise VaultOSError("release lock packageFingerprint is invalid")
    try:
        int(value["packageFingerprint"], 16)
    except ValueError as error:
        raise VaultOSError("release lock packageFingerprint is invalid") from error
    modules = value.get("modules")
    if not isinstance(modules, list) or any(not isinstance(item, str) for item in modules):
        raise VaultOSError("release lock modules must be a string array")
    if len(set(modules)) != len(modules):
        raise VaultOSError("release lock modules contain duplicates")
    managed = value.get("managedFiles")
    if not isinstance(managed, list):
        raise VaultOSError("release lock managedFiles must be an array")
    targets: set[str] = set()
    for index, item in enumerate(managed):
        if not isinstance(item, dict):
            raise VaultOSError(f"release lock managedFiles[{index}] is invalid")
        target = safe_relative(
            item.get("target"), f"release lock managedFiles[{index}].target", protect_obsidian=True
        )
        checksum = item.get("sha256")
        if not isinstance(checksum, str) or len(checksum) != 64:
            raise VaultOSError(f"release lock managedFiles[{index}].sha256 is invalid")
        try:
            int(checksum, 16)
        except ValueError as error:
            raise VaultOSError(
                f"release lock managedFiles[{index}].sha256 is invalid"
            ) from error
        if target in targets:
            raise VaultOSError(f"release lock contains duplicate target {target}")
        targets.add(target)
    return value


def lock_bytes(
    package: Package,
    config: InstanceConfig,
    managed: dict[str, FileSpec],
    installed_at: str | None = None,
) -> bytes:
    now = utc_now()
    value = {
        "schemaVersion": LOCK_SCHEMA_VERSION,
        "product": "vault-os",
        "packageVersion": package.version,
        "packageFingerprint": package.fingerprint,
        "installedAt": installed_at or now,
        "updatedAt": now,
        "systemRoot": config.system_root,
        "modules": list(config.modules),
        "managedFiles": [
            {
                "owner": spec.owner,
                "target": target,
                "sha256": spec.sha256,
            }
            for target, spec in sorted(managed.items())
        ],
    }
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _path_state(root: Path, target: str) -> tuple[Path, bool]:
    path = secure_target(root, target)
    if path.exists() and not path.is_file():
        raise ConflictError(f"target is not a regular file: {target}")
    return path, path.is_file()


def build_install_plan(package: Package, vault: Path, config: InstanceConfig) -> Plan:
    plan = Plan("install", None, package.version, (), config.modules, [], [])
    lock_path, lock_exists = _path_state(vault, package.runtime_target)
    if lock_exists:
        plan.conflicts.append(f"installation already has a release lock: {package.runtime_target}")

    managed = package.managed_files(config)
    for target, spec in sorted(managed.items()):
        _, exists = _path_state(vault, target)
        if exists:
            plan.conflicts.append(f"managed install target already exists: {target}")
        else:
            plan.changes.append(Change("write", target, source_bytes(package, spec), "add"))

    generated_config = config.to_yaml()
    for target, spec in sorted(package.instance_files(config).items()):
        _, exists = _path_state(vault, target)
        if target == config_target(package):
            if exists:
                plan.conflicts.append(f"configuration target already exists: {target}")
            else:
                plan.changes.append(Change("write", target, generated_config, "seed"))
        elif exists:
            plan.instance_preserved += 1
        else:
            plan.changes.append(Change("write", target, source_bytes(package, spec), "seed"))

    if not plan.conflicts:
        plan.changes.append(
            Change("write", package.runtime_target, lock_bytes(package, config, managed), "lock")
        )
    return plan


def _old_managed(lock: dict[str, Any]) -> dict[str, dict[str, str]]:
    return {item["target"]: item for item in lock["managedFiles"]}


def build_update_plan(
    package: Package, vault: Path, config: InstanceConfig, lock: dict[str, Any]
) -> Plan:
    old_modules = tuple(sorted(lock["modules"]))
    plan = Plan(
        "update",
        lock["packageVersion"],
        package.version,
        old_modules,
        config.modules,
        [],
        [],
    )
    old = _old_managed(lock)
    desired = package.managed_files(config)

    for target, entry in sorted(old.items()):
        try:
            path, exists = _path_state(vault, target)
        except ConflictError as error:
            plan.conflicts.append(str(error))
            continue
        if not exists:
            plan.conflicts.append(f"managed file is missing: {target}")
        elif sha256_file(path) != entry["sha256"]:
            plan.conflicts.append(f"managed file was changed locally: {target}")

    for target, spec in sorted(desired.items()):
        if target in old:
            if old[target]["sha256"] == spec.sha256:
                plan.unchanged += 1
            else:
                plan.changes.append(Change("write", target, source_bytes(package, spec), "update"))
            continue
        try:
            _, exists = _path_state(vault, target)
        except ConflictError as error:
            plan.conflicts.append(str(error))
            continue
        if exists:
            plan.conflicts.append(f"new managed target already exists: {target}")
        else:
            plan.changes.append(Change("write", target, source_bytes(package, spec), "add"))

    for target in sorted(set(old) - set(desired)):
        plan.changes.append(Change("delete", target, None, "remove"))

    for target, spec in sorted(package.instance_files(config).items()):
        if target == config_target(package):
            continue
        try:
            _, exists = _path_state(vault, target)
        except ConflictError as error:
            plan.conflicts.append(str(error))
            continue
        if exists:
            plan.instance_preserved += 1
        else:
            plan.changes.append(Change("write", target, source_bytes(package, spec), "seed"))

    metadata_changed = any(
        (
            lock["packageVersion"] != package.version,
            lock["packageFingerprint"] != package.fingerprint,
            tuple(sorted(lock["modules"])) != config.modules,
            lock["systemRoot"] != config.system_root,
        )
    )
    material = any(change.category != "lock" for change in plan.changes)
    if not plan.conflicts and (material or metadata_changed):
        plan.changes.append(
            Change(
                "write",
                package.runtime_target,
                lock_bytes(package, config, desired, lock["installedAt"]),
                "lock",
            )
        )
    return plan


@contextmanager
def operation_lock(vault: Path) -> Iterator[None]:
    path = secure_target(vault, OPERATION_LOCK)
    parent_created = not path.parent.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as error:
        if parent_created:
            try:
                path.parent.rmdir()
            except OSError:
                pass
        raise ConflictError(
            f"another operation or a stale operation lock exists: {OPERATION_LOCK}"
        ) from error
    except OSError as error:
        if parent_created:
            try:
                path.parent.rmdir()
            except OSError:
                pass
        raise ConflictError(f"cannot create operation lock {OPERATION_LOCK}: {error}") from error
    try:
        try:
            os.write(descriptor, f"pid={os.getpid()}\n".encode("ascii"))
        finally:
            os.close(descriptor)
        yield
    finally:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        if parent_created:
            try:
                path.parent.rmdir()
            except OSError:
                pass


def apply_changes(vault: Path, changes: list[Change]) -> None:
    if not changes:
        return
    seen: set[str] = set()
    for change in changes:
        if change.target in seen:
            raise VaultOSError(f"transaction contains duplicate target {change.target}")
        seen.add(change.target)

    transaction_parent = secure_target(vault, TRANSACTION_ROOT)
    transaction_parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="txn-", dir=transaction_parent))
    new_dir = stage / "new"
    backup_dir = stage / "backup"
    new_dir.mkdir()
    backup_dir.mkdir()
    prepared: dict[str, Path] = {}
    for index, change in enumerate(changes):
        if change.action == "write":
            assert change.content is not None
            candidate = new_dir / str(index)
            candidate.write_bytes(change.content)
            prepared[change.target] = candidate

    applied: list[tuple[Change, Path | None]] = []
    try:
        for index, change in enumerate(changes):
            target = secure_target(vault, change.target)
            target.parent.mkdir(parents=True, exist_ok=True)
            backup: Path | None = None
            if target.exists():
                if not target.is_file():
                    raise ConflictError(f"target is not a regular file: {change.target}")
                backup = backup_dir / str(index)
                os.replace(target, backup)
            applied.append((change, backup))
            if change.action == "write":
                os.replace(prepared[change.target], target)
            elif change.action != "delete":
                raise VaultOSError(f"unknown transaction action {change.action}")
    except Exception:
        for change, backup in reversed(applied):
            target = secure_target(vault, change.target)
            if target.exists() and target.is_file():
                target.unlink()
            if backup is not None and backup.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                os.replace(backup, target)
        raise
    finally:
        shutil.rmtree(stage, ignore_errors=True)
        try:
            transaction_parent.rmdir()
        except OSError:
            pass


def execute_install(package: Package, vault: Path, config: InstanceConfig) -> Plan:
    with operation_lock(vault):
        plan = build_install_plan(package, vault, config)
        if plan.conflicts:
            raise ConflictError("install conflicts:\n- " + "\n- ".join(plan.conflicts))
        apply_changes(vault, plan.changes)
        return plan


def execute_update(package: Package, vault: Path) -> Plan:
    with operation_lock(vault):
        config = load_installed_config(package, vault)
        lock = load_lock(package, vault)
        plan = build_update_plan(package, vault, config, lock)
        if plan.conflicts:
            raise ConflictError("update conflicts:\n- " + "\n- ".join(plan.conflicts))
        apply_changes(vault, plan.changes)
        return plan


def diff_installation(package: Package, vault: Path) -> Plan:
    config = load_installed_config(package, vault)
    lock = load_lock(package, vault)
    return build_update_plan(package, vault, config, lock)


def doctor(package: Package, vault: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    details: dict[str, Any] = {"packageVersion": package.version}

    operation_path = secure_target(vault, OPERATION_LOCK)
    if operation_path.exists():
        errors.append(f"operation lock exists: {OPERATION_LOCK}")
    transaction_path = secure_target(vault, TRANSACTION_ROOT)
    if transaction_path.exists() and any(transaction_path.iterdir()):
        warnings.append(f"stale transaction data exists: {TRANSACTION_ROOT}")

    try:
        config = load_installed_config(package, vault)
        details["configuredModules"] = list(config.modules)
        details["systemRoot"] = config.system_root
    except VaultOSError as error:
        errors.append(str(error))
        return {"healthy": False, "errors": errors, "warnings": warnings, "details": details}

    try:
        lock = load_lock(package, vault)
        details["installedVersion"] = lock["packageVersion"]
    except VaultOSError as error:
        errors.append(str(error))
        return {"healthy": False, "errors": errors, "warnings": warnings, "details": details}

    plan = build_update_plan(package, vault, config, lock)
    errors.extend(plan.conflicts)
    counts = plan.counts()
    details["diff"] = counts
    if not plan.conflicts and any(counts[key] for key in ("add", "update", "remove", "seed")):
        warnings.append("installation differs from the current package; run update")
    elif (
        lock["packageVersion"] != package.version
        or lock["packageFingerprint"] != package.fingerprint
    ):
        warnings.append("release metadata differs; run update to refresh the lock")
    if tuple(sorted(lock["modules"])) != config.modules:
        warnings.append("configured module selection has not been applied")
    if lock["systemRoot"] != config.system_root:
        warnings.append("configured system root has not been applied")
    return {
        "healthy": not errors,
        "errors": errors,
        "warnings": warnings,
        "details": details,
    }
