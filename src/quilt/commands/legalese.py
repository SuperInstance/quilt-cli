"""
legalese.py — `quilt legalese` command.

Digest a prompt through the legalese network (JEV claims = neurons,
MOTH carries = notarized synapses). Inspired by quilt-legalese.

`ferre` is the substrate language: every carry is booked, every claim
is typed at the membrane, every synapse is hash-chained.
"""
from __future__ import annotations

import hashlib
import json
import time


QUESTION = "QUESTION"
CLAIM = "CLAIM"
EVIDENCE = "EVIDENCE"
REFUSAL = "REFUSAL"


def _hash(parts: list) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(str(p).encode())
        h.update(b"|")
    return h.hexdigest()[:16]


def digest(prompt: str) -> dict:
    """Digest a prompt through the legalese network."""
    neurons = {
        "question": {
            "id": _hash([QUESTION, prompt]),
            "type": QUESTION,
            "payload": prompt,
            "source": "user",
            "counter": "legalese.invalid_prompt",
            "weight": 1.0,
        },
    }
    synapses = []
    last_hash = "0" * 16

    # Naive decomposition: split on sentence boundaries.
    sentences = [s.strip() for s in prompt.replace("?", ".").split(".")
                  if s.strip()]
    for i, sent in enumerate(sentences):
        claim_id = _hash([CLAIM, sent, i])
        neurons[f"claim_{i}"] = {
            "id": claim_id,
            "type": CLAIM,
            "payload": sent,
            "source": "legalese.decompose",
            "counter": f"claim.{i}.falsifiable",
            "weight": min(1.0, 0.3 + 0.1 * len(sent.split())),
        }
        canon = json.dumps({"f": neurons["question"]["id"],
                              "t": claim_id,
                              "c": claim_id,
                              "p": last_hash,
                              "ts": time.time()},
                             sort_keys=True, separators=(",", ":"))
        row_hash = hashlib.sha256(canon.encode()).hexdigest()[:16]
        synapses.append({"from": neurons["question"]["id"],
                          "to": claim_id, "claim": claim_id,
                          "row_hash": row_hash})
        last_hash = row_hash

    if prompt.strip().endswith("?"):
        refusal_id = _hash([REFUSAL, prompt, "open_question"])
        neurons["refusal_open"] = {
            "id": refusal_id,
            "type": REFUSAL,
            "payload": "open question — cannot be refuted without answer",
            "source": "legalese.refusal",
            "counter": "refusal.open",
            "weight": 0.0,
        }
        canon = json.dumps({"f": neurons["question"]["id"],
                              "t": refusal_id,
                              "c": refusal_id,
                              "p": last_hash,
                              "ts": time.time()},
                             sort_keys=True, separators=(",", ":"))
        row_hash = hashlib.sha256(canon.encode()).hexdigest()[:16]
        synapses.append({"from": neurons["question"]["id"],
                          "to": refusal_id, "claim": refusal_id,
                          "row_hash": row_hash})
        last_hash = row_hash

    return {
        "prompt": prompt,
        "n_neurons": len(neurons),
        "n_synapses": len(synapses),
        "claim_types": {t: sum(1 for c in neurons.values() if c["type"] == t)
                        for t in [QUESTION, CLAIM, EVIDENCE, REFUSAL]},
        "neurons": neurons,
        "synapses": synapses,
        "canary": last_hash,
    }


def run_legalese(args) -> int:
    """`quilt legalese "prompt"` — digest through the legalese network."""
    print(f"=== quilt legalese — ferre network ===\n")
    print(f"  prompt: {args.prompt[:80]}...\n")

    result = digest(args.prompt)

    print(f"  n_neurons:  {result['n_neurons']}")
    print(f"  n_synapses: {result['n_synapses']}")
    print(f"  claim_types: {result['claim_types']}")
    print(f"  canary: {result['canary']}")
    print()

    print(f"  === neurons ===")
    for k, v in result["neurons"].items():
        preview = str(v["payload"])[:60]
        print(f"    {k:20s}  {v['type']:10s}  w={v['weight']:.2f}  "
              f"src={v['source']}  payload: {preview!r}")
    print()

    print(f"  === synapses (first 5) ===")
    for s in result["synapses"][:5]:
        print(f"    {s['from'][:8]} → {s['to'][:8]}  "
              f"row={s['row_hash']}")

    if args.json:
        print()
        print(json.dumps(result, indent=2, default=str))
    return 0


def register(sub):
    p = sub.add_parser("legalese",
                        help="digest a prompt through the legalese network")
    p.add_argument("prompt", type=str, help="prompt to digest")
    p.add_argument("--json", action="store_true", help="output as JSON")
    p.set_defaults(func=run_legalese)
