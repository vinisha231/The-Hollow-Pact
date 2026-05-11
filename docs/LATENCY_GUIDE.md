# Latency Engineering Guide

## Budget

| Pipeline Stage | Target P50 | Target P99 | Failure Mode |
|---------------|-----------|-----------|--------------|
| STT (Whisper API) | 300ms | 600ms | Fall back to text input |
| Guard classifier | 5ms | 20ms | Always local |
| Memory retrieval (pgvector) | 20ms | 80ms | Return empty; degrade gracefully |
| LLM first token | 400ms | 800ms | Return cached bark |
| TTS first audio | 200ms | 400ms | Return cached audio |
| **Total** | **~925ms** | **~1900ms** | |

Players begin hearing audio within ~925ms of finishing speaking.
Full response complete in ~1.3s.

## Tricks

### Pre-generation of combat barks
80% of in-combat companion lines come from a pre-baked voice pack:
- 30 bark templates per companion (attack, hurt, ability, low-hp, victory, etc.)
- Generated offline with ElevenLabs; cached as compressed Ogg Vorbis
- Behavior tree nodes trigger bark types; bark player picks randomly within type
- LLM is NOT called for these

### STT streaming
Don't wait for sentence completion. Stream audio to Whisper in 200ms chunks.
Start the guard + memory pipeline as soon as STT returns partial results.
By the time the player stops speaking, memory retrieval is already in flight.

### LLM streaming
Use streaming API responses. Start sending TTS the moment first tokens arrive.
ElevenLabs accepts streaming text input — first audio byte in ~200ms of LLM start.

### Warm instances
Keep one orchestration worker warmed per active session.
Cold start adds ~800ms. At Hathora / ECS, pre-warm with a dummy request.

### Fallback chain
1. Primary: Streaming Whisper API → Claude Sonnet → ElevenLabs streaming TTS
2. If STT >800ms: fall to text input mode (player typed)
3. If LLM >1200ms: return cached bark of matching emotional valence
4. If TTS >600ms: return pre-generated audio from voice pack

## Latency Monitoring

Emit `latency_ms` on every OrchestratorOutput.
Bucket into:
- `<500ms` — excellent
- `500–1000ms` — acceptable
- `1000–2000ms` — degraded (alert)
- `>2000ms` — broken (page)

Dashboard: show P50/P95/P99 per companion, per session region, per trust band.
(High-trust conversations often run longer — that's expected.)

## Prompt Size Budget

| Block | Max tokens |
|-------|-----------|
| System (persona + agenda) | ~600 |
| Trust tone directive | ~30 |
| World state snapshot | ~80 |
| Short-term memory (20 events) | ~400 |
| Episodic memory (5 retrieved) | ~250 |
| Semantic facts | ~150 |
| **Total system** | **~1,510** |
| User message | ~100 |
| Response | ~200 |
| **Grand total per turn** | **~1,810 tokens** |

This fits comfortably in Claude's context. The system prompt is cacheable
(prompt caching) — saves ~$0.008/turn at Sonnet pricing.
