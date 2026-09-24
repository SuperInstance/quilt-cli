"""Tests for quilt bootstrap/brew/trace commands."""
import os
import subprocess
import sys
import unittest


QUILT_CLI = ["python3", "-m", "quilt"]


class TestQuiltBootstrap(unittest.TestCase):
    def test_bootstrap_help(self):
        result = subprocess.run(
            QUILT_CLI + ["bootstrap", "--help"],
            capture_output=True, text=True, env={**os.environ, "PYTHONPATH": "src"},
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("minimal", result.stdout)

    def test_bootstrap_minimal_help(self):
        result = subprocess.run(
            QUILT_CLI + ["bootstrap", "--mode", "minimal", "--help"],
            capture_output=True, text=True, env={**os.environ, "PYTHONPATH": "src"},
        )
        self.assertEqual(result.returncode, 0)


class TestQuiltBrew(unittest.TestCase):
    def test_brew_help(self):
        result = subprocess.run(
            QUILT_CLI + ["brew", "--help"],
            capture_output=True, text=True, env={**os.environ, "PYTHONPATH": "src"},
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("recipe", result.stdout)

    def test_brew_requires_args(self):
        result = subprocess.run(
            QUILT_CLI + ["brew"],
            capture_output=True, text=True, env={**os.environ, "PYTHONPATH": "src"},
        )
        self.assertNotEqual(result.returncode, 0)


class TestQuiltTrace(unittest.TestCase):
    def test_trace_help(self):
        result = subprocess.run(
            QUILT_CLI + ["trace", "--help"],
            capture_output=True, text=True, env={**os.environ, "PYTHONPATH": "src"},
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("organism.html", result.stdout)


class TestCommandRegistration(unittest.TestCase):
    """The 3 new commands must be registered in the CLI."""

    def test_bootstrap_registered(self):
        result = subprocess.run(
            QUILT_CLI + ["--help"],
            capture_output=True, text=True, env={**os.environ, "PYTHONPATH": "src"},
        )
        self.assertIn("bootstrap", result.stdout)

    def test_brew_registered(self):
        result = subprocess.run(
            QUILT_CLI + ["--help"],
            capture_output=True, text=True, env={**os.environ, "PYTHONPATH": "src"},
        )
        self.assertIn("brew", result.stdout)

    def test_trace_registered(self):
        result = subprocess.run(
            QUILT_CLI + ["--help"],
            capture_output=True, text=True, env={**os.environ, "PYTHONPATH": "src"},
        )
        self.assertIn("trace", result.stdout)


if __name__ == "__main__":
    unittest.main()
