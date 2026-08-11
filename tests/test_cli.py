"""Integration tests for manifest-driven Vault-OS lifecycle commands."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

import yaml

from vault_os.operations import Change, apply_changes


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class VaultOSCliTests(unittest.TestCase):
    def run_cli(
        self,
        package: Path,
        command: str,
        vault: Path,
        *arguments: str,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "vault_os",
                "--package-root",
                str(package),
                command,
                str(vault),
                *arguments,
                "--json",
            ],
            cwd=REPOSITORY_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

    def copy_package(self, destination: Path) -> None:
        shutil.copytree(
            REPOSITORY_ROOT,
            destination,
            ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", "*.pyc"),
        )

    def create_next_package(self, destination: Path, sources: list[str]) -> None:
        self.copy_package(destination)
        repository_path = destination / "manifests/repository.json"
        repository = json.loads(repository_path.read_text(encoding="utf-8"))
        repository["version"] = "0.1.0-dev.2"
        repository_path.write_text(
            json.dumps(repository, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        manifest_path = destination / "manifests/core.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for source in sources:
            source_path = destination / source
            with source_path.open("a", encoding="utf-8") as handle:
                handle.write("\nRelease update fixture.\n")
            entry = next(item for item in manifest["files"] if item["source"] == source)
            entry["sha256"] = hashlib.sha256(source_path.read_bytes()).hexdigest()
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def test_clean_install_uses_directory_name_and_selected_module(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            vault = Path(temporary) / "My Vault"
            result = self.run_cli(REPOSITORY_ROOT, "install", vault, "--module", "para")

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output["modules"]["to"], ["para"])
            config = yaml.safe_load(
                (vault / ".vault-os/config.yaml").read_text(encoding="utf-8")
            )
            self.assertEqual(config["vault"]["name"], "My Vault")
            self.assertEqual(config["modules"], ["para"])
            self.assertTrue(vault.joinpath("99 System/01 Schema/Models/para.json").is_file())
            self.assertFalse(
                vault.joinpath("99 System/01 Schema/Models/knowledge.json").exists()
            )
            self.assertFalse(
                vault.joinpath(
                    ".vault-os/modules/contacts/registers/relationships.yaml"
                ).exists()
            )
            self.assertFalse(vault.joinpath(".obsidian").exists())

            doctor = self.run_cli(REPOSITORY_ROOT, "doctor", vault)
            difference = self.run_cli(REPOSITORY_ROOT, "diff", vault)
            self.assertEqual(doctor.returncode, 0, doctor.stdout + doctor.stderr)
            self.assertTrue(json.loads(doctor.stdout)["healthy"])
            self.assertEqual(difference.returncode, 0, difference.stdout + difference.stderr)
            self.assertEqual(json.loads(difference.stdout)["changes"], [])

    def test_install_conflict_is_preflighted_without_partial_install(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            vault = Path(temporary) / "vault"
            collision = vault / "99 System/README.md"
            collision.parent.mkdir(parents=True)
            collision.write_text("user-owned\n", encoding="utf-8")

            result = self.run_cli(REPOSITORY_ROOT, "install", vault)

            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(collision.read_text(encoding="utf-8"), "user-owned\n")
            self.assertFalse(vault.joinpath(".vault-os/config.yaml").exists())
            self.assertFalse(vault.joinpath(".vault-os/lock.json").exists())
            self.assertFalse(vault.joinpath(".vault-os").exists())

    def test_all_module_install_passes_installed_vault_validator(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            vault = Path(temporary) / "vault"
            install = self.run_cli(
                REPOSITORY_ROOT, "install", vault, "--all-modules"
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)

            validator = vault / "99 System/05 Automation/Validators/validate_vault.py"
            result = subprocess.run(
                [sys.executable, str(validator), str(vault), "--json"],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["summary"]["errors"], 0)

    def test_update_replaces_managed_file_and_preserves_instance_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            next_package = base / "package-next"
            self.create_next_package(next_package, ["src/core/os/principles.md"])
            vault = base / "vault"
            install = self.run_cli(REPOSITORY_ROOT, "install", vault, "--module", "para")
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)

            instance_file = vault / ".vault-os/registers/areas.yaml"
            instance_file.write_text("schema: 1\nvalues: [custom]\n", encoding="utf-8")
            lock_before = (vault / ".vault-os/lock.json").read_bytes()

            difference = self.run_cli(next_package, "diff", vault)
            self.assertEqual(difference.returncode, 0, difference.stdout + difference.stderr)
            self.assertEqual(json.loads(difference.stdout)["counts"]["update"], 1)
            self.assertEqual((vault / ".vault-os/lock.json").read_bytes(), lock_before)

            update = self.run_cli(next_package, "update", vault)
            self.assertEqual(update.returncode, 0, update.stdout + update.stderr)
            self.assertIn(
                "Release update fixture.",
                vault.joinpath("99 System/00 OS/Principles.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                instance_file.read_text(encoding="utf-8"),
                "schema: 1\nvalues: [custom]\n",
            )
            lock = json.loads(
                (vault / ".vault-os/lock.json").read_text(encoding="utf-8")
            )
            self.assertEqual(lock["packageVersion"], "0.1.0-dev.2")

    def test_update_conflict_does_not_partially_apply_release(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            next_package = base / "package-next"
            self.create_next_package(
                next_package,
                ["src/core/os/principles.md", "src/core/os/architecture.md"],
            )
            vault = base / "vault"
            install = self.run_cli(REPOSITORY_ROOT, "install", vault)
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)

            principles = vault / "99 System/00 OS/Principles.md"
            architecture = vault / "99 System/00 OS/Architecture.md"
            principles.write_text("local customization\n", encoding="utf-8")
            architecture_before = architecture.read_bytes()
            lock_before = (vault / ".vault-os/lock.json").read_bytes()

            update = self.run_cli(next_package, "update", vault)

            self.assertEqual(update.returncode, 2, update.stdout + update.stderr)
            self.assertIn("changed locally", update.stderr)
            self.assertEqual(principles.read_text(encoding="utf-8"), "local customization\n")
            self.assertEqual(architecture.read_bytes(), architecture_before)
            self.assertEqual((vault / ".vault-os/lock.json").read_bytes(), lock_before)

    def test_update_applies_changed_module_selection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            vault = Path(temporary) / "vault"
            install = self.run_cli(REPOSITORY_ROOT, "install", vault, "--module", "para")
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            config_path = vault / ".vault-os/config.yaml"
            config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
            config["modules"] = ["knowledge"]
            config_path.write_text(
                yaml.safe_dump(config, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )

            update = self.run_cli(REPOSITORY_ROOT, "update", vault)

            self.assertEqual(update.returncode, 0, update.stdout + update.stderr)
            output = json.loads(update.stdout)
            self.assertGreater(output["counts"]["add"], 0)
            self.assertGreater(output["counts"]["remove"], 0)
            self.assertFalse(vault.joinpath("99 System/01 Schema/Models/para.json").exists())
            self.assertTrue(
                vault.joinpath("99 System/01 Schema/Models/knowledge.json").is_file()
            )
            self.assertTrue(vault.joinpath(".vault-os/registers/areas.yaml").is_file())

    def test_doctor_reports_local_managed_change(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            vault = Path(temporary) / "vault"
            install = self.run_cli(REPOSITORY_ROOT, "install", vault)
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            vault.joinpath("99 System/README.md").write_text(
                "local change\n", encoding="utf-8"
            )

            result = self.run_cli(REPOSITORY_ROOT, "doctor", vault)

            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertFalse(report["healthy"])
            self.assertTrue(
                any("changed locally" in error for error in report["errors"])
            )

    @unittest.skipIf(os.name == "nt", "symbolic-link behavior differs on Windows")
    def test_install_rejects_symlinked_system_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            vault = base / "vault"
            outside = base / "outside"
            vault.mkdir()
            outside.mkdir()
            (vault / "99 System").symlink_to(outside, target_is_directory=True)

            result = self.run_cli(REPOSITORY_ROOT, "install", vault)

            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertFalse(any(outside.iterdir()))

    def test_install_rejects_tampered_package(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            package = base / "package"
            self.copy_package(package)
            with package.joinpath("src/core/os/principles.md").open(
                "a", encoding="utf-8"
            ) as handle:
                handle.write("tampered\n")

            vault = base / "vault"
            result = self.run_cli(package, "install", vault)

            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("package checksum mismatch", result.stderr)
            self.assertFalse(vault.joinpath(".vault-os/lock.json").exists())

    def test_transaction_rolls_back_replaced_files_after_write_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            vault = Path(temporary) / "vault"
            vault.mkdir()
            first = vault / "system/first.md"
            second = vault / "system/second.md"
            first.parent.mkdir()
            first.write_text("first-old\n", encoding="utf-8")
            second.write_text("second-old\n", encoding="utf-8")
            real_replace = os.replace
            failed = False

            def replace_with_one_failure(source: object, target: object) -> None:
                nonlocal failed
                source_path = Path(source)
                target_path = Path(target)
                if (
                    not failed
                    and source_path.parent.name == "new"
                    and target_path == second.resolve()
                ):
                    failed = True
                    raise OSError("simulated write failure")
                real_replace(source, target)

            changes = [
                Change("write", "system/first.md", b"first-new\n", "update"),
                Change("write", "system/second.md", b"second-new\n", "update"),
            ]
            with mock.patch("vault_os.operations.os.replace", replace_with_one_failure):
                with self.assertRaises(OSError):
                    apply_changes(vault, changes)

            self.assertEqual(first.read_text(encoding="utf-8"), "first-old\n")
            self.assertEqual(second.read_text(encoding="utf-8"), "second-old\n")


if __name__ == "__main__":
    unittest.main()
