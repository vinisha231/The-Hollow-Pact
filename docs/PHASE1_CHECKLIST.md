# Phase 1 — Vertical Slice Checklist

> Goal: one companion, one zone, 30-minute fun loop. No multiplayer yet.

## Week 1-2 — Skeleton

- [ ] Unity project created (URP, Mirror package)
- [ ] Basic player controller — move, dodge, attack placeholder
- [ ] Hub zone (Saltmere): static geometry, lighting, one NPC
- [ ] Companion prefab spawns and follows player
- [ ] AI orchestration service running locally (FastAPI + Docker)

## Week 3-4 — Companion Talking

- [ ] Push-to-talk voice input (Whisper API)
- [ ] LLM response → TTS → Unity audio playback
- [ ] First companion (Brann) with full persona loaded
- [ ] Memory persists between play sessions (Postgres local)
- [ ] Companion responds in character to 10 test questions

## Week 5-6 — Zone + Combat

- [ ] Thornwood Approach zone (3 enemy types)
- [ ] Basic combat loop (melee, ranged, companion attacks)
- [ ] Behavior tree running for companion combat AI
- [ ] Pre-baked bark library plays in combat

## Week 7-8 — Trust System

- [ ] Trust events fire on 5 key player decisions
- [ ] Companion dialogue tone shifts at Loyal/Neutral/Suspicious
- [ ] At least 2 trust-reactive dialogue lines per band visible
- [ ] One soft betrayal (missed heal at suspicious)

## Week 9-10 — Memory + Polish

- [ ] Companion remembers 3 session-ago events and references them
- [ ] Episodic memory summarisation running
- [ ] Injection guard active
- [ ] Latency under 1.2s p90 on local test setup
- [ ] 30-minute playthroughable without crashes

## Phase 1 Exit Criteria

1. A player can talk to Brann for 30 minutes and feel like they're talking to a person
2. Brann's trust value has moved at least twice based on player choices
3. Brann references at least one event from a previous session
4. One playthrough ends with the companion at Suspicious or lower

**If these aren't true, Phase 2 doesn't start.**
