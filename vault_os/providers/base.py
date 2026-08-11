"""Provider adapter contract for Vault-OS agent integrations."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Iterable

from ..package import ConflictError, VaultOSError
from ..operations import secure_target


PROVIDER_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class SkillAdapter:
    """Metadata needed to expose one installed canonical skill."""

    name: str
    description: str
    canonical_target: str


@dataclass
class ProviderHealth:
    """Provider-specific diagnostic result."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    details: dict[str, object] = field(default_factory=dict)


def existing_bytes(vault: Path, target: str) -> bytes | None:
    """Read an optional provider artifact without following unsafe targets."""

    path = secure_target(vault, target)
    if not path.exists():
        return None
    if not path.is_file():
        raise ConflictError(f"agent adapter target is not a regular file: {target}")
    return path.read_bytes()


def skill_wrapper(skill: SkillAdapter) -> bytes:
    """Render the common thin wrapper used by provider discovery directories."""

    description = json.dumps(skill.description, ensure_ascii=False)
    text = f"""---
name: {skill.name}
description: {description}
---

# Vault-OS skill adapter

Read and follow `{skill.canonical_target}` completely before taking task actions.
Resolve every relative reference from the directory containing that canonical
`SKILL.md`. The canonical managed skill is authoritative; this provider adapter
only makes it discoverable.
"""
    return text.encode("utf-8")


class ProviderAdapter:
    """Extension point for one local AI client.

    Provider modules own discovery paths, client-specific instruction shims,
    optional MCP configuration, and their validation. The lifecycle orchestrator
    depends only on this contract.
    """

    provider_id = ""
    display_name = ""
    skill_root = ""
    qmd_ignore_patterns: tuple[str, ...] = ()

    def instruction_artifacts(self) -> dict[str, bytes]:
        return {}

    def generated_artifacts(
        self, skills: Iterable[SkillAdapter]
    ) -> dict[str, bytes]:
        result = dict(self.instruction_artifacts())
        for skill in skills:
            result[f"{self.skill_root}/{skill.name}/SKILL.md"] = skill_wrapper(skill)
        return result

    def qmd_configuration(
        self,
        vault: Path,
        command: str,
        previous_command: str | None,
    ) -> dict[str, bytes]:
        return {}

    def doctor(self, vault: Path, qmd_enabled: bool, command: str) -> ProviderHealth:
        return ProviderHealth()

    def skill_count(self, artifacts: Iterable[str]) -> int:
        prefix = f"{self.skill_root}/"
        return sum(target.startswith(prefix) for target in artifacts)


class ProviderRegistry:
    """Validated collection of provider adapters used by the common runtime."""

    def __init__(self, adapters: Iterable[ProviderAdapter]) -> None:
        registered: dict[str, ProviderAdapter] = {}
        for adapter in adapters:
            self._validate(adapter)
            if adapter.provider_id in registered:
                raise ValueError(f"duplicate provider adapter: {adapter.provider_id}")
            registered[adapter.provider_id] = adapter
        if not registered:
            raise ValueError("provider registry must not be empty")
        self._adapters = registered

    @staticmethod
    def _validate(adapter: ProviderAdapter) -> None:
        if not PROVIDER_ID.fullmatch(adapter.provider_id):
            raise ValueError(f"invalid provider adapter id: {adapter.provider_id!r}")
        if not adapter.display_name.strip():
            raise ValueError(f"provider adapter {adapter.provider_id} lacks a name")
        root = PurePosixPath(adapter.skill_root)
        if (
            not adapter.skill_root
            or root.is_absolute()
            or ".." in root.parts
            or root.parts[0] == ".obsidian"
        ):
            raise ValueError(
                f"provider adapter {adapter.provider_id} has unsafe skill root"
            )

    def ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._adapters))

    def require(self, provider_id: str) -> ProviderAdapter:
        try:
            return self._adapters[provider_id]
        except KeyError as error:
            raise VaultOSError(
                f"unsupported agent provider: {provider_id}"
            ) from error

    def select(self, value: str) -> tuple[ProviderAdapter, ...]:
        if value == "all":
            return tuple(self._adapters[item] for item in self.ids())
        return (self.require(value),)

    def resolve(self, provider_ids: Iterable[str]) -> tuple[ProviderAdapter, ...]:
        return tuple(self.require(item) for item in sorted(set(provider_ids)))
