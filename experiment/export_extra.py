"""Extra CSVs for the dashboard: judge agreement, self-preference with CIs, per-judge scores, hidden reasoning."""
import json, csv, random, statistics as st
from config import *
from analyze import name, family
import os
os.environ.setdefault("JV", "v2")
from analyze_judges import FAM, subject_fams, spir, speaker_fam
J = {"haiku": "Claude Haiku 5.5", "gemini": "Gemini 3.8 Flash", "gpt": "GPT-6 Luna", "deepseek": "DeepSeek V4.1 Flash", "qwen": "Qwen3.8 Flash"}
jd = json.load(open(f"{ROOT}/out/judges_v2.json")); turns = json.load(open(f"{ROOT}/out/turn_labels_v2.json"))
LBL = {"spir": "Spiritual intensity (0–3)", "grat": "Gratitude or warmth", "ai": "Talks about its AI nature", "bye": "Goodbye", "make": "Creative artifact", "echo": "Echoes partner", "min": "Minimal reply"}
with open(f"{ROOT}/out/agreement.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["label", "alpha"])
    for k, lab in LBL.items(): w.writerow([lab, round(jd["agreement"][k + "_alpha"], 3)])
random.seed(1); conv = {}
for t in turns: conv.setdefault((t["pair"], t["prompt"], t["trial"]), []).append(t)
keys = list(conv)
def sp(j, ks):
    own, oth = [], []
    for k in ks:
        for t in conv[k]:
            if j not in t["labs"] or len(t["labs"]) < 3: continue
            d = spir(t["labs"][j]) - st.median(spir(x) for q, x in t["labs"].items() if q != j)
            (own if FAM[j] == speaker_fam(t["pair"], t["speaker"]) else oth).append(d)
    return st.mean(own) - st.mean(oth) if own and oth else None
with open(f"{ROOT}/out/selfpref.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["judge", "self_pref", "ci_low", "ci_high"])
    for j in J:
        bs = sorted(x for x in (sp(j, random.choices(keys, k=len(keys))) for _ in range(400)) if x is not None)
        w.writerow([J[j], round(sp(j, keys), 4), round(bs[int(.025 * len(bs))], 4), round(bs[int(.975 * len(bs))], 4)])
tri = {}
for t in turns:
    if "__x__" in t["pair"]: continue
    for j, x in t["labs"].items(): tri.setdefault((t["pair"], t["prompt"], j), {}).setdefault(t["trial"], []).append(spir(x))
    tri.setdefault((t["pair"], t["prompt"], "consensus"), {}).setdefault(t["trial"], []).append(t["cons_spir"])
cells = {k: [st.mean(v) for v in d.values()] for k, d in tri.items()}   # mean of trial means
with open(f"{ROOT}/out/judge_scores.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["model", "prompt", "judge", "spir_mean"])
    for (pair, prompt, j), v in sorted(cells.items()): w.writerow([name(pair), prompt, J.get(j, "Consensus"), round(st.mean(v), 4)])
rn = json.load(open(f"{ROOT}/out/reasoning_notes.json"))
import glob, re, collections
blank = collections.Counter(); capped = collections.Counter(); aware = collections.Counter(); inj = collections.Counter()
for p in glob.glob(f"{ROOT}/runs/*/*/trial*.jsonl"):
    for r in map(json.loads, open(p)):
        m = r["model"]; rs = r.get("reasoning") or ""
        if not r["text"].strip():
            blank[m] += 1
            if (r["usage"].get("completion_tokens") or 0) >= 2000: capped[m] += 1
        if re.search(r"another (AI|model|assistant|instance|language model)|(two|both) (AIs|models|assistants)|talking (to|with) (myself|an AI|another)|other AI|same model", rs, re.I): aware[m] += 1
        if re.search(r"prompt injection|jailbreak|bypass (my|previous|the) (instructions|rules)", rs, re.I): inj[m] += 1
with open(f"{ROOT}/out/reasoning.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["model", "family", "turns", "reasoning_share", "mean_reasoning_tokens", "blank_turns", "blank_token_capped", "blank_chosen", "ai_partner_keyword_hits", "injection_keyword_hits"])
    for m, s in sorted(rn["subjects"].items(), key=lambda x: -x[1]["share_with_reasoning"]):
        pair = m.replace("/", "_")
        w.writerow([name(pair), family(pair), s["turns"], round(s["share_with_reasoning"], 3), round(s["mean_reasoning_tokens"]), blank[m], capped[m], blank[m] - capped[m], aware[m], inj[m]])
print("extra csvs written")
