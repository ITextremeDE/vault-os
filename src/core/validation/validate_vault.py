#!/usr/bin/env python3
"""Validate a Vault-OS instance without modifying it."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import glob
import json
import re
import subprocess
import sys
import unicodedata
import urllib.parse
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml


WIKI_LINK_RE = re.compile(r"(!?)\[\[([^\]]+)\]\]")
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FIELD_TYPES = {"date", "register", "string", "wiki-link-list"}
SENSITIVE_QUERY_KEYS = {
    "access_token",
    "api_key",
    "apikey",
    "auth",
    "authorization",
    "client_secret",
    "credential",
    "credentials",
    "key",
    "password",
    "passwd",
    "secret",
    "sig",
    "signature",
    "token",
}


@dataclass(frozen=True)
class Finding:
    severity: str
    rule: str
    path: str
    line: int | None
    detail: str


@dataclass(frozen=True)
class FieldProfile:
    kind: str
    type: str
    status: str
    area: str
    kind_values: dict[str, str]
    type_values: dict[str, str]
    status_values: dict[str, str]
    required: tuple[str, ...]
    lists: tuple[str, ...]
    dates: tuple[str, ...]
    order: tuple[str, ...]
    external_id_suffixes: tuple[str, ...]
    external_url_suffix: str
    external_require_pair: bool
    external_allow_secrets: bool


@dataclass(frozen=True)
class SchemaModels:
    kinds: dict[str, dict[str, Any]]
    fields: dict[str, dict[str, Any]]


@dataclass(frozen=True)
class RegisterDefinition:
    values: frozenset[str]
    multiple: bool


def normalize(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def relative(path: Path, root: Path) -> str:
    return normalize(path.relative_to(root).as_posix())


def load_yaml(path: Path, label: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        problem = getattr(error, "problem", None) or "invalid YAML"
        raise ValueError(f"{label}: {problem}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label}: root must be a YAML object")
    if value.get("schema") != 1:
        raise ValueError(f"{label}: schema must be 1")
    return value


def resolve_root_file(root: Path, value: object, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label}: path must be a non-empty string")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{label}: path must stay inside the vault")
    candidate = (root / path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise ValueError(f"{label}: resolved path leaves the vault") from error
    return candidate


def string_list(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{label}: expected an array of strings")
    return tuple(value)


def string_map(value: object, label: str) -> dict[str, str]:
    if not isinstance(value, dict) or any(
        not isinstance(source, str)
        or not source
        or not isinstance(target, str)
        or not target
        for source, target in value.items()
    ):
        raise ValueError(f"{label}: expected an object with non-empty string mappings")
    return dict(value)


def field_profile(root: Path, config: dict[str, Any]) -> FieldProfile:
    fields_path = resolve_root_file(root, config.get("fields"), "frontmatter.fields")
    data = load_yaml(fields_path, "frontmatter fields")
    roles = data.get("fields")
    if not isinstance(roles, dict):
        raise ValueError("frontmatter fields: fields must be an object")
    for role in ("kind", "type", "status", "area"):
        if not isinstance(roles.get(role), str) or not roles[role]:
            raise ValueError(f"frontmatter fields: missing role {role}")
    values = data.get("values", {})
    if not isinstance(values, dict):
        raise ValueError("frontmatter fields: values must be an object")
    external = data.get(
        "externalReferences",
        {
            "idSuffixes": ["_id", "_uid"],
            "urlSuffix": "_url",
            "requireVerifiedPair": True,
            "allowSecretsInUrls": False,
        },
    )
    if not isinstance(external, dict):
        raise ValueError("frontmatter fields: externalReferences must be an object")
    id_suffixes = string_list(
        external.get("idSuffixes"),
        "frontmatter fields.externalReferences.idSuffixes",
    )
    if not id_suffixes or any(not suffix.startswith("_") for suffix in id_suffixes):
        raise ValueError(
            "frontmatter fields.externalReferences.idSuffixes must contain underscore-prefixed suffixes"
        )
    url_suffix = external.get("urlSuffix")
    if not isinstance(url_suffix, str) or not url_suffix.startswith("_"):
        raise ValueError(
            "frontmatter fields.externalReferences.urlSuffix must be underscore-prefixed"
        )
    require_pair = external.get("requireVerifiedPair")
    allow_secrets = external.get("allowSecretsInUrls")
    if not isinstance(require_pair, bool) or not isinstance(allow_secrets, bool):
        raise ValueError(
            "frontmatter fields.externalReferences pair and secret policies must be boolean"
        )
    return FieldProfile(
        kind=roles["kind"],
        type=roles["type"],
        status=roles["status"],
        area=roles["area"],
        kind_values=string_map(
            values.get("kind", {}), "frontmatter fields.values.kind"
        ),
        type_values=string_map(
            values.get("type", {}), "frontmatter fields.values.type"
        ),
        status_values=string_map(
            values.get("status", {}), "frontmatter fields.values.status"
        ),
        required=string_list(data.get("required"), "frontmatter fields.required"),
        lists=string_list(data.get("lists"), "frontmatter fields.lists"),
        dates=string_list(data.get("dates"), "frontmatter fields.dates"),
        order=string_list(data.get("order"), "frontmatter fields.order"),
        external_id_suffixes=id_suffixes,
        external_url_suffix=url_suffix,
        external_require_pair=require_pair,
        external_allow_secrets=allow_secrets,
    )


def safe_glob(root: Path, pattern: str, label: str) -> list[Path]:
    candidate = Path(pattern)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"{label}: glob must stay inside the vault")
    matches = [Path(item) for item in glob.glob(str(root / pattern), recursive=True)]
    files: list[Path] = []
    for match in matches:
        resolved = match.resolve()
        try:
            resolved.relative_to(root)
        except ValueError as error:
            raise ValueError(f"{label}: matched path leaves the vault") from error
        if resolved.is_file():
            files.append(resolved)
    return sorted(set(files))


def load_models(
    root: Path, patterns: tuple[str, ...]
) -> SchemaModels:
    paths: list[Path] = []
    for index, pattern in enumerate(patterns):
        paths.extend(safe_glob(root, pattern, f"frontmatter.models[{index}]"))
    paths = sorted(set(paths))
    if not paths:
        raise ValueError("frontmatter.models: no schema model files matched")

    kinds: dict[str, dict[str, Any]] = {}
    fields: dict[str, dict[str, Any]] = {}
    for path in paths:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError(f"schema model {relative(path, root)}: invalid JSON") from error
        if not isinstance(value, dict) or value.get("schemaVersion") != 1:
            raise ValueError(f"schema model {relative(path, root)}: schemaVersion must be 1")
        content_kinds = value.get("contentKinds")
        if not isinstance(content_kinds, dict):
            raise ValueError(f"schema model {relative(path, root)}: contentKinds must be an object")
        model_kinds: list[str] = []
        model_types: set[str] = set()
        for identifier, definition in content_kinds.items():
            if not isinstance(identifier, str) or not isinstance(definition, dict):
                raise ValueError(f"schema model {relative(path, root)}: invalid content kind")
            if identifier in kinds:
                raise ValueError(f"duplicate content kind: {identifier}")
            types = definition.get("types")
            statuses = definition.get("statuses")
            if not isinstance(types, list) or not types or any(not isinstance(item, str) for item in types):
                raise ValueError(f"content kind {identifier}: types must be a non-empty string array")
            if not isinstance(statuses, list) or not statuses or any(
                not isinstance(item, str) for item in statuses
            ):
                raise ValueError(f"content kind {identifier}: statuses must be a non-empty string array")
            if len(types) != len(set(types)):
                raise ValueError(f"content kind {identifier}: types must be unique")
            if len(statuses) != len(set(statuses)):
                raise ValueError(f"content kind {identifier}: statuses must be unique")
            if not isinstance(definition.get("areaRequired"), bool):
                raise ValueError(f"content kind {identifier}: areaRequired must be boolean")
            filename_pattern = definition.get("filenamePattern")
            if filename_pattern is not None:
                if not isinstance(filename_pattern, str) or not filename_pattern:
                    raise ValueError(
                        f"content kind {identifier}: filenamePattern must be a non-empty string"
                    )
                try:
                    re.compile(filename_pattern)
                except re.error as error:
                    raise ValueError(
                        f"content kind {identifier}: invalid filenamePattern"
                    ) from error
            filename_patterns = definition.get("filenamePatternByType", {})
            if not isinstance(filename_patterns, dict) or any(
                key not in types or not isinstance(pattern, str) or not pattern
                for key, pattern in filename_patterns.items()
            ):
                raise ValueError(
                    f"content kind {identifier}: filenamePatternByType must map known types to patterns"
                )
            for pattern in filename_patterns.values():
                try:
                    re.compile(pattern)
                except re.error as error:
                    raise ValueError(
                        f"content kind {identifier}: invalid filenamePatternByType"
                    ) from error
            kinds[identifier] = definition
            model_kinds.append(identifier)
            model_types.update(types)

        model_fields = value.get("fields", {})
        if not isinstance(model_fields, dict):
            raise ValueError(f"schema model {relative(path, root)}: fields must be an object")
        for name, definition in model_fields.items():
            if not isinstance(name, str) or not name or not isinstance(definition, dict):
                raise ValueError(f"schema model {relative(path, root)}: invalid field definition")
            if name in fields:
                raise ValueError(f"duplicate module field: {name}")
            field_type = definition.get("type")
            if field_type not in FIELD_TYPES:
                raise ValueError(f"module field {name}: unsupported type {field_type!r}")
            register = definition.get("register")
            if field_type == "register" and (not isinstance(register, str) or not register):
                raise ValueError(f"module field {name}: register must be a non-empty string")
            required_type = definition.get("typeRequired")
            if required_type is not None and (
                not isinstance(required_type, str) or not required_type
            ):
                raise ValueError(f"module field {name}: typeRequired must be a non-empty string")
            if required_type is not None and required_type not in model_types:
                raise ValueError(
                    f"module field {name}: typeRequired must identify a type in the same model"
                )
            normalized = dict(definition)
            normalized["contentKinds"] = tuple(model_kinds)
            fields[name] = normalized
    return SchemaModels(kinds=kinds, fields=fields)


def load_register(
    root: Path, value: object, label: str, expected_name: str
) -> RegisterDefinition:
    path = resolve_root_file(root, value, label)
    data = load_yaml(path, label)
    if data.get("register") != expected_name:
        raise ValueError(f"{label}: register must be {expected_name!r}")
    values = data.get("values")
    if not isinstance(values, list) or any(not isinstance(item, str) for item in values):
        raise ValueError(f"{label}: values must be an array of strings")
    if len(values) != len(set(values)):
        raise ValueError(f"{label}: values must be unique")
    rules = data.get("rules", {})
    if not isinstance(rules, dict):
        raise ValueError(f"{label}: rules must be an object")
    multiple = rules.get("multiple", False)
    if not isinstance(multiple, bool):
        raise ValueError(f"{label}: rules.multiple must be boolean")
    return RegisterDefinition(frozenset(values), multiple)


def expand_patterns(values: object, system_root: str, label: str) -> tuple[str, ...]:
    patterns = string_list(values, label)
    escaped_system_root = glob.escape(system_root)
    return tuple(pattern.replace("{system}", escaped_system_root) for pattern in patterns)


def is_excluded(path: Path, root: Path, excluded_parts: set[str]) -> bool:
    return any(part in excluded_parts for part in path.relative_to(root).parts)


def vault_files(root: Path, excluded_parts: set[str]) -> list[Path]:
    return sorted(
        (
            path
            for path in root.rglob("*")
            if path.is_file() and not is_excluded(path, root, excluded_parts)
        ),
        key=lambda path: relative(path, root),
    )


def matches(path: str, patterns: tuple[str, ...]) -> bool:
    return any(
        fnmatch.fnmatchcase(path, pattern)
        or (pattern.startswith("**/") and fnmatch.fnmatchcase(path, pattern[3:]))
        for pattern in patterns
    )


def frontmatter(text: str) -> tuple[dict[str, Any] | None, list[str], str | None]:
    if not text.startswith("---\n"):
        return None, [], "frontmatter is missing"
    end = text.find("\n---\n", 4)
    if end < 0:
        return None, [], "frontmatter is not closed"
    raw = text[4:end]
    keys = [
        match.group(1)
        for line in raw.splitlines()
        if (match := re.match(r"^([A-Za-z0-9_]+):", line))
    ]
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as error:
        problem = getattr(error, "problem", None) or "invalid YAML"
        return None, keys, str(problem)
    if not isinstance(data, dict):
        return None, keys, "frontmatter is not a YAML object"
    return data, keys, None


def valid_date(value: Any) -> bool:
    if isinstance(value, dt.datetime):
        return False
    if isinstance(value, dt.date):
        return True
    if not isinstance(value, str) or not DATE_RE.fullmatch(value):
        return False
    try:
        dt.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def is_empty(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def filename_pattern(
    definition: dict[str, Any], canonical_type: object
) -> str | None:
    patterns = definition.get("filenamePatternByType", {})
    if isinstance(canonical_type, str) and canonical_type in patterns:
        return patterns[canonical_type]
    pattern = definition.get("filenamePattern")
    return pattern if isinstance(pattern, str) else None


def module_field_findings(
    data: dict[str, Any],
    rel: str,
    canonical_kind: object,
    canonical_type: object,
    fields: dict[str, dict[str, Any]],
    registers: dict[str, RegisterDefinition],
) -> list[Finding]:
    findings: list[Finding] = []
    for name, definition in fields.items():
        if canonical_kind not in definition["contentKinds"]:
            continue
        required_type = definition.get("typeRequired")
        if required_type == canonical_type and (name not in data or is_empty(data[name])):
            findings.append(
                Finding(
                    "error",
                    "frontmatter.required",
                    rel,
                    1,
                    f"{name} is required for type {required_type!r}",
                )
            )
        if name not in data or data[name] in (None, ""):
            continue
        value = data[name]
        field_type = definition["type"]
        if field_type == "string" and not isinstance(value, str):
            findings.append(
                Finding("error", "frontmatter.string", rel, 1, f"{name} must be a string")
            )
        elif field_type == "date" and not valid_date(value):
            findings.append(
                Finding("error", "frontmatter.date", rel, 1, f"{name} must use YYYY-MM-DD")
            )
        elif field_type == "wiki-link-list":
            if not isinstance(value, list) or any(
                not isinstance(item, str)
                or WIKI_LINK_RE.fullmatch(item) is None
                or not wiki_target(WIKI_LINK_RE.fullmatch(item).group(2))
                for item in value
            ):
                findings.append(
                    Finding(
                        "error",
                        "frontmatter.wiki_link_list",
                        rel,
                        1,
                        f"{name} must be a YAML list of Wiki links",
                    )
                )
        elif field_type == "register":
            register_name = definition["register"]
            register = registers[register_name]
            if register.multiple:
                valid = (
                    isinstance(value, list)
                    and all(isinstance(item, str) for item in value)
                    and all(item in register.values for item in value)
                )
            else:
                valid = isinstance(value, str) and value in register.values
            if not valid:
                shape = "a YAML list" if register.multiple else "one value"
                findings.append(
                    Finding(
                        "error",
                        "frontmatter.register",
                        rel,
                        1,
                        f"{name} must be {shape} from register {register_name!r}",
                    )
                )
    return findings


def external_reference_findings(
    data: dict[str, Any], rel: str, profile: FieldProfile
) -> list[Finding]:
    findings: list[Finding] = []
    bases: set[str] = set()
    for name in data:
        if not isinstance(name, str):
            continue
        if name.endswith(profile.external_url_suffix):
            bases.add(name[: -len(profile.external_url_suffix)])
        for suffix in profile.external_id_suffixes:
            if name.endswith(suffix):
                bases.add(name[: -len(suffix)])

    for base in sorted(bases):
        url_field = base + profile.external_url_suffix
        id_fields = [base + suffix for suffix in profile.external_id_suffixes]
        url_value = data.get(url_field)
        identifiers = [data.get(name) for name in id_fields]
        has_url = not is_empty(url_value)
        has_identifier = any(not is_empty(value) for value in identifiers)
        for id_field, identifier in zip(id_fields, identifiers):
            if not is_empty(identifier) and not isinstance(identifier, str):
                findings.append(
                    Finding(
                        "error",
                        "frontmatter.external_reference_id",
                        rel,
                        1,
                        f"{id_field} must be a string",
                    )
                )
        if profile.external_require_pair and has_url != has_identifier:
            findings.append(
                Finding(
                    "error",
                    "frontmatter.external_reference_pair",
                    rel,
                    1,
                    f"external reference {base!r} requires both URL and ID/UID",
                )
            )
        if not has_url:
            continue
        if not isinstance(url_value, str):
            findings.append(
                Finding(
                    "error",
                    "frontmatter.external_reference_url",
                    rel,
                    1,
                    f"{url_field} must be an HTTP(S) URL",
                )
            )
            continue
        try:
            parsed = urllib.parse.urlsplit(url_value)
        except ValueError:
            findings.append(
                Finding(
                    "error",
                    "frontmatter.external_reference_url",
                    rel,
                    1,
                    f"{url_field} must be an HTTP(S) URL",
                )
            )
            continue
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            findings.append(
                Finding(
                    "error",
                    "frontmatter.external_reference_url",
                    rel,
                    1,
                    f"{url_field} must be an HTTP(S) URL",
                )
            )
        if not profile.external_allow_secrets:
            query_keys = {
                key.casefold().replace("-", "_")
                for key, _ in urllib.parse.parse_qsl(
                    parsed.query, keep_blank_values=True
                )
            }
            if parsed.username is not None or parsed.password is not None or (
                query_keys & SENSITIVE_QUERY_KEYS
            ):
                findings.append(
                    Finding(
                        "error",
                        "frontmatter.external_reference_secret",
                        rel,
                        1,
                        f"{url_field} must not contain credentials or secret query parameters",
                    )
                )
    return findings


def frontmatter_findings(
    root: Path,
    files: Iterable[Path],
    include: tuple[str, ...],
    exclude: tuple[str, ...],
    profile: FieldProfile,
    models: SchemaModels,
    registers: dict[str, RegisterDefinition],
) -> list[Finding]:
    findings: list[Finding] = []
    for path in files:
        rel = relative(path, root)
        if not matches(rel, include) or matches(rel, exclude):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        data, keys, error = frontmatter(text)
        if error or data is None:
            findings.append(Finding("error", "frontmatter.invalid", rel, 1, error or "invalid"))
            continue
        if len(keys) != len(set(keys)):
            findings.append(
                Finding("error", "frontmatter.duplicate_field", rel, 1, "duplicate field name")
            )

        for field in profile.required:
            if field not in data:
                findings.append(
                    Finding("error", "frontmatter.required", rel, 1, f"missing field: {field}")
                )

        kind = data.get(profile.kind)
        content_type = data.get(profile.type)
        status = data.get(profile.status)
        canonical_kind = (
            profile.kind_values.get(kind, kind) if isinstance(kind, str) else kind
        )
        canonical_type = (
            profile.type_values.get(content_type, content_type)
            if isinstance(content_type, str)
            else content_type
        )
        canonical_status = (
            profile.status_values.get(status, status)
            if isinstance(status, str)
            else status
        )
        definition = (
            models.kinds.get(canonical_kind) if isinstance(canonical_kind, str) else None
        )
        if definition is None:
            findings.append(
                Finding("error", "frontmatter.kind", rel, 1, f"unknown kind: {kind!r}")
            )
        else:
            if canonical_type not in definition["types"]:
                findings.append(
                    Finding(
                        "error",
                        "frontmatter.type",
                        rel,
                        1,
                        f"type {content_type!r} is invalid for kind {kind!r}",
                    )
                )
            if canonical_status not in definition["statuses"]:
                findings.append(
                    Finding(
                        "error",
                        "frontmatter.status",
                        rel,
                        1,
                        f"status {status!r} is invalid for kind {kind!r}",
                    )
                )
            pattern = filename_pattern(definition, canonical_type)
            if pattern is not None and re.fullmatch(pattern, path.stem) is None:
                findings.append(
                    Finding(
                        "error",
                        "frontmatter.filename",
                        rel,
                        1,
                        "filename does not match the schema pattern",
                    )
                )

        findings.extend(
            module_field_findings(
                data,
                rel,
                canonical_kind,
                canonical_type,
                models.fields,
                registers,
            )
        )
        findings.extend(external_reference_findings(data, rel, profile))

        for field in profile.lists:
            if field in data and not isinstance(data[field], list):
                findings.append(
                    Finding("error", "frontmatter.list_type", rel, 1, f"{field} must be a YAML list")
                )
        for field in profile.dates:
            if field in data and data[field] not in (None, "") and not valid_date(data[field]):
                findings.append(
                    Finding("error", "frontmatter.date", rel, 1, f"{field} must use YYYY-MM-DD")
                )

        area = data.get(profile.area)
        area_required = bool(definition and definition["areaRequired"])
        if area_required and (not isinstance(area, str) or not area):
            findings.append(
                Finding("error", "frontmatter.area_required", rel, 1, f"{profile.area} is required")
            )
        if area not in (None, "") and (
            not isinstance(area, str) or area not in registers["areas"].values
        ):
            findings.append(
                Finding("error", "frontmatter.area", rel, 1, f"unknown area: {area!r}")
            )

        positions = [keys.index(field) for field in profile.order if field in keys]
        if positions != sorted(positions):
            findings.append(
                Finding("error", "frontmatter.field_order", rel, 1, "base fields are out of order")
            )
    return findings


def without_code(lines: list[str]) -> Iterable[tuple[int, str]]:
    fenced = False
    for number, line in enumerate(lines, 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            yield number, re.sub(r"`[^`]*`", "", line)


def file_indexes(
    root: Path, files: Iterable[Path]
) -> tuple[dict[str, Path], dict[str, list[Path]]]:
    exact: dict[str, Path] = {}
    basename: dict[str, list[Path]] = {}
    for path in files:
        rel = relative(path, root)
        exact[rel] = path
        for key in {normalize(path.name), normalize(path.stem)}:
            basename.setdefault(key, []).append(path)
    return exact, basename


def wiki_target(raw: str) -> str:
    raw = raw.replace("\\|", "|")
    return raw.split("|", 1)[0].split("#", 1)[0].strip().rstrip("\\")


def resolve_wiki(
    target: str, exact: dict[str, Path], basename: dict[str, list[Path]]
) -> tuple[str, list[Path]]:
    normalized = normalize(target.lstrip("/"))
    direct = [exact[item] for item in (normalized, normalized + ".md") if item in exact]
    if direct:
        return "exact", list(dict.fromkeys(direct))
    if "/" not in normalized:
        found = basename.get(normalized, []) or basename.get(normalized + ".md", [])
        unique = list(dict.fromkeys(found))
        if len(unique) == 1:
            return "short", unique
        if len(unique) > 1:
            return "ambiguous", unique
    return "missing", []


def link_findings(
    root: Path,
    markdown: Iterable[Path],
    files: Iterable[Path],
    require_full_paths: bool,
) -> list[Finding]:
    findings: list[Finding] = []
    exact, basename = file_indexes(root, files)
    for path in markdown:
        rel = relative(path, root)
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_number, line in without_code(text.splitlines()):
            for match in WIKI_LINK_RE.finditer(line):
                target = wiki_target(match.group(2))
                if not target:
                    continue
                state, _ = resolve_wiki(target, exact, basename)
                if state == "missing":
                    findings.append(
                        Finding("error", "link.missing", rel, line_number, f"missing target: {target}")
                    )
                elif state == "ambiguous":
                    findings.append(
                        Finding("error", "link.ambiguous", rel, line_number, f"ambiguous target: {target}")
                    )
                elif state == "short" and require_full_paths:
                    findings.append(
                        Finding(
                            "error",
                            "link.noncanonical_path",
                            rel,
                            line_number,
                            f"full path required: {target}",
                        )
                    )

            line_without_wiki = WIKI_LINK_RE.sub("", line)
            for match in MARKDOWN_LINK_RE.finditer(line_without_wiki):
                target = match.group(1).strip().split(" ", 1)[0].strip("<>")
                if (
                    not target
                    or target == "URL"
                    or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target)
                    or target.startswith("#")
                ):
                    continue
                candidate = (path.parent / urllib.parse.unquote(target)).resolve()
                try:
                    candidate.relative_to(root)
                except ValueError:
                    exists = False
                else:
                    exists = candidate.exists()
                rule = "link.markdown_internal" if exists else "link.markdown_missing"
                detail = (
                    "internal links must use a full-path Wiki link"
                    if exists
                    else f"missing local target: {target}"
                )
                findings.append(Finding("error", rule, rel, line_number, detail))
    return findings


def git_output(root: Path, *args: str) -> str:
    result = subprocess.run(
        ("git", *args),
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout


def size_report(root: Path, files: Iterable[Path]) -> dict[str, int]:
    file_list = list(files)
    current_bytes = sum(path.stat().st_size for path in file_list)
    tracked = [item for item in git_output(root, "ls-files", "-z").split("\0") if item]
    tracked_bytes = sum((root / item).stat().st_size for item in tracked if (root / item).is_file())
    head_bytes = 0
    for line in git_output(root, "ls-tree", "-rl", "HEAD").splitlines():
        match = re.match(r"^\d+\s+\w+\s+[0-9a-f]+\s+(\d+)\t", line)
        if match:
            head_bytes += int(match.group(1))
    return {
        "vault_files": len(file_list),
        "vault_bytes": current_bytes,
        "tracked_files": len(tracked),
        "tracked_bytes": tracked_bytes,
        "head_bytes": head_bytes,
        "tracked_delta_bytes": tracked_bytes - head_bytes,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="vault root")
    parser.add_argument(
        "--config", default="Vault-OS/validation.yaml", help="validation profile relative to root"
    )
    parser.add_argument(
        "--instance-config",
        default="Vault-OS/config.yaml",
        help="instance configuration relative to root",
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    try:
        instance = load_yaml(
            resolve_root_file(root, args.instance_config, "instance configuration"),
            "instance configuration",
        )
        paths = instance.get("paths")
        if not isinstance(paths, dict) or not isinstance(paths.get("system"), str):
            raise ValueError("instance configuration: paths.system must be a string")
        system_root = paths["system"]
        resolve_root_file(root, system_root, "instance configuration paths.system")
        validation = load_yaml(
            resolve_root_file(root, args.config, "validation configuration"),
            "validation configuration",
        )
        excluded_parts = set(
            string_list(validation.get("excludePathParts"), "excludePathParts")
        )
        files = vault_files(root, excluded_parts)
        markdown = [path for path in files if path.suffix.lower() == ".md"]
        findings: list[Finding] = []

        frontmatter_config = validation.get("frontmatter")
        if not isinstance(frontmatter_config, dict):
            raise ValueError("frontmatter configuration must be an object")
        if frontmatter_config.get("enabled") is True:
            include = expand_patterns(
                frontmatter_config.get("include"), system_root, "frontmatter.include"
            )
            exclude = expand_patterns(
                frontmatter_config.get("exclude"), system_root, "frontmatter.exclude"
            )
            models = expand_patterns(
                frontmatter_config.get("models"), system_root, "frontmatter.models"
            )
            registers = frontmatter_config.get("registers")
            if not isinstance(registers, dict):
                raise ValueError("frontmatter.registers must be an object")
            profile = field_profile(root, frontmatter_config)
            schema_models = load_models(root, models)
            loaded_registers = {
                "areas": load_register(
                    root,
                    registers.get("areas"),
                    "frontmatter.registers.areas",
                    "areas",
                )
            }
            for definition in schema_models.fields.values():
                if definition["type"] != "register":
                    continue
                register_name = definition["register"]
                if register_name in loaded_registers:
                    continue
                loaded_registers[register_name] = load_register(
                    root,
                    registers.get(register_name),
                    f"frontmatter.registers.{register_name}",
                    register_name,
                )
            findings.extend(
                frontmatter_findings(
                    root,
                    markdown,
                    include,
                    exclude,
                    profile,
                    schema_models,
                    loaded_registers,
                )
            )
        elif frontmatter_config.get("enabled") is not False:
            raise ValueError("frontmatter.enabled must be boolean")

        link_config = validation.get("links")
        if not isinstance(link_config, dict):
            raise ValueError("links configuration must be an object")
        if link_config.get("enabled") is True:
            require_full = link_config.get("requireFullWikiPaths")
            if not isinstance(require_full, bool):
                raise ValueError("links.requireFullWikiPaths must be boolean")
            findings.extend(link_findings(root, markdown, files, require_full))
        elif link_config.get("enabled") is not False:
            raise ValueError("links.enabled must be boolean")

        findings.sort(key=lambda item: (item.path, item.line or 0, item.rule))
        git_config = validation.get("git")
        if not isinstance(git_config, dict) or not isinstance(git_config.get("sizeReport"), bool):
            raise ValueError("git.sizeReport must be boolean")
        sizes = None
        if git_config["sizeReport"]:
            if not (root / ".git").exists():
                raise ValueError("git.sizeReport requires a Git repository")
            sizes = size_report(root, files)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        if args.as_json:
            print(json.dumps({"technical_error": str(error)}, ensure_ascii=False, indent=2))
        else:
            print(f"TECHNICAL ERROR: {error}", file=sys.stderr)
        return 2

    errors = sum(item.severity == "error" for item in findings)
    warnings = sum(item.severity == "warning" for item in findings)
    if args.as_json:
        print(
            json.dumps(
                {
                    "summary": {"errors": errors, "warnings": warnings},
                    "findings": [asdict(item) for item in findings],
                    "size": sizes,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        for item in findings:
            location = f"{item.path}:{item.line}" if item.line else item.path
            print(f"{item.severity.upper()} {item.rule} {location} - {item.detail}")
        print(f"RESULT errors={errors} warnings={warnings}")
        if sizes is not None:
            print(
                "SIZE "
                f"files={sizes['vault_files']} bytes={sizes['vault_bytes']} "
                f"tracked={sizes['tracked_bytes']} head={sizes['head_bytes']} "
                f"delta={sizes['tracked_delta_bytes']:+d}"
            )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
