"""quilt mesh — manage the quilt-mesh-bridge.

Subcommands:
    quilt mesh demo           run the canonical 2-node + bridge demo
    quilt mesh start --port P start a bridge in foreground
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from quilt import QUILT_MESH_BRIDGE


def register(sub):
    p = sub.add_parser("mesh", help="manage the quilt-mesh-bridge")
    sp = p.add_subparsers(dest="mesh_subcmd", metavar="<sub>")

    sp.add_parser("demo", help="run the canonical 2-node + bridge demo").set_defaults(
        func=lambda a: demo_cmd(a))

    p_start = sp.add_parser("start", help="start a bridge in foreground")
    p_start.add_argument("--name", default="bridge")
    p_start.add_argument("--port", type=int, default=7790)
    p_start.add_argument("--peer", action="append", default=[],
                         help="peer ws://host:port (repeatable)")
    p_start.set_defaults(func=lambda a: start_cmd(a))


def _mesh_path():
    if not QUILT_MESH_BRIDGE.exists():
        raise SystemExit(f"quilt-mesh-bridge not found at {QUILT_MESH_BRIDGE}")
    return QUILT_MESH_BRIDGE


def demo_cmd(args) -> int:
    demo = _mesh_path() / "examples" / "mesh_demo.py"
    if not demo.exists():
        raise SystemExit(f"demo not found: {demo}")
    return subprocess.call([sys.executable, str(demo)])


def start_cmd(args) -> int:
    code = _mesh_path() / "src" / "quilt_mesh_bridge" / "bridge.py"
    cmd = [sys.executable, "-m", "quilt_mesh_bridge.bridge",
           "--name", args.name,
           "--port", str(args.port)]
    for peer in args.peer:
        cmd.extend(["--peer", peer])
    return subprocess.call(cmd, cwd=str(_mesh_path()))
