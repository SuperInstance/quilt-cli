"""quilt canon — JEV canon gate + JEV client.

Subcommands:
    quilt canon gate FILE                gate a single file
    quilt canon batch DIR --threshold T gate all files in DIR
    quilt canon ask --state "..."        ask one question
    quilt canon health                   check JEV API health
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

from quilt import QUILT_JEV_TOOLKIT


def register(sub):
    p = sub.add_parser("canon", help="canon gate + JEV client")
    sp = p.add_subparsers(dest="canon_subcmd", metavar="<sub>")

    p_gate = sp.add_parser("gate", help="canon-gate a single file")
    p_gate.add_argument("path", help="file to gate (markdown, code, etc.)")
    p_gate.add_argument("--json", action="store_true",
                        help="emit raw JSON output")
    p_gate.set_defaults(func=lambda a: gate_cmd(a))

    p_batch = sp.add_parser("batch", help="batch-gate all files in a directory")
    p_batch.add_argument("path", help="directory of files")
    p_batch.add_argument("--threshold", type=float, default=0.5)
    p_batch.add_argument("--limit", type=int, default=20)
    p_batch.set_defaults(func=lambda a: batch_cmd(a))

    p_ask = sp.add_parser("ask", help="ask JEV one custom question")
    p_ask.add_argument("--state", required=True,
                       help="text state to evaluate (truncate to 4000 chars)")
    p_ask.add_argument("--question", required=True,
                       help="yes/no question")
    p_ask.set_defaults(func=lambda a: ask_cmd(a))

    p_health = sp.add_parser("health", help="check JEV API health")
    p_health.set_defaults(func=lambda a: health_cmd(a))


def _import_jev_client():
    """Try the JEV toolkit's client; fall back to a minimal one."""
    if QUILT_JEV_TOOLKIT.exists():
        sys.path.insert(0, str(QUILT_JEV_TOOLKIT))
        try:
            from jev_client import JevClient   # type: ignore
            return JevClient
        except ImportError:
            pass
    return _MinimalJevClient


class _MinimalJevClient:
    def __init__(self):
        self.base = os.environ.get("JEV_BASE", "https://api.typesafe.ai")
        self.key = os.environ.get("TYPESAFEAI_KEY", "")

    def ask(self, state: str, questions: dict) -> dict:
        url = f"{self.base}/v1/systemone"
        body = json.dumps({
            "state": state[:4000],
            "model": "jev-latest",
            "questions": questions,
        }).encode()
        req = urllib.request.Request(
            url, data=body, method="POST",
            headers={
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.reason}"}
        except urllib.error.URLError as e:
            return {"error": str(e)}

    def gate(self, text: str) -> dict:
        """Run the standard canon-gate questions on a piece of text."""
        return self.ask(text[:4000], {
            "is_canon": {
                "type": "noul",
                "instructions": "Is this content canon (foundational, durable, doctrine-level)?",
                "criteria": {"true": "canon, durable doctrine", "false": "draft or speculative"},
            },
            "is_doctrine": {
                "type": "noul",
                "instructions": "Does this articulate a clear doctrinal claim?",
                "criteria": {"true": "yes, this is a doctrine", "false": "no, this is not a doctrine"},
            },
            "domain": {
                "type": "choice",
                "instructions": "Which domain is this content in?",
                "criteria": {
                    "cs": "computer science",
                    "ml": "machine learning",
                    "art": "creative",
                    "ops": "operations",
                    "other": "other",
                },
            },
            "depth": {
                "type": "score",
                "instructions": "How mature is this content?",
                "criteria": ["draft", "iterative", "established", "canon"],
            },
        })


def gate_cmd(args) -> int:
    text = open(args.path, encoding="utf-8").read()
    Client = _import_jev_client()
    cli = Client()
    result = cli.gate(text)
    if args.json:
        print(json.dumps(result, indent=2))
        return 0
    if "error" in result:
        print(f"error: {result['error']}")
        return 1
    answers = result.get("answers", {})
    canon_p = answers.get("is_canon", {}).get("noul", 0)
    doctrine_p = answers.get("is_doctrine", {}).get("noul", 0)
    domain = answers.get("domain", {}).get("choice", "?")
    domain_conf = answers.get("domain", {}).get("confidence", 0)
    depth_score = answers.get("depth", {}).get("score", "?")
    print(f"file:    {args.path}")
    print(f"length:  {len(text)} chars")
    print(f"canon_p: {canon_p:.2f}")
    print(f"doctrine: {doctrine_p:.2f}")
    print(f"domain:  {domain} (conf={domain_conf:.2f})")
    print(f"depth:   {depth_score}")
    if canon_p >= 0.7:
        print(f"\n  ★ canon")
    elif canon_p >= 0.4:
        print(f"\n  ~ partial canon")
    else:
        print(f"\n  · draft / speculative")
    return 0


def batch_cmd(args) -> int:
    from pathlib import Path
    Client = _import_jev_client()
    cli = Client()
    root = Path(args.path)
    files = sorted([f for f in root.rglob("*") if f.is_file() and f.suffix in {".md", ".py", ".txt"}])
    files = files[:args.limit]
    print(f"=== gating {len(files)} files in {root} (threshold {args.threshold}) ===\n")
    for f in files:
        text = open(f, encoding="utf-8").read()
        result = cli.gate(text)
        if "error" in result:
            print(f"  ERROR  {f.name}")
            continue
        prob = result.get("answers", {}).get("is_canon", {}).get("noul", 0)
        marker = "★" if prob >= args.threshold else " "
        print(f"  {marker} p={prob:.2f}  {f}")
    return 0


def ask_cmd(args) -> int:
    Client = _import_jev_client()
    cli = Client()
    result = cli.ask(args.state, {"answer": {"type": "noul", "question": args.question}})
    print(json.dumps(result, indent=2))
    return 0


def health_cmd(args) -> int:
    base = os.environ.get("JEV_BASE", "https://api.typesafe.ai")
    try:
        with urllib.request.urlopen(f"{base}/health", timeout=5) as r:
            print(f"JEV /health: HTTP {r.status}")
            print(r.read().decode())
    except Exception as e:
        print(f"JEV /health: ERROR {e}")
        return 1
    return 0
