"""Tests for the quilt CLI itself."""
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from quilt.cli import build_parser, main
from quilt import __version__, fleet_repos, version_string


class TestCLI(unittest.TestCase):
    def test_build_parser(self):
        p = build_parser()
        # Make sure all top-level commands are registered.
        choices = p._subparsers._group_actions[0].choices
        for cmd in ("cell", "quilt", "qult", "fleet", "edge",
                    "canon", "init", "doctor", "version"):
            self.assertIn(cmd, choices, f"missing command: {cmd}")

    def test_help_prints(self):
        # Just ensure it doesn't crash.
        try:
            main(["--help"])
        except SystemExit:
            pass

    def test_version_short(self):
        try:
            main(["version", "--short"])
        except SystemExit:
            pass

    def test_cell_run(self):
        try:
            main(["cell", "run", "--cycles", "3", "--name", "test"])
        except SystemExit as e:
            self.fail(f"cell run failed: {e}")

    def test_cell_canary(self):
        try:
            main(["cell", "canary", "--name", "test"])
        except SystemExit as e:
            self.fail(f"cell canary failed: {e}")

    def test_edge_identity(self):
        try:
            main(["edge", "identity", "--ssid", "test-lan"])
        except SystemExit as e:
            self.fail(f"edge identity failed: {e}")

    def test_init_smoke(self, tmp=None):
        import tempfile
        import os
        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmp)
                main(["init", "quilt-test-smoke",
                      "--type", "cell",
                      "--description", "Test",
                      "--here", "--no-git"])
                target = Path(tmp) / "quilt-test-smoke"
                self.assertTrue(target.exists())
                self.assertTrue((target / "pyproject.toml").exists())
                self.assertTrue((target / "README.md").exists())
                self.assertTrue((target / "src" / "quilt_test_smoke" / "__init__.py").exists())
            except SystemExit as e:
                self.fail(f"init failed: {e}")
            finally:
                os.chdir(old_cwd)


class TestVersion(unittest.TestCase):
    def test_version_string(self):
        s = version_string()
        self.assertIn("quilt-cli", s)
        self.assertIn(__version__, s)


class TestFleetRepos(unittest.TestCase):
    def test_fleet_repos_returns_list(self):
        repos = fleet_repos()
        self.assertIsInstance(repos, list)


if __name__ == "__main__":
    unittest.main()
