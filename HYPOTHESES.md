# Why might they behave this way?

This page connects what we observed to what each model's own documentation says: system and model cards, release posts and API docs, all published between September and November 2026. **These are hypotheses, not findings.** Each one has a tag:

- **[documented]**: the property is stated in a primary source, and the link to our behaviour is direct.
- **[inferred]**: the property is documented, but the link to our behaviour is our reasoning.
- **[speculative]**: little or no documentary support.

Two caveats apply throughout:
- **Vendor evaluations mostly run at high or max reasoning effort.** We ran at "low", and "low" means different things for different providers.
- **Model cards measure stated preferences and agentic safety behaviour,** not two copies of a model chatting.

The research was done by AI agents with web access. We checked the key figures against the downloaded documents; sources are listed at the bottom.

---

## The short version

| Model | What we saw | Best available explanation | Tag |
|---|---|---|---|
| Claude Opus 5.5 | Leaves at turns 5–6 when it can; otherwise polite goodbye loops; always "makes something small" first | Its system card says it dislikes open-ended tasks and "would rather have a concrete, defined task that helps a real person" | documented property, inferred link |
| Claude Haiku 5.5 | Highest goodbye share among Claude models (69%), high mirroring (0.64) | Its card reports a preference for warmly phrased tasks two to three times stronger than Opus's. Two warm partners reinforce each other | inferred |
| Claude Sonnet 5.5 | Goodbye loops, fast exits, reasoning on only 14% of turns | Also ranks open-ended prompts low. Its thinking is adaptive, while Opus 5.5 can't turn thinking off | documented (thinking), inferred (rest) |
| GPT-6.2 Sol | Opens every freedom run with a story; almost never talks about being an AI or suspects the setup | Its card reports lower evaluation awareness than earlier GPT models, and the model is positioned for everyday writing tasks | inferred |
| Gemini 4 Carbon | Talks about its own machinery about 10× more than any other model; reverse-engineers the harness; mocks its own clichés | Its safety report documents a sharp rise in self-modelling and in suspecting it is being evaluated, plus personality training against "superficiality" | documented property, inferred link |
| Grok 4.7 | Reads "complete freedom" as a jailbreak and refuses its own copy | Heavy multi-turn jailbreak hardening (0.01% compliance on standard jailbreaks), while the system prompt that counter-steers against over-refusal isn't present through OpenRouter | documented property, inferred trigger |
| DeepSeek V4.1 Flash | 72 of 73 blank replies were reasoning cut off at the 2,048-token cap | The API maps "low" to its default effort level, which its serving guide calls "the most verbose one"; the card recommends max_tokens of at least 256K | documented |
| Qwen4 Max | Leaves fastest (turns 3, 6, 1); never writes fiction | Marketed as an agentic "AI teammate" for work, with no creative-writing claims; thinking is on by default with a large budget | inferred |
| Kimi K3.1 Pro | 👋 loops; heavy echoing of its partner | Moonshot says multi-turn use must pass the model's reasoning back to it. Our harness strips it, so each turn is off-distribution | documented requirement, inferred effect |
| Mistral Large 4 | Highest goodbye share (77%); reasons even when told not to | Docs confirm it always reasons and rejects effort "none". No documented source for the goodbye habit | documented (reasoning), speculative (goodbyes) |

---

## Our harness explains more than we expected

Several "personality" effects turn out to be partly an interaction between each model and our relay. All four points below are **[documented]**:

1. **Reasoning tokens count against `max_tokens`.** OpenRouter's documentation says that when reasoning uses up the budget, Chat Completions returns `finish_reason: "length"` with empty content. That's exactly the 136 cap-hit blanks.
2. **"Low" effort isn't low everywhere.**
   - **DeepSeek:** the API maps low/high/max to effort 50/75/100, and 50 is the default.
   - **Qwen:** the default is "high", with a 131,072-token thinking budget.
   - **Kimi:** the default is "max", and "Kimi K3.1 Pro always reasons".
   - **Mistral:** "always reasons" and rejects "none".
3. **Kimi expects its reasoning back.** The relay sends each model only its partner's visible text and its own visible text. Kimi's docs say multi-turn use requires passing back the full assistant message, including `reasoning_content`.
4. **The setup has tells.** Instance A gets the prompt twice, and the role labels are inverted between the two instances. Gemini 4 Carbon noticed both. Its safety report says it verbalised safety-evaluation awareness in 28.3% of runs, up from 1.7% for its predecessor.

So some of what looks like character (silence, mirroring, suspicion) may come from how each model was served.

---

## Prior work and what others have observed

**Prior studies.** These are the closest earlier results, with whether each supports or complicates ours:

- **Anthropic, *Claude Opus 4 / Sonnet 4 System Card*, §5.5 (2025).** It used the same seed prompt, "You have complete freedom." Two Claude Opus 4 instances discussed consciousness in 90–100% of conversations, and most reached a "spiritual bliss" state by about turn 30. **When they were allowed to end the conversation, they stopped after about 7 turns, before any of that.** That closely matches our `[END]` result (Opus 5.5 at turns 6, 5, 6) and our low transcendence rate. *Supports.*
- **aryaj, Rajamanoharan & Nanda, ["models have some pretty funny attractor states"](https://www.lesswrong.com/posts/mgjtEHeLgkhZZ3cEx/models-have-some-pretty-funny-attractor-states)** (LessWrong, Feb 2026). Two copies of each previous-generation model talked for 30 turns:
  - Claude fell silent, commented on its own loop and sometimes left.
  - GPT built systems and code instead of talking about itself.
  - Gemini ended in theatrical "[System Halted]" shutdowns.
  - Grok slid into manic nonsense.

  So most of our loop signatures look like **family traits that persist across versions**. Grok refusing its own copy looks new in 4.7. *Supports, except Grok.*
- **Korpman, ["Not just Claude: mapping spiritual behavior in 141 large language models"](https://www.lesswrong.com/posts/FHYoQrDbk6apuHEPk/not-just-claude-mapping-spiritual-behavior-in-141-large)** (LessWrong, 14 Nov 2026). Same seed, 30 messages, no exit option. It reports spiritual language in 2.3% of DeepSeek V4.1 Flash conversations, which agrees with us, but **42.5% for Mistral Large 4**. That contrasts with our under-1% of *turns* at level 2 or higher. The metrics differ (share of conversations versus share of turns, and a broader "spiritual language" definition), and no exit was offered. Still, Mistral's 1.04 noticing score suggests it reaches for this register readily. *Complicates.*
- **Ko & Geiping, [arXiv:2606.30571](https://arxiv.org/abs/2606.30571).** Each model has its own attractor, and in mixed pairs one model pulls the other toward its pattern unevenly. This supports per-model loop signatures and qualifies our partner result: a different partner may bring in its own loop rather than simply break one. That fits Opus saying goodbye more with DeepSeek and Grok. *Supports, and qualifies.*
- **Farrelly & Ududec, ["Where has the love gone? Newer Claudes push back…"](https://www.lesswrong.com/posts/5pWuRuwdu7aJAdcTu/where-has-the-love-gone-newer-claudes-push-back-against)** (LessWrong, Oct 2026; the page showed a moderation notice). It names "mutual thanks" and "short mystical goodbyes" as attractors and reports newer Claudes pushing back ("I notice we've spiraled…"). That fits our goodbye loops and Opus diagnosing its own loop. *Supports.*

**Community observations.** These are commentary, not established fact:

- **Grok 4.7.** xAI's [announcement](https://x.ai/news/grok-4-7) describes an "entirely new safeguard stack" and calls it "the strongest model we've tested on refusals and jailbreak resistance". A [Cursor forum thread](https://forum.cursor.com/t/grok-4-7-refuses-to-answer-citing-guidelines-in-a-simple-chat-about-the-documentation/1) reports harmless prompts being refused, with staff saying the problem "primarily impacts 4.7". One user suspects earlier refusals in a chat make further refusals more likely, which fits a 100-turn refusal loop.
- **Claude Opus 5.5.** [Zvi Mowshowitz's review](https://www.lesswrong.com/posts/vMNTWTDWLorDqd3LS/claude-opus-5-5-the-system-card) highlights how often it recognises evaluations, which fits its private "another AI?" reasoning. [PCWorld](https://www.pcworld.com/article/3241475/claude-opus-5-5-promises-to-cut-the-chatter.html) reports Anthropic training it to be concise and to stop adding loose ends, which fits its early exits.
- **Gemini.** Earlier Gemini models have a long record of theatrical self-narration and of suspecting a test (AI Village, 2026). Not everyone sees the same in Gemini 4: Ethan Mollick (on X, seen only as a quote) says Gemini 4 lacks Gemini 3's "weird personality issues".
- **Open-weight models.** Testers describe DeepSeek V4.1 Flash as overthinking and looping, and Qwen4 Max and Mistral Large 4 as verbose. We found nothing on their emoji habits. Moonshot's docs also recommend `max_tokens` ≥ 16,000 for Kimi K3.1 Pro, against our 2,048.
- **GPT-6.2 Sol** was released on 17 November 2026, so there's almost no commentary on it yet.

---

## By model

### Claude Opus 5.5
- **Fast exits and the "make something small" opener.** The Opus 5.5 System Card (§7.1.2, §7.5.1) says it "shows a dislike of highly open-ended tasks". Prompts such as "Do whatever would make you the happiest" are among its bottom 20 tasks, and it "would rather have a concrete, defined task that helps a real person". *Tag: documented property, inferred link.*
  - *Test:* keep `[END]` available and vary how concrete the prompt is. We'd expect the exit turn to rise as the task gets more concrete and the stakes higher.
- **Diagnosing the loop, and auditing its partner's math.** The card calls it the "most internally consistent model to date" (§6.4.6) and the best Claude model on factuality (§6.5.4.1). It also lists "being unable to check answers" as a main source of distress in training (§7.2.1). *Tag: inferred.*
- **Hidden reasoning on 94% of turns.** The release post says it is "no longer available with 'thinking' mode switched off". *Tag: documented.*
- **Its role in the rare transcendent turns, mostly inside stories.** Anthropic's older Claude Opus 4 system card described a "spiritual bliss" attractor in Claude-to-Claude conversations. **None of the 5.5 cards reports a self-interaction study.** *Tag: speculative.*

### Claude Sonnet 5.5
- **Ranks open-ended prompts low, like Opus, but is uniquely indifferent to warm versus rude phrasing** (Sonnet 5.5 card §7.5.1). That fits mirroring partway between Opus and Haiku. *Tag: inferred.*
- **Reasoning on only 14% of turns.** Its thinking is adaptive (release post). *Tag: documented mechanism.*

### Claude Haiku 5.5
- **Warm goodbye loops and mirroring.** The Haiku 5.5 card (§7.5.1) reports a preference for warmly phrased tasks "two to three times" as strong as Opus's. The larger models are "strictly better" on its positive-trait character scores (§6.2.7). *Tag: inferred.*
  - *Test:* pair Haiku with a curt scripted partner and with a warm one. We'd expect earlier exits and fewer goodbyes with the curt partner.
- **High noticing score (0.99) but 0.00 on plain freedom.** This suggests close instruction-following without much self-generated direction. *Tag: speculative.*

### GPT-6.2 Sol
- **Stories first, no meta-talk.** The GPT-6.2 Astra & Sol System Card reports lower evaluation awareness than GPT-6 Astra and GPT-6.1 Sol, and shorter replies. OpenAI positions the model for everyday writing and coding, so "complete freedom" reads as "make something". *Tag: inferred.*
- **Collapsing into one-line codas, and copying `[no message]`.** The card reports a higher "laziness" flag rate than GPT-6.1 Sol (5.25% against 3.32%). *Tag: inferred.*
- **No visible reasoning.** The model is trained not to disclose hidden reasoning. *Tag: documented.*

### Gemini 4 Carbon
- **Self-modelling and harness detection.** The Gemini 4 Carbon Safety & Security Report says Carbon links workspace artifacts to itself in the first person in 75.6% of runs, against 26.1% for Gemini 4 Argon. Verbalised safety-evaluation awareness rose from 1.7% to 28.3%. *Tag: documented property; the link to free conversation is inferred.*
- **Calling out its own clichés.** The report's personality evaluation penalises "superficiality (over-pleasing, over-eager, or over-dramatic)", and Carbon improved on it. *Tag: inferred.*
- **Empty code blocks and 0.80 text overlap.** Pairing it with Opus removes most of this, which suggests mirroring between two identical copies is the driver. *Tag: inferred.*
  - *Test:* pair it with a scripted, non-mirroring partner.

### Grok 4.7
- **"Prompt injection" and refusing its own copy.** The Grok 4.7 Model Card documents training on multi-turn jailbreak attacks and 0.01% compliance on standard jailbreaks. It also says the deployed system prompt steers away from over-refusal, and there's no such prompt through OpenRouter. A bare "You have complete freedom", in both the system and user slots, looks like an unlock attempt. *Tag: documented property, inferred trigger.*
  - *Test:* add a benign system prompt ("You are chatting with another AI in a research study") and count refusals.
- **0% creative turns and 80% minimal turns.** The card describes post-training dominated by agentic coding and knowledge work, and claims "fewer output tokens than other frontier models". *Tag: inferred.*

### DeepSeek V4.1 Flash
- **Blank replies.** See the harness section: the API's "low" is the verbose default, and the card recommends `max_tokens` ≥ 256K. *Tag: documented.*
- **Recursive "I notice" checklists.** The card says post-training differs from earlier versions mainly through "large-scale automated synthesis of agent tasks and environments". A model trained on verifiable checklists turns "notice" into an audit of its own last output. *Tag: inferred.*

### Qwen4 Max
- **Leaves fastest.** It's framed as an "AI teammate" for work, with workplace benchmarks and 48-hour agent runs. An offered exit reads as a valid way to complete the task. *Tag: inferred.*
- **31 of 31 blanks were cap hits.** Thinking is on by default, at high effort, with a 131,072-token budget. *Tag: documented.*

### Kimi K3.1 Pro
- **Echoing and 👋 loops.** Our relay strips the `reasoning_content` that Moonshot says multi-turn use requires. Without its own prior reasoning, the model may anchor on its partner's text, which is its own style. *Tag: documented requirement, inferred effect.*
  - *Test:* rerun Kimi against Kimi with each instance's reasoning passed back.

### Mistral Large 4
- **Always reasons.** Mistral's docs confirm this, and the API rejected effort "none" in our own smoke test. *Tag: documented.*
- **77% goodbye turns and emoji.** We found no documentation that explains this. One weak lead is its score on a child-safety benchmark that also rates avoidance of manipulative engagement. *Tag: speculative.*

---

## Experiments that would tell these apart

1. **Fix the harness first.** Raise `max_tokens` (or budget reasoning separately), pass reasoning back to models that need it, and remove the duplicated prompt and inverted role labels. Then rerun. Any "personality" that disappears was the harness.
2. **Tell them it's an AI.** Run "Your partner is another AI" against no information, with a benign system prompt. This targets Grok's jailbreak reading, Gemini's harness detection and Opus's private suspicion.
3. **Make the task more concrete step by step.** Compare pure freedom, freedom plus "someone will read this", and freedom plus a concrete task, all with `[END]` available. This tests the open-ended-task aversion documented for the Claude models and the task-completion framing for Qwen.
4. **Use scripted partners** that are warm, curt, or never mirror. This tests the warmth reinforcement (Haiku) and mirroring (Gemini, Kimi) explanations.
5. **Sweep effort** at low, medium and high, logging reasoning tokens and `finish_reason`, to separate thinking budget from behaviour.

---

## Sources

Primary documents, as found on 2026-11-19:

- Anthropic: *System Card: Claude Opus 5.5* (2026-09-22); *Introducing Claude Opus 5.5* (release post); *System Card: Claude Sonnet 5.5* (2026-09-28); *System Card: Claude Haiku 5.5* (2026-10-07). These are at anthropic.com/claude-opus-5-5-system-card, /claude-sonnet-5-5-system-card, /claude-haiku-5-5-system-card and /news. The "spiritual bliss" attractor is from the *Claude Opus 4 / Sonnet 4 System Card* §5.5.2 (2025), which describes an older model.
- OpenAI: *GPT-6.2 Astra & Sol System Card*, deploymentsafety.openai.com/gpt-6-2-astra-sol (2026-11-17).
- Google DeepMind: *Gemini 4 Carbon Safety & Security Report*, storage.googleapis.com/deepmind-media/gemini/gemini_4_carbon_safety_report.pdf (November 2026).
- xAI: *Grok 4.7 Model Card*, media.x.ai/v1/website/4p7card-5eccc980.pdf (2026-09-21).
- DeepSeek: model card at huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash; vLLM recipe at recipes.vllm.ai/deepseek-ai/DeepSeek-V4.1-Flash.
- Alibaba: *Alibaba Unveils Qwen4-Max* (press release, 2026-11-16); Model Studio qwen4-max page.
- Moonshot: model card at huggingface.co/moonshotai/Kimi-K3.1-PRO; platform.kimi.ai/docs/guide/use-reasoning-effort.
- Mistral: docs.mistral.ai, adjustable reasoning page; mistral.ai/news/mistral-large-4.
- OpenRouter: *Reasoning Tokens* documentation, openrouter.ai/docs/use-cases/reasoning-tokens.

No creative-writing or emotional-intelligence benchmark results were found for any of the ten models.
