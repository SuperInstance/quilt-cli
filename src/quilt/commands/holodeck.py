"""
holodeck.py — `quilt holodeck` command.

Run a scenario through the Holodeck: Jepa (geometry) → JEV (truth) →
MOTH (physics) → LLM (language). Each layer has its own Reynolds-as-
knob regime.

The Holodeck composes the lower-layer artifacts into a layered canon
artifact, with witness chain.
"""
from __future__ import annotations

import json
import os
import sys
import time

# Try to import the holodeck module from quilt-spreadsheet-inference.
try:
    sys.path.insert(0, os.path.expanduser(
        "~/repos/quilt-spreadsheet-inference/src"))
    sys.path.insert(0, "/workspace/repos/quilt-spreadsheet-inference/src")
    from quilt_spreadsheet.holodeck import (
        Holodeck, HolodeckRegime, LayerRegime,
    )
    HAS_HOLODECK = True
except Exception as e:
    HAS_HOLODECK = False
    _HOLODECK_IMPORT_ERROR = str(e)


def run_holodeck(args) -> int:
    """`quilt holodeck "scenario"` — run a scenario through the Holodeck."""
    if not HAS_HOLODECK:
        print(f"!! could not import Holodeck: {_HOLODECK_IMPORT_ERROR}")
        return 1

    scenario = args.scenario

    print(f"=== HOLODECK ===")
    print(f"scenario: {scenario}")
    print()

    # Build the regime from args.
    h = Holodeck()
    if args.laminar:
        # All layers laminar (memory holds).
        h.dial("jepa", momentum=0.1, diffusion=1.0)
        h.dial("jev",  momentum=0.1, diffusion=1.0)
        h.dial("moth", momentum=0.1, diffusion=1.0)
        h.dial("llm",  momentum=0.1, diffusion=1.0)
    elif args.turbulent:
        # All layers turbulent (exploration).
        h.dial("jepa", momentum=10.0, diffusion=1.0)
        h.dial("jev",  momentum=10.0, diffusion=1.0)
        h.dial("moth", momentum=10.0, diffusion=1.0)
        h.dial("llm",  momentum=10.0, diffusion=1.0)
    elif args.mixed:
        # Custom mixed: jepa/jev laminar, moth critical, llm turbulent.
        h.dial("jepa", momentum=0.1, diffusion=1.0)
        h.dial("jev",  momentum=0.1, diffusion=1.0)
        h.dial("moth", momentum=1.0, diffusion=1.0)
        h.dial("llm",  momentum=10.0, diffusion=1.0)

    summary = h.regime.summary()
    print("Reynolds regimes (per layer):")
    for layer, info in summary.items():
        print(f"  {layer:7s}: Re={info['re']:.2f}  regime={info['regime']}")
    print()

    # Run the scenario.
    t0 = time.time()
    composed = h.run(scenario)
    elapsed_ms = (time.time() - t0) * 1000

    # Pretty-print.
    print(f"--- LAYER 1: JEPA (geometry) — regime={summary['jepa']['regime']} ---")
    emb = composed["layers"]["jepa"]["embedding"]
    print(f"  embedding: {dict(list(emb.items())[:4])}...")
    print(f"  interpretation: {composed['layers']['jepa']['interpretation']}")
    print()

    print(f"--- LAYER 2: JEV (truth) — regime={summary['jev']['regime']} ---")
    total = composed['layers']['jev'].get('canon_alignment_total', 10)
    print(f"  canon_alignment: {composed['layers']['jev']['canon_alignment']}/{total}")
    print(f"  fingerprint: {composed['layers']['jev']['fingerprint']}")
    print(f"  interpretation: {composed['layers']['jev']['interpretation']}")
    print()

    print(f"--- LAYER 3: MOTH (physics) — regime={summary['moth']['regime']} ---")
    print(f"  mass: {composed['layers']['moth']['mass']:.3f}")
    print(f"  energy: {composed['layers']['moth']['energy']:.3f}")
    print(f"  constraints: {composed['layers']['moth']['applicable_constraints']}")
    print(f"  interpretation: {composed['layers']['moth']['interpretation']}")
    print()

    print(f"--- LAYER 4: LLM (language) — regime={summary['llm']['regime']} ---")
    print(f"  {composed['layers']['llm']['narrative']}")
    print()

    print(f"--- COMPOSED ---")
    print(f"  canary: {composed['canary']}")
    print(f"  witness chain length: {composed['witness_chain_length']}")
    print(f"  total elapsed: {elapsed_ms:.0f}ms")
    print()
    print("The Holodeck composed the scenario through four lenses.")
    print("Each lens is dialable via Reynolds. The canary is the witness chain.")

    return 0


def register(sub):
    p = sub.add_parser("holodeck",
                       help="run a scenario through the Holodeck "
                            "(Jepa → JEV → MOTH → LLM with per-layer Reynolds)")
    p.add_argument("scenario", type=str,
                    help="the scenario to compose through the Holodeck")
    p.add_argument("--laminar", action="store_true",
                    help="all layers laminar (memory holds)")
    p.add_argument("--critical", action="store_true",
                    help="all layers critical (default)")
    p.add_argument("--turbulent", action="store_true",
                    help="all layers turbulent (exploration)")
    p.add_argument("--mixed", action="store_true",
                    help="mixed: jepa/jev laminar, moth critical, llm turbulent")
    p.set_defaults(func=run_holodeck)
