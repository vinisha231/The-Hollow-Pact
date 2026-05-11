# Companion Design Guide

## Core Design Principle

A companion should feel like a person who *has opinions*, not a tool that *serves the player*.
The moment a player says "wait, are they actually angry at me?" — that's the whole game.

---

## The Trust Dial

Trust is never shown as a number. Players read it through:

| Trust Band | Dialogue tone | Combat | Loot | Misc |
|------------|--------------|--------|------|------|
| Devoted (80-100) | Warm, proactive, shares worries | Overprotective, tanks for player | Shares everything | Brings gifts |
| Loyal (60-79) | Professional, cooperative, dry humour | Reliable, follows orders | Fair split | Occasional personal moment |
| Neutral (40-59) | Reserved, gives clipped answers | Competent, non-committal | Keeps fair share | Minimal small talk |
| Suspicious (20-39) | Terse, second-guesses instructions | Slow reactions, "misses" occasionally | Hoards consumables | Avoids eye contact |
| Hostile (0-19) | Cold contempt, sarcastic | Sandbags, fails at key moments | Steals small items | Actively seeks exits |

---

## Trust Events — Designer Guidelines

### High positive events (+5 to +15)
- Keeping a specific promise made earlier
- Helping someone the companion cares about
- Completing a quest related to companion's agenda (even accidentally)
- Defending the companion in social conflict
- Sharing meaningful personal information

### High negative events (-10 to -25)
- Breaking a named promise
- Abandoning the companion in a fight
- Humiliating the companion in front of NPCs
- Acting against companion's stated values repeatedly
- Discovering the companion was right and ignoring it
- Blocking companion's hidden agenda (even unknowingly)

### The "unknowing" problem
Players should NOT know when they're hurting trust. Trust events fire silently.
The only feedback is the companion's tone and behaviour over time.

**Avoid:** trust events for trivial decisions (which path to take, what to buy)
**Use:** trust events for decisions with moral weight or interpersonal consequence

---

## Hidden Agenda Design

### Rules
1. **The player should be able to reconstruct the agenda in hindsight.** Drop breadcrumbs in every zone.
2. **The agenda must create at least one moment of player conflict.** The companion's goal should occasionally cost the party something.
3. **The agenda has a completion path.** It shouldn't be permanently hidden. Either it's revealed by events, or the companion achieves/fails it by campaign end.
4. **No two companions should have compatible agendas.** Tension is better than harmony.

### Agenda Reveal Curve
```
Sessions 1-3: No hints. Companion is just their personality.
Sessions 4-8: One environmental hint (item, NPC reaction, companion hesitation).
Sessions 9-15: Companion "slips" — one loaded dialogue line that doesn't quite add up.
Sessions 16+: Either agenda completes, triggers a betrayal, or player confronts companion.
```

---

## Voice Design

### The 5-line voice test
Before shipping any companion, write 5 lines that only THIS companion would say.
If any line could come from a different companion, rewrite it.

**Bad (generic):**
- "Let's be careful in there."
- "I'm glad we made it."
- "That was tough."

**Good (Brann-specific):**
- "The formation's wrong. Wide on the left — you're leaving your back exposed."
- "I've fought worse odds. Not by much, but."
- "You want my opinion? You've not been asking for it."

### In-combat lines
Pre-generate 30+ lines per companion for:
- Attacking: "Moving on the left flank", "Don't miss this", "Eyes up"
- Taking damage: "That got through", "Still here", "First blood to them"
- Ally down: "Get up — NOW", "Someone help them", *(for hostile trust: silence)*
- Victory: "Done.", "Clean enough.", "Next time try not to get cornered"
- Betrayal combat: "I'm done protecting you", "This ends here", "You should have listened"

---

## The Betrayal Scene

The single most important moment in the game. Rules:

1. **Always preceded by 3+ telegraphed warnings.** Check the betrayal beat's `telegraphed_by` field.
2. **The companion speaks first.** They get a monologue. It's earned.
3. **The monologue calls out specific events.** "That merchant in Saltmere — you remember what you did?" Reference real player choices from memory.
4. **The companion is NOT wrong.** From their perspective, this is justice. The player should feel at least partially implicated.
5. **After the hard betrayal, they become an antagonist NPC, not a corpse.** They have a face, a name, a goal. You might face them in Act 3.

---

## What Makes Companions Feel Alive

| Mechanic | Effect | Cost |
|----------|--------|------|
| Remember player's name | Warmth | Low — just inject it |
| Reference a past promise by name | Continuity | Medium — semantic fact |
| Disagree with the player in front of NPCs | Personality | Low — dialogue trigger |
| Have an opinion on other companions | Texture | Medium — cross-companion event |
| Notice when something is wrong ("You've been quiet") | Intimacy | Medium — inactivity trigger |
| Refuse an order with a reason | Agency | Low — intent="refuse_order" |
| Say something genuinely funny | Humanisation | High — requires voice + timing |
