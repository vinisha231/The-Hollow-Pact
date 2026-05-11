# The Hollow Pact

> *An asymmetric AI co-op adventure where your party member might be plotting against you.*

---

## The Pitch

You and up to 3 friends (or randoms) form an adventuring party. Each human player is paired with an **AI-driven companion** — a fully voiced, persistent character with its own backstory, goals, and opinions. The AI fights alongside you, talks in real time, remembers what you did three sessions ago, and decides whether you're worth its loyalty.

**The twist:** AI companions have hidden agendas. Maybe yours is secretly cursed and trying to reach a shrine you don't know exists. Maybe it was a noble whose family your character's family wronged generations ago. Maybe it just doesn't like how you treat villagers. If it decides you're not its person anymore, it can desert, sabotage, or — in the worst case — turn on the party at the worst possible moment.

*BG3 meets Hades meets a tabletop DM who's been reading your diary.*

---

## Core Features

### The AI Companion System
- **Persistent personality** — generated from templates (warmth, ambition, deception tolerance, loyalty threshold) plus a backstory hook
- **Hidden agenda** — 1-3 secret goals only revealed through gameplay
- **Living memory** — companions remember specific events across long campaigns
- **Trust meter (hidden)** — every action moves a private trust value; you read them through tone and behavior
- **Real conversation** — push-to-talk voice or text, responds in character to anything

### Adventure & Combat
- Hub-and-spoke world with hand-crafted regions
- Real-time tactical combat — dodge, block, ability cooldowns
- Phase-change bosses designed assuming companions will sometimes refuse orders
- Mimic enemy type that copies companion dialogue to confuse players

### Multiplayer
- 1–4 human players, drop-in/drop-out
- Persistent character identity across sessions and parties
- Cross-party AI opinions ("your guy's a snake, watch him")

### The Betrayal Layer
- **Soft betrayal** — sandbagging fights, selling intel, "accidentally" missing heals
- **Hard betrayal** — companion turns mid-boss, steals the macguffin, becomes a recurring antagonist
- **Redemption** — soft betrayals are recoverable; hard betrayals are permanent

---

## Technical Architecture

### AI Stack
```
Player input (voice/text)
        ↓
Speech-to-text (Whisper API / whisper.cpp)
        ↓
Conversation Orchestrator
   ├── injection defense
   ├── memory retrieval (vector DB)
   ├── world state injection
   └── companion goals + trust injection
        ↓
LLM (Claude Sonnet / GPT-4o / Llama 3 70B)
   └── returns dialogue + structured intent
        ↓
Intent Router
   ├── dialogue → TTS → game audio
   └── actions → behavior tree override
        ↓
World Update → memory store write-back
```

### Memory Architecture
| Layer | Store | Contents |
|-------|-------|----------|
| Short-term | Rolling prompt window (~20 events) | Recent context |
| Episodic | Vector DB (pgvector) | Summarized events, semantic search |
| Semantic | JSON / graph | Structured world facts |
| Personality | Static system prompt | Never edited at runtime |

### Latency Budget
| Step | Target |
|------|--------|
| STT | < 400ms |
| LLM first token | < 600ms |
| TTS first audio | < 300ms |

---

## Build Phases

| Phase | Focus | Duration |
|-------|-------|----------|
| 1 | Vertical slice — one companion, one zone, AI works | 3–4 months |
| 2 | Betrayal mechanic — trust system, hidden agendas | 2 months |
| 3 | Multiplayer — netcode, dedicated servers | 3 months |
| 4 | Content & matchmaking — 3+ zones, 4–5 archetypes | 4–6 months |
| 5 | Live ops — seasonal campaigns, community companions | Ongoing |

---

## Tech Stack

- **Engine:** Unity (URP) — better LLM integration tooling, lighter footprint
- **Netcode:** Mirror / Fish-Net with server-authoritative model
- **Hosting:** Hathora / AWS GameLift for on-demand party instances
- **Auth:** Steam / Epic / PSN SDKs
- **Matchmaking:** Open Match + Redis
- **Save:** Postgres + S3
- **AI:** Claude Sonnet (story beats) + Llama 3 70B self-hosted (combat chatter)
- **Voice:** ElevenLabs streaming TTS + Whisper STT

---

## Cost Model

~$0.30–0.50 per player per hour at full Claude pricing. Mitigations:
- Cache combat barks aggressively (80% of combat lines pre-generated)
- Small model for in-combat reactions, big model for story beats
- Self-hosted Llama 3 70B for low-stakes chatter

---

## Why This Could Work

Nobody has shipped a game where the AI character is the **headline feature done well**. The technical bar is high enough that a small team with the right skills can build something a 200-person studio can't easily clone. The window for being first in this category is open right now.

---

## License

MIT — see [LICENSE](LICENSE)
