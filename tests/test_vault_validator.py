"""Integration tests for the portable, configuration-driven vault validator."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPOSITORY_ROOT / "src/core/validation/validate_vault.py"
YAML_AVAILABLE = importlib.util.find_spec("yaml") is not None


@unittest.skipUnless(YAML_AVAILABLE, "PyYAML is required for vault validation tests")
class VaultValidatorTests(unittest.TestCase):
    def create_vault(self, root: Path, content_type: str = "planning") -> None:
        runtime = root / ".vault-os"
        (runtime / "schema").mkdir(parents=True)
        (runtime / "registers").mkdir(parents=True)
        shutil.copy(
            REPOSITORY_ROOT / "instance-template/vault-os.yaml",
            runtime / "config.yaml",
        )
        shutil.copy(
            REPOSITORY_ROOT / "instance-template/validation/vault.yaml",
            runtime / "validation.yaml",
        )
        shutil.copy(
            REPOSITORY_ROOT / "instance-template/schema/fields.yaml",
            runtime / "schema/fields.yaml",
        )
        (runtime / "registers/areas.yaml").write_text(
            "schema: 1\nregister: areas\nvalues:\n  - Example\n",
            encoding="utf-8",
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

        content = root / "Projects/example.md"
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
            root.joinpath(".vault-os/schema/fields.yaml").write_text(
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
            root.joinpath("Projects/example.md").write_text(
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


if __name__ == "__main__":
    unittest.main()
