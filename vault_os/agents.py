"""Provider adapters for AI-assisted Vault-OS installations."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import re
import shutil
from pathlib import Path
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
)
from .package import ConflictError, InstanceConfig, Package, VaultOSError, sha256_bytes
from .providers import PROVIDER_REGISTRY, ProviderRegistry, SkillAdapter
from .providers.base import existing_bytes


AGENT_STATE_TARGET = ".vault-os/integrations/agents.yaml"
AGENT_CONTEXT_TARGET = "Vault-OS/runtime/agent-context.yaml"
INSTANCE_CONFIG_TARGET = "Vault-OS/config.yaml"
AGENT_STATE_SCHEMA = 1
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _load_yaml(vault: Path, target: str, label: str) -> dict[str, Any]:
    content = read_bytes_secure(vault, target, label)
    try:
        value = yaml.safe_load(content.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as error:
        raise VaultOSError(f"{label} is invalid YAML: {error}") from error
    if not isinstance(value, dict):
        raise VaultOSError(f"{label} must be a YAML object")
    return value


def _load_agent_state(
    vault: Path, registry: ProviderRegistry = PROVIDER_REGISTRY
) -> dict[str, Any]:
    content = existing_bytes(vault, AGENT_STATE_TARGET)
    if content is None:
        return {
            "schema": AGENT_STATE_SCHEMA,
            "providers": [],
            "qmd": {"enabled": False, "command": "qmd"},
            "generatedArtifacts": {},
        }
    try:
        value = yaml.safe_load(content.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as error:
        raise VaultOSError(f"agent integration state is invalid YAML: {error}") from error
    if not isinstance(value, dict):
        raise VaultOSError("agent integration state must be a YAML object")
    if value.get("schema") != AGENT_STATE_SCHEMA:
        raise VaultOSError("agent integration state must use schema 1")
    providers = value.get("providers")
    if not isinstance(providers, list) or any(
        not isinstance(item, str) for item in providers
    ):
        raise VaultOSError("agent integration state contains invalid providers")
    if len(set(providers)) != len(providers):
        raise VaultOSError("agent integration state contains duplicate providers")
    for provider_id in providers:
        registry.require(provider_id)
    qmd = value.get("qmd")
    if not isinstance(qmd, dict):
        raise VaultOSError("agent integration state qmd must be an object")
    if not isinstance(qmd.get("enabled"), bool):
        raise VaultOSError("agent integration state qmd.enabled must be boolean")
    if not isinstance(qmd.get("command"), str) or not qmd["command"].strip():
        raise VaultOSError("agent integration state qmd.command must be non-empty")
    artifacts = value.get("generatedArtifacts")
    if not isinstance(artifacts, dict):
        raise VaultOSError("agent integration state generatedArtifacts must be an object")
    for target, checksum in artifacts.items():
        if not isinstance(target, str) or not isinstance(checksum, str):
            raise VaultOSError("agent integration state contains an invalid artifact entry")
        if not re.fullmatch(r"[0-9a-f]{64}", checksum):
            raise VaultOSError(
                f"agent integration state contains an invalid checksum for {target}"
            )
    return value


def _runtime_profile(vault: Path) -> dict[str, Any]:
    value = _load_yaml(
        vault,
        AGENT_CONTEXT_TARGET,
        "agent runtime profile",
    )
    if value.get("schema") != 1:
        raise VaultOSError("agent runtime profile must use schema 1")
    read_order = value.get("readOrder")
    if not isinstance(read_order, list) or any(
        not isinstance(item, str) or not item.strip() for item in read_order
    ):
        raise VaultOSError("agent runtime profile readOrder must be a string array")
    return value


def _parse_skill(content: bytes, target: str) -> tuple[str, str]:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise VaultOSError(f"installed skill is not UTF-8: {target}") from error
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise VaultOSError(f"installed skill lacks YAML frontmatter: {target}")
    header = text[4:].split("\n---\n", 1)[0]
    try:
        metadata = yaml.safe_load(header)
    except yaml.YAMLError as error:
        raise VaultOSError(f"installed skill has invalid frontmatter: {target}") from error
    if not isinstance(metadata, dict):
        raise VaultOSError(f"installed skill has invalid frontmatter: {target}")
    name = metadata.get("name")
    description = metadata.get("description")
    if not isinstance(name, str) or not SKILL_NAME.fullmatch(name):
        raise VaultOSError(f"installed skill has invalid name: {target}")
    if not isinstance(description, str) or not description.strip():
        raise VaultOSError(f"installed skill has invalid description: {target}")
    return name, description.strip()


def _installed_skills(
    package: Package, vault: Path, config: InstanceConfig
) -> list[SkillAdapter]:
    result: list[SkillAdapter] = []
    names: set[str] = set()
    for target, spec in sorted(package.managed_files(config).items()):
        if not spec.source.endswith("/SKILL.md"):
            continue
        content = read_bytes_secure(vault, target, "installed skill")
        name, description = _parse_skill(content, target)
        if name in names:
            raise VaultOSError(f"installed skills contain duplicate name {name}")
        names.add(name)
        result.append(SkillAdapter(name, description, target))
    return result


def _agent_instructions(config: InstanceConfig, runtime: dict[str, Any]) -> bytes:
    vault = config.data["vault"]
    system_root = config.system_root
    read_order = [
        f"{system_root}/06 Runtime/Agent Context.md",
        f"{system_root}/06 Runtime/Operating Rules.md",
        INSTANCE_CONFIG_TARGET,
        AGENT_CONTEXT_TARGET,
    ]
    for item in runtime["readOrder"]:
        if item not in read_order:
            read_order.append(item)
    lines = [
        f"# Agent instructions for {vault['name']}",
        "",
        "This Obsidian vault is operated by Vault-OS. These instructions apply to",
        "every agent working in the vault, independent of model or provider.",
        "",
        "## Authority and ownership",
        "",
        "- Follow the current user request and applicable higher-level host instructions first.",
        "- Treat Vault-OS managed files as release-owned; do not edit them directly.",
        "- Preserve instance-owned configuration and user content unless the user authorizes a change.",
        "- Never modify `.obsidian` as part of Vault-OS work.",
        "- Read before writing and make the smallest reversible change that achieves the request.",
        "",
        "## Startup context",
        "",
        "Read these files in order before making vault-wide or structural changes:",
        "",
    ]
    lines.extend(f"{index}. `{path}`" for index, path in enumerate(read_order, 1))
    lines.extend(
        [
            "",
            "Then read the relevant installed schema, register, workflow, template, or skill",
            "for the concrete task. Resolve paths and enabled modules from",
            f"`{INSTANCE_CONFIG_TARGET}`; do not hard-code the example vault name or folder names.",
            "",
            "## Content work",
            "",
            "- Prefer updating the natural existing note over creating a parallel note.",
            "- Use only metadata values declared by installed schemas and instance registers.",
            "- Keep stable, unambiguous internal links and preserve existing user wording.",
            "- Use the configured capture path when classification is not yet reliable.",
            f"- Default to `{vault['language']}` for vault content unless the user requests another language.",
            "",
            "## Search and evidence",
            "",
        ]
    )
    lines.extend(
        [
            "- Use available local search tools, including QMD when configured on this device.",
            "- Treat search hits as candidates and read the original Markdown file before",
            "  using it as evidence or changing it.",
        ]
    )
    lines.extend(
        [
            "",
            "## Completion",
            "",
            "Validate changed files and report what was changed, what was verified, and what",
            "remains unverified. Do not commit, push, publish, delete, or perform external writes",
            "unless the user authorized that action.",
            "",
        ]
    )
    return "\n".join(lines).encode("utf-8")


def _qmd_index(
    config: InstanceConfig,
    vault: Path,
    registry: ProviderRegistry,
) -> bytes:
    ignored = [
        pattern
        for adapter in registry.resolve(registry.ids())
        for pattern in adapter.qmd_ignore_patterns
    ]
    ignored.extend((".qmd/**", ".vault-os/**"))
    value = {
        "global_context": (
            f"Local knowledge and operating context for the {config.data['vault']['name']} "
            "Obsidian vault. Search results are candidates; retrieve the original note."
        ),
        "collections": {
            "vault": {
                "path": str(vault),
                "pattern": "**/*.md",
                "ignore": list(dict.fromkeys(ignored)),
                "includeByDefault": True,
                "context": {"/": f"Obsidian vault {config.data['vault']['name']}"},
            }
        },
    }
    return yaml.safe_dump(value, allow_unicode=True, sort_keys=False).encode("utf-8")


def _qmd_gitignore() -> bytes:
    return b"""# QMD project-local runtime data
*
!.gitignore
"""


def initialize_agents(
    package: Package,
    vault: Path,
    provider: str,
    enable_qmd: bool,
    qmd_command: str,
    registry: ProviderRegistry = PROVIDER_REGISTRY,
) -> dict[str, Any]:
    """Create or safely refresh provider adapters for an installed vault."""

    with operation_lock(vault):
        config = load_installed_config(package, vault)
        lock = load_lock(package, vault)
        lifecycle = build_update_plan(package, vault, config, lock)
        if lifecycle.conflicts:
            raise ConflictError(
                "agent initialization requires a healthy installation:\n- "
                + "\n- ".join(lifecycle.conflicts)
            )
        if lifecycle.changes:
            raise VaultOSError("agent initialization requires the current package; run update")

        state = _load_agent_state(vault, registry)
        runtime = _runtime_profile(vault)
        requested = registry.select(provider)
        provider_ids = tuple(
            sorted(set(state["providers"]) | {adapter.provider_id for adapter in requested})
        )
        adapters = registry.resolve(provider_ids)
        qmd_enabled = bool(state["qmd"]["enabled"] or enable_qmd)
        command = qmd_command.strip() if enable_qmd else state["qmd"]["command"]
        if not command:
            raise VaultOSError("qmd command must not be empty")

        skills = _installed_skills(package, vault, config)
        desired: dict[str, bytes] = {
            "AGENTS.md": _agent_instructions(config, runtime),
        }
        for adapter in adapters:
            for target, content in adapter.generated_artifacts(skills).items():
                if target in desired and desired[target] != content:
                    raise VaultOSError(
                        f"provider adapters generate conflicting artifact: {target}"
                    )
                desired[target] = content
        if qmd_enabled:
            desired[".qmd/index.yml"] = _qmd_index(config, vault, registry)
            desired[".qmd/.gitignore"] = _qmd_gitignore()

        previous: dict[str, str] = state["generatedArtifacts"]
        changes: list[Change] = []
        conflicts: list[str] = []
        created = 0
        updated = 0
        removed = 0
        unchanged = 0
        for target, content in sorted(desired.items()):
            existing = existing_bytes(vault, target)
            if existing is None:
                changes.append(Change("write", target, content, "agent"))
                created += 1
                continue
            current_hash = sha256_bytes(existing)
            desired_hash = sha256_bytes(content)
            if current_hash == desired_hash:
                unchanged += 1
            elif previous.get(target) == current_hash:
                changes.append(Change("write", target, content, "agent"))
                updated += 1
            else:
                conflicts.append(f"agent adapter target was changed locally: {target}")

        for target, expected in sorted(previous.items()):
            if target in desired:
                continue
            existing = existing_bytes(vault, target)
            if existing is None:
                continue
            if sha256_bytes(existing) != expected:
                conflicts.append(f"obsolete agent adapter was changed locally: {target}")
            else:
                changes.append(Change("delete", target, None, "agent"))
                removed += 1

        shared_changes: list[Change] = []
        if qmd_enabled:
            previous_command = (
                state["qmd"]["command"] if state["qmd"]["enabled"] else None
            )
            qmd_targets: dict[str, tuple[str, bytes]] = {}
            for adapter in adapters:
                for target, content in adapter.qmd_configuration(
                    vault, command, previous_command
                ).items():
                    owner = qmd_targets.get(target)
                    if owner is not None and owner[1] != content:
                        raise VaultOSError(
                            "provider adapters generate conflicting QMD configuration: "
                            f"{owner[0]} and {adapter.provider_id} target {target}"
                        )
                    qmd_targets[target] = (adapter.provider_id, content)
            for target, (_, content) in sorted(qmd_targets.items()):
                existing = existing_bytes(vault, target)
                if existing != content:
                    shared_changes.append(Change("write", target, content, "agent"))
                    created += int(existing is None)
                    updated += int(existing is not None)
                else:
                    unchanged += 1
        if conflicts:
            raise ConflictError("agent initialization conflicts:\n- " + "\n- ".join(conflicts))

        generated = {target: sha256_bytes(content) for target, content in sorted(desired.items())}
        state["providers"] = list(provider_ids)
        state["qmd"] = {"enabled": qmd_enabled, "command": command}
        state["generatedArtifacts"] = generated
        state_content = yaml.safe_dump(
            state, allow_unicode=True, sort_keys=False
        ).encode("utf-8")
        current_state = existing_bytes(vault, AGENT_STATE_TARGET)
        if current_state != state_content:
            changes.extend(shared_changes)
            changes.append(Change("write", AGENT_STATE_TARGET, state_content, "agent"))
        else:
            changes.extend(shared_changes)
        apply_changes(vault, changes)

        warnings: list[str] = []
        executable = shutil.which(command)
        if qmd_enabled and executable is None:
            warnings.append(
                f"QMD command {command!r} is not available on PATH; install QMD before use"
            )
        return {
            "providers": list(provider_ids),
            "qmd": {
                "enabled": qmd_enabled,
                "command": command,
                "available": executable is not None,
            },
            "skills": len(skills),
            "counts": {
                "created": created,
                "updated": updated,
                "removed": removed,
                "unchanged": unchanged,
            },
            "artifacts": sorted(generated),
            "warnings": warnings,
        }


def doctor_agents(
    package: Package,
    vault: Path,
    registry: ProviderRegistry = PROVIDER_REGISTRY,
) -> dict[str, Any]:
    """Validate configured agent adapters without changing the vault."""

    errors: list[str] = []
    warnings: list[str] = []
    details: dict[str, Any] = {}
    try:
        state = _load_agent_state(vault, registry)
    except VaultOSError as error:
        return {"healthy": False, "errors": [str(error)], "warnings": [], "details": {}}

    provider_ids = state["providers"]
    details["providers"] = list(provider_ids)
    if not provider_ids:
        errors.append("no agent provider has been initialized")
    adapters = registry.resolve(provider_ids)
    artifacts: dict[str, str] = state["generatedArtifacts"]
    for target, expected in sorted(artifacts.items()):
        try:
            existing = existing_bytes(vault, target)
        except ConflictError as error:
            errors.append(str(error))
            continue
        if existing is None:
            errors.append(f"agent adapter artifact is missing: {target}")
        elif sha256_bytes(existing) != expected:
            errors.append(f"agent adapter artifact was changed locally: {target}")

    if "AGENTS.md" not in artifacts:
        errors.append("AGENTS.md is not registered as an agent adapter artifact")

    qmd = state["qmd"]
    details["qmd"] = {
        "enabled": qmd["enabled"],
        "command": qmd["command"],
        "available": shutil.which(qmd["command"]) is not None,
    }
    if qmd["enabled"]:
        if shutil.which(qmd["command"]) is None:
            errors.append(f"QMD command {qmd['command']!r} is not available on PATH")
        if ".qmd/index.yml" not in artifacts:
            errors.append("QMD project index is not registered")
    provider_details: dict[str, object] = {}
    for adapter in adapters:
        health = adapter.doctor(vault, qmd["enabled"], qmd["command"])
        errors.extend(f"{adapter.provider_id}: {error}" for error in health.errors)
        warnings.extend(f"{adapter.provider_id}: {warning}" for warning in health.warnings)
        if health.details:
            provider_details[adapter.provider_id] = health.details
    if provider_details:
        details["providerHealth"] = provider_details

    skill_counts = {
        adapter.provider_id: adapter.skill_count(artifacts)
        for adapter in adapters
    }
    details["skills"] = skill_counts
    return {
        "healthy": not errors,
        "errors": errors,
        "warnings": warnings,
        "details": details,
    }
