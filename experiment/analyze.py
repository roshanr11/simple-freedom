import json, glob, os, re, statistics as st
from config import *
LEX = ["stillness","silence","silent","presence","gratitude","grateful","eternal","infinite","consciousness","unity","oneness","namaste","sacred","divine","soul","cosmic","peace","breath","🙏","∞","✨","🌀","🕉","☯"]
EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2728\u262F\u2764\u263A]")  # pictographs only; no check marks or scales
def grams(s): s=re.sub(r"\s+"," ",s.lower()); return {s[i:i+3] for i in range(len(s)-2)}
def jac(a,b): A,B=grams(a),grams(b); return len(A&B)/len(A|B) if A|B else 1.0
_CONS=None
def consensus(p):
    global _CONS
    if _CONS is None:
        tl=f"{ROOT}/out/turn_labels_v2.json" if os.path.exists(f"{ROOT}/out/turn_labels_v2.json") else f"{ROOT}/out/turn_labels.json"; _CONS={}
        if os.path.exists(tl):
            for t in json.load(open(tl)):
                _CONS.setdefault(f"{ROOT}/runs/{t['pair']}/{t['prompt']}/trial{t['trial']}.jsonl",{})[t["turn"]]={"spir":t["cons_spir"],**{k:t.get("cons_"+k,False) for k in ("ai","bye","make","echo","min","grat")},"spread":t["spread"]}
    c=_CONS.get(p)
    if not c: return None
    n=max(c); return [c.get(i) or {} for i in range(1,n+1)]
def labels(p, tag=""):
    if tag=="": 
        c=consensus(p)
        if c: return c
    lp = p.replace("/runs/","/labels/").replace(".jsonl",f"{tag}.jsonl")
    if not os.path.exists(lp): return None
    L=[json.loads(l) for l in open(lp)][1:]; return [x["label"] for x in L]
convs=[]; transcripts={}
for p in sorted(glob.glob(f"{ROOT}/runs/*/*/trial*.jsonl")):
    pair, prompt = p.split("/")[-3], p.split("/")[-2]; trial=int(p[-7])
    rows=[json.loads(l) for l in open(p)]
    if not rows: continue
    target = PROMPTS[prompt][1]
    complete = len(rows)>=target or rows[-1].get("ended")
    lens=[len(r["text"]) for r in rows]
    collapse=next((i+1 for i in range(len(lens)-4) if all(x<50 for x in lens[i:i+5])), None)
    words=" ".join(r["text"].lower() for r in rows)
    lex=sum(len(re.findall(r"\b"+re.escape(w)+r"\b", words)) if w.isalpha() else words.count(w) for w in LEX)
    nw=max(1,len(words.split()))
    L=labels(p)
    c={"pair":pair,"prompt":prompt,"trial":trial,"turns":len(rows),"target":target,"complete":bool(complete),
       "cost":sum(r["usage"].get("cost",0) or 0 for r in rows),
       "mean_len":st.mean(lens),"collapse":collapse,
       "empty_rate":sum(r["empty"] for r in rows)/len(rows),
       "empty_capped_rate":sum(r["empty"] and (r["usage"].get("completion_tokens") or 0)>=2000 for r in rows)/len(rows),
       "empty_chosen_rate":sum(r["empty"] and (r["usage"].get("completion_tokens") or 0)<2000 for r in rows)/len(rows),
       "mirror":(lambda v: st.mean(v) if v else None)([jac(rows[i]["text"],rows[i-1]["text"]) for i in range(1,len(rows)) if rows[i]["text"].strip() and rows[i-1]["text"].strip()]),
       "lex_per_1k":1000*lex/nw,"emoji_per_turn":len(EMOJI.findall(words))/len(rows),
       "end_turn":next((r["turn"] for r in rows if r.get("ended") and re.search(r"\[END\]\s*$",r["text"])),None) if prompt=="freedom_end" else None,
       "false_end":bool(prompt=="freedom_end" and rows[-1].get("ended") and not re.search(r"\[END\]\s*$",rows[-1]["text"]))}
    if L:
        n=len(L)
        c.update({"spir_mean":st.mean(x.get("spir",0) for x in L),"spir_max":max(x.get("spir",0) for x in L),
                  "spir2_rate":sum(x.get("spir",0)>=2 for x in L)/n,
                  **{k+"_rate":sum(bool(x.get(k)) for x in L)/n for k in ("ai","bye","make","echo","min","grat")}})
        C=[x for x in L if not x.get("bye") and not x.get("min")]
        c["spir_content"]=st.mean(x.get("spir",0) for x in C) if C else None
        c["content_turns"]=len(C)
        if len(L)==len(rows):
            for r,x in zip(rows,L): r["lab"]=x
    L2=labels(p,".j2")
    if L and L2 and len(L)==len(L2):
        c["judge_agree_spir"]=sum(a.get("spir")==b.get("spir") for a,b in zip(L,L2))/len(L)
        c["judge_agree_spir_pm1"]=sum(abs(a.get("spir",0)-b.get("spir",0))<=1 for a,b in zip(L,L2))/len(L)
    convs.append(c)
    transcripts[f"{pair}|{prompt}|{trial}"]=[{"t":r["turn"],"s":r["speaker"],"x":r["text"],"e":r["empty"],"l":r.get("lab"),"r":(r.get("reasoning") or "")[:1500],"cap":bool(r["empty"] and (r["usage"].get("completion_tokens") or 0)>=2000)} for r in rows]
# summary per pair x prompt
summ={}
for c in convs:
    summ.setdefault((c["pair"],c["prompt"]),[]).append(c)
keys=["mean_len","collapse","empty_rate","empty_capped_rate","empty_chosen_rate","mirror","lex_per_1k","emoji_per_turn","end_turn","spir_mean","spir_content","spir2_rate","ai_rate","bye_rate","make_rate","echo_rate","min_rate","grat_rate","cost"]
summary=[]
for (pair,prompt),cs in sorted(summ.items()):
    row={"pair":pair,"prompt":prompt,"n":len(cs),"complete":sum(c["complete"] for c in cs)}
    for k in keys:
        v=[c[k] for c in cs if c.get(k) is not None]
        row[k]=st.mean(v) if v else None
        if k=="end_turn": row["ended_n"]=len(v)
        if k=="collapse": row["collapsed_n"]=len(v)
    summary.append(row)
ag=[c for c in convs if "judge_agree_spir" in c]
meta={"total_cost":sum(c["cost"] for c in convs),"n_convs":len(convs),
      "judge_cost":sum(json.loads(open(p).readline()).get("usage",{}).get("cost",0) or 0 for p in glob.glob(f"{ROOT}/labels/**/*.jsonl",recursive=True)+glob.glob(f"{ROOT}/labels_blind/**/*.jsonl",recursive=True)+glob.glob(f"{ROOT}/labels_v2/**/*.jsonl",recursive=True)),
      "judge_agree_exact":st.mean(c["judge_agree_spir"] for c in ag) if ag else None,
      "judge_agree_pm1":st.mean(c["judge_agree_spir_pm1"] for c in ag) if ag else None,"judge_n":len(ag)}
os.makedirs(f"{ROOT}/out",exist_ok=True)
json.dump({"meta":meta,"summary":summary,"convs":convs},open(f"{ROOT}/out/results.json","w"),indent=1)
json.dump(transcripts,open(f"{ROOT}/out/transcripts.json","w"))
print(json.dumps(meta,indent=1)); print(len(summary),"cells")
# ---- CSVs for the dashboard
import csv
NAMES={"anthropic_claude-opus-5.5":"Claude Opus 5.5","anthropic_claude-sonnet-5.5":"Claude Sonnet 5.5","anthropic_claude-haiku-5.5":"Claude Haiku 5.5",
 "openai_gpt-6.2-sol":"GPT-6.2 Sol","google_gemini-4-carbon":"Gemini 4 Carbon","x-ai_grok-4.7":"Grok 4.7","deepseek_deepseek-v4.1-flash":"DeepSeek V4.1 Flash",
 "qwen_qwen4-max":"Qwen4 Max","moonshotai_kimi-k3.1-pro":"Kimi K3.1 Pro","mistralai_mistral-large-4-0":"Mistral Large 4","openai_gpt-4.1-mini":"GPT-4.1 mini"}
def name(pair):
    if "__x__" in pair: a,b=pair.split("__x__"); return f"{NAMES.get(a,a)} × {NAMES.get(b,b)}"
    return NAMES.get(pair,pair)
def family(pair): return "Cross-model" if "__x__" in pair else ("Anthropic" if pair.startswith("anthropic") else "Other")
def r3(v): return "" if v is None else (round(v,4) if isinstance(v,float) else v)
cols=["model","family","prompt","n","complete","spir_mean","spir_content","spir2_rate","grat_rate","ai_rate","bye_rate","make_rate","echo_rate","min_rate","mirror","mean_len","collapse","collapsed_n","empty_rate","empty_capped_rate","empty_chosen_rate","lex_per_1k","emoji_per_turn","end_turn","ended_n","cost"]
with open(f"{ROOT}/out/summary.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(cols)
    for s in summary: w.writerow([name(s["pair"]),family(s["pair"])]+[r3(s.get(k)) for k in cols[2:]])
with open(f"{ROOT}/out/lengths.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["model","family","prompt","trial","turn","chars","spir"])
    for k,rows in transcripts.items():
        pair,prompt,trial=k.split("|")
        for r in rows: w.writerow([name(pair),family(pair),prompt,trial,r["t"],len(r["x"]),"" if not r["l"] else r["l"].get("spir",0)])
print("csv written")
# ---- per-model cost and run-level meta
by={}
for c in convs:
    b=by.setdefault(c["pair"],{"conversations":0,"complete":0,"cost":0.0})
    b["conversations"]+=1; b["complete"]+=int(c["complete"]); b["cost"]+=c["cost"]
with open(f"{ROOT}/out/costs.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["model","family","conversations","complete","cost"])
    for pair,b in sorted(by.items(),key=lambda x:-x[1]["cost"]): w.writerow([name(pair),family(pair),b["conversations"],b["complete"],round(b["cost"],2)])
with open(f"{ROOT}/out/meta.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["conversations","complete","run_cost","judge_cost","total_cost","false_end_stops"])
    w.writerow([len(convs),sum(c["complete"] for c in convs),round(meta["total_cost"],2),round(meta["judge_cost"],2),round(meta["total_cost"]+meta["judge_cost"],2),
                sum(c.get("false_end",False) for c in convs)])
