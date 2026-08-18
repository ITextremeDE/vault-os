"""Render instance-aware managed artifacts from portable package sources."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

import yaml

from .package import InstanceConfig, VaultOSError


TOKEN_RE = re.compile(
    r"\{\{(fields|moduleFields|values|paths|expressions)\.([A-Za-z0-9_.-]+)\}\}"
)
FIELD_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class MaterializationProfile:
    fields: dict[str, str]
    area_format: str
    module_fields: dict[str, str]
    values: dict[str, dict[str, str]]
    preferred_values: dict[str, dict[str, str]]


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


def parse_materialization_profile(content: bytes) -> MaterializationProfile:
    try:
        value = yaml.safe_load(content.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as error:
        raise VaultOSError(f"materialization field profile is invalid YAML: {error}") from error
    if not isinstance(value, dict) or value.get("schema") != 1:
        raise VaultOSError("materialization field profile must use schema 1")

    fields = _string_map(value.get("fields"), "materialization fields")
    for role in ("kind", "type", "status", "area"):
        if role not in fields:
            raise VaultOSError(f"materialization field profile lacks role {role}")
    formats = value.get("formats", {})
    if not isinstance(formats, dict):
        raise VaultOSError("materialization formats must be an object")
    area_format = formats.get("area", "text")
    if area_format not in {"text", "wiki-link"}:
        raise VaultOSError(
            "materialization formats.area must be 'text' or 'wiki-link'"
        )
    module_fields = _string_map(
        value.get("moduleFields", {}), "materialization moduleFields"
    )
    for label, mapping in (("fields", fields), ("moduleFields", module_fields)):
        invalid = sorted(name for name in mapping.values() if not FIELD_RE.fullmatch(name))
        if invalid:
            raise VaultOSError(
                f"materialization {label} contains invalid field name: {invalid[0]}"
            )

    raw_values = value.get("values", {})
    if not isinstance(raw_values, dict):
        raise VaultOSError("materialization values must be an object")
    values = {
        role: _string_map(raw_values.get(role, {}), f"materialization values.{role}")
        for role in ("kind", "type", "status")
    }
    raw_preferences = value.get("preferredValues", {})
    if not isinstance(raw_preferences, dict):
        raise VaultOSError("materialization preferredValues must be an object")
    preferred_values = {
        role: _string_map(
            raw_preferences.get(role, {}),
            f"materialization preferredValues.{role}",
        )
        for role in ("kind", "type", "status")
    }
    for role, preferences in preferred_values.items():
        for token, stored in preferences.items():
            canonical = token.rsplit(".", 1)[-1]
            if values[role].get(stored) != canonical:
                raise VaultOSError(
                    f"materialization preferredValues.{role}.{token} must name a stored value mapped to {canonical!r}"
                )
    return MaterializationProfile(
        fields, area_format, module_fields, values, preferred_values
    )


def _stored_value(profile: MaterializationProfile, role: str, token: str) -> str:
    mapping = profile.values.get(role)
    if mapping is None:
        raise VaultOSError(f"materialization has no value role {role}")
    canonical = token.rsplit(".", 1)[-1]
    preferred = profile.preferred_values[role].get(token)
    if preferred is not None:
        return preferred
    matches = [stored for stored, target in mapping.items() if target == canonical]
    if len(matches) > 1:
        raise VaultOSError(
            f"materialization values.{role} maps {canonical!r} ambiguously"
        )
    return matches[0] if matches else canonical


def _quoted_fragment(value: str) -> str:
    """Escape a value for a token embedded inside a double-quoted scalar."""
    return json.dumps(value, ensure_ascii=False)[1:-1]


def render_instance_source(
    content: bytes,
    config: InstanceConfig,
    profile_content: bytes,
    label: str,
) -> bytes:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise VaultOSError(f"materialized source is not UTF-8: {label}") from error
    profile = parse_materialization_profile(profile_content)

    def replacement(match: re.Match[str]) -> str:
        namespace, key = match.groups()
        if namespace == "fields":
            value = profile.fields.get(key)
            if value is None:
                raise VaultOSError(f"{label}: unknown materialization field {key}")
            return value
        if namespace == "moduleFields":
            return profile.module_fields.get(key, key)
        if namespace == "expressions":
            if key != "areaFolderName":
                raise VaultOSError(f"{label}: unknown materialization expression {key}")
            area = f"this.{profile.fields['area']}"
            if profile.area_format == "text":
                return area
            area_file = f"{area}.asFile()"
            basename = f"{area_file}.basename"
            folder = f"{area_file}.folder"
            return (
                f'if({basename}.startsWith(\\"_\\") || {basename} == \\"README\\", '
                f'{folder}.split(\\"/\\").reverse()[0], {basename})'
            )
        if namespace == "paths":
            value = config.data["paths"].get(key)
            if not isinstance(value, str):
                raise VaultOSError(f"{label}: unknown configured path {key}")
            return _quoted_fragment(value)

        role, separator, token = key.partition(".")
        if not separator or not token:
            raise VaultOSError(f"{label}: invalid materialization value token {key}")
        return _quoted_fragment(_stored_value(profile, role, token))

    rendered = TOKEN_RE.sub(replacement, text)
    unresolved = TOKEN_RE.search(rendered)
    if unresolved is not None:
        raise VaultOSError(f"{label}: unresolved materialization token {unresolved.group(0)}")
    return rendered.encode("utf-8")
