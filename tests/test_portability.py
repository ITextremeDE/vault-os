"""Tests for the distributable-file portability boundary."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPOSITORY_ROOT / "scripts/check_portability.py"
MATRIX_CHECKER = REPOSITORY_ROOT / "scripts/validate_portability_matrix.py"
MANIFEST_CHECKER = REPOSITORY_ROOT / "scripts/validate_manifests.py"


class PortabilityCheckTests(unittest.TestCase):
    def run_checker(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CHECKER), str(root)],
            check=False,
            capture_output=True,
            text=True,
        )

    def copy_manifest_fixture(self, root: Path) -> None:
        shutil.copytree(REPOSITORY_ROOT / "manifests", root / "manifests")
        shutil.copytree(REPOSITORY_ROOT / "src", root / "src")
        shutil.copytree(REPOSITORY_ROOT / "analysis", root / "analysis")
        shutil.copytree(REPOSITORY_ROOT / "instance-template", root / "instance-template")

    def run_manifest_checker(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(MANIFEST_CHECKER), str(root)],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_repository_distribution_is_neutral(self) -> None:
        result = self.run_checker(REPOSITORY_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_source_vault_name_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            core = root / "src/core"
            core.mkdir(parents=True)
            (core / "example.md").write_text("Hard-coded MindOS name\n", encoding="utf-8")

            result = self.run_checker(root)

        self.assertEqual(result.returncode, 1)
        self.assertIn("source vault name", result.stdout)

    def test_manifest_target_with_source_vault_name_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.copy_manifest_fixture(root)
            manifest_path = root / "manifests/core.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"][0]["target"] = "MindOS/README.md"
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            result = self.run_checker(root)

        self.assertEqual(result.returncode, 1)
        self.assertIn("source vault name", result.stdout)
        self.assertIn("manifests/core.json", result.stdout)

    def test_manifest_private_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.copy_manifest_fixture(root)
            manifest_path = root / "manifests/core.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"][0]["target"] = "/Users/jschadek/private.md"
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            result = self.run_checker(root)

        self.assertEqual(result.returncode, 1)
        self.assertIn("personal macOS path", result.stdout)

    def test_manifest_origins_remain_historical_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.copy_manifest_fixture(root)
            manifest_path = root / "manifests/core.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"][0]["origins"] = ["99 System/MindOS.md"]
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            result = self.run_checker(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_portability_matrix_is_well_formed(self) -> None:
        result = subprocess.run(
            [sys.executable, str(MATRIX_CHECKER)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_repository_manifests_are_valid(self) -> None:
        result = subprocess.run(
            [sys.executable, str(MANIFEST_CHECKER)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_german_context_action_sections_follow_convention(self) -> None:
        templates_root = REPOSITORY_ROOT / "src/modules"
        old_heading = "# 🧩 Kontext und Aktionen"
        new_heading = "# 🧩 Kontext & Aktionen"
        separator = "\n\n---\n\n"
        matching_templates = []

        for template in templates_root.glob("*/templates/de/*.md"):
            content = template.read_text(encoding="utf-8")
            self.assertNotIn(old_heading, content, str(template))
            if new_heading in content:
                matching_templates.append(template)
                for preceding_content in content.split(new_heading)[:-1]:
                    self.assertTrue(
                        preceding_content.endswith(separator), str(template)
                    )

        self.assertTrue(matching_templates, "no German context/action template found")

    def test_manifest_inventory_ignores_ds_store_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.copy_manifest_fixture(root)
            (root / "src/core/.DS_Store").write_bytes(b"finder metadata")
            (root / "instance-template/.DS_Store").write_bytes(b"finder metadata")

            result = self.run_manifest_checker(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_manifest_rejects_changed_managed_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.copy_manifest_fixture(root)
            with (root / "src/core/README.md").open("a", encoding="utf-8") as handle:
                handle.write("changed\n")

            result = self.run_manifest_checker(root)

        self.assertEqual(result.returncode, 1)
        self.assertIn("checksum mismatch", result.stdout)

    def test_manifest_rejects_parent_traversal_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.copy_manifest_fixture(root)
            manifest_path = root / "manifests/core.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"][0]["target"] = "../outside.md"
            manifest_path.write_text(
                json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
            )

            result = self.run_manifest_checker(root)

        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot traverse parents", result.stdout)

    def test_manifest_requires_fixed_runtime_lock_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.copy_manifest_fixture(root)
            manifest_path = root / "manifests/runtime.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"][0]["target"] = "User Content/release-lock.json"
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            result = self.run_manifest_checker(root)

        self.assertEqual(result.returncode, 1)
        self.assertIn(".vault-os/lock.json", result.stdout)

    def test_manifest_rejects_hidden_instance_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.copy_manifest_fixture(root)
            manifest_path = root / "manifests/instance.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"][0]["target"] = ".vault-os/config.yaml"
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            result = self.run_manifest_checker(root)

        self.assertEqual(result.returncode, 1)
        self.assertIn("visible for synchronization", result.stdout)

    def test_manifest_rejects_materialized_instance_seed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.copy_manifest_fixture(root)
            manifest_path = root / "manifests/instance.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"][0]["materialize"] = "instance"
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            result = self.run_manifest_checker(root)

        self.assertEqual(result.returncode, 1)
        self.assertIn("only managed files may be materialized", result.stdout)

    def test_manifest_rejects_english_as_a_localized_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.copy_manifest_fixture(root)
            manifest_path = root / "manifests/modules/journal.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            template = next(
                entry
                for entry in manifest["files"]
                if entry["source"] == "src/modules/journal/templates/daily-note.md"
            )
            template["localizedSources"]["en"] = template["localizedSources"]["de"]
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            result = self.run_manifest_checker(root)

        self.assertEqual(result.returncode, 1)
        self.assertIn("English must use the canonical source", result.stdout)

    def test_manifest_rejects_localized_instance_seed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.copy_manifest_fixture(root)
            manifest_path = root / "manifests/instance.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            seed = manifest["files"][0]
            seed["localizedSources"] = {
                "de": {"source": seed["source"], "sha256": seed["sha256"]}
            }
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            result = self.run_manifest_checker(root)

        self.assertEqual(result.returncode, 1)
        self.assertIn("only managed files may provide localizedSources", result.stdout)

    def test_manifest_requires_canonical_visible_instance_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.copy_manifest_fixture(root)
            manifest_path = root / "manifests/instance.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"][0]["target"] = "Instance/config.yaml"
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            result = self.run_manifest_checker(root)

        self.assertEqual(result.returncode, 1)
        self.assertIn("Vault-OS/ root", result.stdout)

    def test_manifest_requires_every_split_domain(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.copy_manifest_fixture(root)
            manifest_path = root / "manifests/instance.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            fields = next(
                entry
                for entry in manifest["files"]
                if entry["source"] == "instance-template/schema/fields.yaml"
            )
            fields.pop("origins")
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            result = self.run_manifest_checker(root)

        self.assertEqual(result.returncode, 1)
        self.assertIn("origin coverage", result.stdout)

    def test_manifest_requires_every_pure_module_origin(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.copy_manifest_fixture(root)
            manifest_path = root / "manifests/modules/review.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            workflow = next(
                entry
                for entry in manifest["files"]
                if entry["source"]
                == "src/modules/review/workflows/content-review.md"
            )
            workflow["origins"] = ["99 System/Review.base"]
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            result = self.run_manifest_checker(root)

        self.assertEqual(result.returncode, 1)
        self.assertIn("origin coverage", result.stdout)

    def test_manifest_requires_every_pure_instance_origin(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.copy_manifest_fixture(root)
            manifest_path = root / "manifests/instance.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            relationship = next(
                entry
                for entry in manifest["files"]
                if entry["source"]
                == "instance-template/modules/contacts/registers/relationships.yaml"
            )
            relationship.pop("origins")
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            result = self.run_manifest_checker(root)

        self.assertEqual(result.returncode, 1)
        self.assertIn("origin coverage", result.stdout)


if __name__ == "__main__":
    unittest.main()
