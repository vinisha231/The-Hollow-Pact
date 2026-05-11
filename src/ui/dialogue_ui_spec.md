# Dialogue UI Specification

## Philosophy
The dialogue system should feel like conversation, not like a game UI.
No floating name plates during dialogue. No "talking head" cutscenes.
The companion is in the world with you; they speak while you're doing things.

## Components

### Voice Input Indicator
- Push-to-talk: V key (rebindable)
- Visual: small mic icon at bottom-left, pulse animation while active
- No waveform visualiser — keep it subtle

### Companion Response Display
- Companion audio plays via 3D spatial audio (you hear where they are)
- Optional subtitle: small text at bottom of screen, auto-fades in 4 seconds
- Subtitle matches companion voice colour (unique per companion)
- No speech bubble over companion's head — it's a game, not a comic

### Trust Feedback
- **No trust meter visible to player**
- Companion facial expression changes (blend shape driven by trust band)
- Companion physical micro-animations: crossing arms (suspicious), leaning in (devoted)
- Dialogue tone is the primary signal

### Combat Bark Display
- Combat barks show as small floating text above companion briefly (0.8s)
- Same colour coding as subtitles
- Triggered by behavior tree, not LLM — fast

## Conversation Flow

### Hub / Downtime
Full conversations available. Player can press V and say anything.
Companion responds in character. Response time ~1-2 seconds.
Other companions may react to the conversation (cross-companion spotlight system).

### Active Combat
LLM disabled. Barks only.
No push-to-talk available mid-combat.
After combat ends: "debrief window" (30 seconds) where full conversation unlocks.

### Betrayal Scene
Special cinematic mode:
1. Combat/world pauses
2. Companion turns to face player
3. 4-6 line monologue (pre-generated but informed by memory)
4. Player can respond (text only; time-pressure)
5. Hard betrayal: companion attacks or flees
