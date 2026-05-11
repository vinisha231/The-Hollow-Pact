# Product Roadmap

## Phase 1 — Vertical Slice (Months 1-4)
*Prove the core loop works*

### Milestones
- **M1 (Month 1):** Unity project running, player moves around Saltmere, Brann spawns and walks with you
- **M2 (Month 2):** Brann responds to voice input. Memory persists between sessions. Trust changes based on 5 events.
- **M3 (Month 3):** Thornwood Approach combat works. Brann participates via behavior tree. Pre-baked barks play.
- **M4 (Month 4):** 30-minute playthrough without crashes. Brann references a past session memory. One soft betrayal visible at Suspicious trust.

### Success Criteria
- 3 internal playtesters played for 30 minutes and said "I forgot it was AI"
- Brann's trust moved at least twice during each playtest
- P95 dialogue latency under 1.5s

---

## Phase 2 — Betrayal System (Months 5-6)
*The main feature*

### Milestones
- **M5:** Trust UI-free; player reads trust through dialogue only. Designer can tune trust weights in config.
- **M6:** Hidden agenda partially surfaces through gameplay. One scripted hard betrayal fires at act1_treasure_room.

### Success Criteria
- 5 playtesters experienced betrayal. All 5 said they "should have seen it coming."
- Betrayal monologue references 2+ real player choices.

---

## Phase 3 — Multiplayer (Months 7-9)
*Scale the loop*

### Milestones
- **M7:** 2-player co-op working locally. Spotlight system prevents dialogue chaos.
- **M8:** Hathora-hosted dedicated servers. Drop-in/drop-out working.
- **M9:** 4-player sessions stable. Cross-companion opinions injected and visible in dialogue.

### Success Criteria
- 4-player session with strangers; no one complained about companion chaos
- Host migration works on disconnect

---

## Phase 4 — Content (Months 10-15)
*Enough game to ship*

### Milestones
- 3 zones beyond Saltmere (Thornwood, Ashfall, Varek Ruins) complete
- 4 companions (Brann, Lyra, Ossian, The Echo) complete with full agenda arcs
- Matchmaking with strangers working
- Act 1 and Act 2 complete (8-12 hours)
- Public beta

### Success Criteria
- 100-hour internal playtest without LLM-induced immersion breaks
- 40% of Act 1 completions reached the treasure room betrayal beat
- NPS > 40 in beta survey

---

## Phase 5 — Launch + Live Ops
*Ship and keep going*

### Launch
- Steam Early Access, Epic
- 4 companions, 5 zones, Acts 1-2
- Price: $25

### Live Ops
- Season 2 companion (Month 18)
- Act 3 (Month 20)
- Community companion vote (Month 22)
- Season 3 companion (Month 24)

### Revenue Model
- Base game: $25
- Season Pass: $15/year (seasonal content + companions)
- No pay-to-win, no cosmetic gambling
- No subscription

---

## What Could Kill This

1. **LLM latency degrades** — if AI backend consistently exceeds 2s, players notice
2. **Companions feel samey** — if Brann and Lyra start sounding alike, the premise fails
3. **Betrayal feels random** — if players feel cheated, not complicit, retention collapses
4. **Cost runaway at scale** — if API costs exceed $1/player/hr, the economics break
5. **Multiplayer companion chaos** — 4 AIs competing for attention destroys the vibe
