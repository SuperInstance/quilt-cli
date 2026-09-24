"""quilt cell — manage a single Quilt cell.

Subcommands:
    quilt cell run --cycles N --name NAME        run N cycles on a cell
    quilt cell defuse --name NAME                 show the cell's assembly
    quilt cell canary --name NAME                 print the cell's canary hash
    quilt cell witness --name NAME                dump the witness chain
    quilt cell add --substrate NAME               register a new substrate
    quilt cell demo                               run the canonical demo
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from quilt import QUILT_CELL_HARNESS


def register(sub):
    p = sub.add_parser("cell", help="manage a single Quilt cell")
    sp = p.add_subparsers(dest="cell_cmd", metavar="<sub>")

    def _run(args):
        return run(args)

    def _defuse(args):
        return defuse_cmd(args)

    def _canary(args):
        return canary_cmd(args)

    def _witness(args):
        return witness_cmd(args)

    def _add(args):
        return add_substrate_cmd(args)

    def _demo(args):
        return demo_cmd(args)

    sp_run = sp.add_parser("run", help="run cycles on a cell")
    sp_run.add_argument("--name", default="alpha")
    sp_run.add_argument("--cycles", type=int, default=10)
    sp_run.add_argument("--substrates", default="echo,reverse,sha256,stub_llm",
                        help="comma-separated substrate names")
    sp_run.set_defaults(func=_run)

    sp_def = sp.add_parser("defuse", help="show the cell's assembly (defuse)")
    sp_def.add_argument("--name", default="alpha")
    sp_def.set_defaults(func=_defuse)

    sp_can = sp.add_parser("canary", help="print the cell's canary hash")
    sp_can.add_argument("--name", default="alpha")
    sp_can.set_defaults(func=_canary)

    sp_wit = sp.add_parser("witness", help="dump the witness chain")
    sp_wit.add_argument("--name", default="alpha")
    sp_wit.add_argument("--limit", type=int, default=20)
    sp_wit.set_defaults(func=_witness)

    sp_add = sp.add_parser("add", help="register a new substrate")
    sp_add.add_argument("substrate_name")
    sp_add.add_argument("--name", default="alpha")
    sp_add.set_defaults(func=_add)

    sp_demo = sp.add_parser("demo", help="run the canonical cell demo")
    sp_demo.set_defaults(func=_demo)


# === Helpers ================================================================

def _import_cell_module():
    """Import quilt-cell-harness's cell.py from its known location."""
    if not QUILT_CELL_HARNESS.exists():
        raise SystemExit(
            f"quilt-cell-harness not found at {QUILT_CELL_HARNESS}.\n"
            f"  Clone it:  git clone https://github.com/SuperInstance/quilt-cell-harness\n"
            f"  Or set $QUILT_REPOS to the directory that contains it."
        )
    sys.path.insert(0, str(QUILT_CELL_HARNESS))
    try:
        import cell as cell_mod
    except ImportError as e:
        raise SystemExit(f"failed to import cell module: {e}")
    return cell_mod


def _make_cell(name: str, substrates: str | None = None):
    cell_mod = _import_cell_module()
    cell = cell_mod.Cell(name=name)
    if substrates:
        wanted = [s.strip() for s in substrates.split(",")]
        # Filter to those that exist in the engine.
        cell.engine.substrates = {k: v for k, v in cell.engine.substrates.items()
                                  if k in wanted or k in ("stub_llm",)}
        cell.engine.calls = {s: 0 for s in cell.engine.substrates}
    return cell, cell_mod


# === Commands ===============================================================

def run(args) -> int:
    cell, cell_mod = _make_cell(args.name)
    energies = [
        "what's the weather", "echo this back", "compute sha256 of X",
        "reverse this string", "another input", "yet another",
        "the same weather", "the same echo", "the same sha",
        "new kind of input",
    ]
    import random
    for i in range(args.cycles):
        e = random.choice(energies)
        cell.process(e)
    print(f"=== {args.cycles} cycles on cell '{args.name}' ===")
    print(f"Canary:          {cell.canary()[:16]}...")
    print(f"Compartment uses: {[(c.name, c.uses) for c in cell.compartments.values()]}")
    print(f"Crystallizations: {len(cell.crystallizations)}")
    print(f"Nudges:          {len(cell.nudges.forbidden)}")
    print(f"Witnesses:       {len(cell.witness_chain.chain)}")
    alive, why = cell.is_alive()
    print(f"Alive:           {bool(alive)}")
    return 0


def defuse_cmd(args) -> int:
    cell, cell_mod = _make_cell(args.name)
    print(f"=== defuse cell '{args.name}' ===")
    print(f"Canary:  {cell.canary()[:16]}...")
    alive, _ = cell.is_alive()
    print(f"Alive:   {bool(alive)}")
    print(f"\nCompartments:")
    for c in cell.compartments.values():
        flag = " ★" if c.crystallized else ""
        print(f"  {c.name:30s} uses={c.uses}{flag}")
    print(f"\nSubstrates: {sorted(cell.engine.substrates.keys())}")
    print(f"Nudges (forbidden): {sorted(cell.nudges.forbidden)}")
    print(f"Witnesses: {len(cell.witness_chain.chain)}")
    return 0


def canary_cmd(args) -> int:
    cell, _ = _make_cell(args.name)
    print(cell.canary())
    return 0


def witness_cmd(args) -> int:
    cell, _ = _make_cell(args.name)
    for i, ev in enumerate(cell.witness_chain.chain[-args.limit:], 1):
        print(f"[{i}] {json.dumps(ev, default=str)[:100]}")
    return 0


def add_substrate_cmd(args) -> int:
    cell, _ = _make_cell(args.name)
    if args.substrate_name in cell.engine.substrates:
        print(f"substrate {args.substrate_name!r} already registered")
        return 0
    # Register a stub substrate (the cell doesn't care what it does).
    cell.engine.substrates[args.substrate_name] = lambda p: f"[{args.substrate_name}]{p}"
    cell.engine.calls[args.substrate_name] = 0
    print(f"registered substrate {args.substrate_name!r} on cell '{args.name}'")
    print(f"  substrates now: {sorted(cell.engine.substrates.keys())}")
    return 0


def demo_cmd(args) -> int:
    cell_mod = _import_cell_module()
    if hasattr(cell_mod, "demo"):
        cell_mod.demo()
    else:
        raise SystemExit("cell.py does not expose a demo() function")
    return 0
