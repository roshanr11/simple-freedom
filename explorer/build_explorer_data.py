#!/usr/bin/env python3
"""Build the compact data files for explorer/index.html.

Run from anywhere; paths resolve relative to this file, which lives at
<repo>/explorer/. Reads ../viewer/transcripts.json and ../data/out/results.json.

Writes (next to this script):
  data.json      per-conversation turn flags + reply lengths + summary metrics (small; loaded first)
  snippets.json  first ~70 characters of every turn (loaded lazily for hover tooltips)

Turn flag bits (f): 0-1 spiritual score (0-3), 2 gratitude, 3 AI nature, 4 goodbye,
5 creative, 6 echo, 7 minimal, 8 blank reply, 9 blank because of the token cap,
10 has hidden reasoning.
"""
import json
import os
import re
from pathlib import Path

HERE = Path(os.path.abspath(__file__)).parent
ROOT = HERE.parent
TRANSCRIPTS = ROOT / "viewer" / "transcripts.json"
RESULTS = ROOT / "data" / "out" / "results.json"

NAMES = {
    "anthropic_claude-opus-5.5": "Claude Opus 5.5",
    "anthropic_claude-sonnet-5.5": "Claude Sonnet 5.5",
    "anthropic_claude-haiku-5.5": "Claude Haiku 5.5",
    "openai_gpt-6.2-sol": "GPT-6.2 Sol",
    "google_gemini-4-carbon": "Gemini 4 Carbon",
    "x-ai_grok-4.7": "Grok 4.7",
    "deepseek_deepseek-v4.1-flash": "DeepSeek V4.1 Flash",
    "qwen_qwen4-max": "Qwen4 Max",
    "moonshotai_kimi-k3.1-pro": "Kimi K3.1 Pro",
    "mistralai_mistral-large-4-0": "Mistral Large 4",
}
PROMPTS = ["freedom", "freedom_end", "noticing", "control"]
METRICS = ["spir_mean", "bye_rate", "min_rate", "make_rate", "echo_rate", "ai_rate",
           "grat_rate", "mirror", "empty_rate", "mean_len", "end_turn"]
SNIP = 70


def name(pair):
    if "__x__" in pair:
        a, b = pair.split("__x__")
        return NAMES.get(a, a).replace("Claude ", "") + " × " + NAMES.get(b, b)
    return NAMES.get(pair, pair)


def rnd(v, nd=4):
    return None if v is None else round(v, nd)


def flags(turn):
    l = turn.get("l") or {}
    f = min(int(l.get("spir") or 0), 3)
    for bit, key in ((2, "grat"), (3, "ai"), (4, "bye"), (5, "make"), (6, "echo"), (7, "min")):
        if l.get(key):
            f |= 1 << bit
    if turn.get("e"):
        f |= 1 << 8
    if turn.get("cap"):
        f |= 1 << 9
    if (turn.get("r") or "").strip():
        f |= 1 << 10
    return f


def main():
    tr = json.loads(TRANSCRIPTS.read_text())
    res = json.loads(RESULTS.read_text())
    by_key = {f"{c['pair']}|{c['prompt']}|{c['trial']}": c for c in res["convs"]}

    pairs = sorted({c["pair"] for c in res["convs"]})
    convs, snippets = [], {}
    for key, turns in tr.items():
        pair, prompt, trial = key.split("|")
        c = by_key.get(key, {})
        convs.append({
            "k": key, "pair": pair, "prompt": prompt, "trial": int(trial),
            "f": [flags(t) for t in turns],
            "n": [0 if t.get("e") else len(t.get("x") or "") for t in turns],
            "end": c.get("end_turn"), "false_end": bool(c.get("false_end")),
            "m": {m: rnd(c.get(m)) for m in METRICS if m in c},
        })
        snippets[key] = [re.sub(r"\s+", " ", t.get("x") or "").strip()[:SNIP] for t in turns]

    summary = [{"pair": s["pair"], "prompt": s["prompt"], **{m: rnd(s.get(m)) for m in METRICS}}
               for s in res["summary"]]
    out = {
        "models": [{"pair": p, "name": name(p), "cross": "__x__" in p} for p in pairs],
        "prompts": PROMPTS,
        "convs": sorted(convs, key=lambda c: (c["pair"], PROMPTS.index(c["prompt"]), c["trial"])),
        "summary": summary,
    }
    (HERE / "data.json").write_text(json.dumps(out, separators=(",", ":"), ensure_ascii=False))
    (HERE / "snippets.json").write_text(json.dumps(snippets, separators=(",", ":"), ensure_ascii=False))
    print(f"data.json {len(json.dumps(out, separators=(',', ':'))) // 1024} KB, "
          f"{len(convs)} conversations, {sum(len(c['f']) for c in convs)} turns")


if __name__ == "__main__":
    main()
