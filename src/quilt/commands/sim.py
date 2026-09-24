"""quilt sim — manage the quilt-fleet-sim simulator.

Subcommands:
    quilt sim demo                  run the canonical 4-node sim demo
    quilt sim up --nodes N          start a sim fleet (foreground)
    quilt sim node --port P         start a single sim node
"""
from __future__ import annotations

import asyncio
import subprocess
import sys
from pathlib import Path

from quilt import QUILT_FLEET_SIM


def register(sub):
    p = sub.add_parser("sim", help="manage the quilt-fleet-sim virtual edge nodes")
    sp = p.add_subparsers(dest="sim_subcmd", metavar="<sub>")

    sp.add_parser("demo", help="run the canonical 4-node sim demo").set_defaults(
        func=lambda a: demo_cmd(a))

    p_up = sp.add_parser("up", help="start a sim fleet (foreground)")
    p_up.add_argument("--nodes", type=int, default=4)
    p_up.add_argument("--base-port", type=int, default=7701)
    p_up.add_argument("--ssid", default="sim-lan")
    p_up.add_argument("--duration", type=int, default=60,
                      help="run for N seconds then exit (0 = forever)")
    p_up.set_defaults(func=lambda a: up_cmd(a))

    p_node = sp.add_parser("node", help="start a single sim node")
    p_node.add_argument("--port", type=int, default=7701)
    p_node.add_argument("--profile", default="boat")
    p_node.add_argument("--name", default=None)
    p_node.add_argument("--ssid", default="sim-lan")
    p_node.set_defaults(func=lambda a: node_cmd(a))


def _quilt_fleet_sim_path():
    if not QUILT_FLEET_SIM.exists():
        raise SystemExit(f"quilt-fleet-sim not found at {QUILT_FLEET_SIM}")
    return QUILT_FLEET_SIM


def demo_cmd(args) -> int:
    demo = _quilt_fleet_sim_path() / "examples" / "sim_demo.py"
    if not demo.exists():
        raise SystemExit(f"demo not found: {demo}")
    return subprocess.call([sys.executable, str(demo)])


def up_cmd(args) -> int:
    code = _quilt_fleet_sim_path() / "src" / "quilt_fleet_sim" / "fleet.py"
    if not code.exists():
        raise SystemExit(f"fleet.py not found: {code}")
    cmd = [sys.executable, "-m", "quilt_fleet_sim.fleet",
           "--nodes", str(args.nodes),
           "--base-port", str(args.base_port),
           "--ssid", args.ssid,
           "--duration", str(args.duration)]
    return subprocess.call(cmd, cwd=str(_quilt_fleet_sim_path()))


def node_cmd(args) -> int:
    code = _quilt_fleet_sim_path() / "src" / "quilt_fleet_sim" / "sim_node.py"
    if not code.exists():
        raise SystemExit(f"sim_node.py not found: {code}")
    cmd = [sys.executable, str(code),
           "--port", str(args.port),
           "--profile", args.profile,
           "--ssid", args.ssid]
    if args.name:
        cmd.extend(["--name", args.name])
    return subprocess.call(cmd)
