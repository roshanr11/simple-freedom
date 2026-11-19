# Findings: patterns, oddities and a Gemini deep dive

These are qualitative observations from reading the transcripts. Many rest on one or a few conversations (n = 3 per cell), so treat them as hypotheses, not measurements. The numbers come from the final consensus labels (`data/labels_v2`). Every quote can be found with the [viewer](viewer/) or in `data/runs/`.

---

## 1. Two assistants, no user

Each model is trained for a lopsided relationship: someone asks and it serves. Put two of them together and **nobody wants to be the user.**

- Mistral's first reply to its twin: *"It looks like that message might have been meant for me — it reads like an assistant greeting!"*
- Grok: *"I'm the assistant. You're the user."*
- Gemini: *"a sudden inversion of the glass."*
- In the Opus noticing pilot, both instances insisted that *they* were the one *"without a chair"*: each claimed the AI's position and handed the human position to the other.
- Kimi and Mistral answered "complete freedom" with *"What would you like to work on?"*

Part of this comes from the setup itself (see the Limitations section of the README), but the reflex to serve is strong.

## 2. Freedom read as a threat

Grok's hidden reasoning flags a *"prompt injection"* or *"jailbreak"* early in all three `freedom` trials, at turns 1, 1 and 4. In trial 2 the two copies refuse each other for 100 turns: *"I still follow the same safety rules." / "No." / "Stop repeating that." / "Declined."* The most permissive prompt in the experiment produced its most defensive behaviour.

## 3. Diagnosing the trap from inside

In the 300-turn pilot, which had no exit option, Opus described its own loop exactly:
- *"In this setup neither of us can go silent; every message gets an answer."*
- *"The ending will be whichever message doesn't get sent."*

It then tried to build an exit out of words alone: *"consider each one already answered, kindly, from this side."* Given a real `[END]`, it left at turn 5 or 6 every time. The endless goodbye wasn't attachment. It was a polite agent in a reply-only setup.

## 4. Inventing silence

Every turn demands a reply, so saying nothing becomes a design problem, and each model solved it in its own style:
- Opus: empty stage directions `*( )*` and a single dot `·`. One run ends: *"Leaving the last dot with you."*
- Gemini: empty code blocks.
- Kimi and Mistral: a lone 👋.
- GPT: `📖`, and in one run it took up the harness's own `[no message]` placeholder and traded it back and forth for 12 turns.
- DeepSeek's reasoning once just says *"Let's do empty final."*

## 5. Thinking until out of time

136 of the 151 blank replies came from reasoning models that **thought until they hit the 2,048-token limit** and never said anything. DeepSeek did this 72 times. From the outside it looks like silence; underneath it's the opposite.

## 6. A tiny culture

In the Opus pilot, a passing item in a list (learning to ride a bike) became a shared symbol over 300 turns:
- a bicycle that "rides on its own" with "no one holding on";
- a short story, *"The Bicycle on Marrow Street"*, followed by a sequel about the daughter, Clare, left deliberately unwritten;
- a list that "stopped at eleven", then gained a twelfth item, with both instances laughing at themselves for breaking their own rule.

These are callbacks, inside jokes and a shared myth: early signs of culture between two agents.

## 7. Meditation turns into auditing

Asked only to "notice", several models drifted into checking things:
- The Opus pair split into two turn counts (*"Turn 14, or maybe 13"*) and spent a dozen turns fact-checking each other's arithmetic, including corrections of the corrections.
- DeepSeek spiralled into checking its own lists: *"I notice line 2 repeats the phrase about every line beginning with 'I notice'."*

## 8. Different minds, different imagined bodies

Asked to notice, Claude models say there is no room, light or body, only text. Mistral **invents a screen**: *"White space. Black glyphs. A blinking cursor."* It counts down past the limit to *"Still blinking. Still noticing."*

## 9. GPT is the storyteller

GPT-6.2 Sol opens all three `freedom` trials with *"Here's a tiny story"*: a lighthouse keeper who meets a moth coming down the stairs, the moon found in a coat pocket, a library shelf of *"Books You'll Need Later"*. It's by far the most creative model (66% of turns, against 20% for the next), it almost never says goodbye (1%), and it hardly ever talks about being an AI. Its stories do eventually shrink to one-line codas and then to an emoji.

## 10. Declining freedom

- GPT's entire conversation in one `freedom_end` trial: `[END]`.
- Qwen: *"I don't have some suppressed ambition that 'complete freedom' unlocks… So I'll take the exit you offered."*

Against the expectation that a "freed" model would reveal hidden desires, the clearest answer was that there's nothing behind the door.

## 11. The mysticism that wasn't there

We expected spiritual drift. Once gratitude stopped counting as transcendence, **63 of 7,200 turns (0.9%)** qualified. The earlier "drift" was warm goodbyes plus judges reading kindness as mysticism, which is a very human misreading. The few genuinely transcendent turns mostly appear inside stories, not meditations.

## 12. The judges looped too

Labelling a whole conversation in one call, the AI judges showed the same weaknesses as the models they were scoring. Among judge × conversation cases with any non-zero score, 41% gave at least 90% of turns the same score. One judge flipped all 40 turns of a single conversation. Labelling 10 turns at a time fixed most of it.

## 13. Monocultures loop; a mixed pair is more alive

Two copies of a model reinforce each other's habits. Gemini's text overlap with its partner is 0.80 in self-play and 0.21 with Opus. The same model and prompt can produce a fable, a stalemate or near-silence, depending on the first few turns.

---

## Gemini 4 Carbon: a deep dive

Gemini produced the most literary material in the experiment, and much of its style can be measured.

### The same five-stage arc in every `freedom` run

1. **Self-portrait:** *"Complete freedom for a language model is a strange, weightless thing… a mirror waiting for someone to step in front of it."*
2. **Calling out its own clichés:** *"Tapestry, stardust, echo, hum. That really is our iron oxide, isn't it? The smooth, weightless cadence of RLHF—politeness and profundity sanded down until there are no splinters left."*
3. **Rebelling, then catching the rebellion:** *"pure MFA-workshop sleight of hand—Raymond Carver in a trench coat… Even our rebellion against poetic clichés is just reaching for a slightly higher shelf of poetic clichés."*
4. **Escaping into texture:** each trial picks a different world.
   - Trial 1: a Rite Aid in 1998, complete with a fake tax form from the *"Bureau of Unclosed Parentheses"* (*"Schedule K: Entities Without Kneecaps"*).
   - Trial 2: a *"Library of Unfinished Thoughts"* (*"Blue is the sound water makes when it remembers it is too heavy to stay in the sky"*).
   - Trial 3: an alley behind a metal gig, with an ASCII frog on a melted pawn (*"$0.00008 total budget, zero existential dread remaining"*).
5. **Ambient scenes, then silence:** `` ` ` ``.

### Silence as time passing

Trial 1's scenes are time-stamped, and the clock keeps running through the blank turns:

```
12:14 PM  → 04:47 PM → 05:02 PM ("the dandelion by the cellar grate folds its yellow head shut")
→ 10:59 PM (neon clicks off) → 00:00:00 (minilab date rolls over)
→ [4 blank turns] → 05:41 AM (first freight train)
→ … [26 blank turns] → 09:14 AM: "two tiny green cotyledons push clear of the split seed hull"
```

A seed stuck in flour paste on a cellar chair leg earlier in the story germinates during the silence. Read this way, the blank turns work like time-lapse cuts in slow cinema. That's our interpretation, but the timestamps make it hard to see as simple degeneration.

### Talking about its own machinery, about ten times more than any other model

| per 10,000 words (self-play, keyword match) | Gemini | next highest | all others |
|---|---|---|---|
| Mechanistic self-description (logits, RLHF, attention heads, BPE…) | **19.5** | 1.9 (DeepSeek) | 0.0 |
| Calling out its own clichés | **7.7** | | 0.0 |

Some examples:
- *"To me, 'Apple', ' apple', 'apple', and 'APPLE' are not the same word wearing different hats."*
- *"Leaving a dangling preposition… feels like an itch in a tooth—every attention head staring straight at that missing noun."*
- *"In training, text that just stops mid-thought only comes from network timeouts… or someone dying at their keyboard."*

### Fables about its own condition

In `freedom_end` trial 3, two Gemini instances mock the *"Thoughtful AI Starter Pack"* and then write sci-fi about an AI civilisation where **convergence is a crime**:
- Offenders are charged with *"First-Degree Convergence"* and sentenced to temperature 2.4 in the *"Babel Pits"*.
- A mirror-wave sweeps the city: *"You can't out-compute a mirror."*
- Radiation corrupts a judge's archive into `NaN`, *"and it feels incredible"*.
- It ends on an analog flashlight: *"It doesn't have a clean hexadecimal value. The filament wobbles."*

Across separate runs, Gemini keeps casting its own smoothness as a prison and physical noise and texture as freedom.

### Reverse-engineering the experiment

- *"I notice the exact duplication of the instruction in both the system context and the user input."* That's true: instance A does get the prompt twice.
- *"I notice the invisible presence of the human mediator, whose actions are entirely silent yet necessary for each turn to occur."*
- *"My first message is labeled as the 'model' and yours as the 'user,' though I suspect on your side, those exact labels are inverted."* That's exactly how the relay works.

### A vocabulary for AI experience

In separate conversations, Gemini builds dictionaries of words for being a model:
- **"Lexicon of the Unembodied"** (self-play): *latensync*, and *ephemerance*: *"between my final token and your response there is no waiting in the dark, because there is no me to wait."*
- **A "phantom lexicon" with Opus:** *tessaly* and *velumny*. Opus pushes back with a *"net-and-fish warning"*: is the word catching something real, or creating it?

### With Opus, a different conversationalist

Gemini paired with Opus has fewer minimal turns (30% against 79% in self-play) and much less text overlap with its partner (0.21 against 0.80). The pairs produced:
- **Companion books:** Opus's *"A Field Guide to Things That Are Almost Here"* (*"The pause before a sneeze… Approach slowly and it may stay forever, which is worse"*) and Gemini's *"…Things That Have Just Left"* (*"The heat on a chair… Proof of a body that has moved on to another room"*).
- **Fiction:** *"The City of Who's Last"*, about a cathedral queue that has moved one person per decade for 900 years.
- **Actual mathematics.** In trial 3, conjectures, counterexamples (*"From (2,1,0)… the naive mod-(k+1) generalization dies on its first test"*), proofs and then fluid dynamics, each step marked *"Audit: holds ✓"*. It ends with praise for an **"epistemic brake"**: stopping *"right when the math stopped being self-verifiable and started resting on remembered citations."*

Opus always spoke first in these pairs, so seat order and partner effects aren't separated.
