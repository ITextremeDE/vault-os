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

from vault_os.agents import doctor_agents, initialize_agents
from vault_os.operations import Change, apply_changes
from vault_os.package import ConflictError, Package, VaultOSError
from vault_os.providers import ProviderAdapter, ProviderRegistry
from vault_os.providers.codex import _merge_qmd


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class VaultOSCliTests(unittest.TestCase):
    def run_cli(
        self,
        package: Path,
        command: str,
        vault: Path,
        *arguments: str,
        environment: dict[str, str] | None = None,
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
            env=environment,
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
        repository["version"] = "0.1.0-dev.12"
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
            self.assertEqual(output["counts"]["directory"], 5)
            config = yaml.safe_load(
                (vault / "Vault-OS/config.yaml").read_text(encoding="utf-8")
            )
            self.assertEqual(config["vault"]["name"], "My Vault")
            self.assertEqual(config["modules"], ["para"])
            self.assertTrue(vault.joinpath("99 System/01 Schema/Models/para.json").is_file())
            self.assertFalse(
                vault.joinpath("99 System/01 Schema/Models/knowledge.json").exists()
            )
            self.assertFalse(
                vault.joinpath(
                    "Vault-OS/modules/contacts/registers/relationships.yaml"
                ).exists()
            )
            self.assertTrue(vault.joinpath("Vault-OS/schema/fields.yaml").is_file())
            self.assertTrue(vault.joinpath("00 Inbox").is_dir())
            self.assertEqual(
                sorted(
                    path.relative_to(vault / ".vault-os").as_posix()
                    for path in (vault / ".vault-os").rglob("*")
                    if path.is_file()
                ),
                ["lock.json"],
            )
            self.assertFalse(vault.joinpath(".obsidian").exists())

            doctor = self.run_cli(REPOSITORY_ROOT, "doctor", vault)
            difference = self.run_cli(REPOSITORY_ROOT, "diff", vault)
            self.assertEqual(doctor.returncode, 0, doctor.stdout + doctor.stderr)
            self.assertTrue(json.loads(doctor.stdout)["healthy"])
            self.assertEqual(difference.returncode, 0, difference.stdout + difference.stderr)
            self.assertEqual(json.loads(difference.stdout)["changes"], [])

            validator = vault / "99 System/05 Automation/Validators/validate_vault.py"
            validation = subprocess.run(
                [sys.executable, str(validator), str(vault), "--json"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                validation.returncode, 0, validation.stdout + validation.stderr
            )

    def test_install_creates_configured_inbox_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            config_path = base / "config.yaml"
            config = yaml.safe_load(
                REPOSITORY_ROOT.joinpath("instance-template/vault-os.yaml").read_text(
                    encoding="utf-8"
                )
            )
            config["paths"]["inbox"] = "00 Eingang"
            config_path.write_text(
                yaml.safe_dump(config, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            vault = base / "MindOS"

            result = self.run_cli(
                REPOSITORY_ROOT, "install", vault, "--config", str(config_path)
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertTrue(vault.joinpath("00 Eingang").is_dir())
            self.assertIn(
                {
                    "action": "mkdir",
                    "category": "directory",
                    "target": "00 Eingang",
                },
                report["changes"],
            )
            lock = json.loads(
                vault.joinpath(".vault-os/lock.json").read_text(encoding="utf-8")
            )
            self.assertNotIn(
                "00 Eingang", {entry["target"] for entry in lock["managedFiles"]}
            )
            bootstrapped = self.run_cli(REPOSITORY_ROOT, "bootstrap", vault)
            self.assertEqual(
                bootstrapped.returncode,
                0,
                bootstrapped.stdout + bootstrapped.stderr,
            )
            self.assertTrue(vault.joinpath("00 Eingang/README.md").is_file())

    def test_install_rejects_file_at_configured_inbox_without_partial_install(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            vault = Path(temporary) / "vault"
            vault.mkdir()
            collision = vault / "00 Inbox"
            collision.write_text("user-owned\n", encoding="utf-8")

            result = self.run_cli(REPOSITORY_ROOT, "install", vault)

            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("target is not a directory: 00 Inbox", result.stderr)
            self.assertEqual(collision.read_text(encoding="utf-8"), "user-owned\n")
            self.assertFalse(vault.joinpath("Vault-OS/config.yaml").exists())
            self.assertFalse(vault.joinpath(".vault-os/lock.json").exists())

    def test_install_conflict_is_preflighted_without_partial_install(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            vault = Path(temporary) / "vault"
            collision = vault / "99 System/README.md"
            collision.parent.mkdir(parents=True)
            collision.write_text("user-owned\n", encoding="utf-8")

            result = self.run_cli(REPOSITORY_ROOT, "install", vault)

            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(collision.read_text(encoding="utf-8"), "user-owned\n")
            self.assertFalse(vault.joinpath("Vault-OS/config.yaml").exists())
            self.assertFalse(vault.joinpath(".vault-os/lock.json").exists())
            self.assertFalse(vault.joinpath(".vault-os").exists())

    def test_install_rejects_bootstrap_filename_reserved_for_agents(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            config_path = base / "config.yaml"
            config = yaml.safe_load(
                REPOSITORY_ROOT.joinpath("instance-template/vault-os.yaml").read_text(
                    encoding="utf-8"
                )
            )
            config["bootstrap"]["profileFile"] = "AGENTS.md"
            config_path.write_text(
                yaml.safe_dump(config, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            vault = base / "vault"

            install = self.run_cli(
                REPOSITORY_ROOT, "install", vault, "--config", str(config_path)
            )

            self.assertEqual(install.returncode, 1, install.stdout + install.stderr)
            self.assertIn("reserved for agent integration", install.stderr)
            self.assertFalse(vault.joinpath(".vault-os/lock.json").exists())

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
            for target in (
                "00 Inbox",
                "01 Projects",
                "02 Areas",
                "03 Resources",
                "04 Archive",
                "05 Journal",
                "05 Journal/Daily",
                "05 Journal/Weekly",
                "05 Journal/Yearly",
            ):
                self.assertTrue(vault.joinpath(target).is_dir(), target)

    def test_para_and_journal_bootstrap_create_configured_structure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            config_path = base / "config.yaml"
            config = yaml.safe_load(
                REPOSITORY_ROOT.joinpath("instance-template/vault-os.yaml").read_text(
                    encoding="utf-8"
                )
            )
            config["vault"] = {"name": "MindOS", "language": "de"}
            config["paths"].update(
                {
                    "inbox": "00 Eingang",
                    "projects": "01 Projekte",
                    "areas": "02 Bereiche",
                    "resources": "03 Ressourcen",
                    "archive": "04 Archiv",
                    "journal": "05 Journal",
                    "journalDaily": "05 Journal/Täglich",
                    "journalWeekly": "05 Journal/Wöchentlich",
                    "journalYearly": "05 Journal/Jährlich",
                }
            )
            config["modules"] = ["para", "journal"]
            config_path.write_text(
                yaml.safe_dump(config, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            vault = base / "MindOS"

            install = self.run_cli(
                REPOSITORY_ROOT, "install", vault, "--config", str(config_path)
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            self.assertEqual(json.loads(install.stdout)["counts"]["directory"], 9)
            bootstrapped = self.run_cli(REPOSITORY_ROOT, "bootstrap", vault)
            self.assertEqual(
                bootstrapped.returncode,
                0,
                bootstrapped.stdout + bootstrapped.stderr,
            )
            report = json.loads(bootstrapped.stdout)
            self.assertEqual(
                report["counts"], {"created": 12, "preserved": 0, "skipped": 0}
            )
            for target in (
                "00 Eingang/README.md",
                "01 Projekte/README.md",
                "02 Bereiche/README.md",
                "03 Ressourcen/README.md",
                "04 Archiv/README.md",
                "05 Journal/README.md",
                "05 Journal/Täglich/README.md",
                "05 Journal/Wöchentlich/README.md",
                "05 Journal/Jährlich/README.md",
            ):
                self.assertTrue(vault.joinpath(target).is_file(), target)
            validator = vault / "99 System/05 Automation/Validators/validate_vault.py"
            validation = subprocess.run(
                [sys.executable, str(validator), str(vault), "--json"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                validation.returncode, 0, validation.stdout + validation.stderr
            )

    def test_bootstrap_creates_configured_user_owned_start_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            vault = Path(temporary) / "vault"
            install = self.run_cli(
                REPOSITORY_ROOT,
                "install",
                vault,
                "--module",
                "para",
                "--module",
                "inbox",
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            config_path = vault / "Vault-OS/config.yaml"
            config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
            config["bootstrap"]["profileFile"] = "Ich.md"
            config_path.write_text(
                yaml.safe_dump(config, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            lock_before = vault.joinpath(".vault-os/lock.json").read_bytes()

            bootstrapped = self.run_cli(REPOSITORY_ROOT, "bootstrap", vault)

            self.assertEqual(
                bootstrapped.returncode,
                0,
                bootstrapped.stdout + bootstrapped.stderr,
            )
            report = json.loads(bootstrapped.stdout)
            self.assertEqual(report["counts"], {"created": 8, "preserved": 0, "skipped": 1})
            self.assertEqual(
                report["created"],
                [
                    "00 Inbox/README.md",
                    "01 Projects/README.md",
                    "02 Areas/README.md",
                    "03 Resources/README.md",
                    "04 Archive/README.md",
                    "Dashboard.md",
                    "Ich.md",
                    "README.md",
                ],
            )
            for target in report["created"]:
                text = vault.joinpath(target).read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\n"), target)
                metadata = yaml.safe_load(text.split("---\n", 2)[1])
                self.assertEqual(metadata["kind"], "system")
                self.assertEqual(metadata["status"], "active")
            self.assertIn(
                "[[Ich|Ich]]",
                vault.joinpath("Dashboard.md").read_text(encoding="utf-8"),
            )
            self.assertIn(
                "[[99 System/03 Workflows/Inbox|Inbox workflow]]",
                vault.joinpath("00 Inbox/README.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(vault.joinpath(".vault-os/lock.json").read_bytes(), lock_before)

            difference = self.run_cli(REPOSITORY_ROOT, "diff", vault)
            self.assertEqual(difference.returncode, 0, difference.stdout + difference.stderr)
            self.assertEqual(json.loads(difference.stdout)["changes"], [])
            validator = vault / "99 System/05 Automation/Validators/validate_vault.py"
            validation = subprocess.run(
                [sys.executable, str(validator), str(vault), "--json"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                validation.returncode, 0, validation.stdout + validation.stderr
            )

    def test_bootstrap_is_idempotent_and_preserves_existing_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            vault = Path(temporary) / "vault"
            install = self.run_cli(REPOSITORY_ROOT, "install", vault)
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            readme = vault / "README.md"
            readme.write_text("user-owned\n", encoding="utf-8")

            first = self.run_cli(REPOSITORY_ROOT, "bootstrap", vault)
            second = self.run_cli(REPOSITORY_ROOT, "bootstrap", vault)

            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            first_report = json.loads(first.stdout)
            second_report = json.loads(second.stdout)
            self.assertEqual(
                first_report["counts"],
                {"created": 3, "preserved": 1, "skipped": 2},
            )
            self.assertEqual(
                second_report["counts"],
                {"created": 0, "preserved": 4, "skipped": 2},
            )
            self.assertEqual(readme.read_text(encoding="utf-8"), "user-owned\n")
            self.assertTrue(vault.joinpath("Profile.md").is_file())
            self.assertTrue(vault.joinpath("Dashboard.md").is_file())
            self.assertTrue(vault.joinpath("00 Inbox/README.md").is_file())
            self.assertFalse(vault.joinpath("01 Projects/README.md").exists())
            self.assertFalse(vault.joinpath("02 Areas/README.md").exists())

    def test_bootstrap_conflict_does_not_create_partial_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            vault = Path(temporary) / "vault"
            install = self.run_cli(REPOSITORY_ROOT, "install", vault, "--module", "para")
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            vault.joinpath("Dashboard.md").mkdir()

            bootstrapped = self.run_cli(REPOSITORY_ROOT, "bootstrap", vault)

            self.assertEqual(
                bootstrapped.returncode,
                2,
                bootstrapped.stdout + bootstrapped.stderr,
            )
            self.assertIn("not a regular file", bootstrapped.stderr)
            self.assertFalse(vault.joinpath("Profile.md").exists())
            self.assertFalse(vault.joinpath("README.md").exists())
            self.assertFalse(vault.joinpath("00 Inbox/README.md").exists())
            self.assertFalse(vault.joinpath("01 Projects/README.md").exists())
            self.assertFalse(vault.joinpath("02 Areas/README.md").exists())

    def test_bootstrap_honors_instance_field_and_value_mappings(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            vault = Path(temporary) / "vault"
            install = self.run_cli(REPOSITORY_ROOT, "install", vault)
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            fields_path = vault / "Vault-OS/schema/fields.yaml"
            fields = yaml.safe_load(fields_path.read_text(encoding="utf-8"))
            fields["fields"] = {
                "kind": "art",
                "type": "typ",
                "status": "zustand",
                "area": "bereich",
            }
            fields["values"] = {
                "kind": {"System": "system"},
                "type": {
                    "Übersicht": "dashboard",
                    "Liesmich": "readme",
                    "Betriebsdokument": "operating-document",
                },
                "status": {"Aktiv": "active"},
            }
            fields["required"] = [
                "art",
                "typ",
                "zustand",
                "aliases",
                "tags",
                "cssclasses",
                "created",
            ]
            fields["order"] = [
                "art",
                "typ",
                "zustand",
                "bereich",
                "aliases",
                "tags",
                "cssclasses",
                "created",
            ]
            fields_path.write_text(
                yaml.safe_dump(fields, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )

            bootstrapped = self.run_cli(REPOSITORY_ROOT, "bootstrap", vault)

            self.assertEqual(
                bootstrapped.returncode,
                0,
                bootstrapped.stdout + bootstrapped.stderr,
            )
            dashboard = vault.joinpath("Dashboard.md").read_text(encoding="utf-8")
            metadata = yaml.safe_load(dashboard.split("---\n", 2)[1])
            self.assertEqual(
                (metadata["art"], metadata["typ"], metadata["zustand"]),
                ("System", "Übersicht", "Aktiv"),
            )
            validator = vault / "99 System/05 Automation/Validators/validate_vault.py"
            validation = subprocess.run(
                [sys.executable, str(validator), str(vault), "--json"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                validation.returncode, 0, validation.stdout + validation.stderr
            )

    def test_update_materializes_templates_and_review_view_for_instance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            config_path = base / "config.yaml"
            config = yaml.safe_load(
                REPOSITORY_ROOT.joinpath("instance-template/vault-os.yaml").read_text(
                    encoding="utf-8"
                )
            )
            config["vault"] = {"name": "Beispiel", "language": "de"}
            config["paths"].update(
                {
                    "projects": "01 Projekte",
                    "areas": "02 Bereiche",
                    "resources": "03 Ressourcen",
                    "contacts": "03 Ressourcen/Kontakte",
                }
            )
            config_path.write_text(
                yaml.safe_dump(config, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            vault = base / "vault"
            install = self.run_cli(
                REPOSITORY_ROOT,
                "install",
                vault,
                "--config",
                str(config_path),
                "--all-modules",
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)

            fields_path = vault / "Vault-OS/schema/fields.yaml"
            fields = yaml.safe_load(fields_path.read_text(encoding="utf-8"))
            fields["fields"] = {
                "kind": "art",
                "type": "typ",
                "status": "zustand",
                "area": "bereich",
            }
            fields["values"] = {
                "kind": {"Kontakt": "contact", "Projekt": "project", "System": "system"},
                "type": {
                    "Person": "person",
                    "Einzelkontakt": "person",
                    "Ansprechpartner": "representative",
                    "Dashboard": "dashboard",
                },
                "status": {
                    "Aktiv": "active",
                    "Offen": "open",
                    "Abgeschlossen": "completed",
                    "Archiviert": "archived",
                    "Warten auf": "waiting",
                },
            }
            fields["preferredValues"] = {
                "kind": {},
                "type": {"contact.person": "Einzelkontakt"},
                "status": {},
            }
            fields["moduleFields"] = {
                "relationship": "beziehung",
                "relevance": "relevanz",
                "last_contact": "letzter_kontakt",
                "organizations": "organisationen",
            }
            fields_path.write_text(
                yaml.safe_dump(fields, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )

            update = self.run_cli(REPOSITORY_ROOT, "update", vault)
            self.assertEqual(update.returncode, 0, update.stdout + update.stderr)

            person = vault.joinpath(
                "99 System/04 Assets/Templates/Contacts/Person.md"
            ).read_text(encoding="utf-8")
            self.assertIn('art: "Kontakt"', person)
            self.assertIn('typ: "Einzelkontakt"', person)
            self.assertIn('zustand: "Aktiv"', person)
            self.assertIn("beziehung: []", person)
            self.assertNotIn("{{fields.", person)

            organization = vault.joinpath(
                "99 System/04 Assets/Templates/Contacts/Organization.md"
            ).read_text(encoding="utf-8")
            self.assertIn('FROM "03 Ressourcen/Kontakte"', organization)
            self.assertIn('typ = "Ansprechpartner"', organization)
            self.assertIn("contains(organisationen", organization)

            dashboard = vault.joinpath(
                "99 System/04 Assets/Templates/PARA/Area Dashboard.md"
            ).read_text(encoding="utf-8")
            self.assertIn('FROM "01 Projekte" OR "02 Bereiche"', dashboard)
            self.assertIn("bereich = this.bereich", dashboard)
            self.assertNotIn("{{area}}", dashboard)

            review = vault.joinpath("99 System/Review.base").read_text(
                encoding="utf-8"
            )
            self.assertIn('art != "System"', review)
            self.assertIn("- typ", review)

            lock = json.loads(
                vault.joinpath(".vault-os/lock.json").read_text(encoding="utf-8")
            )
            hashes = {item["target"]: item["sha256"] for item in lock["managedFiles"]}
            target = "99 System/04 Assets/Templates/Contacts/Person.md"
            self.assertEqual(
                hashes[target], hashlib.sha256(vault.joinpath(target).read_bytes()).hexdigest()
            )
            difference = self.run_cli(REPOSITORY_ROOT, "diff", vault)
            self.assertEqual(difference.returncode, 0, difference.stdout + difference.stderr)
            self.assertEqual(json.loads(difference.stdout)["changes"], [])

    def test_update_replaces_managed_file_and_preserves_instance_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            next_package = base / "package-next"
            self.create_next_package(next_package, ["src/core/os/principles.md"])
            vault = base / "vault"
            install = self.run_cli(REPOSITORY_ROOT, "install", vault, "--module", "para")
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)

            instance_file = vault / "Vault-OS/registers/areas.yaml"
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
            self.assertEqual(lock["packageVersion"], "0.1.0-dev.12")

    def test_update_migrates_legacy_hidden_instance_files_without_deleting_them(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            vault = Path(temporary) / "vault"
            install = self.run_cli(REPOSITORY_ROOT, "install", vault, "--module", "para")
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)

            visible_root = vault / "Vault-OS"
            legacy_root = vault / ".vault-os"
            for source in sorted(path for path in visible_root.rglob("*") if path.is_file()):
                target = legacy_root / source.relative_to(visible_root)
                target.parent.mkdir(parents=True, exist_ok=True)
                source.replace(target)
            shutil.rmtree(visible_root)
            legacy_areas = legacy_root / "registers/areas.yaml"
            legacy_areas.write_text(
                "schema: 1\nvalues: [custom]\n", encoding="utf-8"
            )

            update = self.run_cli(REPOSITORY_ROOT, "update", vault)

            self.assertEqual(update.returncode, 0, update.stdout + update.stderr)
            self.assertEqual(
                vault.joinpath("Vault-OS/registers/areas.yaml").read_text(
                    encoding="utf-8"
                ),
                "schema: 1\nvalues: [custom]\n",
            )
            self.assertTrue(legacy_areas.is_file())
            validation = vault.joinpath("Vault-OS/validation.yaml").read_text(
                encoding="utf-8"
            )
            self.assertIn("fields: Vault-OS/schema/fields.yaml", validation)
            self.assertNotIn("fields: .vault-os/schema/fields.yaml", validation)

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
            config_path = vault / "Vault-OS/config.yaml"
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
            self.assertTrue(vault.joinpath("Vault-OS/registers/areas.yaml").is_file())

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

    def test_agent_init_registers_codex_and_claude_instructions_and_skills(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            vault = Path(temporary) / "vault"
            install = self.run_cli(
                REPOSITORY_ROOT,
                "install",
                vault,
                "--module",
                "knowledge",
                "--module",
                "search",
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            runtime_path = vault / "Vault-OS/runtime/agent-context.yaml"
            runtime = yaml.safe_load(runtime_path.read_text(encoding="utf-8"))
            runtime["readOrder"] = ["03 Resources/Start Here.md"]
            runtime_path.write_text(
                yaml.safe_dump(runtime, sort_keys=False), encoding="utf-8"
            )

            initialized = self.run_cli(REPOSITORY_ROOT, "agent-init", vault)

            self.assertEqual(
                initialized.returncode, 0, initialized.stdout + initialized.stderr
            )
            report = json.loads(initialized.stdout)
            self.assertEqual(report["providers"], ["claude", "codex"])
            self.assertEqual(report["skills"], 6)
            agents = vault.joinpath("AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("99 System/06 Runtime/Agent Context.md", agents)
            self.assertIn("Vault-OS/runtime/agent-context.yaml", agents)
            self.assertIn("03 Resources/Start Here.md", agents)
            self.assertIn(
                "Do not add, rename, move, or remove top-level vault directories",
                agents,
            )
            self.assertTrue(
                vault.joinpath("CLAUDE.md")
                .read_text(encoding="utf-8")
                .startswith("@AGENTS.md\n")
            )
            for provider_root in (".agents/skills", ".claude/skills"):
                wrapper = vault / provider_root / "vault-search/SKILL.md"
                self.assertTrue(wrapper.is_file())
                self.assertIn(
                    "99 System/04 Assets/Skills/Vault Search/SKILL.md",
                    wrapper.read_text(encoding="utf-8"),
                )

            second = self.run_cli(REPOSITORY_ROOT, "agent-init", vault)
            health = self.run_cli(REPOSITORY_ROOT, "doctor", vault, "--ai")
            validator = vault / "99 System/05 Automation/Validators/validate_vault.py"
            validation = subprocess.run(
                [sys.executable, str(validator), str(vault), "--json"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertEqual(json.loads(second.stdout)["counts"]["created"], 0)
            self.assertEqual(health.returncode, 0, health.stdout + health.stderr)
            self.assertTrue(json.loads(health.stdout)["healthy"])
            self.assertEqual(
                validation.returncode, 0, validation.stdout + validation.stderr
            )

    def test_agent_init_preserves_preexisting_agents_file_and_stops_atomically(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            vault = Path(temporary) / "vault"
            install = self.run_cli(REPOSITORY_ROOT, "install", vault)
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            agents = vault / "AGENTS.md"
            agents.write_text("user instructions\n", encoding="utf-8")
            state = vault / ".vault-os/integrations/agents.yaml"
            self.assertFalse(state.exists())

            initialized = self.run_cli(REPOSITORY_ROOT, "agent-init", vault)

            self.assertEqual(
                initialized.returncode, 2, initialized.stdout + initialized.stderr
            )
            self.assertEqual(agents.read_text(encoding="utf-8"), "user instructions\n")
            self.assertFalse(vault.joinpath("CLAUDE.md").exists())
            self.assertFalse(state.exists())

    def test_agent_init_rejects_package_metadata_update(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            next_package = base / "package-next"
            self.create_next_package(next_package, [])
            vault = base / "vault"
            install = self.run_cli(REPOSITORY_ROOT, "install", vault)
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)

            initialized = self.run_cli(next_package, "agent-init", vault)

            self.assertEqual(
                initialized.returncode, 1, initialized.stdout + initialized.stderr
            )
            self.assertIn("requires the current package", initialized.stderr)
            self.assertFalse(vault.joinpath("AGENTS.md").exists())

    def test_agent_runtime_accepts_a_provider_without_core_changes(self) -> None:
        class ExampleProviderAdapter(ProviderAdapter):
            provider_id = "example"
            display_name = "Example Agent"
            skill_root = ".example/skills"
            qmd_ignore_patterns = (".example/**",)

            def instruction_artifacts(self) -> dict[str, bytes]:
                return {"EXAMPLE.md": b"Read AGENTS.md first.\n"}

        with tempfile.TemporaryDirectory() as temporary:
            vault = Path(temporary) / "vault"
            install = self.run_cli(
                REPOSITORY_ROOT, "install", vault, "--module", "search"
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            registry = ProviderRegistry((ExampleProviderAdapter(),))

            result = initialize_agents(
                Package.load(REPOSITORY_ROOT),
                vault,
                "example",
                False,
                "qmd",
                registry,
            )
            health = doctor_agents(Package.load(REPOSITORY_ROOT), vault, registry)

            self.assertEqual(result["providers"], ["example"])
            self.assertTrue(vault.joinpath("EXAMPLE.md").is_file())
            wrapper = vault / ".example/skills/vault-search/SKILL.md"
            self.assertTrue(wrapper.is_file())
            self.assertIn(
                "99 System/04 Assets/Skills/Vault Search/SKILL.md",
                wrapper.read_text(encoding="utf-8"),
            )
            self.assertTrue(health["healthy"])
            self.assertEqual(health["details"]["skills"], {"example": 2})

    @unittest.skipIf(os.name == "nt", "test helper uses a POSIX executable")
    def test_agent_init_configures_project_local_qmd_for_both_providers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            vault = base / "vault"
            install = self.run_cli(
                REPOSITORY_ROOT, "install", vault, "--module", "search"
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            vault.joinpath(".codex").mkdir()
            vault.joinpath(".codex/config.toml").write_text(
                'model_verbosity = "low"\n', encoding="utf-8"
            )
            vault.joinpath(".mcp.json").write_text(
                json.dumps({"mcpServers": {"existing": {"command": "example"}}})
                + "\n",
                encoding="utf-8",
            )
            executable_root = base / "bin"
            executable_root.mkdir()
            qmd = executable_root / "qmd"
            qmd.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            qmd.chmod(0o755)
            environment = os.environ.copy()
            environment["PATH"] = str(executable_root) + os.pathsep + environment["PATH"]

            initial = self.run_cli(
                REPOSITORY_ROOT,
                "agent-init",
                vault,
                environment=environment,
            )
            self.assertEqual(initial.returncode, 0, initial.stdout + initial.stderr)
            agents_before_qmd = vault.joinpath("AGENTS.md").read_bytes()

            initialized = self.run_cli(
                REPOSITORY_ROOT,
                "agent-init",
                vault,
                "--qmd",
                environment=environment,
            )

            self.assertEqual(
                initialized.returncode, 0, initialized.stdout + initialized.stderr
            )
            report = json.loads(initialized.stdout)
            self.assertTrue(report["qmd"]["enabled"])
            self.assertTrue(report["qmd"]["available"])
            self.assertEqual(vault.joinpath("AGENTS.md").read_bytes(), agents_before_qmd)
            index = yaml.safe_load(vault.joinpath(".qmd/index.yml").read_text())
            self.assertEqual(
                index["collections"]["vault"]["path"], str(vault.resolve())
            )
            codex = vault.joinpath(".codex/config.toml").read_text(encoding="utf-8")
            self.assertIn('model_verbosity = "low"', codex)
            self.assertIn("[mcp_servers.qmd]", codex)
            claude = json.loads(vault.joinpath(".mcp.json").read_text(encoding="utf-8"))
            self.assertIn("existing", claude["mcpServers"])
            self.assertEqual(claude["mcpServers"]["qmd"]["args"], ["mcp"])

            qmd_next = executable_root / "qmd-next"
            qmd_next.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            qmd_next.chmod(0o755)
            refreshed = self.run_cli(
                REPOSITORY_ROOT,
                "agent-init",
                vault,
                "--qmd",
                "--qmd-command",
                "qmd-next",
                environment=environment,
            )
            self.assertEqual(refreshed.returncode, 0, refreshed.stdout + refreshed.stderr)
            self.assertIn(
                'command = "qmd-next"',
                vault.joinpath(".codex/config.toml").read_text(encoding="utf-8"),
            )
            claude = json.loads(vault.joinpath(".mcp.json").read_text(encoding="utf-8"))
            self.assertEqual(claude["mcpServers"]["qmd"]["command"], "qmd-next")

            health = self.run_cli(
                REPOSITORY_ROOT,
                "doctor",
                vault,
                "--ai",
                environment=environment,
            )
            self.assertEqual(health.returncode, 0, health.stdout + health.stderr)
            self.assertTrue(json.loads(health.stdout)["healthy"])

    def test_codex_qmd_preserves_compatible_inline_definition(self) -> None:
        existing = b'''model_verbosity = "low"

[mcp_servers]
qmd = { command = "qmd", args = ["mcp"], cwd = "..", required = false }
'''

        self.assertEqual(_merge_qmd(existing, "qmd"), existing)

    def test_codex_qmd_rejects_conflicting_inline_definition(self) -> None:
        existing = b'''[mcp_servers]
qmd = { command = "existing-qmd", args = ["mcp"] }
'''

        with self.assertRaisesRegex(ConflictError, "already defines"):
            _merge_qmd(existing, "qmd")

    def test_codex_qmd_rejects_invalid_toml(self) -> None:
        with self.assertRaisesRegex(ConflictError, "invalid TOML"):
            _merge_qmd(b"[mcp_servers\n", "qmd")

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

    def test_package_requires_fixed_runtime_lock_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary) / "package"
            self.copy_package(package)
            manifest_path = package / "manifests/runtime.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"][0]["target"] = "User Content/release-lock.json"
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(VaultOSError, ".vault-os/lock.json"):
                Package.load(package)

    def test_package_rejects_hidden_instance_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary) / "package"
            self.copy_package(package)
            manifest_path = package / "manifests/instance.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"][0]["target"] = ".vault-os/config.yaml"
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(VaultOSError, "visible for synchronization"):
                Package.load(package)

    def test_package_rejects_instance_target_outside_canonical_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary) / "package"
            self.copy_package(package)
            manifest_path = package / "manifests/instance.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"][0]["target"] = "Instance/config.yaml"
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(VaultOSError, "Vault-OS/ root"):
                Package.load(package)

    def test_device_sync_rebuilds_and_refreshes_only_local_release_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            primary = base / "primary"
            install = self.run_cli(
                REPOSITORY_ROOT, "install", primary, "--module", "para"
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)

            secondary = base / "secondary"
            shutil.copytree(
                primary,
                secondary,
                ignore=shutil.ignore_patterns(
                    ".vault-os", ".agents", ".claude", ".codex", ".qmd"
                ),
            )
            synchronized = self.run_cli(REPOSITORY_ROOT, "device-sync", secondary)

            self.assertEqual(
                synchronized.returncode,
                0,
                synchronized.stdout + synchronized.stderr,
            )
            report = json.loads(synchronized.stdout)
            self.assertEqual(report["operation"], "device-sync")
            self.assertEqual(report["counts"]["lock"], 1)
            self.assertTrue(secondary.joinpath(".vault-os/lock.json").is_file())
            health = self.run_cli(REPOSITORY_ROOT, "doctor", secondary)
            self.assertEqual(health.returncode, 0, health.stdout + health.stderr)

            old_lock = secondary.joinpath(".vault-os/lock.json").read_bytes()
            config_path = primary / "Vault-OS/config.yaml"
            config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
            config["modules"] = ["knowledge"]
            config_path.write_text(
                yaml.safe_dump(config, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            updated = self.run_cli(REPOSITORY_ROOT, "update", primary)
            self.assertEqual(updated.returncode, 0, updated.stdout + updated.stderr)

            shutil.rmtree(secondary)
            shutil.copytree(
                primary,
                secondary,
                ignore=shutil.ignore_patterns(
                    ".vault-os", ".agents", ".claude", ".codex", ".qmd"
                ),
            )
            secondary.joinpath(".vault-os").mkdir()
            secondary.joinpath(".vault-os/lock.json").write_bytes(old_lock)

            refreshed = self.run_cli(REPOSITORY_ROOT, "device-sync", secondary)

            self.assertEqual(refreshed.returncode, 0, refreshed.stdout + refreshed.stderr)
            refreshed_lock = json.loads(
                secondary.joinpath(".vault-os/lock.json").read_text(encoding="utf-8")
            )
            self.assertEqual(refreshed_lock["modules"], ["knowledge"])
            self.assertEqual(
                refreshed_lock["packageFingerprint"],
                Package.load(REPOSITORY_ROOT).fingerprint,
            )

    def test_device_sync_rejects_incomplete_or_modified_synced_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            primary = base / "primary"
            install = self.run_cli(REPOSITORY_ROOT, "install", primary)
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            secondary = base / "secondary"
            shutil.copytree(
                primary,
                secondary,
                ignore=shutil.ignore_patterns(".vault-os"),
            )
            secondary.joinpath("99 System/README.md").write_text(
                "not synchronized\n", encoding="utf-8"
            )

            synchronized = self.run_cli(REPOSITORY_ROOT, "device-sync", secondary)

            self.assertEqual(
                synchronized.returncode,
                2,
                synchronized.stdout + synchronized.stderr,
            )
            self.assertIn("does not match", synchronized.stderr)
            self.assertFalse(secondary.joinpath(".vault-os/lock.json").exists())

    def test_device_sync_recovers_invalid_local_lock_after_full_verification(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            primary = base / "primary"
            install = self.run_cli(REPOSITORY_ROOT, "install", primary)
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            secondary = base / "secondary"
            shutil.copytree(
                primary,
                secondary,
                ignore=shutil.ignore_patterns(".vault-os"),
            )
            secondary.joinpath(".vault-os").mkdir()
            secondary.joinpath(".vault-os/lock.json").write_text(
                "not json\n", encoding="utf-8"
            )
            config_before = secondary.joinpath("Vault-OS/config.yaml").read_bytes()

            synchronized = self.run_cli(REPOSITORY_ROOT, "device-sync", secondary)

            self.assertEqual(
                synchronized.returncode,
                0,
                synchronized.stdout + synchronized.stderr,
            )
            lock = json.loads(
                secondary.joinpath(".vault-os/lock.json").read_text(encoding="utf-8")
            )
            self.assertEqual(lock["packageVersion"], "0.1.0-dev.11")
            self.assertEqual(
                secondary.joinpath("Vault-OS/config.yaml").read_bytes(),
                config_before,
            )

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
                Change("mkdir", "00 Inbox", None, "directory"),
                Change("write", "system/second.md", b"second-new\n", "update"),
            ]
            with mock.patch("vault_os.operations.os.replace", replace_with_one_failure):
                with self.assertRaises(OSError):
                    apply_changes(vault, changes)

            self.assertEqual(first.read_text(encoding="utf-8"), "first-old\n")
            self.assertEqual(second.read_text(encoding="utf-8"), "second-old\n")
            self.assertFalse(vault.joinpath("00 Inbox").exists())


if __name__ == "__main__":
    unittest.main()
