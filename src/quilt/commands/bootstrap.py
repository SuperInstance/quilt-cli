"""quilt bootstrap — bring up the Quilt walker fleet in a fresh sandbox.

Delegates to quilt-bootstrap. Uses the 10 walker repos:
- quilt-seed, quilt-schema-registry, quilt-trace, quilt-organism
- quilt-optimization, quilt-director, quilt-fleet-snapshot
- quilt-brewer, quilt-perception
"""
from __future__ import annotations
import os
import subprocess
import sys


def register(sub):
    p = sub.add_parser("bootstrap",
                        help="bring up the Quilt walker fleet (delegates to quilt-bootstrap)")
    p.add_argument("--mode", choices=["minimal", "full", "demo"],
                    default="full",
                    help="which set of repos to bootstrap (default: full)")
    p.add_argument("--prefix", default="/workspace",
                    help="where to install (default: /workspace)")
    p.set_defaults(func=lambda a: bootstrap_cmd(a))


def bootstrap_cmd(args) -> int:
    """Run quilt-bootstrap in passthrough mode."""
    cli_args = ["--mode", args.mode]
    if args.prefix != "/workspace":
        cli_args.extend(["--prefix", args.prefix])

    print(f"\n🌱 quilt bootstrap — mode={args.mode} prefix={args.prefix}\n")

    # Run quilt-bootstrap if installed
    cmd = [sys.executable, "-m", "quilt_bootstrap"] + cli_args
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode
