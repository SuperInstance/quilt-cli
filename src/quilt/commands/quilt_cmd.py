"""quilt quilt — manage a Quilt (multi-cell community).

Named `quilt_cmd` (not `quilt`) because `quilt` clashes with the
package name itself.

Subcommands:
    quilt quilt create --name Q --cells a,b,c    spin up a Quilt
    quilt quilt defuse --name Q                  show the quilt's assembly
    quilt quilt canary --name Q                  print the composed canary
    quilt quilt route --name Q --from a --to b   send a cross-cell ask
"""
from __future__ import annotations

import sys

from quilt import QUILT_CELL_HARNESS


def register(sub):
    p = sub.add_parser("quilt", help="manage a Quilt (multi-cell community)")
    sp = p.add_subparsers(dest="quilt_subcmd", metavar="<sub>")

    sp.add_parser("create", help="create a new quilt").set_defaults(
        func=lambda a: create_cmd(a))
    p_create = sp.choices["create"]
    p_create.add_argument("--name", required=True)
    p_create.add_argument("--cells", default="alpha,beta",
                          help="comma-separated cell names")

    sp.add_parser("defuse", help="show the quilt's assembly").set_defaults(
        func=lambda a: defuse_cmd(a))
    p_def = sp.choices["defuse"]
    p_def.add_argument("--name", required=True)

    sp.add_parser("canary", help="print the composed canary").set_defaults(
        func=lambda a: canary_cmd(a))
    p_can = sp.choices["canary"]
    p_can.add_argument("--name", required=True)

    sp.add_parser("route", help="send a cross-cell ask").set_defaults(
        func=lambda a: route_cmd(a))
    p_route = sp.choices["route"]
    p_route.add_argument("--name", required=True)
    p_route.add_argument("--from", dest="src", required=True)
    p_route.add_argument("--to", required=True)
    p_route.add_argument("--port", default="witness")
    p_route.add_argument("--payload", default="hello from quilt cli")


def _import_quilt_module():
    if not QUILT_CELL_HARNESS.exists():
        raise SystemExit(
            f"quilt-cell-harness not found at {QUILT_CELL_HARNESS}")
    sys.path.insert(0, str(QUILT_CELL_HARNESS))
    try:
        import quilt as q_mod
    except ImportError as e:
        raise SystemExit(f"failed to import quilt module: {e}")
    return q_mod


def create_cmd(args) -> int:
    q_mod = _import_quilt_module()
    cell_names = [c.strip() for c in args.cells.split(",")]
    cells = []
    for cn in cell_names:
        c = q_mod.Cell(name=cn)
        cells.append(c)
    quilt = q_mod.Quilt(cells=cells, name=args.name)
    print(f"created quilt '{args.name}' with {len(cells)} cells: {cell_names}")
    print(f"  canary: {quilt.canary()[:16]}...")
    print(f"  alive:  {bool(quilt.is_alive()[0])}")
    return 0


def defuse_cmd(args) -> int:
    q_mod = _import_quilt_module()
    # For now, rebuild from cell names is not stored. Just print the
    # structure of the module so the user can see what's there.
    print(f"=== defuse quilt '{args.name}' ===")
    print(f"(quilt.py is in {QUILT_CELL_HARNESS}/quilt.py)")
    print()
    print("Public API:")
    for name in dir(q_mod):
        if not name.startswith("_"):
            attr = getattr(q_mod, name)
            if callable(attr) and not isinstance(attr, type):
                print(f"  {name}()")
            elif isinstance(attr, type):
                print(f"  class {name}")
    return 0


def canary_cmd(args) -> int:
    q_mod = _import_quilt_module()
    # Make a fresh 2-cell quilt to demonstrate.
    cells = [q_mod.Cell(name=f"{args.name}_a"), q_mod.Cell(name=f"{args.name}_b")]
    quilt = q_mod.Quilt(cells=cells, name=args.name)
    print(quilt.canary())
    return 0


def route_cmd(args) -> int:
    q_mod = _import_quilt_module()
    cells = [q_mod.Cell(name=f"{args.src}"), q_mod.Cell(name=f"{args.to}")]
    quilt = q_mod.Quilt(name=args.name)
    quilt.add(cells[0])
    quilt.add(cells[1])
    try:
        result = quilt.ask(args.src, args.to, args.port, args.payload)
    except Exception as e:
        print(f"route failed: {e}")
        return 1
    print(f"  routed {args.src} → {args.to} via {args.port}")
    print(f"  result: {result}")
    return 0
