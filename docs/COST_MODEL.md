# AI Cost Model

## Baseline Assumptions

| Parameter | Value |
|-----------|-------|
| Players per session | 4 |
| Average session length | 2 hours |
| Dialogue turns per player per hour | 30 |
| Tokens per turn (in + out) | ~800 |
| In-combat turns (pre-cached barks) | 70% |

## Per-player-hour cost

```
                    Turns/hr   Tokens/turn   Total tokens/hr
──────────────────────────────────────────────────────────────
Cached combat barks     21         0 (cached)       0
LLM dialogue turns       9           800          7,200

                                              7,200 tokens/player/hr
```

### At Claude Sonnet 4.6 pricing ($3/$15 per MTok in/out)
Assuming 60/40 input/output split:
```
Input:  7,200 × 0.60 = 4,320 tokens = $0.013
Output: 7,200 × 0.40 = 2,880 tokens = $0.043
──────────────────────────────────────────────
Total per player per hour: ~$0.056
```

### At scale (1,000 concurrent players)
```
1,000 players × $0.056 = $56/hr = $1,344/day
```

## Model Tiering Strategy

| Context | Model | Reasoning |
|---------|-------|-----------|
| Idle / hub chatter | Llama 3 70B (self-hosted) | Cheap, good enough for banter |
| Combat reactions | Claude Haiku 4.5 | Sub-300ms, low cost |
| Story beats, betrayals | Claude Sonnet 4.6 | Quality matters here |
| Periodic reflection passes | Claude Opus 4.7 | Once per session, worth the cost |

### Break-even for self-hosted GPU
- 1× A100 SXM 80GB: ~$3.50/hr on Lambda/CoreWeave
- Throughput: ~50 concurrent LLM sessions at Llama 70B 4-bit
- At 50 sessions × 7,200 tokens/hr: 360k tokens/hr
- GPU cost per 1M tokens: ~$9.70
- vs Sonnet: $15/1M output, $3/1M input → avg ~$10/1M
- **Break-even at ~37 concurrent sessions**

## Caching Strategy

### Tier 1 — Pre-generated voice packs (zero cost at runtime)
- 30 combat barks per companion per archetype
- Generated offline in TTS, cached as audio files
- Triggered by behavior tree node types (attack, hurt, victory, etc.)
- Covers ~70% of in-combat audio

### Tier 2 — Prompt caching (Anthropic API)
- System prompt (persona + backstory) is identical per companion
- Enable prompt caching: system prompt block gets ~90% cache hit rate
- Saves ~400 tokens per turn at 0.1× cost

### Tier 3 — Response caching (Redis)
- Cache common hub NPC dialogues (shopkeeper, innkeeper)
- TTL: 5 minutes
- Saves ~10% of total calls

## Monthly Cost Projection (Phase 1 Beta)

| Scenario | MAU | Avg hr/month | Total player-hrs | Est. cost |
|----------|-----|-------------|-----------------|-----------|
| Small beta | 500 | 20 | 10,000 | $560 |
| Medium launch | 5,000 | 15 | 75,000 | $4,200 |
| Hit | 50,000 | 20 | 1,000,000 | $56,000 |

**At "hit" scale, move 60% of traffic to self-hosted → ~$30,000/mo**

## Cost Telemetry

Every LLM call logs:
- model used
- tokens in/out
- cost estimate
- companion_id + trust_band (to correlate cost with trust states)
- cache hit/miss

Weekly review of: per-companion cost, cost-per-betrayal, cost-per-session.
