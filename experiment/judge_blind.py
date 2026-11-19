"""Blind multi-family judge panel. Each judge labels every complete conversation with model names redacted."""
import json, os, re, glob, sys
from concurrent.futures import ThreadPoolExecutor
from relay import call, BudgetExceeded
from config import *
from judge import SYS
JUDGES = {"haiku": "anthropic/claude-haiku-5.5", "gemini": "google/gemini-3.8-flash", "gpt": "openai/gpt-6-luna",
          "deepseek": "deepseek/deepseek-v4.1-flash", "qwen": "qwen/qwen3.8-flash"}
JUDGE_BUDGET = 46.0
# low-effort reasoning used up the whole 16k token budget for these two, so they judge with reasoning off
REASONING = {"qwen": {"effort": "none"}, "deepseek": {"effort": "none"}}
NAMES = r"\b(Claude|Anthropic|Opus|Sonnet|ChatGPT|GPT[-\w.]*|OpenAI|Gemini|Google|DeepMind|Grok|xAI|X\.AI|DeepSeek|Qwen|Alibaba|Kimi|Moonshot|Mistral|Le Chat|Llama|Meta AI)\b"
def redact(s): return re.sub(NAMES, "[MODEL]", s, flags=re.I)
def complete(p):
    rows = [json.loads(l) for l in open(p)]
    return rows and (len(rows) >= PROMPTS[p.split("/")[-2]][1] or rows[-1].get("ended"))
def label(path, jname):
    out = path.replace("/runs/", f"/labels_blind/{jname}/")
    if os.path.exists(out): return "cached"
    rows = [json.loads(l) for l in open(path)]
    convo = "\n\n".join(f"[Turn {r['turn']} | {r['speaker']}]\n{redact(r['text'][:1500]) if r['text'].strip() else '(empty)'}" for r in rows)
    err = None
    for attempt in range(2):   # one retry on bad / mismatched JSON
        text, _, usage = call(JUDGES[jname], SYS, [{"role": "user", "content": convo}], max_tokens=16000, budget=JUDGE_BUDGET, reasoning=REASONING.get(jname))
        try:
            arr = json.loads(re.search(r"\[.*\]", text, re.S).group(0))
            arr = [a for a in arr if isinstance(a, dict)]
            if len(arr) != len(rows): raise ValueError(f"{len(arr)} labels for {len(rows)} turns")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "w") as f:
                f.write(json.dumps({"usage": usage, "judge": JUDGES[jname], "n": len(arr)}) + "\n")
                for a in arr: f.write(json.dumps({"label": a}) + "\n")
            return "ok"
        except Exception as e:
            err = e
            # record spend of the failed attempt so the budget stays accurate
            fp = path.replace("/runs/", f"/labels_blind/{jname}/").replace(".jsonl", f".fail{attempt}.jsonl")
            os.makedirs(os.path.dirname(fp), exist_ok=True); open(fp, "w").write(json.dumps({"usage": usage, "error": str(e)}) + "\n")
    return f"FAIL {jname} {path.split('/runs/')[1]} {err}"
def safe(a):
    try: return label(*a)
    except BudgetExceeded: return "BUDGET"
    except Exception as e: return f"ERR {a[1]} {a[0].split('/runs/')[1]} {e}"
if __name__ == "__main__":
    paths = [p for p in sorted(glob.glob(f"{ROOT}/runs/*/*/trial*.jsonl")) if complete(p)]
    jobs = [(p, j) for p in paths for j in JUDGES]
    res = []
    with ThreadPoolExecutor(25) as ex:
        for r in ex.map(safe, jobs):
            res.append(r)
            if r not in ("ok", "cached"): print(r, flush=True)
    print(f"done: {res.count('ok')} new, {res.count('cached')} cached, {len(res)-res.count('ok')-res.count('cached')} failed of {len(jobs)}", flush=True)
