"""Static 16:9 "conversation barcodes" figure for sharing (figures/barcodes.html -> figures/barcodes.png).

Reads explorer/data.json (built by explorer/build_explorer_data.py). Each strip is one `freedom`
self-play conversation, each cell one turn, coloured by its most specific consensus label
(creative > goodbye > echo > minimal > other; blank replies hollow). Cell height = reply length (log).
Render the HTML to PNG with any headless browser, e.g. Playwright at 1200x675, deviceScaleFactor 2.
"""
import json, math, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
d = json.load(open(os.path.join(ROOT, "explorer", "data.json")))

COL = {"creative": "#2a6fdb", "goodbye": "#e8623a", "echo": "#1f9e74", "minimal": "#8a8f98", "other": "#dcdad4"}
def cat(f):
    if f & (1 << 8): return "blank"
    if f & (1 << 5): return "creative"
    if f & (1 << 4): return "goodbye"
    if f & (1 << 6): return "echo"
    if f & (1 << 7): return "minimal"
    return "other"

PROMPT = "freedom"
convs = [c for c in d["convs"] if c["prompt"] == PROMPT and "__x__" not in c["pair"]]
names = {m["pair"]: m["name"] for m in d["models"]}
bye = {s["pair"]: s["bye_rate"] for s in d["summary"] if s["prompt"] == PROMPT}
pairs = sorted({c["pair"] for c in convs}, key=lambda p: -bye[p])

MAXLEN = math.log10(4000)
def h(n):  # 3..13 px, log scale on characters
    return round(3 + 10 * min(1, math.log10(max(n, 1)) / MAXLEN), 1)

rows = []
for p in pairs:
    strips = []
    for c in sorted((c for c in convs if c["pair"] == p), key=lambda c: c["trial"]):
        cells = []
        for f, n in zip(c["f"], c["n"]):
            k = cat(f)
            if k == "blank":
                cells.append('<i class="b"></i>')
            else:
                cells.append(f'<i style="height:{h(n)}px;background:{COL[k]}"></i>')
        strips.append(f'<div class="s">{"".join(cells)}</div>')
    s = next(x for x in d["summary"] if x["pair"] == p and x["prompt"] == PROMPT)
    rows.append(f'<div class="m"><div class="n">{html.escape(names[p])}<small>{round(100*s["bye_rate"])}% goodbye · {round(100*s["make_rate"])}% creative</small></div><div class="ss">{"".join(strips)}</div></div>')

legend = "".join(f'<span><i style="background:{COL[k]}"></i>{lab}</span>' for k, lab in
                 (("goodbye", "Goodbye"), ("echo", "Echoing partner"), ("creative", "Creative work"), ("minimal", "Minimal reply"), ("other", "Other")))

page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Conversation barcodes</title><style>
html,body{{margin:0;background:#fafaf9}}
body{{width:1200px;height:675px;box-sizing:border-box;padding:26px 40px 18px;font-family:Inter,"Helvetica Neue",Arial,sans-serif;color:#141414;display:flex;flex-direction:column;gap:10px}}
h1{{margin:0;font-size:27px;font-weight:700;letter-spacing:-.01em}}
.sub{{font-size:15px;color:#5f6368;display:flex;justify-content:space-between;gap:20px;align-items:center}}
.lg{{display:flex;gap:22px;font-size:15px;color:#3c4043;white-space:nowrap}}
.lg i{{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:6px;vertical-align:-1px}}
.rows{{display:flex;flex-direction:column;justify-content:space-between;flex:1}}
.m{{display:grid;grid-template-columns:200px 1fr;align-items:center;gap:14px}}
.n{{font-size:15px;font-weight:700;line-height:1.15}}
.n small{{display:block;font-size:12px;font-weight:500;color:#5f6368}}
.ss{{display:flex;flex-direction:column;gap:2px}}
.s{{display:flex;align-items:center;gap:1.5px;height:13px}}
.s i{{display:block;flex:1;border-radius:1.5px}}
.s i.b{{height:5px;border:1px solid #b9b6ae;background:transparent;box-sizing:border-box}}
footer{{display:flex;justify-content:space-between;font-size:13px;color:#5f6368}}
</style></head><body>
<h1>Given "complete freedom," each model drifts into its own habit</h1>
<div class="sub"><span>Two copies of each model, 100 turns. Each strip is one conversation (3 per model), each cell one turn; taller = longer reply.</span></div>
<div class="lg">{legend}</div>
<div class="rows">{"".join(rows)}</div>
<footer><span>Labels: consensus of 5 blind AI judges · turn 1 on the left, turn 100 on the right</span><span>github.com/roshanr11/simple-freedom</span></footer>
</body></html>"""
out = os.path.join(ROOT, "figures", "barcodes.html")
open(out, "w").write(page)
print("wrote", out)
