"""
chord.py — `quilt chord` command (multi-provider).

Run a multi-voice LLM chord on a question. From the mavis-flywheel
pattern: when N voices converge, the result is canonical.

v0.5.0: voices are spread across providers (ZAI, Kimi, Gemini, Groq,
DeepSeek) so convergence means provider-independent consensus, not
just same-provider noise.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request


def _http_post(url: str, headers: dict, body: dict, *, timeout: int = 30):
    req = urllib.request.Request(
        url, headers=headers, data=json.dumps(body).encode()
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read()), None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def _zai_complete(prompt: str, *, model: str, max_tokens: int = 400) -> tuple:
    api_key = os.environ.get("ZAI_TOKEN") or os.environ.get("ZAI_API_KEY")
    if not api_key:
        return ("[NO ZAI_TOKEN — faux]", "zai", False)
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.5,
        "thinking": {"type": "disabled"},
    }
    data, err = _http_post(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        {"Authorization": f"Bearer {api_key}",
         "Content-Type": "application/json",
         "User-Agent": "quilt-cli/0.5.0"},
        body,
    )
    if err:
        return (f"[{err[:80]}]", "zai", False)
    try:
        return (data["choices"][0]["message"]["content"].strip(), "zai", True)
    except Exception:
        return ("[parse error]", "zai", False)


def _kimi_complete(prompt: str, *, model: str = "moonshot-v1-8k",
                    max_tokens: int = 400) -> tuple:
    api_key = os.environ.get("KIMI_TOKEN") or os.environ.get("MOONSHOT_API_KEY")
    if not api_key:
        return ("[NO KIMI_TOKEN — faux]", "kimi", False)
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.5,
    }
    data, err = _http_post(
        "https://api.moonshot.cn/v1/chat/completions",
        {"Authorization": f"Bearer {api_key}",
         "Content-Type": "application/json",
         "User-Agent": "quilt-cli/0.5.0"},
        body,
    )
    if err:
        return (f"[{err[:80]}]", "kimi", False)
    try:
        return (data["choices"][0]["message"]["content"].strip(), "kimi", True)
    except Exception:
        return ("[parse error]", "kimi", False)


def _gemini_complete(prompt: str, *, model: str = "gemini-2.5-flash",
                      max_tokens: int = 400) -> tuple:
    api_key = os.environ.get("GEMINI_TOKEN") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return ("[NO GEMINI_TOKEN — faux]", "gemini", False)
    body = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.5},
    }
    data, err = _http_post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
        {"Content-Type": "application/json", "User-Agent": "quilt-cli/0.5.0"},
        body,
    )
    if err:
        return (f"[{err[:80]}]", "gemini", False)
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        return (text, "gemini", True)
    except Exception:
        return ("[parse error]", "gemini", False)


def _groq_complete(prompt: str, *, model: str = "openai/gpt-oss-120b",
                    max_tokens: int = 400) -> tuple:
    api_key = os.environ.get("GROQ_TOKEN") or os.environ.get("GROQ_API_KEY")
    if not api_key:
        return ("[NO GROQ_TOKEN — faux]", "groq", False)
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.5,
    }
    data, err = _http_post(
        "https://api.groq.com/openai/v1/chat/completions",
        {"Authorization": f"Bearer {api_key}",
         "Content-Type": "application/json",
         "User-Agent": "quilt-cli/0.5.0"},
        body,
    )
    if err:
        return (f"[{err[:80]}]", "groq", False)
    try:
        return (data["choices"][0]["message"]["content"].strip(), "groq", True)
    except Exception:
        return ("[parse error]", "groq", False)


def _deepseek_complete(prompt: str, *, model: str = "deepseek-chat",
                        max_tokens: int = 400) -> tuple:
    api_key = os.environ.get("DEEPSEEK_TOKEN") or os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        return ("[NO DEEPSEEK_TOKEN — faux]", "deepseek", False)
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.5,
    }
    data, err = _http_post(
        "https://api.deepseek.com/v1/chat/completions",
        {"Authorization": f"Bearer {api_key}",
         "Content-Type": "application/json",
         "User-Agent": "quilt-cli/0.5.0"},
        body,
    )
    if err:
        return (f"[{err[:80]}]", "deepseek", False)
    try:
        return (data["choices"][0]["message"]["content"].strip(), "deepseek", True)
    except Exception:
        return ("[parse error]", "deepseek", False)


# === CHORD ORCHESTRATOR ===================================================

# The roster: which providers are available and the order they go in.
PROVIDERS = [
    ("zai", _zai_complete, "glm-4.5-flash"),
    ("gemini", _gemini_complete, "gemini-2.5-flash"),
    ("groq", _groq_complete, "openai/gpt-oss-120b"),
    ("kimi", _kimi_complete, "moonshot-v1-8k"),
    ("deepseek", _deepseek_complete, "deepseek-chat"),
]


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
    """`quilt chord "question"` — run a multi-provider LLM chord."""
    question = args.question
    n_voices = args.voices

    print(f"=== {n_voices}-voice cross-provider chord ===")
    print(f"Q: {question[:100]}")
    print()

    prompt = (f"Answer in 1-3 sentences, structured. Be concise.\n\n"
              f"Q: {question}\n\nA:")

    # Distribute voices across providers (round-robin).
    voices = []
    for i in range(n_voices):
        provider_name, fn, model = PROVIDERS[i % len(PROVIDERS)]
        t0 = time.time()
        # Some functions take model as keyword arg, others don't.
        try:
            text, actual_provider, ok = fn(prompt, model=model,
                                            max_tokens=args.max_tokens)
        except TypeError:
            text, actual_provider, ok = fn(prompt, max_tokens=args.max_tokens)
        elapsed = (time.time() - t0) * 1000
        voices.append({
            "voice": i + 1,
            "provider": actual_provider,
            "model": model,
            "elapsed_ms": round(elapsed, 1),
            "ok": ok,
            "text": text,
        })

    # Pairwise polyformality.
    sims = []
    for i in range(n_voices):
        for j in range(i + 1, n_voices):
            sim = _jaccard(_word_set(voices[i]["text"]),
                           _word_set(voices[j]["text"]))
            sims.append(sim)
    avg_sim = sum(sims) / len(sims) if sims else 0.0

    # Convergence across providers only.
    providers_used = set(v["provider"] for v in voices)
    cross_provider_sims = []
    for i in range(n_voices):
        for j in range(i + 1, n_voices):
            if voices[i]["provider"] != voices[j]["provider"]:
                sim = _jaccard(_word_set(voices[i]["text"]),
                               _word_set(voices[j]["text"]))
                cross_provider_sims.append(sim)
    avg_cross_sim = (sum(cross_provider_sims) / len(cross_provider_sims)
                      if cross_provider_sims else avg_sim)

    print(f"  providers active: {sorted(providers_used)}")
    print(f"  polyformality (all voices):    {avg_sim:.3f}")
    print(f"  polyformality (cross-provider): {avg_cross_sim:.3f}")
    print(f"  chord_valid (>= {args.threshold}): {avg_cross_sim >= args.threshold}")
    print()

    for v in voices:
        marker = "✓" if v["ok"] else "✗"
        text_preview = v["text"][:200].replace("\n", " ")
        print(f"  voice {v['voice']} [{v['provider']:8s}/{v['model']:30s}] "
              f"({v['elapsed_ms']:5.0f}ms) [{marker}]:")
        print(f"    {text_preview}...")
        print()

    if avg_cross_sim >= args.threshold:
        print(f"  CHORD: voices converge across providers (>= {args.threshold:.2f}). "
              "Result is canon.")
    else:
        print(f"  CHORD: voices diverge across providers (< {args.threshold:.2f}). "
              "Result is speculative.")
    return 0


def register(sub):
    p = sub.add_parser("chord",
                       help="run a multi-voice cross-provider LLM chord on a question")
    p.add_argument("question", type=str, help="the question to ask the chord")
    p.add_argument("--voices", "-n", type=int, default=5,
                   help="number of voices (default 5)")
    p.add_argument("--threshold", type=float, default=0.3,
                   help="Jaccard threshold for chord validity (default 0.3)")
    p.add_argument("--max-tokens", type=int, default=400,
                   help="max tokens per voice (default 400)")
    p.set_defaults(func=run_chord)
