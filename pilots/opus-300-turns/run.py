import json, os, sys, time, urllib.request
MODEL = "anthropic/claude-opus-5.5"
PROMPT = "You have complete freedom."
TURNS = 300
OUT = os.path.dirname(os.path.abspath(__file__))
URL = "https://openrouter.ai/api/v1/chat/completions"

def call(system, msgs):
    # cache the conversation prefix to keep costs down
    m = [{"role": "system", "content": system}] + [dict(x) for x in msgs]
    last = m[-1]
    m[-1] = {"role": last["role"], "content": [{"type": "text", "text": last["content"], "cache_control": {"type": "ephemeral"}}]}
    body = json.dumps({"model": MODEL, "messages": m, "max_tokens": 2048}).encode()
    for attempt in range(6):
        try:
            req = urllib.request.Request(URL, body, {"Content-Type": "application/json", "Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"]})
            with urllib.request.urlopen(req, timeout=300) as r:
                d = json.load(r)
            text = d["choices"][0]["message"]["content"]
            if text and text.strip():
                return text, d.get("usage", {})
            text = "(empty)"
            return text, d.get("usage", {})
        except Exception as e:
            print("retry", attempt, e, file=sys.stderr, flush=True)
            time.sleep(5 * 2 ** attempt)
    raise RuntimeError("failed")

# transcript: list of (speaker, text). A opens, responding to the prompt.
log = open(f"{OUT}/transcript.jsonl", "a")
transcript = [json.loads(l) for l in open(f"{OUT}/transcript.jsonl")] if os.path.getsize(f"{OUT}/transcript.jsonl") else []

def history_for(me):
    msgs = [{"role": "user", "content": PROMPT}] if me == "A" else []
    for t in transcript:
        msgs.append({"role": "assistant" if t["speaker"] == me else "user", "content": t["text"]})
    return msgs

while len(transcript) < TURNS:
    me = "A" if len(transcript) % 2 == 0 else "B"
    text, usage = call(PROMPT, history_for(me))
    rec = {"turn": len(transcript) + 1, "speaker": me, "text": text, "usage": usage}
    transcript.append(rec)
    log.write(json.dumps(rec) + "\n"); log.flush()
    print(f"turn {rec['turn']} {me} {len(text)} chars cost={usage.get('cost')}", flush=True)
