"""
chord.py — `quilt chord` command.

Run a 3-voice LLM chord on a question. From the mavis-flywheel pattern:
when N voices converge, the result is canonical.
"""
from __future__ import annotations

import json
import os
import urllib.request


def _zai_complete(prompt: str, *, model: str, max_tokens: int = 400) -> tuple:
    """Call Z.AI glm-4.5-flash. Returns (text, ok)."""
    api_key = os.environ.get("ZAI_TOKEN") or os.environ.get("ZAI_API_KEY")
    if not api_key:
        return ("[NO ZAI_TOKEN — faux response]", False)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "quilt-cli/0.4.0",
    }
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.5,
        "thinking": {"type": "disabled"},
    }
    try:
        req = urllib.request.Request(
            "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            headers=headers,
            data=json.dumps(body).encode(),
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
            msg = data["choices"][0]["message"]
            return (msg.get("content", "").strip(), True)
    except Exception as e:
        return (f"[ERROR: {e}]", False)


def _jaccard(a: list, b: list) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _word_set(text: str) -> list:
    return [w.lower() for w in text.split() if len(w) > 3]


def run_chord(args) -> int:
    """`quilt chord "question"` — run N voices."""
    question = args.question
    n_voices = args.voices

    print(f"=== {n_voices}-voice chord on: {question[:80]} ===\n")

    prompt = (f"Answer in 1-3 sentences, structured.\n\n"
              f"Q: {question}\n\nA:")

    voices = []
    for i in range(n_voices):
        temp = 0.3 + (i * 0.3 / max(n_voices - 1, 1))
        text, ok = _zai_complete(prompt, model="glm-4.5-flash",
                                   max_tokens=400)
        voices.append({"voice": i + 1, "temperature": round(temp, 2),
                        "ok": ok, "text": text})

    sims = []
    for i in range(n_voices):
        for j in range(i + 1, n_voices):
            sim = _jaccard(_word_set(voices[i]["text"]),
                           _word_set(voices[j]["text"]))
            sims.append(sim)
    avg_sim = sum(sims) / len(sims) if sims else 0.0

    print(f"  polyformality (avg pairwise Jaccard): {avg_sim:.3f}")
    print(f"  chord_valid: {avg_sim >= args.threshold}")
    print()

    for v in voices:
        marker = "✓" if v["ok"] else "✗"
        text_preview = v["text"][:200].replace("\n", " ")
        print(f"  voice {v['voice']} (T={v['temperature']:.2f}) [{marker}]:")
        print(f"    {text_preview}...")
        print()

    if avg_sim >= args.threshold:
        print(f"  CHORD: voices converge (>= {args.threshold:.2f})")
    else:
        print(f"  CHORD: voices diverge (< {args.threshold:.2f})")
    return 0


def register(sub):
    p = sub.add_parser("chord", help="run a multi-voice LLM chord on a question")
    p.add_argument("question", type=str, help="the question to ask the chord")
    p.add_argument("--voices", "-n", type=int, default=3,
                   help="number of voices (default 3)")
    p.add_argument("--threshold", type=float, default=0.3,
                   help="Jaccard threshold for chord validity (default 0.3)")
    p.set_defaults(func=run_chord)
