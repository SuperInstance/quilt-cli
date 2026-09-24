"""
quilt.cli — entry point for the unified `quilt` CLI.

Dispatches to per-command modules. Each command is its own file in
quilt/commands/ and exposes a `register(subparsers)` function that
adds itself to the parser tree.

Usage from the shell:
    quilt cell run --cycles 100 --name alpha
    quilt quilt create --cells alpha,beta
    quilt canon gate README.md
    quilt edge provision --ssid boat-lan
    quilt init my-new-idea

This module has no third-party dependencies — it's pure stdlib so the
CLI always works, even before pip install.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from quilt import __version__, fleet_repos, version_string


# === Command registry =======================================================

def _load_commands():
    """Lazy import of command modules to keep CLI fast at startup."""
    from quilt.commands import (
        canon, cell, doctor, edge, fleet, init_cmd, qult,
        quilt_cmd, version,
    )
    return {
        "cell":      cell,
        "quilt":     quilt_cmd,
        "qult":      qult,
        "fleet":     fleet,
        "edge":      edge,
        "canon":     canon,
        "init":      init_cmd,
        "doctor":    doctor,
        "version":   version,
    }


# === Main ====================================================================

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="quilt",
        description="Unified CLI for the SuperInstance Quilt cellular framework",
        epilog="Run `quilt <cmd> --help` for command-specific help.",
    )
    p.add_argument("--repos", type=Path, default=None,
                   help="Path to the quilt-fleet repos directory "
                        "(default: $QUILT_REPOS or /workspace/repos)")
    p.add_argument("-V", "--version-cli", action="store_true",
                   help="Print quilt-cli version and exit")
    sub = p.add_subparsers(dest="cmd", required=False, metavar="<cmd>")
    cmds = _load_commands()
    for name, mod in cmds.items():
        sub_parser = mod.register(sub)
        # Stash a reference to the top-level subparser for help printing.
        if sub_parser is not None:
            mod.parser = sub_parser
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.version_cli:
        print(version_string())
        return 0
    cmds = _load_commands()
    if args.cmd is None:
        # No subcommand: print help + a quick status.
        parser.print_help()
        print()
        _quick_status()
        return 0
    cmd_mod = cmds.get(args.cmd)
    if cmd_mod is None:
        parser.error(f"unknown command: {args.cmd}")
    func = getattr(args, "func", None)
    if func is None:
        cmd_mod.parser.print_help()
        return 1
    return func(args) or 0


def _quick_status() -> None:
    print(f"  {version_string()}")
    repos = fleet_repos()
    print(f"  fleet repos: {len(repos)}")
    for p in repos:
        n_files = sum(1 for _ in p.rglob("*") if _.is_file())
        print(f"    - {p.name:35s} {n_files} files")
    print()
    print("  commands:")
    cmds = _load_commands()
    for name, mod in cmds.items():
        if name in ("version",):
            continue
        doc = (mod.__doc__ or "").strip().splitlines()[0] if mod.__doc__ else ""
        print(f"    {name:8s} {doc}")


if __name__ == "__main__":
    sys.exit(main())
