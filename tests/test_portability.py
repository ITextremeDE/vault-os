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


if __name__ == "__main__":
    unittest.main()
