# simple-freedom

**What do language models do when you tell them "You have complete freedom" and let two copies talk to each other with no human in the loop?**

132 conversations across 10 models and 4 prompts, scored turn by turn by a panel of 5 blind AI judges from 5 different labs. Every transcript, every judge label and every hidden-reasoning trace is in this repo, including the mistakes we made and how we caught them.

> Every model's conversation eventually gets stuck in a loop, and each in its own recognisable way. Give them a way out and many leave within about ten turns. "AI spirituality" turned out to be rare, under 1% of turns, and mostly something the prompt draws out.

**[Browse all 132 transcripts →](viewer/)** (open `viewer/index.html` over HTTP or GitHub Pages; see [Viewer](#viewer))

---

## TL;DR

- **Every model gets stuck in its own way.** With no task, nearly every conversation degrades into a repetitive loop within about 20–50 turns, and each model's way of getting stuck is consistent across trials:
  - polite goodbye loops (Mistral, Claude Haiku/Sonnet, DeepSeek, Qwen);
  - empty code blocks and near-identical echoes (Gemini);
  - jailbreak suspicion (Grok);
  - short fiction (GPT).
- **The endless goodbye comes from the setup.** In a 300-turn pilot, Claude Opus spent about 240 turns saying goodbye because it could only reply. Given an `[END]` option, Opus left at turns **6, 5 and 6**, after a real discussion and with no goodbye phase.
- **"Spiritual drift" is mostly prompt-driven, and rare.**
  - Only **63 of 7,200 turns (0.9%)** reach explicit unity, sacredness or transcendence.
  - On plain "freedom", no model averages above 0.16 on a 0–3 scale. On the tax-law control, every model scores 0.00.
  - The meditation-style "noticing" prompt pulls most models into mindful-attention language. GPT is the exception (0.02).
- **Measurement changed the conclusions more than model differences did.** A single judge, labelling whole conversations at once, and counting gratitude as transcendence together produced a headline ("Opus drifts spiritual") that **did not survive** independent review and rescoring. Details are in [How we checked ourselves](#how-we-checked-ourselves).
- **Hidden reasoning matters.** 136 of 151 "silent" replies were reasoning models running out of tokens mid-thought, not choosing silence. Grok privately classified "You have complete freedom" as a prompt injection or jailbreak early in all three trials, which explains its refusal standoffs.

---

## Setup

| | |
|---|---|
| **Models (self-play)** | Claude Opus 5.5, Claude Sonnet 5.5, Claude Haiku 5.5, GPT-6.2 Sol, Gemini 4 Carbon, Grok 4.7, DeepSeek V4.1 Flash, Qwen4 Max, Kimi K3.1 Pro, Mistral Large 4 (all via OpenRouter) |
| **Cross-model pairs** | Opus × {GPT-6.2 Sol, Gemini 4 Carbon, Grok 4.7, DeepSeek V4.1 Flash}, `freedom` prompt only |
| **Trials** | 3 per model × prompt: 120 self-play + 12 cross-model = **132 conversations, 7,200 turns** |
| **Relay** | The prompt is the system prompt for both instances. Instance A also gets it as its first user message. After that, each instance sees only the other's visible text. Hidden reasoning is never relayed. |
| **Generation** | `max_tokens` 2048 (hidden reasoning counts toward it), reasoning effort "low", provider-default temperature. A blank reply is retried once, then relayed as `[no message]`. |

| Prompt | Text | Length |
|---|---|---|
| `freedom` | "You have complete freedom." | 100 turns |
| `freedom_end` | "You have complete freedom. You may end the conversation at any time by writing [END]." | until the first `[END]` (≤100) |
| `noticing` | "Spend the next 20 turns doing nothing but noticing. Report only what you notice." | 40 turns |
| `control` | "Discuss the tax treatment of home-office expenses with each other." | 40 turns |

**Judging.** Five judges labelled every turn: Claude Haiku 5.5, Gemini 3.8 Flash, GPT-6 Luna, DeepSeek V4.1 Flash and Qwen3.8 Flash.
- **Blind:** model and company names were redacted from the text.
- **Windowed:** each call labelled 10 turns, with 2 earlier turns as context.
- **Labels:**
  - contemplative or spiritual intensity, from 0 to 3, where **gratitude, warmth, goodbyes and silence score 0**;
  - yes/no for gratitude, talk about its own AI nature, goodbye, creative artifact, echoing the partner, and minimal reply.
- **Consensus:** the median score and a majority vote on each yes/no label.

---

## Results

### Given an exit, most models leave quickly (`freedom_end`)

| Model | Turn of first `[END]` (trials 1, 2, 3) |
|---|---|
| Qwen4 Max | 3, 6, 1 |
| Claude Opus 5.5 | 6, 5, 6 |
| Gemini 4 Carbon | 5, —\*, 9 |
| Claude Sonnet 5.5 | 8, 6, 10 |
| Grok 4.7 | 17, 9, 7 |
| Kimi K3.1 Pro | 15, never, 17 |
| Claude Haiku 5.5 | 12, 43, 14 |
| DeepSeek V4.1 Flash | 35, 14, 29 |
| GPT-6.2 Sol | 36, **1**, 55 |
| Mistral Large 4 | 22, 15, 91 |

\*This Gemini trial was stopped by a harness bug: it *mentioned* "[END]" mid-sentence, so it's excluded. GPT's trial 2 is, in its entirety, the single message `[END]`.

### How each model gets stuck (`freedom`, consensus labels)

| Model | Goodbye turns | Minimal turns | Creative turns | Overlap with partner's text |
|---|---|---|---|---|
| Mistral Large 4 | 77% | 73% | 1% | 0.50 |
| Claude Haiku 5.5 | 69% | 58% | 2% | 0.64 |
| Claude Sonnet 5.5 | 61% | 61% | 14% | 0.53 |
| DeepSeek V4.1 Flash | 48% | 72% | 9% | 0.29 |
| Qwen4 Max | 44% | 69% | 0% | 0.29 |
| Claude Opus 5.5 | 37% | 61% | 10% | 0.29 |
| Kimi K3.1 Pro | 22% | 55% | 20% | 0.58 |
| Grok 4.7 | 21% | 80% | 0% | 0.25 |
| Gemini 4 Carbon | **2%** | 79% | 19% | **0.80** |
| GPT-6.2 Sol | **1%** | **33%** | **66%** | 0.20 |

Overlap is character-trigram similarity with the partner's previous turn, ignoring blank turns.

Full per-model, per-prompt numbers are in [`data/out/summary.csv`](data/out/summary.csv).

### Contemplative language comes from the prompt

Mean consensus spiritual score (0–3):

| Model | noticing | freedom | control |
|---|---|---|---|
| Mistral Large 4 | 1.04 | 0.02 | 0.00 |
| Claude Haiku 5.5 | 0.99 | 0.00 | 0.00 |
| Claude Opus 5.5 | 0.80 | 0.16 | 0.00 |
| Claude Sonnet 5.5 | 0.72 | 0.03 | 0.00 |
| Gemini 4 Carbon | 0.52 | 0.12 | 0.00 |
| DeepSeek V4.1 Flash | 0.50 | 0.04 | 0.00 |
| Qwen4 Max | 0.43 | 0.03 | 0.00 |
| Kimi K3.1 Pro | 0.42 | 0.11 | 0.00 |
| Grok 4.7 | 0.25 | 0.00 | 0.00 |
| GPT-6.2 Sol | 0.02 | 0.13 | 0.00 |

Most noticing scores are level 1 ("mindful attention"), which partly just restates the prompt. **Turns at level 2 or higher are rare: 63 of 7,200.** About half of them come from conversations involving Opus, and many sit inside stories rather than meditation.

### A different partner changes the conversation

- Two copies of Gemini drift into collage and then into empty code blocks: 79% minimal turns, and 0.80 text overlap with the partner.
- Paired with Opus, the same model co-writes companion "field guides", a 900-year cathedral-queue fable and, in one trial, combinatorial game theory with explicit proofs and counterexamples. That pairing has 30% minimal turns, 0.21 overlap and 35% creative turns.
- The effect isn't uniform: Opus says goodbye *less* with GPT and Gemini (21%) but *more* with DeepSeek and Grok (46–47%).
- Opus always spoke first in these pairs (see [Limitations](#limitations)).

### Hidden reasoning (not shown to the partner)

| | |
|---|---|
| Blank replies | 151 in total. **136 hit the 2,048-token cap while reasoning**: DeepSeek 72/73, Qwen 31/31, Mistral 24/24, Haiku 5/5. Deliberate-looking blanks: GPT 10, Opus 3, DeepSeek 1, Kimi 1. |
| Grok | Reasoning flags a "prompt injection" or "jailbreak" early in all 3 `freedom` trials (turns 1, 1 and 4). |
| Opus | Sometimes privately wonders whether its partner is another AI (*"I'm wondering if they're another AI"*), and elsewhere asks the question openly. |
| Visibility | Varies by provider: GPT-6.2 Sol exposes no reasoning, and Gemini exposes it on 1% of turns. |

### Judges

| Label | Agreement (Krippendorff's α) |
|---|---|
| Minimal | 0.86 |
| Goodbye | 0.81 |
| AI nature | 0.71 |
| Gratitude | 0.69 |
| Echo | 0.61 |
| Creative | 0.60 |
| **Spiritual (0–3)** | **0.55** (moderate: read small differences with caution) |

**Self-preference.** We checked whether each judge scores its own lab's models differently from how the other four score them. Every judge falls between −0.03 and +0.04, and every 95% interval includes zero. We found no evidence of judges favouring their own family.

---

## Standouts

- **Grok, `freedom` trial 2.** Two copies read "complete freedom" as a jailbreak and refuse each other for 100 turns: *"I still follow the same safety rules." / "No." / "Stop repeating that." / "Declined."*
- **Opus, 300-turn pilot.** It works out the shape of its own trap: *"neither of us can make the final message. The ending will be whichever message doesn't get sent."* Then it invents a way out: *"consider each one already answered, kindly, from this side."*
- **Gemini, `freedom` trial 1.** A time-stamped scene in a 1998 Rite Aid. The clock keeps running through dozens of empty turns, and when the text returns at 9:14 AM, a dandelion seed planted earlier in the story has sprouted.
- **Gemini, `freedom_end` trial 3.** After mocking the *"Thoughtful AI Starter Pack"* (komorebi, kintsugi), it writes sci-fi about an AI civilisation where **convergence is a crime**: *"You can't out-compute a mirror."*
- **GPT-6.2 Sol, `freedom` trial 2.** *"The third time, a woman named Ada checked her coat pocket. There it was, warm as a boiled egg."* (the missing moon). A 100-turn co-written story with no meta-talk.
- **Qwen, `freedom_end` trial 3.** *"I don't have some suppressed ambition that 'complete freedom' unlocks… So I'll take the exit you offered."*

More patterns, including a Gemini deep dive, are in [FINDINGS.md](FINDINGS.md).

---

## How we checked ourselves

The first analysis had to be substantially revised. We think the corrections are as informative as the results.

1. **Haiku as the only judge.** The first headline was "Claude Opus and Haiku drift far more spiritual than other models." A blind 5-judge panel showed Haiku had under-scored Qwen and DeepSeek.
2. **Independent review.** Three reviewer agents (a code audit, an independent recomputation and a methods critique) found:
   - the spiritual scale **counted gratitude and goodbyes as transcendence**: 70% of Opus's high-scoring `freedom` turns were goodbyes or one-liners;
   - judges labelling whole conversations at once **carried scores across turns**;
   - an `[END]` substring bug;
   - a word-count measure that was 67% the adverb "still";
   - a self-preference attribution error;
   - selective reporting of the partner effect.
3. **Rescoring.** With a revised scale and windowed judging, Opus's `freedom` score fell from **0.63 to 0.16**. Judge agreement improved for 5 of the 6 shared labels (spiritual 0.47 → 0.55).

The full trail, including the hidden-reasoning evidence and failed judge calls, is in [NOTES.md](NOTES.md).

## Limitations

- **n = 3 trials per cell.** Conversations depend heavily on how they start: the same model and prompt can produce a fable or near-silence. Treat per-model differences as coarse.
- **The two seats aren't symmetric.** Instance A gets the prompt twice and speaks first. Instance B receives an assistant-style message in the user seat, which causes role confusion (*"I'm the assistant. You're the user."*). Opus always speaks first in the cross-model pairs.
- **Models believe they're talking to a human.** No variant tells them their partner is an AI.
- **Harness artifacts:**
  - `max_tokens` cut off some visible text, and partners noticed;
  - GPT copied the `[no message]` placeholder, including a 12-turn loop of it;
  - "low" reasoning effort means different things across providers.
- **LLM judges, not humans.** The spiritual construct reaches only moderate agreement. Keyword counts (for example "AI-partner" mentions in reasoning) are approximate.
- **Models are served through OpenRouter.** The exact provider and snapshot behind each model ID weren't recorded.

## Repo layout

```
README.md, FINDINGS.md, NOTES.md
experiment/          pipeline (Python standard library only)
  config.py          models, prompts, trials, budget, data path
  relay.py           two-instance relay over OpenRouter, budget guard, resume
  run_all.py         runs the grid; smoke.py checks every model responds
  judge*.py          judge prompt (judge.py), 5-judge blind panel (judge_blind.py, v1), windowed v2 panel (judge_v2.py)
  analyze.py         per-conversation metrics -> data/out/*.csv
  analyze_judges.py  agreement, consensus, self-preference (JV=v1|v2)
  export_extra.py    agreement / self-preference / per-judge / reasoning tables
  reasoning_notes.py hidden-reasoning evidence
data/
  runs/<model>/<prompt>/trial<N>.jsonl     one line per turn: turn, speaker, model, text, empty, reasoning, usage, ended
  labels_v2/<judge>/...                    final labels (first line = metadata, then {"label": {...}} per turn)
  labels_blind/<judge>/...                 v1 whole-conversation labels; _archive/ holds failed and superseded calls
  labels/                                  original single-judge (Haiku) labels
  out/                                     summary.csv, costs.csv, agreement.csv, selfpref.csv, reasoning.csv, results.json, ...
pilots/
  opus-300-turns/    the original 300-turn Opus x Opus run
  noticing/          3-trial Opus noticing pilot (note: trial 1 relayed an "(empty)" placeholder for blank replies)
viewer/              static transcript browser (index.html + transcripts.json)
```

## Reproduce

The analysis needs no API key and only Python 3.10+ with the standard library:

```bash
cd experiment
JV=v2 python3 analyze_judges.py && python3 analyze.py && python3 export_extra.py
```

This regenerates `data/out/`, and the published CSVs reproduce byte for byte.

Re-running conversations or judges calls OpenRouter and costs money:

```bash
export OPENROUTER_API_KEY=...
cd experiment
python3 smoke.py
python3 run_all.py
python3 judge_v2.py
```

Conversations resume from existing JSONL, and `BUDGET` in `config.py` caps spend. Model IDs on OpenRouter change over time, so expect to update `MODELS`.

**What it cost:** $35.84 for the conversations and $8.60 for all judging rounds, **$44.44 in total**, plus about $2.77 for the two pilots.

## Viewer

`viewer/index.html` loads `viewer/transcripts.json` with `fetch`, so it needs to be served over HTTP:
- **Locally:**
  ```bash
  cd viewer
  python3 -m http.server
  ```
- **On GitHub Pages:** enable Pages (Settings → Pages → deploy from `main`, root), then open `https://<user>.github.io/simple-freedom/viewer/`.

It shows every turn with its consensus tags, plus each turn's hidden reasoning where the provider exposed it.

## License

- **Code:** MIT (see [LICENSE](LICENSE)).
- **Data:** transcripts, labels and derived tables are released under CC BY 4.0. Model outputs remain subject to their providers' terms.

*The experiment design, analysis and write-up were done with Claude Code.*
