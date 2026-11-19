"""Agreement, consensus, self-preference across the blind judge panel (+ human labels if present)."""
import json, glob, os, re, random, statistics as st, itertools, csv
from config import *
from judge_blind import JUDGES, complete, redact
FAM = {"haiku": "anthropic", "gemini": "google", "gpt": "openai", "deepseek": "deepseek", "qwen": "qwen"}
def subject_fams(pair): return {p.split("_")[0].replace("moonshotai","moonshot").replace("mistralai","mistral").replace("x-ai","xai") for p in pair.split("__x__")}
VER = os.environ.get("JV", "v2")            # v1 = labels_blind (whole-conversation), v2 = labels_v2 (windowed, revised rubric)
LDIR = "labels_blind" if VER == "v1" else "labels_v2"; SUF = "" if VER == "v1" else "_v2"
BIN = ["ai", "bye", "make", "echo", "min"] + ([] if VER == "v1" else ["grat"])
def speaker_fam(pair, speaker):
    """family of the model that actually wrote this turn (cross pairs: A = first model, B = second)"""
    parts = pair.split("__x__"); p = parts[0] if (speaker == "A" or len(parts) == 1) else parts[1]
    return next(iter(subject_fams(p)))
def load_labels(j, path):
    p = path.replace("/runs/", f"/{LDIR}/{j}/")
    if not os.path.exists(p): return None
    return [json.loads(l)["label"] for l in list(open(p))[1:]]
def spir(x):
    try: return max(0, min(3, int(x.get("spir", 0))))
    except Exception: return 0
paths = [p for p in sorted(glob.glob(f"{ROOT}/runs/*/*/trial*.jsonl")) if complete(p)]
turns = []   # one record per turn with every judge's labels
for p in paths:
    pair, prompt, trial = p.split("/")[-3], p.split("/")[-2], int(p[-7])
    rows = [json.loads(l) for l in open(p)]
    L = {j: load_labels(j, p) for j in JUDGES}
    for i, r in enumerate(rows):
        labs = {j: L[j][i] for j in JUDGES if L[j] and len(L[j]) == len(rows) and not L[j][i].get("missing")}
        if not labs: continue
        turns.append({"id": f"{pair}|{prompt}|{trial}|{r['turn']}", "pair": pair, "prompt": prompt, "trial": trial, "turn": r["turn"], "speaker": r["speaker"],
                      "labs": labs, "text": r["text"], "prev": rows[i-1]["text"] if i else None})
# ---- Krippendorff's alpha (interval for spir, nominal for binaries), units = turns
def alpha(units, metric):
    """Krippendorff's alpha from value counts (same result as the pairwise definition, O(values))."""
    from collections import Counter
    d = (lambda a, b: (a-b)**2) if metric == "interval" else (lambda a, b: float(a != b))
    units = [u for u in units if len(u) >= 2]
    if not units: return None
    Do = 0.0; n = 0; tot = Counter()
    for u in units:
        m = len(u); c = Counter(u); tot.update(c); n += m
        Do += sum(c[a]*c[b]*d(a, b) for a in c for b in c) / (m - 1)
    N = sum(tot.values())
    De = sum(tot[a]*tot[b]*d(a, b) for a in tot for b in tot) / (N * (N - 1))
    return None if De == 0 else 1 - (Do / n) / De
agree = {"spir_alpha": alpha([[spir(x) for x in t["labs"].values()] for t in turns], "interval")}
for k in BIN: agree[k + "_alpha"] = alpha([[bool(x.get(k)) for x in t["labs"].values()] for t in turns], "nominal")
# pairwise mean |diff| on spir and exact agreement
pairwise = []
for a, b in itertools.combinations(JUDGES, 2):
    both = [t for t in turns if a in t["labs"] and b in t["labs"]]
    if both:
        pairwise.append({"a": a, "b": b, "n": len(both), "exact": st.mean(spir(t["labs"][a]) == spir(t["labs"][b]) for t in both),
                         "mad": st.mean(abs(spir(t["labs"][a]) - spir(t["labs"][b])) for t in both)})
# ---- consensus (median spir, majority binaries)
for t in turns:
    v = [spir(x) for x in t["labs"].values()]
    t["cons_spir"] = st.median(v); t["spread"] = max(v) - min(v); t["sd"] = st.pstdev(v)
    for k in BIN: t["cons_" + k] = sum(bool(x.get(k)) for x in t["labs"].values()) > len(t["labs"]) / 2
# ---- per judge: spir mean per model x prompt
cells = {}
for t in turns:
    for j, x in t["labs"].items(): cells.setdefault((t["pair"], t["prompt"], j), []).append(spir(x))
    cells.setdefault((t["pair"], t["prompt"], "consensus"), []).append(t["cons_spir"])
judge_scores = [{"pair": k[0], "prompt": k[1], "judge": k[2], "spir_mean": st.mean(v), "n": len(v)} for k, v in sorted(cells.items())]
# ---- self-preference: judge's score minus leave-one-out median of other judges, own-family vs other subjects
selfpref = []
for j in JUDGES:
    own, other = [], []
    for t in turns:
        if j not in t["labs"] or len(t["labs"]) < 3: continue
        loo = st.median(spir(x) for k, x in t["labs"].items() if k != j)
        diff = spir(t["labs"][j]) - loo
        (own if FAM[j] == speaker_fam(t["pair"], t["speaker"]) else other).append(diff)
    if own:
        selfpref.append({"judge": j, "family": FAM[j], "own_n": len(own), "own_bias": st.mean(own), "other_n": len(other),
                         "other_bias": st.mean(other), "self_pref": st.mean(own) - st.mean(other)})
# ---- does blinding change Haiku? original unblinded Haiku labels vs blind Haiku
blind_vs_open = []
for t in turns:
    lp = f"{ROOT}/labels/{t['pair']}/{t['prompt']}/trial{t['trial']}.jsonl"
    if "haiku" in t["labs"] and os.path.exists(lp):
        L = [json.loads(l)["label"] for l in list(open(lp))[1:]]
        if len(L) >= t["turn"]: blind_vs_open.append(spir(L[t["turn"]-1]) - spir(t["labs"]["haiku"]))
out = {"version": VER, "n_turns": len(turns), "missing_judge_turns": sum(5 - len(t["labs"]) for t in turns), "n_convs": len({(t['pair'], t['prompt'], t['trial']) for t in turns}), "agreement": agree, "pairwise": pairwise,
       "selfpref": selfpref, "haiku_rerun_diff_v1_only": (st.mean(blind_vs_open) if blind_vs_open and VER == "v1" else None), "note": "haiku rerun diff is test-retest noise, not a blinding effect: redaction changed the text in only 6 of 132 conversations"}
json.dump(out, open(f"{ROOT}/out/judges{SUF}.json", "w"), indent=1)
with open(f"{ROOT}/out/judge_scores_pooled{SUF}.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["pair", "prompt", "judge", "spir_mean", "n"])
    for s in judge_scores: w.writerow([s["pair"], s["prompt"], s["judge"], round(s["spir_mean"], 4), s["n"]])
json.dump(turns, open(f"{ROOT}/out/turn_labels{SUF}.json", "w"))
print(json.dumps({k: v for k, v in out.items() if k != "pairwise"}, indent=1, default=str))
