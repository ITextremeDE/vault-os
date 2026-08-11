"""Codex project adapter."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import json
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised on Python 3.10
    import tomli as tomllib

from ..package import ConflictError, VaultOSError
from .base import ProviderAdapter, ProviderHealth, existing_bytes


QMD_START = "# >>> Vault-OS QMD adapter >>>"
QMD_END = "# <<< Vault-OS QMD adapter <<<"


def _parse_toml(text: str) -> dict[str, object]:
    try:
        return tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise ConflictError("existing .codex/config.toml contains invalid TOML") from error


def _qmd_definition(command: str) -> dict[str, object]:
    return {
        "command": command,
        "args": ["mcp"],
        "cwd": "..",
        "required": False,
    }


def _qmd_block(command: str) -> str:
    encoded = json.dumps(command, ensure_ascii=False)
    return (
        f"{QMD_START}\n"
        "[mcp_servers.qmd]\n"
        f"command = {encoded}\n"
        'args = ["mcp"]\n'
        'cwd = ".."\n'
        "required = false\n"
        f"{QMD_END}\n"
    )


def _merge_qmd(
    existing: bytes | None, command: str, previous_command: str | None = None
) -> bytes:
    try:
        text = existing.decode("utf-8") if existing is not None else ""
    except UnicodeDecodeError as error:
        raise ConflictError("existing .codex/config.toml is not UTF-8") from error
    parsed = _parse_toml(text)
    start = text.find(QMD_START)
    end = text.find(QMD_END)
    block = _qmd_block(command)
    if (start == -1) != (end == -1):
        raise ConflictError("existing .codex/config.toml has an incomplete Vault-OS block")
    if start != -1:
        if end < start:
            raise ConflictError("existing .codex/config.toml has an invalid Vault-OS block")
        end += len(QMD_END)
        if end < len(text) and text[end] == "\n":
            end += 1
        current_block = text[start:end]
        previous_block = (
            _qmd_block(previous_command) if previous_command is not None else None
        )
        if current_block not in {block, previous_block}:
            raise ConflictError("Vault-OS QMD block in .codex/config.toml was changed locally")
        candidate = text[:start] + block + text[end:]
        _parse_toml(candidate)
        return candidate.encode("utf-8")
    servers = parsed.get("mcp_servers", {})
    if not isinstance(servers, dict):
        raise ConflictError("existing .codex/config.toml has invalid mcp_servers")
    if "qmd" in servers:
        if servers["qmd"] == _qmd_definition(command):
            return existing if existing is not None else b""
        raise ConflictError("existing .codex/config.toml already defines mcp_servers.qmd")
    prefix = text
    if prefix and not prefix.endswith("\n"):
        prefix += "\n"
    if prefix and not prefix.endswith("\n\n"):
        prefix += "\n"
    candidate = prefix + block
    _parse_toml(candidate)
    return candidate.encode("utf-8")


class CodexProviderAdapter(ProviderAdapter):
    provider_id = "codex"
    display_name = "Codex"
    skill_root = ".agents/skills"
    qmd_ignore_patterns = (".agents/**",)

    def qmd_configuration(
        self,
        vault: Path,
        command: str,
        previous_command: str | None,
    ) -> dict[str, bytes]:
        target = ".codex/config.toml"
        return {target: _merge_qmd(existing_bytes(vault, target), command, previous_command)}

    def doctor(self, vault: Path, qmd_enabled: bool, command: str) -> ProviderHealth:
        health = ProviderHealth()
        if not qmd_enabled:
            return health
        try:
            content = existing_bytes(vault, ".codex/config.toml")
            if content is None:
                health.errors.append("Codex config is missing: .codex/config.toml")
            elif _merge_qmd(content, command, command) != content:
                health.errors.append("Codex QMD MCP block differs from agent state")
        except VaultOSError as error:
            health.errors.append(str(error))
        return health
