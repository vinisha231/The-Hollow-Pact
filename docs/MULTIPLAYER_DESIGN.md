# Multiplayer Design Notes

## The AI Companion in a Multi-Human Party

Running companions in a 4-player party is 10x harder than solo.
Here's why and how to handle it.

### Problem 1 — Dialogue chaos

Four humans talking simultaneously plus four AI companions = noise.
Solutions:

1. **Spotlight system** — only one companion speaks per 5-second window
2. **Context priority** — companions defer to the player they're bonded to
3. **Combat silence** — companions emit barks only; no LLM in active combat
4. **Downtime window** — hub/camp time unlocks full conversations; all companions active

### Problem 2 — Cross-companion relationships

AI companions notice each other. Ossian is suspicious of Lyra. Lyra senses something dark in Ossian.
These relationships add texture and can drive conflict.

Implementation:
- Each companion has a `companion_opinions` dict injected in system prompt
- Opinions update based on observed other-companion actions
- "I notice Lyra hesitated at the shrine" → small negative Ossian→Lyra opinion
- Opinions influence whether companions back each other up in combat

### Problem 3 — Bonded vs unbonded players

Each companion is bonded to one human player. Other players can also interact with them.
Trust events from non-bonded players have 50% weight.
A non-bonded player being awful to Brann's bonded player will still affect Brann's trust.

### Problem 4 — Drop-in/drop-out

When a human leaves, their companion:
1. Delivers a short in-character farewell line
2. Enters "background" mode — participates in combat via behavior tree only
3. No LLM calls until player returns

When a human joins mid-session:
1. Session state is sent to their client
2. Companion delivers an in-character acknowledgement
3. Memory store loads their campaign history if returning player

### Problem 5 — Random strangers

Matchmade randoms don't share campaign history. Companions adjust:
- Memory block still includes bonded player's history
- Non-bonded players get "first meeting" context
- Trust starts at 40 (slightly below neutral) for randoms

## Netcode Decisions

### Mirror (Unity) with server-authority
- Companion actions are authoritative on the server
- Client sends intent; server validates and applies
- Companion position is server-owned (prevents desync)
- Dialogue audio is client-local (not synced frame-by-frame)

### Lobby → Session flow
```
1. Player creates lobby (or matchmaker does)
2. Hathora allocates dedicated server
3. All clients connect via Mirror
4. Session state loads from Postgres
5. Each companion's persona is loaded on server
6. Play begins
```

### Latency tolerance
Real-time tactics game, not competitive. 150ms server latency is fine.
Combat is server-authoritative; movement uses client prediction with server correction.
Companion dialogue is fire-and-forget from the server — players don't sync on audio timing.

## Party Size Scaling

| Players | Empty slots | Difficulty | Loot |
|---------|-------------|------------|------|
| 4 | 0 | Normal | Normal |
| 3 | 1 companion missing | -10% HP on enemies | +15% gold |
| 2 | 2 | -20% | +30% |
| 1 | 3 | -30% | +50% |

Solo run with one AI companion is intentionally supported and tuned.
