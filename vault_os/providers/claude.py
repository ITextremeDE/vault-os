"""Claude Code project adapter."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..package import ConflictError, VaultOSError
from .base import ProviderAdapter, ProviderHealth, existing_bytes


def _instructions() -> bytes:
    return b"""@AGENTS.md

# Claude Code adapter

Project skills are registered under `.claude/skills`. The imported `AGENTS.md`
is the provider-neutral canonical instruction source for this vault.
"""


def _qmd_definition(command: str) -> dict[str, Any]:
    return {
        "command": command,
        "args": ["mcp"],
        "env": {"QMD_CONFIG_DIR": "${CLAUDE_PROJECT_DIR:-.}/.qmd"},
    }


def _merge_qmd(
    existing: bytes | None, command: str, previous_command: str | None = None
) -> bytes:
    if existing is None:
        value: dict[str, Any] = {}
    else:
        try:
            value = json.loads(existing.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ConflictError(f"existing .mcp.json is invalid JSON: {error}") from error
        if not isinstance(value, dict):
            raise ConflictError("existing .mcp.json must contain an object")
    servers = value.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        raise ConflictError("existing .mcp.json mcpServers must be an object")
    desired = _qmd_definition(command)
    current = servers.get("qmd")
    if current is not None and current != desired:
        previous = (
            _qmd_definition(previous_command) if previous_command is not None else None
        )
        if current != previous:
            raise ConflictError("existing .mcp.json already defines a different qmd server")
    if current == desired and existing is not None:
        return existing
    servers["qmd"] = desired
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


class ClaudeProviderAdapter(ProviderAdapter):
    provider_id = "claude"
    display_name = "Claude Code"
    skill_root = ".claude/skills"
    qmd_ignore_patterns = (".claude/**",)

    def instruction_artifacts(self) -> dict[str, bytes]:
        return {"CLAUDE.md": _instructions()}

    def qmd_configuration(
        self,
        vault: Path,
        command: str,
        previous_command: str | None,
    ) -> dict[str, bytes]:
        target = ".mcp.json"
        return {target: _merge_qmd(existing_bytes(vault, target), command, previous_command)}

    def doctor(self, vault: Path, qmd_enabled: bool, command: str) -> ProviderHealth:
        health = ProviderHealth()
        try:
            instructions = existing_bytes(vault, "CLAUDE.md")
            if instructions is None:
                health.errors.append("Claude instructions are missing: CLAUDE.md")
            elif not instructions.startswith(b"@AGENTS.md\n"):
                health.errors.append("CLAUDE.md does not import AGENTS.md")
            if qmd_enabled:
                mcp = existing_bytes(vault, ".mcp.json")
                if mcp is None:
                    health.errors.append("Claude MCP config is missing: .mcp.json")
                else:
                    _merge_qmd(mcp, command, command)
        except VaultOSError as error:
            health.errors.append(str(error))
        return health
