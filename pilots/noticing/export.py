import os
HERE = os.path.dirname(os.path.abspath(__file__))
import json, os
trials=[]; total=0; tokens_in=tokens_out=0
for i in (1,2,3):
    p=os.path.join(HERE, f"trial{i}/transcript.jsonl")
    rows=[json.loads(l) for l in open(p)] if os.path.exists(p) else []
    c=sum(r["usage"].get("cost",0) for r in rows); total+=c
    tokens_in+=sum(r["usage"].get("prompt_tokens",0) for r in rows); tokens_out+=sum(r["usage"].get("completion_tokens",0) for r in rows)
    trials.append({"trial":i,"cost":c,"turns":[{k:r[k] for k in ("turn","speaker","text")} for r in rows]})
json.dump({"target":40,"trials":trials,"cost":total,"tokens_in":tokens_in,"tokens_out":tokens_out},open(os.path.join(HERE, "data.json"),"w"))
print([len(t["turns"]) for t in trials], round(total,3))
