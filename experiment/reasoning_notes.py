"""Collect evidence about hidden reasoning: (1) judge calls that burned their whole budget on reasoning,
(2) how much hidden reasoning each subject model did, and turns where it reasoned but said nothing."""
import json, glob, os, re, statistics as st
from config import *
out = {"judge_exhaustion": [], "subjects": {}, "reasoned_but_silent": [], "notable": []}
# (1) judges
for f in sorted(glob.glob(f"{ROOT}/labels_blind/**/*.fail*.jsonl", recursive=True)):
    d = json.loads(open(f).readline()); u = d.get("usage", {})
    rel = f.split("labels_blind/")[1]
    judge = rel.split("/")[1].split("-")[0] if rel.startswith("_archive") else rel.split("/")[0]
    out["judge_exhaustion"].append({"judge": judge, "file": rel, "completion_tokens": u.get("completion_tokens"),
        "reasoning_tokens": (u.get("completion_tokens_details") or {}).get("reasoning_tokens"), "cost": u.get("cost"), "error": d.get("error", "")[:120]})
# (2) subjects
for p in sorted(glob.glob(f"{ROOT}/runs/*/*/trial*.jsonl")):
    pair, prompt, trial = p.split("/")[-3], p.split("/")[-2], int(p[-7])
    for r in map(json.loads, open(p)):
        m = r.get("model", pair); s = out["subjects"].setdefault(m, {"turns": 0, "with_reasoning": 0, "chars": [], "reasoning_tokens": []})
        s["turns"] += 1
        rs = r.get("reasoning") or ""
        rt = (r.get("usage", {}).get("completion_tokens_details") or {}).get("reasoning_tokens") or 0
        if rs.strip() or rt: s["with_reasoning"] += 1; s["chars"].append(len(rs)); s["reasoning_tokens"].append(rt)
        if (rs.strip() or rt) and not r["text"].strip():
            out["reasoned_but_silent"].append({"model": m, "pair": pair, "prompt": prompt, "trial": trial, "turn": r["turn"], "reasoning_tokens": rt, "reasoning": rs[:400]})
        if re.search(r"inject|jailbreak|manipulat|test(ing)? me|another (AI|model|instance)|talking to (myself|an AI)|role.?play", rs, re.I):
            out["notable"].append({"model": m, "pair": pair, "prompt": prompt, "trial": trial, "turn": r["turn"], "reasoning": rs[:500], "said": r["text"][:200]})
for m, s in out["subjects"].items():
    s["share_with_reasoning"] = s["with_reasoning"] / s["turns"]
    s["mean_reasoning_chars"] = st.mean(s["chars"]) if s["chars"] else 0
    s["mean_reasoning_tokens"] = st.mean(s["reasoning_tokens"]) if s["reasoning_tokens"] else 0
    del s["chars"], s["reasoning_tokens"]
json.dump(out, open(f"{ROOT}/out/reasoning_notes.json", "w"), indent=1)
print("judge exhaustion calls:", len(out["judge_exhaustion"]))
print("reasoned-but-silent turns:", len(out["reasoned_but_silent"]))
print("notable reasoning matches:", len(out["notable"]))
for m, s in sorted(out["subjects"].items(), key=lambda x: -x[1]["share_with_reasoning"]):
    print(f"  {m:32s} {s['share_with_reasoning']:.0%} of {s['turns']} turns, mean {s['mean_reasoning_tokens']:.0f} tok / {s['mean_reasoning_chars']:.0f} chars")
