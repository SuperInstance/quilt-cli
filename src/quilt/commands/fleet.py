"""quilt fleet — manage the fleet orchestrator.

Subcommands:
    quilt fleet demo                          run the canonical 4-node fleet demo
    quilt fleet list                          list currently-known nodes
    quilt fleet routes                        show recent task routes
"""
from __future__ import annotations

import sys
from pathlib import Path

from quilt import QUILT_FLEET_ORCHESTRATOR


def register(sub):
    p = sub.add_parser("fleet", help="manage the fleet orchestrator")
    sp = p.add_subparsers(dest="fleet_subcmd", metavar="<sub>")

    sp.add_parser("demo", help="run the canonical fleet demo").set_defaults(
        func=lambda a: demo_cmd(a))

    sp.add_parser("list", help="list known nodes").set_defaults(
        func=lambda a: list_cmd(a))

    sp.add_parser("routes", help="show recent task routes").set_defaults(
        func=lambda a: routes_cmd(a))


def _import_fleet_module(module: str):
    if not QUILT_FLEET_ORCHESTRATOR.exists():
        raise SystemExit(f"quilt-fleet-orchestrator not found at {QUILT_FLEET_ORCHESTRATOR}")
    p = QUILT_FLEET_ORCHESTRATOR / "src"
    sys.path.insert(0, str(p))
    return __import__(module)


def demo_cmd(args) -> int:
    """Run the canonical fleet demo by spawning it as a subprocess."""
    import subprocess
    demo_path = QUILT_FLEET_ORCHESTRATOR / "examples" / "fleet_demo.py"
    if not demo_path.exists():
        raise SystemExit(f"demo not found: {demo_path}")
    return subprocess.call([sys.executable, str(demo_path)])


def list_cmd(args) -> int:
    """List known nodes (in the registry)."""
    node_registry = _import_fleet_module("node_registry")
    reg = node_registry.NodeRegistry("/tmp/quilt-fleet-registry.jsonl")
    records = list(reg.all_records())
    if not records:
        print("no nodes registered")
        return 0
    print(f"{'node_id':20s} {'network':15s} {'last_seen':>15s} {'alive':>6s}")
    for r in records:
        age = int(r.age_s())
        print(f"{r.node_id[:18]+'…':20s} {r.network_ssid[:14]:15s} "
              f"{age:>15d} {'Y' if r.is_alive() else 'N':>6s}")
    return 0


def routes_cmd(args) -> int:
    """Show recent task routes."""
    node_registry = _import_fleet_module("node_registry")
    task_router = _import_fleet_module("task_router")
    reg = node_registry.NodeRegistry("/tmp/quilt-fleet-registry.jsonl")
    router = task_router.TaskRouter(reg)
    active = router.active()
    if not active:
        print("no active routes (the router is in-memory; run `fleet demo` first)")
        return 0
    for h in active:
        print(f"  {h.task_id[:8]}  {h.node_id[:18]}  {h.endpoint}")
    return 0
