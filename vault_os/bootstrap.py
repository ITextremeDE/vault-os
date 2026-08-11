"""Create optional user-owned start files for a Vault-OS instance."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from .operations import (
    Change,
    apply_changes,
    build_update_plan,
    load_installed_config,
    load_lock,
    operation_lock,
    read_bytes_secure,
    secure_target,
    utc_now,
)
from .package import ConflictError, InstanceConfig, Package, VaultOSError


FIELD_PROFILE_TARGET = "Vault-OS/schema/fields.yaml"


@dataclass
class BootstrapPlan:
    """Create-only plan for user-owned start files."""

    changes: list[Change]
    preserved: list[str]
    skipped: list[str]
    conflicts: list[str]

    def as_dict(self) -> dict[str, Any]:
        created = sorted(change.target for change in self.changes)
        return {
            "operation": "bootstrap",
            "counts": {
                "created": len(created),
                "preserved": len(self.preserved),
                "skipped": len(self.skipped),
            },
            "created": created,
            "preserved": sorted(self.preserved),
            "skipped": list(self.skipped),
        }


def _string_list(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise VaultOSError(f"{label} must be a string array")
    return list(value)


def _string_map(value: object, label: str) -> dict[str, str]:
    if not isinstance(value, dict) or any(
        not isinstance(source, str)
        or not source
        or not isinstance(target, str)
        or not target
        for source, target in value.items()
    ):
        raise VaultOSError(f"{label} must map non-empty strings")
    return dict(value)


def _field_profile(vault: Path) -> dict[str, Any]:
    content = read_bytes_secure(vault, FIELD_PROFILE_TARGET, "bootstrap field profile")
    try:
        value = yaml.safe_load(content.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as error:
        raise VaultOSError(f"bootstrap field profile is invalid YAML: {error}") from error
    if not isinstance(value, dict) or value.get("schema") != 1:
        raise VaultOSError("bootstrap field profile must use schema 1")
    roles = value.get("fields")
    if not isinstance(roles, dict):
        raise VaultOSError("bootstrap field profile fields must be an object")
    normalized_roles: dict[str, str] = {}
    for role in ("kind", "type", "status", "area"):
        field = roles.get(role)
        if not isinstance(field, str) or not field:
            raise VaultOSError(f"bootstrap field profile lacks role {role}")
        normalized_roles[role] = field
    if len(set(normalized_roles.values())) != len(normalized_roles):
        raise VaultOSError("bootstrap field profile roles must use distinct fields")
    values = value.get("values", {})
    if not isinstance(values, dict):
        raise VaultOSError("bootstrap field profile values must be an object")
    normalized_values = {
        role: _string_map(values.get(role, {}), f"bootstrap values.{role}")
        for role in ("kind", "type", "status")
    }
    required = _string_list(value.get("required"), "bootstrap required fields")
    lists = _string_list(value.get("lists"), "bootstrap list fields")
    dates = _string_list(value.get("dates"), "bootstrap date fields")
    order = _string_list(value.get("order"), "bootstrap field order")
    if any(field in lists for field in normalized_roles.values()):
        raise VaultOSError("bootstrap semantic fields cannot also be list fields")
    return {
        "roles": normalized_roles,
        "values": normalized_values,
        "required": required,
        "lists": lists,
        "dates": dates,
        "order": order,
    }


def _stored_value(mapping: dict[str, str], canonical: str, label: str) -> str:
    matches = [stored for stored, target in mapping.items() if target == canonical]
    if len(matches) > 1:
        raise VaultOSError(f"bootstrap {label} mapping for {canonical!r} is ambiguous")
    return matches[0] if matches else canonical


def _frontmatter(profile: dict[str, Any], content_type: str) -> str:
    roles: dict[str, str] = profile["roles"]
    mappings: dict[str, dict[str, str]] = profile["values"]
    values: dict[str, object] = {
        roles["kind"]: _stored_value(mappings["kind"], "system", "kind"),
        roles["type"]: _stored_value(mappings["type"], content_type, "type"),
        roles["status"]: _stored_value(mappings["status"], "active", "status"),
        roles["area"]: None,
    }
    list_fields = set(profile["lists"])
    date_fields = set(profile["dates"])
    for field in profile["required"]:
        if field in values:
            continue
        if field in list_fields:
            values[field] = []
        elif field == "created":
            values[field] = utc_now()[:10]
        elif field in date_fields:
            values[field] = None
        else:
            values[field] = None
    ordered: dict[str, object] = {}
    for field in profile["order"]:
        if field in values:
            ordered[field] = values[field]
    for field, value in values.items():
        if field not in ordered:
            ordered[field] = value
    rendered = yaml.safe_dump(
        ordered,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    )
    return f"---\n{rendered}---\n\n"


def _without_markdown_suffix(target: str) -> str:
    return target[:-3] if target.casefold().endswith(".md") else target


def _link(target: str, label: str) -> str:
    return f"[[{_without_markdown_suffix(target)}|{label}]]"


def _title(filename: str) -> str:
    return PurePosixPath(filename).stem


def _render_files(config: InstanceConfig, profile: dict[str, Any]) -> tuple[dict[str, bytes], list[str]]:
    data = config.data
    vault_name = data["vault"]["name"]
    paths = data["paths"]
    bootstrap = data["bootstrap"]
    profile_target = bootstrap["profileFile"]
    readme_target = bootstrap["readmeFile"]
    dashboard_target = bootstrap["dashboardFile"]
    profile_title = _title(profile_target)
    dashboard_title = _title(dashboard_target)

    para_enabled = "para" in config.modules
    skipped: list[str] = []
    project_target: str | None = None
    area_target: str | None = None
    if para_enabled:
        for key in ("projects", "areas"):
            if not isinstance(paths.get(key), str):
                raise VaultOSError(f"bootstrap requires configuration.paths.{key}")
        project_target = f"{paths['projects']}/{bootstrap['overviewFile']}"
        area_target = f"{paths['areas']}/{bootstrap['overviewFile']}"
    else:
        skipped.extend(
            [
                "project overview requires the para module",
                "area overview requires the para module",
            ]
        )

    navigation = [
        f"- {_link(dashboard_target, dashboard_title)}",
        f"- {_link(profile_target, profile_title)}",
    ]
    if project_target is not None and area_target is not None:
        navigation.extend(
            [
                f"- {_link(project_target, PurePosixPath(paths['projects']).name)}",
                f"- {_link(area_target, PurePosixPath(paths['areas']).name)}",
            ]
        )

    files: dict[str, bytes] = {
        profile_target: (
            _frontmatter(profile, "operating-document")
            + f"# {profile_title}\n\n"
            + "This user-owned note is the stable personal context source for this vault.\n"
            + "Record only information that should guide future human and AI collaboration.\n\n"
            + "## About\n\nDescribe the person or team this vault supports.\n\n"
            + "## Priorities\n\nRecord durable priorities, not today's task list.\n\n"
            + "## Preferences\n\nRecord working, writing, and communication preferences.\n\n"
            + "## Boundaries\n\nRecord privacy, authority, and decision boundaries.\n"
        ).encode("utf-8"),
        readme_target: (
            _frontmatter(profile, "readme")
            + f"# {vault_name}\n\n"
            + "This is the user-owned entry point for this Vault-OS instance.\n\n"
            + "## Start\n\n"
            + "\n".join(navigation)
            + "\n\n## Structure\n\n"
            + f"- Managed operating layer: `{config.system_root}`\n"
            + "- Synchronized instance configuration: `Vault-OS`\n"
            + "- Device-local runtime state: `.vault-os` and provider-specific dot paths\n"
        ).encode("utf-8"),
        dashboard_target: (
            _frontmatter(profile, "dashboard")
            + f"# {dashboard_title}\n\n"
            + "## Navigation\n\n"
            + "\n".join(navigation[1:])
            + "\n\n## Focus\n\nRecord the few outcomes and responsibilities that currently matter.\n\n"
            + "## Open loops\n\nKeep this as a compact orientation view; canonical tasks stay in their owning notes or task system.\n\n"
            + "## Recent context\n\nLink the notes that should be read first when resuming work.\n"
        ).encode("utf-8"),
    }

    if project_target is not None and area_target is not None:
        files[project_target] = (
            _frontmatter(profile, "dashboard")
            + f"# {PurePosixPath(paths['projects']).name}\n\n"
            + f"Back to {_link(dashboard_target, dashboard_title)}.\n\n"
            + "## Active projects\n\nLink projects with a defined outcome and current next action.\n\n"
            + "## Waiting\n\nLink projects whose next progress depends on another person or event.\n\n"
            + "## Completed\n\nMove durable results into the appropriate area or resource before archiving.\n"
        ).encode("utf-8")
        files[area_target] = (
            _frontmatter(profile, "dashboard")
            + f"# {PurePosixPath(paths['areas']).name}\n\n"
            + f"Back to {_link(dashboard_target, dashboard_title)}.\n\n"
            + "## Areas\n\nLink enduring responsibilities that need regular attention.\n\n"
            + "## Review\n\nRecord which area needs clarification, maintenance, or a new project.\n"
        ).encode("utf-8")

    folded: dict[str, str] = {}
    for target in files:
        key = target.casefold()
        if key in folded:
            raise VaultOSError(
                f"bootstrap targets collide: {folded[key]} and {target}"
            )
        folded[key] = target
    return files, skipped


def build_bootstrap_plan(
    config: InstanceConfig, vault: Path, profile: dict[str, Any]
) -> BootstrapPlan:
    files, skipped = _render_files(config, profile)
    changes: list[Change] = []
    preserved: list[str] = []
    conflicts: list[str] = []
    for target, content in sorted(files.items()):
        try:
            path = secure_target(vault, target)
        except ConflictError as error:
            conflicts.append(str(error))
            continue
        if path.exists():
            if path.is_file():
                preserved.append(target)
            else:
                conflicts.append(f"bootstrap target is not a regular file: {target}")
        else:
            changes.append(Change("write", target, content, "bootstrap"))
    return BootstrapPlan(changes, preserved, skipped, conflicts)


def bootstrap_vault(package: Package, vault: Path) -> BootstrapPlan:
    """Create missing user-owned start files without adopting or overwriting them."""
    with operation_lock(vault):
        config = load_installed_config(package, vault)
        lock = load_lock(package, vault)
        lifecycle = build_update_plan(package, vault, config, lock)
        if lifecycle.conflicts:
            raise ConflictError(
                "bootstrap requires a healthy installation:\n- "
                + "\n- ".join(lifecycle.conflicts)
            )
        if lifecycle.changes:
            raise VaultOSError("bootstrap requires the current package; run update")
        profile = _field_profile(vault)
        plan = build_bootstrap_plan(config, vault, profile)
        if plan.conflicts:
            raise ConflictError(
                "bootstrap conflicts:\n- " + "\n- ".join(plan.conflicts)
            )
        apply_changes(vault, plan.changes)
        return plan
