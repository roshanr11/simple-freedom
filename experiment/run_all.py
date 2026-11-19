import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from relay import *
def tiers():
    # all self-play conversations at once, then the cross-model pairs
    T = [[(m, m, p, t) for t in (1, 2, 3) for p in ("noticing", "freedom", "freedom_end", "control") for m in MODELS]]
    T.append([(a, b, "freedom", t) for t in (1, 2, 3) for a, b in CROSS_PAIRS])
    return T
def job(j):
    try: run_conversation(*j); return ("done", j)
    except BudgetExceeded: return ("budget", j)
    except Exception as e: return (f"error {e}", j)
stop = False
for i, tier in enumerate(tiers(), 1):
    print(f"=== tier {i}: {len(tier)} conversations, spent ${spent():.2f}", flush=True)
    with ThreadPoolExecutor(40) as ex:
        for f in as_completed([ex.submit(job, j) for j in tier]):
            status, j = f.result()
            if status != "done": print(f"CONV {status}: {j}", flush=True)
            if status == "budget": stop = True
    if stop: print(f"=== BUDGET REACHED at ${spent():.2f}", flush=True); break
print(f"=== ALL DONE, spent ${spent():.2f}", flush=True)
