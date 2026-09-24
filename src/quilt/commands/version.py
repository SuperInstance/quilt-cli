"""quilt version — print versions of quilt and known plugins."""
from __future__ import annotations

import sys

from quilt import __version__, fleet_repos


def register(sub):
    p = sub.add_parser("version", help="print quilt and plugin versions")
    p.add_argument("--short", action="store_true",
                   help="just print the version number")
    p.set_defaults(func=lambda a: version_cmd(a))


def version_cmd(args) -> int:
    if args.short:
        print(__version__)
        return 0
    print(f"quilt-cli: {__version__}")
    print(f"python:    {sys.version.split()[0]}")
    print()
    print("fleet repos:")
    for r in fleet_repos():
        # Look for version in pyproject.toml or __init__.py.
        v = _detect_version(r)
        print(f"  {r.name:35s} {v}")


def _detect_version(repo: Path) -> str:
    """Best-effort version detection."""
    pyproject = repo / "pyproject.toml"
    if pyproject.exists():
        for line in pyproject.read_text().splitlines():
            s = line.strip()
            if s.startswith("version") and "=" in s:
                val = s.split("=", 1)[1].strip().strip('"').strip("'")
                return val
    # Look for an __init__.py with __version__ in src/ or in the root.
    for init_path in [
        repo / "src" / repo.name.replace("-", "_") / "__init__.py",
        repo / "src" / (repo.name.split("-")[-1]) / "__init__.py",
        repo / repo.name.replace("-", "_") / "__init__.py",
    ]:
        if init_path.exists():
            for line in init_path.read_text().splitlines():
                if "__version__" in line and "=" in line:
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val
    # Look in any file under the repo for `__version__ = "X.Y.Z"`.
    for p in repo.rglob("__init__.py"):
        try:
            for line in p.read_text().splitlines():
                if "__version__" in line and "=" in line:
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val and val[0].isdigit():
                        return val
        except Exception:
            continue
    return "?"
