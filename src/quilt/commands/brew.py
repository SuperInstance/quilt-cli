"""quilt brew — grow a new substrate walker from a recipe.

Delegates to quilt-brewer. Available recipes:
- quilt-perception (sensor_stream)
- quilt-fable (narrative)
- quilt-orchestrator (dag)
- quilt-linker (graph)
"""
from __future__ import annotations
import sys
import subprocess


def register(sub):
    p = sub.add_parser("brew",
                        help="grow a new substrate walker from a recipe (delegates to quilt-brewer)")
    p.add_argument("recipe", nargs="?",
                    help="recipe name (e.g. quilt-perception)")
    p.add_argument("dest", nargs="?",
                    help="destination directory")
    p.add_argument("--list", action="store_true",
                    help="list available recipes")
    p.set_defaults(func=lambda a: brew_cmd(a))


def brew_cmd(args) -> int:
    """Run quilt-brewer in passthrough mode."""
    if args.list:
        cmd = [sys.executable, "-m", "quilt_brewer", "--list"]
    else:
        if not args.recipe or not args.dest:
            print("  Usage: quilt brew <recipe> <dest>")
            print("         quilt brew --list")
            return 1
        cmd = [sys.executable, "-m", "quilt_brewer", "brew",
                args.recipe, args.dest]

    result = subprocess.run(cmd, capture_output=False)
    return result.returncode
