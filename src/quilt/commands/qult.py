"""quilt qult — manage a Qult (fractal composition of Quilts).

Subcommands:
    quilt qult create --name Q --quilts q1,q2   spin up a Qult
    quilt qult demo                              run the canonical demo
"""
from __future__ import annotations

import sys

from quilt import QUILT_CELL_HARNESS


def register(sub):
    p = sub.add_parser("qult", help="manage a Qult (fractal composition of Quilts)")
    sp = p.add_subparsers(dest="qult_subcmd", metavar="<sub>")

    sp.add_parser("create", help="create a new qult").set_defaults(
        func=lambda a: create_cmd(a))
    p_create = sp.choices["create"]
    p_create.add_argument("--name", required=True)
    p_create.add_argument("--quilts", default="q1,q2",
                          help="comma-separated quilt names")

    sp.add_parser("demo", help="run the canonical qult demo").set_defaults(
        func=lambda a: demo_cmd(a))


def _import_qult_module():
    if not QUILT_CELL_HARNESS.exists():
        raise SystemExit(f"quilt-cell-harness not found at {QUILT_CELL_HARNESS}")
    sys.path.insert(0, str(QUILT_CELL_HARNESS))
    try:
        import qult as q_mod
    except ImportError as e:
        raise SystemExit(f"failed to import qult module: {e}")
    return q_mod


def _import_cell_module():
    if not QUILT_CELL_HARNESS.exists():
        raise SystemExit(f"quilt-cell-harness not found at {QUILT_CELL_HARNESS}")
    sys.path.insert(0, str(QUILT_CELL_HARNESS))
    import cell as cell_mod
    return cell_mod


def _import_quilt_module():
    if not QUILT_CELL_HARNESS.exists():
        raise SystemExit(f"quilt-cell-harness not found at {QUILT_CELL_HARNESS}")
    sys.path.insert(0, str(QUILT_CELL_HARNESS))
    import quilt as q_mod
    return q_mod


def create_cmd(args) -> int:
    cell_mod = _import_cell_module()
    q_mod = _import_quilt_module()
    qult_mod = _import_qult_module()

    quilt_names = [q.strip() for q in args.quilts.split(",")]
    quilts = []
    for qn in quilt_names:
        cells = [cell_mod.Cell(name=f"{qn}_a"), cell_mod.Cell(name=f"{qn}_b")]
        q = q_mod.Quilt(name=qn)
        for c in cells:
            q.add(c)
        quilts.append(q)
    qult = qult_mod.Qult(quilts=quilts, name=args.name)
    print(f"created qult '{args.name}' with {len(quilts)} quilts")
    print(f"  canary: {qult.canary()[:16]}...")
    alive, why = qult.is_alive()
    print(f"  alive:  {alive}")
    return 0


def demo_cmd(args) -> int:
    qult_mod = _import_qult_module()
    if hasattr(qult_mod, "demo"):
        qult_mod.demo()
    else:
        raise SystemExit("qult.py does not expose a demo() function")
    return 0
