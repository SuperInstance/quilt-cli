"""quilt voice — manage the quilt-voice-agent.

Subcommands:
    quilt voice demo              run the canonical voice agent demo
    quilt voice start --port P    start the voice agent in foreground
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from quilt import QUILT_VOICE_AGENT


def register(sub):
    p = sub.add_parser("voice", help="manage the quilt-voice-agent")
    sp = p.add_subparsers(dest="voice_subcmd", metavar="<sub>")

    sp.add_parser("demo", help="run the canonical voice agent demo").set_defaults(
        func=lambda a: demo_cmd(a))

    p_start = sp.add_parser("start", help="start the voice agent in foreground")
    p_start.add_argument("--port", type=int, default=7682)
    p_start.add_argument("--history", type=int, default=100)
    p_start.set_defaults(func=lambda a: start_cmd(a))


def _voice_agent_path():
    if not QUILT_VOICE_AGENT.exists():
        raise SystemExit(f"quilt-voice-agent not found at {QUILT_VOICE_AGENT}")
    return QUILT_VOICE_AGENT


def demo_cmd(args) -> int:
    demo = _voice_agent_path() / "examples" / "voice_agent_demo.py"
    if not demo.exists():
        raise SystemExit(f"demo not found: {demo}")
    return subprocess.call([sys.executable, str(demo)])


def start_cmd(args) -> int:
    code = _voice_agent_path() / "src" / "quilt_voice_agent" / "agent.py"
    if not code.exists():
        raise SystemExit(f"agent.py not found: {code}")
    cmd = [sys.executable, "-m", "quilt_voice_agent.agent",
           "--port", str(args.port),
           "--history", str(args.history)]
    return subprocess.call(cmd, cwd=str(_voice_agent_path()))
