"""quilt init — scaffold a new quilt-fleet repo.

Subcommands:
    quilt init NAME [--type TYPE]      create a new quilt repo

Types:
    cell       — a single-cell repo (extends quilt-cell-harness)
    quilt      — a multi-cell community repo
    edge       — an UNO Q edge node repo
    ml         — an ML substrate zoo
    observer   — a vessel observability tap
    service    — a service that consumes/produces quilt state
    polyformal — a polyformality port of an existing concept
"""
from __future__ import annotations

import datetime
import os
import stat
import textwrap
from pathlib import Path

from quilt import QUILT_REPOS


TYPES = {
    "cell": "A single-cell repo (extends quilt-cell-harness)",
    "quilt": "A multi-cell community repo",
    "edge": "An UNO Q edge node repo",
    "ml": "An ML substrate zoo",
    "observer": "A vessel observability tap",
    "service": "A service that consumes/produces quilt state",
    "polyformal": "A polyformality port of an existing concept",
}


TEMPLATES = {
    "cell": {
        "pyproject": """\
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
version = "0.1.0"
description = "{description}"
requires-python = ">=3.9"
license = {{ text = "MIT" }}

[tool.setuptools.packages.find]
where = ["src"]
""",
        "readme": """\
# {name}

> {description}

A Quilt cell specialized for {description_lower}.

## Run

```bash
pip install -e .
python3 -m {module_name}
```

## Doctrines

This repo demonstrates the Quilt cell doctrine:
- A cell is an engine + compartments, not an LLM with stuff hung off it.
- The LLM is one substrate among many.
- Substrate agnosticism is structural, not aspirational.

## License

MIT.
""",
        "main": """\
\"\"\"{name} — {description}.\"\"\"
import sys
sys.path.insert(0, "/workspace/repos/quilt-cell-harness")
from cell import Cell


def main():
    cell = Cell(name="{name}")
    for _ in range(10):
        cell.process("hello")
    print(f"canary: {{cell.canary()[:16]}}...")
    print(f"alive:  {{bool(cell.is_alive()[0])}}")


if __name__ == "__main__":
    main()
""",
    },
    "service": {
        "pyproject": """\
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
version = "0.1.0"
description = "{description}"
requires-python = ">=3.9"
license = {{ text = "MIT" }}

[tool.setuptools.packages.find]
where = ["src"]
""",
        "readme": """\
# {name}

> {description}

A service that participates in the Quilt fleet.

## What it does

<!-- TODO -->

## Run

```bash
pip install -e .
python3 -m {module_name}
```

## License

MIT.
""",
        "main": """\
\"\"\"{name} — {description}.\"\"\"
def main():
    print("{name}: hello from a quilt service")


if __name__ == "__main__":
    main()
""",
    },
}


def register(sub):
    p = sub.add_parser("init", help="scaffold a new quilt repo")
    p.add_argument("name", help="repo name (e.g. quilt-foo)")
    p.add_argument("--type", choices=sorted(TYPES), default="cell",
                   help="what kind of repo to scaffold")
    p.add_argument("--description", default=None,
                   help="one-line description (default: 'A new Quilt {type}')")
    p.add_argument("--here", action="store_true",
                   help="create in current directory instead of $QUILT_REPOS")
    p.add_argument("--no-git", action="store_true",
                   help="skip git init + initial commit")
    p.add_argument("--github", action="store_true",
                   help="also create the GitHub repo (requires $GITHUB_TOKEN)")
    p.set_defaults(func=lambda a: init_cmd(a))


def init_cmd(args) -> int:
    name = args.name
    if not name.replace("-", "").replace("_", "").isalnum():
        raise SystemExit(f"invalid repo name: {name!r}")
    type_dir = args.type
    description = args.description or f"A new Quilt {type_dir}"
    description_lower = description.lower()

    if args.here:
        target = Path(".").resolve() / name
    else:
        target = QUILT_REPOS / name
    if target.exists():
        raise SystemExit(f"target already exists: {target}")

    template = TEMPLATES.get(args.type, TEMPLATES["cell"])
    module_name = name.replace("-", "_")

    print(f"=== scaffolding {args.type!r} repo: {name} ===")
    print(f"  target: {target}")
    print(f"  description: {description}")

    # Layout
    (target / "src" / module_name).mkdir(parents=True)
    (target / "tests").mkdir()
    (target / "examples").mkdir()
    (target / "docs").mkdir()

    # Files
    (target / "src" / module_name / "__init__.py").write_text(
        f'"""{name} — {description}."""\n__version__ = "0.1.0"\n'
    )
    (target / "src" / module_name / "__main__.py").write_text(
        template["main"].format(name=name, description=description,
                                description_lower=description_lower,
                                module_name=module_name)
    )
    (target / "tests" / "test_smoke.py").write_text(
        textwrap.dedent("""\
        import unittest
        import sys
        sys.path.insert(0, "src")
        import {module_name}


        class TestSmoke(unittest.TestCase):
            def test_version(self):
                self.assertTrue(hasattr({module_name}, "__version__"))


        if __name__ == "__main__":
            unittest.main()
        """).format(module_name=module_name)
    )
    (target / "pyproject.toml").write_text(
        template["pyproject"].format(name=name, description=description)
    )
    (target / "README.md").write_text(
        template["readme"].format(name=name, description=description,
                                  description_lower=description_lower,
                                  module_name=module_name)
    )
    (target / "LICENSE").write_text(
        "MIT License\n\nCopyright (c) {} SuperInstance / Casey\n".format(
            datetime.date.today().year)
        + "\nPermission is hereby granted, free of charge, to any person obtaining a copy\n"
        + 'of this software and associated documentation files (the "Software"), to deal\n'
        + "in the Software without restriction, including without limitation the rights\n"
        + "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n"
        + "copies of the Software, and to permit persons to whom the Software is\n"
        + "furnished to do so, subject to the following conditions:\n\n"
        + "The above copyright notice and this permission notice shall be included in all\n"
        + "copies or substantial portions of the Software.\n\n"
        + 'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n'
        + "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n"
        + "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n"
        + "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n"
        + "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n"
        + "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n"
        + "SOFTWARE.\n"
    )
    (target / ".gitignore").write_text(
        "__pycache__/\n*.pyc\n*.pyo\n.venv/\n.env\nbuild/\ndist/\n*.egg-info/\n"
    )

    print(f"  ✓ wrote {len(list(target.rglob('*')))} files")
    print()

    # git init
    if not args.no_git:
        import subprocess
        try:
            subprocess.run(["git", "init", "-q"], cwd=target, check=True)
            subprocess.run(["git", "config", "user.name", "Casey"], cwd=target, check=False)
            subprocess.run(["git", "config", "user.email", "casey@superinstance.dev"], cwd=target, check=False)
            subprocess.run(["git", "add", "-A"], cwd=target, check=True)
            subprocess.run(["git", "commit", "-q", "-m",
                            f"v0.1.0 — initial scaffold via quilt init --type {args.type}"],
                           cwd=target, check=True)
            print(f"  ✓ git init + initial commit")
        except Exception as e:
            print(f"  ⚠ git init failed: {e}")

    # GitHub
    if args.github:
        import subprocess
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            print(f"  ⚠ GITHUB_TOKEN not set; skipping GitHub repo creation")
        else:
            import urllib.request
            body = f'{{"name":"{name}","description":"{description}","private":false}}'.encode()
            req = urllib.request.Request(
                "https://api.github.com/user/repos",
                data=body, method="POST",
                headers={"Authorization": f"token {token}",
                         "Content-Type": "application/json",
                         "Accept": "application/vnd.github.v3+json"},
            )
            try:
                with urllib.request.urlopen(req, timeout=15) as r:
                    data = json.loads(r.read()) if r.status == 201 else {}
                    full_name = data.get("full_name", f"SuperInstance/{name}")
                    print(f"  ✓ created github repo {full_name}")
                # Push
                subprocess.run(
                    ["git", "remote", "add", "origin",
                     f"https://x-access-token:{token}@github.com/SuperInstance/{name}.git"],
                    cwd=target, check=True,
                )
                subprocess.run(["git", "push", "-u", "origin", "master"],
                               cwd=target, check=True)
                print(f"  ✓ pushed to github")
            except Exception as e:
                print(f"  ⚠ github publish failed: {e}")

    print()
    print(f"  next steps:")
    print(f"    cd {target}")
    print(f"    pip install -e .")
    print(f"    python3 -m {module_name}")
    return 0


# Tiny helper for the github path (init_cmd.py was importing json inline).
import json
