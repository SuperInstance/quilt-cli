"""quilt — unified CLI for the SuperInstance Quilt cellular framework.

This package provides a single `quilt` command that wraps the
disparate tools across the SuperInstance fleet:

  quilt cell ...     → cell.py (cell runtime, crystallization, defuse)
  quilt quilt ...    → quilt.py (multi-cell community)
  quilt qult ...     → qult.py (fractal composition)
  quilt fleet ...    → fleet orchestrator (registry, canary, router)
  quilt edge ...     → UNO Q edge node provisioning
  quilt canon ...    → JEV canon gate + JEV client
  quilt init ...     → scaffold a new quilt-foo repo
  quilt doctor ...   → check system state, list fleet, audit canon
  quilt version      → print versions of quilt + plugins
"""
from __future__ import annotations

__version__ = "0.3.3"


# === Fleet paths =============================================================
#
# Where the quilt CLI looks for repos. Override via env vars.

import os
from pathlib import Path

QUILT_REPOS = Path(os.environ.get("QUILT_REPOS", "/workspace/repos"))
QUILT_CELL_HARNESS = QUILT_REPOS / "quilt-cell-harness"
QUILT_EDGE_NODE = QUILT_REPOS / "quilt-edge-node"
QUILT_EDGE_ML = QUILT_REPOS / "quilt-edge-ml"
QUILT_FLEET_ORCHESTRATOR = QUILT_REPOS / "quilt-fleet-orchestrator"
QUILT_EDGE_OBSERVER = QUILT_REPOS / "quilt-edge-observer"
QUILT_JEV_TOOLKIT = QUILT_REPOS / "quilt-jev-toolkit"
QUILT_CLI = QUILT_REPOS / "quilt-cli"
QUILT_FLEET_SIM = QUILT_REPOS / "quilt-fleet-sim"
QUILT_VOICE_AGENT = QUILT_REPOS / "quilt-voice-agent"
QUILT_FULL_STACK_DEMO = QUILT_REPOS / "quilt-full-stack-demo"
QUILT_MESH_BRIDGE = QUILT_REPOS / "quilt-mesh-bridge"
QUILT_SPREADSHEET = QUILT_REPOS / "quilt-spreadsheet-inference"
QUILT_FLUIDICS = QUILT_REPOS / "quilt-fluidics"


def fleet_repos() -> list[Path]:
    """Return the list of known quilt-fleet repos that exist."""
    candidates = [
        QUILT_CELL_HARNESS,
        QUILT_EDGE_NODE,
        QUILT_EDGE_ML,
        QUILT_FLEET_ORCHESTRATOR,
        QUILT_EDGE_OBSERVER,
        QUILT_JEV_TOOLKIT,
        QUILT_CLI,
        QUILT_FLEET_SIM,
        QUILT_VOICE_AGENT,
        QUILT_FULL_STACK_DEMO,
        QUILT_MESH_BRIDGE,
        QUILT_SPREADSHEET,
        QUILT_FLUIDICS,
    ]
    return [p for p in candidates if p.exists()]


def version_string() -> str:
    """Return a one-line version banner."""
    return f"quilt-cli/{__version__} (Python)"
QUILT_MESH_BRIDGE = QUILT_REPOS / "quilt-mesh-bridge"
