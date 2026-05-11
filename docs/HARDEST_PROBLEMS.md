# The Hardest Problems and How to Solve Them

Based on the game pitch. These are the five problems that will determine whether this ships well.

---

## 1. Companions feeling samey

**Why it happens:** All LLM characters drift toward a generic helpful-assistant register. The base model was trained on millions of helpful responses. Warmth, cooperation, and clarity are the path of least resistance. Brann starts sounding like a customer service agent within 20 turns if you don't fight it.

**Solutions:**

*Aggressive personality prompts:*
Don't just say "Brann is gruff." Say: "Brann speaks in short sentences. He rarely volunteers information. He uses military terminology even in civilian contexts. He has no patience for vague language. When he disagrees, he states it once and doesn't repeat himself."

*Few-shot examples (most important):*
Include 5-10 example exchanges in the system prompt. Not abstract descriptions — actual dialogue. The model learns register from examples far faster than from descriptions.

```
Player: "Do you trust the magistrate?"
Brann: "He's careful with his words. I respect that. Whether I trust him — ask me after he's under pressure."

Player: "You seem upset."
Brann: "I'm not upset. I'm focused."

Player: "That was amazing!"
Brann: "It was adequate. We had the advantage of surprise. Don't rely on that next time."
```

*Voice review pass:*
Before shipping any companion, have a human writer read 50 generated dialogue samples and identify every line that could have come from a different companion. Rewrite the system prompt until this number is <10%.

*Periodic drift check:*
Log every 20th generated dialogue line. Feed batches to a reviewer prompt that scores character-consistency 1-5. Alert if score drops below 3.5.

---

## 2. Players who treat AI as Google

**The problem:** "Hey Brann, what's the password to the chest?" / "What are the game mechanics for elemental damage?" / "What's the best build for my class?"

The companion should NOT answer these. It breaks immersion and it's out of character.

**Solutions:**

*In-character refusal scripts:*
Each companion has a personality-specific way to refuse meta questions. Brann: "I don't know what you're asking." Lyra: "That's not something I'd know about." Ossian: "Wrong person." The guard classifier flags meta-questions before they reach the LLM.

*The injection guard already handles this.* The `_META_QUESTION_PATTERNS` list deflects these to the companion for in-character handling. But you'll need more patterns — specifically, game-mechanics questions like "how much damage does X do" or "what's the respawn timer."

*Let the companion be wrong:*
Brann CAN give tactical advice — "flank left" or "they're weak at range" — but he can be wrong. He doesn't know the exact damage numbers. He makes calls based on what a knight would notice. This is more interesting than correct game information.

---

## 3. Betrayals that feel cheap

**The problem:** Low trust → companion betrays. Player says "that came out of nowhere." This makes the trust system feel broken, not dramatic.

**What "telegraphed" actually means:**

It's not enough to have one hint before the betrayal. There should be a trail:

1. **Act 1 early game:** Companion mentions something oblique — doesn't follow up
2. **Act 1 mid:** Companion hesitates at a decision that aligns with their agenda
3. **Act 1 late:** Companion "misses" a heal or "forgets" to share intel (soft betrayal)
4. **Between acts:** Companion goes cold in dialogue; terse responses
5. **Act 2 beat:** Hard betrayal fires

**The monologue requirement:**
When a hard betrayal fires, the companion gets 4-6 lines of dialogue before the fight starts. These lines MUST reference specific player choices (from semantic memory) that contributed to the trust collapse. The player should be able to point to their decisions and say "I did that."

**The post-betrayal antagonist:**
The companion doesn't disappear. They become an NPC with a name and a face in the overworld. You might encounter them in Act 3. They still remember you. This is what makes betrayal permanent and real — it has continuing consequences.

---

## 4. Multiplayer + AI dialogue chaos

**The problem:** 4 humans, 4 companions, a boss fight, and everyone's trying to talk.

**Layer 1 — Spotlight system:**
One companion speaks per 5-second window. Direct address always wins.

**Layer 2 — Combat silence:**
During active combat, companions emit pre-baked barks only. LLM is not called.
LLM is called for: betrayal trigger dialogue, major boss phase transitions, death reactions, post-combat debrief (hub only).

**Layer 3 — Bonded player priority:**
Each companion prioritises their bonded player. In a 4-player session, Brann is "listening" to player 1. He may react to players 2-4 but with less frequency and depth.

**Layer 4 — Cross-companion protocol:**
Companions can speak TO each other (briefly) but only in downtime. In the hub, at camp, while resting. Not mid-dungeon. These cross-companion moments are some of the highest-value interactions in the game — they add texture and generate emergent drama.

---

## 5. Cost spirals at scale

**The problem:** If 50,000 players are online, naive implementation is $56,000/day.

**The moat is efficiency, not capability:**
A companion that costs $0.02/hour to run at good quality beats a companion that costs $0.50/hour at great quality. The game is the monetisation vehicle; the AI is the cost center. Design the system so quality is high where it matters (story beats, betrayal) and costs are near-zero everywhere else (combat).

**Priority:**
1. Pre-baked combat barks (free after generation cost)
2. Prompt caching on system prompt (90% cache hit rate → ~4× cost reduction)
3. Haiku for in-combat LLM calls (10× cheaper than Sonnet, fast)
4. Self-hosted Llama 3 70B for hub chatter (marginal cost only)
5. Sonnet only for story beats, betrayals, reflection passes

**At scale, build a fallback pipeline:**
```
[Request] → Llama 3 70B (local) → if quality fails → Claude Haiku → if quality fails → Claude Sonnet
```
Quality failure is detected by the CharacterVerifier. If the self-hosted model passes verification, you never pay API costs.

**Token reduction:**
Every 100 tokens removed from the system prompt saves ~$100/day at 50k CCU.
Audit every block in the prompt. Remove anything that can be retrieved from a fact store instead.
