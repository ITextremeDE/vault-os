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

    def test_area_format_can_require_resolvable_wiki_links(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.create_vault(root)
            fields_path = root / "Vault-OS/schema/fields.yaml"
            fields = yaml.safe_load(fields_path.read_text(encoding="utf-8"))
            fields["formats"]["area"] = "wiki-link"
            fields_path.write_text(
                yaml.safe_dump(fields, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            project = root / "Projects/2026-08-11 Example.md"
            project.write_text(
                project.read_text(encoding="utf-8").replace(
                    "area: Example", 'area: "[[Areas/Example/_Example|Example]]"'
                ),
                encoding="utf-8",
            )
            area = root / "Areas/Example/_Example.md"
            area.parent.mkdir(parents=True)
            area.write_text(
                """---
kind: area
type: area
status: open
area: "[[Areas/Example/_Example|Example]]"
aliases: []
tags: []
cssclasses: []
created: 2026-08-18
---

# Example
""",
                encoding="utf-8",
            )

            result = self.run_validator(root)
            project.write_text(
                project.read_text(encoding="utf-8").replace(
                    "_Example|Example", "_Example|Wrong"
                ),
                encoding="utf-8",
            )
            invalid_alias = self.run_validator(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("RESULT errors=0 warnings=0", result.stdout)
        self.assertEqual(
            invalid_alias.returncode,
            1,
            invalid_alias.stdout + invalid_alias.stderr,
        )
        self.assertIn("frontmatter.area_format", invalid_alias.stdout)

    def test_area_format_rejects_the_other_representation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.create_vault(root)
            project = root / "Projects/2026-08-11 Example.md"
            project.write_text(
                project.read_text(encoding="utf-8").replace(
                    "area: Example", 'area: "[[Projects/2026-08-11 Example]]"'
                ),
                encoding="utf-8",
            )
            text_result = self.run_validator(root)

            fields_path = root / "Vault-OS/schema/fields.yaml"
            fields = yaml.safe_load(fields_path.read_text(encoding="utf-8"))
            fields["formats"]["area"] = "wiki-link"
            fields_path.write_text(
                yaml.safe_dump(fields, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            project.write_text(
                project.read_text(encoding="utf-8").replace(
                    'area: "[[Projects/2026-08-11 Example]]"', "area: Example"
                ),
                encoding="utf-8",
            )
            link_result = self.run_validator(root)

        self.assertEqual(text_result.returncode, 1, text_result.stdout + text_result.stderr)
        self.assertIn("frontmatter.area_format", text_result.stdout)
        self.assertEqual(link_result.returncode, 1, link_result.stdout + link_result.stderr)
        self.assertIn("frontmatter.area_format", link_result.stdout)

    def test_area_register_rejects_wiki_link_syntax(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.create_vault(root)
            root.joinpath("Vault-OS/registers/areas.yaml").write_text(
                'schema: 1\nregister: areas\nvalues: ["[[Areas/Example]]"]\n',
                encoding="utf-8",
            )

            result = self.run_validator(root)

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("values must be canonical plain names", result.stderr)

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
            note.parent.mkdir(parents=True)
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
            "frontmatter.filename",
            "frontmatter.external_reference_pair",
            "frontmatter.external_reference_id",
            "frontmatter.external_reference_secret",
        ):
            self.assertIn(rule, result.stdout)
            self.assertNotIn("redacted-secret", result.stdout)

    def test_single_wiki_link_module_fields_are_validated(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.create_vault(root)
            role = root / "Contacts/Roles/Example – Doe, Jane – Manager.md"
            role.parent.mkdir(parents=True)
            role.write_text(
                """---
kind: contact
type: role
status: active
area: Example
aliases: []
tags: []
cssclasses: []
created: 2026-08-14
person: "[[Projects/2026-08-11 Example]]"
organization: "[[Projects/2026-08-11 Example]]"
function: Manager
start_date:
end_date:
---

# Example – Doe, Jane – Manager
""",
                encoding="utf-8",
            )

            valid = self.run_validator(root)
            self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)

            role.write_text(
                role.read_text(encoding="utf-8").replace(
                    'organization: "[[Projects/2026-08-11 Example]]"',
                    "organization: Example Inc",
                ),
                encoding="utf-8",
            )
            invalid = self.run_validator(root)

        self.assertEqual(invalid.returncode, 1, invalid.stdout + invalid.stderr)
        self.assertIn("frontmatter.wiki_link", invalid.stdout)

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
            note = root / "Contacts/Roles/Example – Doe, Jane – Manager.md"
            note.parent.mkdir(parents=True)
            note.write_text(
                """---
kind: contact
type: role
status: active
area: Example
aliases: []
tags: []
cssclasses: []
created: 2026-08-11
person:
organization:
function: Manager
---

# Example – Doe, Jane – Manager
""",
                encoding="utf-8",
            )

            result = self.run_validator(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("frontmatter.required", result.stdout)


if __name__ == "__main__":
    unittest.main()
