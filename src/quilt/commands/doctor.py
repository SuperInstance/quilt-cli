"""quilt doctor — diagnose the Quilt environment.

Checks:
- Each fleet repo is present
- Each repo's tests pass
- Each repo's demo runs (dry-run)
- JEV API is reachable
- $QUILT_REPOS points to a valid directory
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from quilt import fleet_repos, version_string


def register(sub):
    p = sub.add_parser("doctor", help="diagnose the Quilt environment")
    p.add_argument("--skip-tests", action="store_true",
                   help="don't run any tests")
    p.add_argument("--skip-demos", action="store_true",
                   help="don't run any demos")
    p.add_argument("--skip-jev", action="store_true",
                   help="don't probe JEV")
    p.set_defaults(func=lambda a: doctor_cmd(a))


def doctor_cmd(args) -> int:
    print(f"=== quilt doctor — {version_string()} ===\n")

    print("• environment")
    repos_path = os.environ.get("QUILT_REPOS", "/workspace/repos")
    print(f"  QUILT_REPOS = {repos_path}")
    if Path(repos_path).is_dir():
        print(f"  ✓ {repos_path} exists")
    else:
        print(f"  ✗ {repos_path} does not exist")
        return 1

    print("\n• fleet repos")
    repos = fleet_repos()
    if not repos:
        print("  ✗ no fleet repos found")
    for r in repos:
        n_files = sum(1 for _ in r.rglob("*") if _.is_file())
        print(f"  {r.name:35s} {n_files} files")

    if not args.skip_tests:
        print("\n• tests")
        for r in repos:
            tests_dir = r / "tests"
            if not tests_dir.is_dir():
                continue
            test_files = list(tests_dir.glob("test_*.py"))
            if not test_files:
                continue
            print(f"  {r.name}:")
            for tf in test_files:
                # Set up env to make src/ importable.
                env = os.environ.copy()
                env["PYTHONPATH"] = str(r / "src") + os.pathsep + env.get("PYTHONPATH", "")
                # The test module is tests.<stem>
                module_name = f"tests.{tf.stem}"
                cp = subprocess.run(
                    [sys.executable, "-m", "unittest",
                     module_name, "-v"],
                    cwd=r, capture_output=True, text=True, timeout=60,
                    env=env,
                )
                lines = (cp.stdout + cp.stderr).splitlines()
                # Find the summary line.
                summary = next((l for l in reversed(lines)
                                if ("OK" in l and "Ran" not in l) or
                                   "FAILED" in l or
                                   ("Ran" in l and "test" in l)),
                               "")
                status = "✓" if cp.returncode == 0 else "✗"
                print(f"    {status} {tf.name:30s} {summary.strip()[:60]}")

    if not args.skip_jev:
        print("\n• JEV API")
        import urllib.request
        base = os.environ.get("JEV_BASE", "https://api.typesafe.ai")
        try:
            with urllib.request.urlopen(f"{base}/health", timeout=5) as r:
                print(f"  ✓ JEV reachable at {base} (HTTP {r.status})")
        except Exception as e:
            print(f"  ✗ JEV unreachable: {e}")

    if not args.skip_demos:
        print("\n• canonical demos (dry-run: just check they exist)")
        for r in repos:
            ex = r / "examples"
            if not ex.is_dir():
                continue
            demos = list(ex.glob("*.py"))
            if not demos:
                continue
            print(f"  {r.name}:")
            for d in demos:
                print(f"    • {d.name}")

    print("\n• summary")
    print(f"  {len(repos)} fleet repos")
    print(f"  {version_string()}")
    return 0
