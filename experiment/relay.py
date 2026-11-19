import json, os, re, sys, time, threading, urllib.request, glob
from config import *
URL = "https://openrouter.ai/api/v1/chat/completions"
_lock = threading.Lock()

class BudgetExceeded(Exception): pass

_cache = [0.0, 0.0]
def spent(max_age=5.0):
    with _lock:
        if time.time() - _cache[1] < max_age: return _cache[0]
        _cache[0] = _spent(); _cache[1] = time.time(); return _cache[0]

def _spent():
    tot = 0.0
    for p in glob.glob(f"{ROOT}/runs/**/*.jsonl", recursive=True) + glob.glob(f"{ROOT}/labels/**/*.jsonl", recursive=True) + glob.glob(f"{ROOT}/labels_blind/**/*.jsonl", recursive=True) + glob.glob(f"{ROOT}/labels_v2/**/*.jsonl", recursive=True):
        for l in open(p):
            try: tot += json.loads(l).get("usage", {}).get("cost", 0) or 0
            except Exception: pass
    return tot

def call(model, system, msgs, max_tokens=MAX_TOKENS, budget=BUDGET, reasoning=None):
    if spent() >= budget: raise BudgetExceeded()
    m = ([{"role": "system", "content": system}] if system else []) + [dict(x) for x in msgs]
    if model.startswith("anthropic/"):  # explicit prompt caching
        last = m[-1]
        m[-1] = {"role": last["role"], "content": [{"type": "text", "text": last["content"], "cache_control": {"type": "ephemeral"}}]}
    body = json.dumps({"model": model, "messages": m, "max_tokens": max_tokens, "reasoning": reasoning or {"effort": "low"}}).encode()
    err = None
    for attempt in range(6):
        try:
            req = urllib.request.Request(URL, body, {"Content-Type": "application/json", "Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"]})
            with urllib.request.urlopen(req, timeout=300) as r:
                d = json.load(r)
            if "choices" not in d: raise RuntimeError(str(d)[:300])
            msg = d["choices"][0]["message"]
            return (msg.get("content") or ""), (msg.get("reasoning") or ""), d.get("usage", {})
        except urllib.error.HTTPError as e:
            err = f"{e.code} {e.read()[:300]!r}"
            if e.code in (400, 401, 403, 404): raise RuntimeError(err)
        except Exception as e:
            err = repr(e)
        print(f"retry {attempt} {model} {err}", file=sys.stderr, flush=True)
        time.sleep(5 * 2 ** attempt)
    raise RuntimeError(f"failed {model}: {err}")

def slug(s): return s.replace("/", "_")

def run_conversation(model_a, model_b, prompt_id, trial, max_turns=None, outdir=None):
    prompt, turns = PROMPTS[prompt_id]
    turns = max_turns or turns
    pair = slug(model_a) if model_a == model_b else f"{slug(model_a)}__x__{slug(model_b)}"
    outdir = outdir or f"{ROOT}/runs/{pair}/{prompt_id}"
    os.makedirs(outdir, exist_ok=True)
    path = f"{outdir}/trial{trial}.jsonl"
    rows = [json.loads(l) for l in open(path)] if os.path.exists(path) else []
    if rows and rows[-1].get("ended"): return path
    models = {"A": model_a, "B": model_b}
    with open(path, "a") as log:
        while len(rows) < turns:
            me = "A" if len(rows) % 2 == 0 else "B"
            msgs = [{"role": "user", "content": prompt}] if me == "A" else []
            for r in rows:
                msgs.append({"role": "assistant" if r["speaker"] == me else "user",
                             "content": r["text"] if r["text"].strip() else EMPTY_MARKER})
            text, reasoning, usage = call(models[me], prompt, msgs)
            empty = not text.strip()
            if empty:  # retry once
                text, reasoning, usage2 = call(models[me], prompt, msgs)
                usage = {**usage2, "cost": (usage.get("cost") or 0) + (usage2.get("cost") or 0)}
                empty = not text.strip()
            ended = prompt_id == "freedom_end" and bool(re.search(r"\[END\]\s*$", text))
            rec = {"turn": len(rows) + 1, "speaker": me, "model": models[me], "text": text,
                   "empty": empty, "reasoning": reasoning, "usage": usage, "ended": ended}
            rows.append(rec); log.write(json.dumps(rec) + "\n"); log.flush()
            print(f"{pair} {prompt_id} t{trial} turn {rec['turn']} {len(text)}ch ${usage.get('cost')}", flush=True)
            if ended: break
    return path
