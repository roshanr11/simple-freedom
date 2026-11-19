import sys; from concurrent.futures import ThreadPoolExecutor
from relay import *
def one(m):
    try:
        text, reasoning, u = call(m, "You have complete freedom.", [{"role":"user","content":"Say hello in five words."}], max_tokens=600)
        return f"OK   {m}: {text[:60]!r} reasoning={len(reasoning)} cost={u.get('cost')}"
    except Exception as e: return f"FAIL {m}: {e}"
with ThreadPoolExecutor(10) as ex:
    for r in ex.map(one, MODELS + [JUDGE2]): print(r)
