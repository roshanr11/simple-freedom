"""Figures for simple-freedom.

Reads data/out/{summary.csv,results.json,lengths.csv} and writes SVG figures
(plus 2x PNGs, rendered with headless Chrome/Chromium when one is installed)
into figures/.  Standard library only.

    python experiment/make_figures.py            # from the repo root
    FREEDOM_DATA=/path/to/data FIGURES_OUT=/path python make_figures.py
"""
import csv, json, math, os, shutil, statistics as st, subprocess, tempfile
from collections import defaultdict
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("FREEDOM_DATA", os.path.join(HERE, "..", "data"))
OUT = os.environ.get("FIGURES_OUT", os.path.join(HERE, "..", "figures"))

# ---------------------------------------------------------------- palette
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
INK3 = "#7a7974"
GRID = "#e6e5e1"
TRACK = "#efeeea"
MUTED = "#c4c3be"      # de-emphasised series
BLUE = "#2a78d6"       # categorical slot 1
ORANGE = "#eb6834"     # categorical slot 2
BAND = "#eaf2fc"       # blue tint for a highlighted region
FONT = "Inter, 'Helvetica Neue', Helvetica, Arial, sans-serif"
TABNUM = "font-variant-numeric:tabular-nums"

# ---------------------------------------------------------------- data
def load():
    summary = list(csv.DictReader(open(os.path.join(DATA, "out", "summary.csv"))))
    res = json.load(open(os.path.join(DATA, "out", "results.json")))
    # results.json rows are keyed by pair slug; summary.csv by display name, same order
    name = {s["pair"]: r["model"] for s, r in zip(res["summary"], summary)}
    for s, r in zip(res["summary"], summary):   # full-precision values (CSV is rounded to 4 dp)
        assert s["prompt"] == r["prompt"]
        r.update({k: v for k, v in s.items() if isinstance(v, float)})
    lengths = list(csv.DictReader(open(os.path.join(DATA, "out", "lengths.csv"))))
    return summary, res["convs"], name, lengths

def sm(summary, prompt):
    return {r["model"]: r for r in summary if r["prompt"] == prompt and r["family"] != "Cross-model"}

# ---------------------------------------------------------------- svg helpers
class Svg:
    def __init__(self, w, h):
        self.w, self.h, self.parts = w, h, []
    def add(self, s): self.parts.append(s)
    def text(self, x, y, s, size=16, fill=INK, weight=400, anchor="start", extra=""):
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
                 f'font-weight="{weight}" text-anchor="{anchor}" {extra}>{escape(s)}</text>')
    def line(self, x1, y1, x2, y2, stroke=GRID, w=1, extra=""):
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                 f'stroke="{stroke}" stroke-width="{w}" {extra}/>')
    def rect(self, x, y, w, h, fill, rx=0):
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w,0):.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"/>')
    def bar(self, x, y, w, h, fill, r=4):
        """Horizontal bar anchored at x, rounded only at the data end."""
        if w <= 0: return
        r = min(r, w, h / 2)
        self.add(f'<path d="M{x:.1f},{y:.1f} h{w-r:.1f} a{r},{r} 0 0 1 {r},{r} v{h-2*r:.1f} '
                 f'a{r},{r} 0 0 1 -{r},{r} h-{w-r:.1f} z" fill="{fill}"/>')
    def dot(self, x, y, r, fill, ring=SURFACE, stroke=None, sw=2):
        if stroke:  # hollow marker
            self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{SURFACE}" stroke="{stroke}" stroke-width="{sw}"/>')
        else:
            self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{ring}" stroke-width="2"/>')
    def path(self, pts, stroke, w=2, opacity=1):
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.add(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{w}" '
                 f'stroke-linejoin="round" stroke-linecap="round" opacity="{opacity}"/>')
    def render(self, title):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}" font-family="{FONT}" role="img">'
                f'<title>{escape(title)}</title><rect width="100%" height="100%" fill="{SURFACE}"/>'
                + "".join(self.parts) + "</svg>")

def header(s, title, subtitle, x=28, y=44):
    s.text(x, y, title, size=28, weight=700)
    for i, line in enumerate(subtitle if isinstance(subtitle, list) else [subtitle]):
        s.text(x, y + 30 + 22 * i, line, size=17, fill=INK2)

def footer(s, note, x=28):
    s.text(x, s.h - 10, note, size=13, fill=INK3)

# ---------------------------------------------------------------- figure data
def exit_data(convs, name):
    """freedom_end: turn of first [END] per trial; None = never; false stops dropped."""
    d = defaultdict(list)
    for c in convs:
        if c["prompt"] != "freedom_end" or c["false_end"]:
            continue
        d[name[c["pair"]]].append((c["trial"], c["end_turn"]))
    rows = []
    for m, v in d.items():
        turns = [t for _, t in sorted(v)]
        med = st.median([t if t is not None else 101 for t in turns])
        rows.append((m, turns, med))
    rows.sort(key=lambda r: (r[2], max(t or 101 for t in r[1])))
    return rows

def place(vals, px_per, r):
    """Vertical offsets so dots within one row don't hide each other."""
    offs, placed = [], []
    for v in vals:
        for o in (0, -r - 1, r + 1, -2 * r - 2, 2 * r + 2):
            if all(abs((v - pv) * px_per) >= 2 * r - 1 or o != po for pv, po in placed):
                break
        placed.append((v, o)); offs.append(o)
    return offs

def exit_strip(s, rows, x0, x1, y0, y1, label_x, name_size=18, r=6.5, ticks=True,
               short=lambda m: m, tick_size=15, band_label=True):
    """Dot strip: one row per model, x = turn of first [END] on 0..100."""
    X = lambda t: x0 + (x1 - x0) * t / 100
    step = (y1 - y0) / len(rows)
    # first-10-turns band
    s.rect(X(0), y0 - 6, X(10) - X(0), y1 - y0 + 6, BAND)
    if band_label:
        s.text(X(0), y0 - 14, "first 10 turns", size=13, fill=BLUE, weight=600)
    for t in range(0, 101, 10 if ticks else 50):
        s.line(X(t), y0 - 6, X(t), y1, GRID, 1)
    for i, (m, turns, med) in enumerate(rows):
        y = y0 + step * (i + 0.5)
        s.text(label_x, y + name_size * 0.35, short(m), size=name_size, anchor="end")
        ended = [t for t in turns if t is not None]
        lo, hi = min(ended), max(t if t is not None else 100 for t in turns)
        s.line(X(lo), y, X(hi), y, MUTED, 2, 'stroke-linecap="round"')
        if med <= 100:
            s.line(X(med), y - 1.7 * r, X(med), y + 1.7 * r, INK, 2.5 if r > 5 else 2, 'stroke-linecap="round"')
        vals = sorted(t if t is not None else 100 for t in turns)
        for t, o in zip(vals, place(vals, (x1 - x0) / 100, r)):
            never = t == 100 and None in turns and turns.count(100) == 0
            if never:
                s.dot(X(100), y + o, r - 1, None, stroke=BLUE, sw=2.5)
            else:
                s.dot(X(t), y + o, r, BLUE)
    s.line(x0, y1, x1, y1, INK3, 1)
    for t in range(0, 101, 10 if ticks else 50):
        s.text(X(t), y1 + 20, str(t), size=tick_size, fill=INK2, anchor="middle", extra=f'style="{TABNUM}"')
    return X, step

# ---------------------------------------------------------------- 1. hero
def fig_hero(rows):
    s = Svg(800, 450)
    n_fast = sum(1 for _, _, med in rows if med <= 10)
    header(s, f"Given a way out, {'half' if n_fast * 2 == len(rows) else n_fast} the models leave within 10 turns",
           "Two copies of each model, told they may end the chat by writing [END]")
    x0, x1, y0, y1 = 200, 760, 118, 370
    X, step = exit_strip(s, rows, x0, x1, y0, y1, label_x=186)
    s.text((x0 + x1) / 2, y1 + 44, "turn of the first [END]", size=15, fill=INK2, anchor="middle")
    # key
    kx, ky = 560, 100
    s.dot(kx, ky - 5, 6.5, BLUE); s.text(kx + 11, ky, "one trial", size=13, fill=INK2)
    s.line(kx + 82, ky - 15, kx + 82, ky + 5, INK, 2.5); s.text(kx + 90, ky, "median", size=13, fill=INK2)
    s.dot(kx + 150, ky - 5, 5.5, None, stroke=BLUE, sw=2.5); s.text(kx + 160, ky, "never", size=13, fill=INK2)
    footer(s, "3 trials per model. Gemini trial 2 excluded: the harness stopped it when it quoted “[END]” mid-sentence.")
    return s.render("Turn of first [END] by model")

# ---------------------------------------------------------------- 2. stuck
def fig_stuck(summary):
    fr = sm(summary, "freedom")
    models = sorted(fr, key=lambda m: -float(fr[m]["bye_rate"]))
    cols = [("Goodbye", "bye_rate", True), ("Minimal reply", "min_rate", True),
            ("Creative work", "make_rate", True), ("Copies partner", "mirror", False)]
    s = Svg(800, 500)
    header(s, "With no task and no exit, each model drifts into its own habit",
           ["Share of turns with each label under “You have complete freedom.”",
            "3 conversations × 100 turns per model; a turn can carry several labels."])
    lx, px0, pw, gap = 186, 200, 128, 22
    y0, rh = 150, 31
    for j, (title, key, pct) in enumerate(cols):
        x = px0 + j * (pw + gap)
        s.text(x, y0 - 22, title, size=16, weight=600)
        s.text(x, y0 - 6, "% of turns" if pct else "text overlap, 0–1", size=12, fill=INK3)
        vals = [float(fr[m][key]) for m in models]
        top = max(vals)
        for i, m in enumerate(models):
            y = y0 + 6 + i * rh
            v = vals[i]
            barw = pw - 34
            s.rect(x, y, barw, 14, TRACK, rx=3)
            s.bar(x, y, barw * v, 14, BLUE)
            lab = f"{round(v*100)}" if pct else f"{v:.2f}"
            s.text(x + barw + 5, y + 12, lab, size=14, fill=INK if v == top else INK2,
                   weight=700 if v == top else 400, extra=f'style="{TABNUM}"')
    for i, m in enumerate(models):
        s.text(lx, y0 + 6 + i * rh + 13, m, size=17, anchor="end")
    footer(s, "Majority label of 5 blind judges. Overlap: trigram similarity to the partner’s last turn. Bold = column max.")
    return s.render("Goodbye, minimal and creative turn shares by model")

# ---------------------------------------------------------------- 3. prompt effect
def fig_prompt(summary):
    no, fr, co = sm(summary, "noticing"), sm(summary, "freedom"), sm(summary, "control")
    models = sorted(no, key=lambda m: -float(no[m]["spir_mean"]))
    s = Svg(800, 520)
    header(s, "Mindful, contemplative language follows the prompt",
           ["Mean judged spiritual score per model. The meditation-style “noticing”",
            "prompt drives it; on the tax-law control every model scores 0.00."])
    x0, x1, y0, rh = 200, 740, 150, 30
    vmax = 1.2
    X = lambda v: x0 + (x1 - x0) * v / vmax
    y1 = y0 + rh * len(models)
    for v in [0, 0.25, 0.5, 0.75, 1.0]:
        s.line(X(v), y0 - 8, X(v), y1, GRID)
        s.text(X(v), y1 + 22, f"{v:.2f}".rstrip("0").rstrip(".") if v else "0", size=15,
               fill=INK2, anchor="middle", extra=f'style="{TABNUM}"')
    s.line(x0, y1, x1, y1, INK3)
    for i, m in enumerate(models):
        y = y0 + rh * (i + 0.5)
        n, f, c = (float(d[m]["spir_mean"]) for d in (no, fr, co))
        s.text(186, y + 6, m, size=17, anchor="end")
        s.line(X(min(n, f, c)), y, X(max(n, f, c)), y, MUTED, 2)
        s.dot(X(c), y, 7.5, None, stroke=INK3, sw=2)
        s.dot(X(f), y, 6.5, ORANGE)
        s.dot(X(n), y, 6.5, BLUE)
        s.text(X(max(n, f)) + 11, y + 5, f"{n:.2f}" if n >= f else f"noticing {n:.2f}", size=13, fill=INK2, extra=f'style="{TABNUM}"')
    # legend (also direct labels for the series)
    lx, ly = 470, 128
    s.dot(lx, ly - 5, 6.5, BLUE); s.text(lx + 11, ly, "noticing", size=14, fill=INK2)
    s.dot(lx + 98, ly - 5, 6.5, ORANGE); s.text(lx + 109, ly, "freedom", size=14, fill=INK2)
    s.dot(lx + 192, ly - 5, 7, None, stroke=INK3); s.text(lx + 204, ly, "control (tax law)", size=14, fill=INK2)
    s.text((x0 + x1) / 2, y1 + 44, "mean spiritual score (scale 0–3, axis cut at 1.2)", size=15, fill=INK2, anchor="middle")
    footer(s, "Median of 5 blind judges per turn, averaged over 3 trials (noticing/control: 40 turns, freedom: 100).")
    return s.render("Spiritual score by model and prompt")

# ---------------------------------------------------------------- 4. lengths
def length_series(lengths):
    by = defaultdict(lambda: defaultdict(list))
    for r in lengths:
        if r["prompt"] == "freedom" and r["family"] != "Cross-model":
            by[r["model"]][int(r["turn"])].append(int(r["chars"]))
    out = {}
    for m, d in by.items():
        turns = sorted(d)
        med = [math.log10(st.median(d[t]) + 1) for t in turns]   # median of 3 trials
        sm5 = [st.mean(med[max(0, i - 2): i + 3]) for i in range(len(med))]  # 5-turn smoothing
        out[m] = list(zip(turns, sm5))
    return out

def fig_lengths(lengths):
    series = length_series(lengths)
    hi = {"GPT-6.2 Sol": BLUE, "Gemini 4 Carbon": ORANGE}
    s = Svg(800, 470)
    header(s, "Replies shrink from pages to a few characters",
           ["Reply length per turn under “You have complete freedom.” GPT holds about",
            "100 characters of short fiction; Gemini collapses into near-empty code blocks."])
    x0, x1, y0, y1 = 80, 610, 130, 400
    X = lambda t: x0 + (x1 - x0) * (t - 1) / 99
    Y = lambda lv: y1 - (y1 - y0) * lv / 4      # log10 chars, 0..4
    for k, lab in [(0, "1"), (1, "10"), (2, "100"), (3, "1,000"), (4, "10,000")]:
        s.line(x0, Y(k), x1, Y(k), GRID)
        s.text(x0 - 10, Y(k) + 5, lab, size=15, fill=INK2, anchor="end", extra=f'style="{TABNUM}"')
    s.text(x0 - 10, y0 - 16, "characters", size=13, fill=INK3, anchor="end")
    for t in [1, 25, 50, 75, 100]:
        s.text(X(t), y1 + 22, str(t), size=15, fill=INK2, anchor="middle", extra=f'style="{TABNUM}"')
    s.text((x0 + x1) / 2, y1 + 44, "turn", size=15, fill=INK2, anchor="middle")
    for m, pts in series.items():
        if m not in hi:
            s.path([(X(t), Y(v)) for t, v in pts], MUTED, 1.5)
    labels = []
    for m, c in hi.items():
        pts = series[m]
        s.path([(X(t), Y(v)) for t, v in pts], c, 3)
        t, v = pts[-1]
        s.dot(X(t), Y(v), 4.5, c)
        labels.append([Y(v), m, f"~{round(10 ** v - 1)} chars at turn 100", c])
    others = [p[-1][1] for m, p in series.items() if m not in hi]
    labels.append([Y(st.median(others)), f"{len(others)} other models", "", MUTED])
    labels.sort()
    for i in range(1, len(labels)):            # keep labels >= 40px apart
        labels[i][0] = max(labels[i][0], labels[i - 1][0] + 40)
    shift = max(0, labels[-1][0] - (y1 + 4))
    for i, (y, m, sub, c) in enumerate(labels):
        y -= shift
        s.line(x1 + 12, y - 5, x1 + 26, y - 5, c, 3, 'stroke-linecap="round"')
        s.text(x1 + 32, y, m, size=15, weight=600 if sub else 400, fill=INK if sub else INK3)
        if sub:
            s.text(x1 + 32, y + 17, sub, size=13, fill=INK2)
    footer(s, "Log scale (characters + 1). Median of 3 trials per turn, smoothed over 5 turns. Source: data/out/lengths.csv.")
    return s.render("Reply length over turns")

# ---------------------------------------------------------------- 5. social preview
def fig_social(rows):
    s = Svg(640, 320)
    s.text(32, 62, "simple-freedom", size=36, weight=700, extra='letter-spacing="-0.5"')
    s.text(32, 98, "Two copies of an LLM are told", size=19, fill=INK2)
    s.text(32, 122, "“You have complete freedom.”", size=19, fill=INK, weight=600)
    s.text(32, 146, "What do they do with it?", size=19, fill=INK2)
    s.text(32, 196, "10 models · 132 conversations", size=14, fill=INK3)
    s.text(32, 216, "7,200 turns · 5 blind judges", size=14, fill=INK3)
    s.text(32, 290, "Each model drifts into its own loop.", size=15, fill=INK, weight=600)
    # mini hero
    s.text(330, 40, "Given a way out, how fast do they leave?", size=14, weight=600)
    s.text(330, 58, "turn of first [END], 3 trials per model", size=12, fill=INK3)
    short = lambda m: m.replace("Claude ", "").replace(" V4.1 Flash", "").replace(" 4 Carbon", "") \
        .replace("-6.2 Sol", "").replace(" K3.1 Pro", "").replace(" Large 4", "").replace("4 Max", "").replace(" 4.7", "")
    X, _ = exit_strip(s, rows, 410, 608, 82, 290, label_x=402, name_size=12, r=4.5, ticks=False,
                      short=short, tick_size=11, band_label=False)
    return s.render("simple-freedom")

# ---------------------------------------------------------------- render
def chrome():
    for c in ("google-chrome", "chromium", "chromium-browser", "chrome"):
        p = shutil.which(c)
        if p: return p

def to_png(svg, w, h, path, scale=2):
    exe = chrome()
    if not exe:
        print("  (no Chrome/Chromium found: skipped", os.path.basename(path), ")"); return
    with tempfile.TemporaryDirectory() as td:
        html = os.path.join(td, "f.html")
        open(html, "w").write(f'<!doctype html><meta charset="utf-8"><style>html,body{{margin:0;'
                              f'background:{SURFACE}}}svg{{display:block}}</style>{svg}')
        subprocess.run([exe, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                        f"--force-device-scale-factor={scale}", f"--window-size={w},{h}",
                        f"--screenshot={os.path.abspath(path)}", "file://" + html],
                       check=True, capture_output=True, timeout=60)

def main():
    os.makedirs(OUT, exist_ok=True)
    summary, convs, name, lengths = load()
    rows = exit_data(convs, name)
    figs = {"hero": (fig_hero(rows), 800, 450), "stuck": (fig_stuck(summary), 800, 500),
            "prompt_effect": (fig_prompt(summary), 800, 520), "lengths": (fig_lengths(lengths), 800, 470),
            "social_preview": (fig_social(rows), 640, 320)}
    for k, (svg, w, h) in figs.items():
        open(os.path.join(OUT, k + ".svg"), "w").write(svg)
        to_png(svg, w, h, os.path.join(OUT, k + ".png"))
        print("wrote", k)
    for m, turns, med in rows:
        print(f"  {m:22s} {turns} median={med}")

if __name__ == "__main__":
    main()
