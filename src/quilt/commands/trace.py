"""quilt trace — render any substrate walker's receipts as HTML.

Delegates to quilt-trace. Reads a JSONL or list of receipts and produces
a self-contained HTML page with a D3.js force-directed chain graph.
"""
from __future__ import annotations
import sys
import subprocess


def register(sub):
    p = sub.add_parser("trace",
                        help="render substrate walker receipts as HTML (delegates to quilt-trace)")
    p.add_argument("source",
                    help="source file (JSONL) or '-' for stdin")
    p.add_argument("--out", default=None,
                    help="output file (default: organism.html)")
    p.add_argument("--title", default="Substrate Walker Witness Chain",
                    help="title for the rendered page")
    p.set_defaults(func=lambda a: trace_cmd(a))


def trace_cmd(args) -> int:
    """Run quilt-trace in passthrough mode."""
    cli_args = [args.source]
    if args.out:
        cli_args.extend(["--out", args.out])
    if args.title:
        cli_args.extend(["--title", args.title])

    cmd = [sys.executable, "-m", "quilt_tracer"] + cli_args
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode
