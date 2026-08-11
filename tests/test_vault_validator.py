"""Integration tests for the portable, configuration-driven vault validator."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPOSITORY_ROOT / "src/core/validation/validate_vault.py"
YAML_AVAILABLE = importlib.util.find_spec("yaml") is not None


@unittest.skipUnless(YAML_AVAILABLE, "PyYAML is required for vault validation tests")
class VaultValidatorTests(unittest.TestCase):
    def create_vault(self, root: Path, content_type: str = "planning") -> None:
        instance = root / "Vault-OS"
        (instance / "schema").mkdir(parents=True)
        (instance / "registers").mkdir(parents=True)
        shutil.copy(
            REPOSITORY_ROOT / "instance-template/vault-os.yaml",
            instance / "config.yaml",
        )
        shutil.copy(
            REPOSITORY_ROOT / "instance-template/validation/vault.yaml",
            instance / "validation.yaml",
        )
        shutil.copy(
            REPOSITORY_ROOT / "instance-template/schema/fields.yaml",
            instance / "schema/fields.yaml",
        )
        (instance / "registers/areas.yaml").write_text(
            "schema: 1\nregister: areas\nvalues:\n  - Example\n",
            encoding="utf-8",
        )
        contact_registers = instance / "modules/contacts/registers"
        contact_registers.mkdir(parents=True)
        for register in ("relationships", "relevance"):
            shutil.copy(
                REPOSITORY_ROOT
                / f"instance-template/modules/contacts/registers/{register}.yaml",
                contact_registers / f"{register}.yaml",
            )

        models = root / "99 System/01 Schema/Models"
        models.mkdir(parents=True)
        shutil.copy(
            REPOSITORY_ROOT / "src/core/schema/system.schema.json",
            models / "core.json",
        )
        for module in ("contacts", "journal", "knowledge", "para"):
            shutil.copy(
                REPOSITORY_ROOT / f"src/modules/{module}/schema/model.json",
                models / f"{module}.json",
            )

        content = root / "Projects/2026-08-11 Example.md"
        content.parent.mkdir()
        content.write_text(
            "\n".join(
                (
                    "---",
                    "kind: project",
                    f"type: {content_type}",
                    "status: open",
                    "area: Example",
                    "aliases: []",
                    "tags: []",
                    "cssclasses: []",
                    "created: 2026-08-11",
                    "---",
                    "",
                    "# Example",
                    "",
                )
            ),
            encoding="utf-8",
        )

    def run_validator(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), str(root)],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_valid_configured_vault_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.create_vault(root)
            result = self.run_validator(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("RESULT errors=0 warnings=0", result.stdout)

    def test_invalid_module_type_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.create_vault(root, content_type="invented")
            result = self.run_validator(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("frontmatter.type", result.stdout)

    def test_instance_profile_maps_localized_fields_and_values(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.create_vault(root)
            root.joinpath("Vault-OS/schema/fields.yaml").write_text(
                """schema: 1
fields:
  kind: art
  type: typ
  status: status
  area: bereich
values:
  kind:
    Projekt: project
  type:
    Planung: planning
  status:
    Offen: open
required: [art, typ, status, bereich, aliases, tags, cssclasses, created]
lists: [aliases, tags, cssclasses]
dates: [created, modified, reviewed]
order: [art, typ, status, bereich, aliases, tags, cssclasses, created, modified]
""",
                encoding="utf-8",
            )
            root.joinpath("Projects/2026-08-11 Example.md").write_text(
                """---
art: Projekt
typ: Planung
status: Offen
bereich: Example
aliases: []
tags: []
cssclasses: []
created: 2026-08-11
---

# Example
""",
                encoding="utf-8",
            )

            result = self.run_validator(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("RESULT errors=0 warnings=0", result.stdout)

    def test_instance_profile_maps_module_fields_and_filename_patterns(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.create_vault(root)
            root.joinpath("Vault-OS/schema/fields.yaml").write_text(
                """schema: 1
fields:
  kind: art
  type: typ
  status: status
  area: bereich
values:
  kind: {Kontakt: contact}
  type: {Ansprechpartner: representative}
  status: {Aktiv: active}
moduleFields:
  relationship: beziehung
  relevance: relevanz
  last_contact: letzter_kontakt
  organizations: organisationen
filenamePatterns:
  contact: "^Historischer Kontakt$"
required: [art, typ, status, bereich, aliases, tags, cssclasses, created]
lists: [aliases, tags, cssclasses]
dates: [created, modified, reviewed, letzter_kontakt]
order: [art, typ, status, bereich, aliases, tags, cssclasses, created, modified]
externalReferences:
  idSuffixes: [_id, _uid]
  urlSuffix: _url
  requireVerifiedPair: true
  allowSecretsInUrls: false
""",
                encoding="utf-8",
            )
            root.joinpath(
                "Vault-OS/modules/contacts/registers/relationships.yaml"
            ).write_text(
                "schema: 1\nregister: relationships\nvalues: [Geschäftskontakt]\nrules: {multiple: true, allowScalar: true}\n",
                encoding="utf-8",
            )
            root.joinpath(
                "Vault-OS/modules/contacts/registers/relevance.yaml"
            ).write_text(
                "schema: 1\nregister: relevance\nvalues: [Hoch]\nrules: {multiple: false}\n",
                encoding="utf-8",
            )
            root.joinpath("Projects/2026-08-11 Example.md").unlink()
            note = root / "Contacts/Historischer Kontakt.md"
            note.parent.mkdir()
            note.write_text(
                """---
art: Kontakt
typ: Ansprechpartner
status: Aktiv
bereich: Example
aliases: []
tags: []
cssclasses: []
created: 2026-08-11
beziehung: Geschäftskontakt
relevanz: Hoch
letzter_kontakt: 2026-08-10
organisationen:
  - "[[Contacts/Historischer Kontakt]]"
---

# Historischer Kontakt
""",
                encoding="utf-8",
            )

            result = self.run_validator(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("RESULT errors=0 warnings=0", result.stdout)

    def test_module_fields_filename_and_external_references_are_validated(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.create_vault(root)
            note = root / "Contacts/Wrong.md"
            note.parent.mkdir()
            note.write_text(
                """---
kind: contact
type: representative
status: active
area: Example
aliases: []
tags: []
cssclasses: []
created: 2026-08-11
job: [Manager]
relationship: invented
relevance: urgent
last_contact: yesterday
organizations:
  - Not a wiki link
service_url: https://example.invalid/account?token=redacted-secret
archive_id: [invalid]
archive_url: https://example.invalid/archive
---

# Wrong
""",
                encoding="utf-8",
            )

            result = self.run_validator(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        for rule in (
            "frontmatter.string",
            "frontmatter.register",
            "frontmatter.date",
            "frontmatter.wiki_link_list",
            "frontmatter.filename",
            "frontmatter.external_reference_pair",
            "frontmatter.external_reference_id",
            "frontmatter.external_reference_secret",
        ):
            self.assertIn(rule, result.stdout)
            self.assertNotIn("redacted-secret", result.stdout)

    def test_explicit_external_reference_pair_supports_nonderived_names(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.create_vault(root)
            fields_path = root / "Vault-OS/schema/fields.yaml"
            fields = yaml.safe_load(fields_path.read_text(encoding="utf-8"))
            fields["externalReferences"]["pairs"] = [
                {"id": "bookstack_page_id", "url": "bookstack_url"}
            ]
            fields_path.write_text(
                yaml.safe_dump(fields, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            note = root / "Projects/2026-08-11 Example.md"
            text = note.read_text(encoding="utf-8").replace(
                "created: 2026-08-11\n",
                "created: 2026-08-11\nbookstack_page_id: page-1\nbookstack_url: https://example.invalid/page/1\n",
            )
            note.write_text(text, encoding="utf-8")

            valid = self.run_validator(root)
            self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)

            note.write_text(
                text.replace("bookstack_url: https://example.invalid/page/1\n", ""),
                encoding="utf-8",
            )
            invalid = self.run_validator(root)

        self.assertEqual(invalid.returncode, 1, invalid.stdout + invalid.stderr)
        self.assertIn("frontmatter.external_reference_pair", invalid.stdout)

    def test_type_specific_required_field_must_not_be_empty(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.create_vault(root)
            note = root / "Contacts/Doe, Jane.md"
            note.parent.mkdir()
            note.write_text(
                """---
kind: contact
type: representative
status: active
area: Example
aliases: []
tags: []
cssclasses: []
created: 2026-08-11
organizations: []
---

# Jane Doe
""",
                encoding="utf-8",
            )

            result = self.run_validator(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("frontmatter.required", result.stdout)


if __name__ == "__main__":
    unittest.main()
