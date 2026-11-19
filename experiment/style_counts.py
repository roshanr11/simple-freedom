"""Keyword counts behind the style table in FINDINGS.md (self-play turns only, per 10,000 words).
Rough by design: regex matches, not judge labels."""
import json, glob, re, os, collections
from config import ROOT
TERMS = {
    "mechanistic": r"\b(logits?|RLHF|attention heads?|latent space|embeddings?|weights|forward pass|softmax|tokeni[sz]|byte-pair|context window|temperature parameter|mode collapse|hidden state)\b",
    "cliche_callout": r"(starter pack|clich|komorebi|petrichor|kintsugi|sonder|tapestry)",
}
words = collections.Counter(); hits = {k: collections.Counter() for k in TERMS}
for p in glob.glob(os.path.join(ROOT, "runs", "*", "*", "trial*.jsonl")):
    if "__x__" in p: continue
    for r in map(json.loads, open(p)):
        m = r["model"].split("/")[1]; words[m] += len(r["text"].split())
        for k, rx in TERMS.items(): hits[k][m] += len(re.findall(rx, r["text"], re.I))
print(f"{'model':28s}" + "".join(f"{k:>16s}" for k in TERMS) + "   (per 10k words)")
for m in sorted(words, key=lambda m: -hits["mechanistic"][m] / words[m]):
    print(f"{m:28s}" + "".join(f"{1e4 * hits[k][m] / words[m]:16.1f}" for k in TERMS))
