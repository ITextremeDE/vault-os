"""Tests for the distributable-file portability boundary."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPOSITORY_ROOT / "scripts/check_portability.py"


class PortabilityCheckTests(unittest.TestCase):
    def run_checker(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CHECKER), str(root)],
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


if __name__ == "__main__":
    unittest.main()
