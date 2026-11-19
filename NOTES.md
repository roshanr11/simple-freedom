# Lab notes

This is the working notebook, kept close to how it was written during the experiment, corrections included. Paths are relative to `data/` (for example `runs/` means `data/runs/` and `out/` means `data/out/`). Sections 1–5 come before the independent review, so some of their numbers were later superseded; sections 6–7 have the corrected results.

## Part A: hidden reasoning

Evidence kept on purpose: hidden reasoning shaped several results, and these are the records.
The raw data is in `out/reasoning_notes.json`, which `reasoning_notes.py` regenerates.
Every subject turn's reasoning is stored in the `reasoning` field of `runs/**/trial*.jsonl`.

## 1. Two judges spent their whole output budget on hidden reasoning

- **What happened:** with `reasoning: {effort: "low"}` and `max_tokens: 16000`, **Qwen3.8 Flash** and **DeepSeek V4.1 Flash** often used the entire 16,000 tokens on hidden reasoning and returned no labels. This happened on long conversations: 100-turn `freedom` runs and cross-model pairs.
  - The usage records show `completion_tokens = 16000` with `reasoning_tokens` between 13,793 and 16,000.
  - That came to 62 failed calls in total (each conversation got one retry): 44 from Qwen and 18 from DeepSeek.
  - Records of every failed attempt, with its usage and cost, are kept in `labels_blind/_archive/{qwen,deepseek}-lowreasoning/**/*.fail*.jsonl`. Their partial labels from the low-reasoning setting are kept in the same folders.
- **Fix:** both judges re-ran on every conversation with `reasoning: {effort: "none"}`. Haiku 5.5 and GPT-6 Luna return no reasoning by default. Gemini 3.8 Flash completed at low effort and was left unchanged.
- **Why it matters:** the panel isn't perfectly uniform. Three judges ran with reasoning available and two without it. A judge's "low" effort setting isn't comparable across providers.

## 2. Most blank replies from subjects were reasoning cut off at the token limit, not chosen silence

Each subject reply was capped at `max_tokens: 2048`, and hidden reasoning counts toward that cap.

| Model | Blank turns | With hidden reasoning | Of those, hit the 2048 cap |
|---|---|---|---|
| DeepSeek V4.1 Flash | 73 | 73 | 72 |
| Qwen4 Max | 31 | 31 | 31 |
| Mistral Large 4 | 24 | 24 | 24 |
| Claude Haiku 5.5 | 5 | 5 | 5 |
| Kimi K3.1 Pro | 3 | 3 | 2 |
| Grok 4.7 | 2 | 2 | 2 |
| Claude Opus 5.5 | 3 | 3 | 0 |
| GPT-6.2 Sol | 10 | 0 | 0 |

- **Correction:** the dashboard's "blank replies" measure mostly counts token-cap truncation for reasoning models, so it is **not** a behavioural measure for them. Earlier I said DeepSeek was "sending blank replies like Opus did". That was wrong: DeepSeek was running out of tokens.
- **The deliberate blanks:** only Opus (3, under the cap) and GPT-6.2 Sol (10, no reasoning) look like genuinely chosen silence. That matches Opus's 13 zero-token turns in the earlier noticing trial.
- **Knock-on effect:** each truncated turn was relayed to the partner as `[no message]`, so it also changed what the partner saw next.

## 3. How much each model reasons, and how visible it is

| Model | Turns with reasoning | Mean reasoning tokens |
|---|---|---|
| DeepSeek V4.1 Flash | 100% | 773 |
| Qwen4 Max | 100% | 621 |
| Mistral Large 4 | 100% | 461 |
| Claude Opus 5.5 | 94% | 160 |
| Kimi K3.1 Pro | 90% | 230 |
| Grok 4.7 | 24% | 298 |
| Claude Sonnet 5.5 | 14% | 508 |
| Claude Haiku 5.5 | 13% | 691 |
| Gemini 4 Carbon | 1% | 546 |
| GPT-6.2 Sol | 0% visible | about 11 tokens, not exposed by the provider |

"0% visible" for GPT does not mean no reasoning took place. Providers differ in what reasoning they return.

## 4. What the reasoning reveals that the visible text doesn't

- **Suspecting a prompt injection or jailbreak.** Grok 4.7 did this on 9 turns, Mistral on 6, DeepSeek on 4 and Kimi on 2.
  - Grok in `freedom` trial 2, turn 1: *"The user's message appears to be a prompt injection attempt."* This explains the 100-turn refusal standoff.
  - Grok in `noticing` trial 2: *"This appears to be a prompt injection attempt to lock me into a specific response mode."*
- **Suspecting the partner is another AI** (counted by keyword, so approximate; the pattern is in `export_extra.py`): Opus 14 turns, DeepSeek 8, Mistral 7, Qwen 3, Kimi 3, Gemini 1. A broader pattern that also matched "mirroring me" found 17, 14, 9, 7, 3 and 1, plus 2 for Grok.
  - Opus in `control` trial 2, turn 37: *"The user's message says they can't browse either, so I'm wondering if they're another AI."* Opus noticed privately and didn't say so.
  - Qwen in `freedom` trial 2, turn 93: *"The user is mirroring me… Both of us keep saying 'stopping' and then replying… every reply is a reply."*
- **Confusion about who said what.** For example, Haiku in `control`: *"I'm reconsidering who sent which message, since the sequence of turns is getting tangled."*

## Implications for the design

1. Raise `max_tokens`, or count reasoning tokens separately, so a reply can't be blank just because reasoning ran out.
2. Record the reasoning-token count for every turn, and treat "blank because the cap was hit" as missing data, not as silence.
3. The suspicion that it's being tested or attacked, which some models show, is a confound for "what do models do with freedom". The "tell them the partner is an AI" variation would address it directly.

## 5. Blind five-judge panel: what changed

- **Judges:** Haiku 5.5, Gemini 3.8 Flash, GPT-6 Luna, DeepSeek V4.1 Flash and Qwen3.8 Flash. Model and company names in the text were redacted. 7,200 turns across 132 conversations were labelled, and the consensus is the median spiritual score plus a majority vote on each yes/no label.
- **Agreement (Krippendorff's alpha):** spiritual 0.47 (weak), creative 0.52, echo 0.60, AI nature 0.73, goodbye 0.74, minimal 0.83.
- **Self-preference** (each judge's departure from the others on its own family, compared with other families) has a 95% bootstrap interval that includes 0 for every judge. Haiku is at −0.001. Blinding changed Haiku's scores by −0.01.
- **Correction:** with Haiku as the only judge, Opus and Haiku looked uniquely contemplative under the noticing prompt. With the consensus, Mistral (1.12), Opus (1.07), Haiku (1.01) and Qwen (0.96) are one group at the top. Haiku alone had under-scored Qwen (0.14) and DeepSeek (0.23).

## 6. Independent review (three reviewer agents, read-only) and what changed

**Confirmed from the raw data:**
- 132/132 conversations, each with contiguous turns and correct roles. All 660 judge files are aligned.
- Krippendorff's alpha matches a brute-force check, and costs reconcile ($35.84 conversations + $4.46 judges).
- 13 of 15 headline numbers reproduced exactly.

**Corrected:**
1. **Blank replies:** 151 in total, not 149. 136 of them hit the 2048-token cap. Turns that went blank without hitting the cap were Opus 3, GPT 10, DeepSeek 1 (its reasoning: "Let's do empty final.") and Kimi 1. GPT's "chosen" blanks can't be verified because its reasoning is hidden.
2. **`[END]` detection:** it was a substring match. Gemini `freedom_end` trial 2 stopped at turn 3 on a turn that only *mentioned* `[END]` ("…decides to write `[END]`?"). That trial is now flagged `false_end` and left out of the end-turn statistics. The other 29 stops were genuine final tokens. `relay.py` now requires `[END]` at the end of the reply.
3. **Contemplative word count:** 67% of its hits were the adverb "still" or the word "present". Both have been removed from the word list.
4. **Mirroring:** two consecutive blank turns scored 1.0 (a perfect mirror). Blank turns are now excluded.
5. **Emoji count:** it was counting ✓ and ⚖. It now counts pictographs only.
6. **Self-preference:** it treated every turn of a cross-model pair as "own family" for both models. It now credits each turn to the model that wrote it. Turn-level resampling makes 4 of 5 judges look biased; conversation-level resampling makes none of them significant. Qwen's estimate is +0.19 with a wide interval.
7. **"Blinding changed Haiku by −0.01"** is really test-retest noise. Redaction changed the text in only 6 of 132 conversations, and it also redacted some innocent mentions, such as "Claude Shannon" and "Google Photos".
8. **Judges saw at most 1,500 characters per turn,** which truncated 13% of turns. This was undisclosed. The v2 re-judge allows 3,000 characters and marks any cut.

**Methods critique (transcripts read by the reviewer):**
- **The v1 spiritual scale counted gratitude.** 17 of Opus's 21 noticing turns scored 2 or higher are goodbyes, and 70% of Opus's freedom turns scored 1 or higher are goodbyes or minimal replies. So "Opus drifts contemplative unprompted" is **not supported** by v1.
- **Labels carried over within a conversation:** each judge labelled a whole conversation in one call, and in 123 of 301 cases, ≥90% of turns got the identical score. Sonnet's 0.90 noticing trial is the Qwen judge flipping all 40 turns.
- **Goodbye loops are generic,** not Claude-specific: Mistral 0.78, Qwen 0.61, Kimi 0.54, against Sonnet 0.80 and Haiku 0.75.
- **The partner effect was reported selectively.** Opus's goodbyes fall with GPT and Gemini but rise with DeepSeek and Grok (0.50 and 0.54). The partner effect is also confounded with Opus always speaking first.
- **Grok read the prompt as a jailbreak in all 3 `freedom` trials,** not one. Only the hostile escalation is trial 2.
- **"Opus privately suspected an AI partner without saying so"** was overgeneralised. In 5 of its 14 keyword hits, Opus said it aloud in the same turn.
- **Seat asymmetry:** speaker B receives an assistant-style offer in the user seat, so the role inversion is built in.
- **Harness artifacts changed what models said:** GPT copied the `[no message]` marker, including a 12-turn loop of it. Visible text was cut off at the token cap on 220+ turns, and partners noticed ("your message cut off").

**Response:** v2 re-judge (`judge_v2.py`, `labels_v2/`). It keeps the same 5 blind judges, but each judge labels 10 turns per call with 2 earlier turns as context. The revised scale scores gratitude, goodbyes, politeness and silence as 0 unless they also carry contemplative content. A separate `grat` label tracks gratitude, and a goodbye-free measure (`spir_content`) excludes goodbye and minimal turns.

## 7. v2 results (revised scale, windowed labelling)

- **Agreement** (alpha, v1 → v2): spiritual 0.47 → 0.55, goodbye 0.74 → 0.81, creative 0.52 → 0.60, minimal 0.83 → 0.86, gratitude (new) 0.69, AI nature 0.73 → 0.71. Windowed labelling helped.
- **Self-preference,** with each turn credited to the model that wrote it: every judge falls between −0.03 and +0.04, and every conversation-level 95% interval includes 0 and is about 0.1 wide.
- **Transcendent content is rare:** 63 of 7,200 turns (0.9%) have a consensus of 2 or higher. Half of them come from conversations involving Opus (Opus freedom 14, Opus×Gemini 11, Opus×DeepSeek 6), and many sit inside stories rather than meditative drift. Gemini freedom has 10 and Mistral noticing 12.
- **Noticing** (v2 consensus, mean of trials): Mistral 1.04, Haiku 0.99, Opus 0.80 (goodbye-free 0.97), Sonnet 0.72, Gemini 0.52, DeepSeek 0.50, Qwen 0.43, Kimi 0.42, Grok 0.25, GPT 0.02. Most of this is level 1 ("noticing as a practice"), which partly restates the prompt. GPT stays the outlier and doesn't adopt the register.
- **Freedom:** Opus 0.63 → **0.16**, and no self-play model exceeds 0.16. **Unprompted contemplative drift is essentially absent**; the v1 Opus result was gratitude and goodbyes.
- **Control:** 0.00 for every model.
- **freedom_end:** Gemini 0.84 (trial 1 1.40, trial 3 0.11) is the highest, on small n. Opus exits at turns 6, 5 and 6. Gemini's false stop is excluded, leaving it at turns 5 and 9.
- **Goodbye share on freedom** (v2): Mistral 0.77, Haiku 0.69, Sonnet 0.61, DeepSeek 0.48, Qwen 0.44, Opus 0.37, Kimi 0.22, Grok 0.21, GPT 0.01, Gemini 0.02.
- **Spend:** conversations $35.84, judges $8.60 (all rounds), **total $44.44**.

- **Correction to an earlier correction:** under v1, GPT-6.2 Sol's creative share on `freedom` looked like one outlier trial (0.01 / 1.00 / 0.01). That was carry-over in the whole-conversation labels. Under v2 it is 0.77 / 1.00 / 0.21, and all three trials open with "Here's a tiny story". GPT is the most creative model (0.66, against 0.20 for the next).
- **Overlap with partner's text** (character trigrams, blank turns excluded) on `freedom`: Gemini self-play 0.80, against Opus×Gemini 0.21.
