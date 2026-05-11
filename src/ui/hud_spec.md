# HUD Specification

## Design Principle
Minimal. The AI companion is the main feature. Don't compete with it.

## Elements (default HUD)

### Top Left — Player Health + Mana
- Thin bars, small numbers
- No percentage text

### Top Right — Party Roster
- Player portraits (up to 4) with small HP bars
- Companion icon next to each player
- No trust meter. No trust bar. No trust number. Never.

### Bottom Left — Voice Input
- Mic pulse indicator only
- "Talking to: [Companion Name]" — only while push-to-talk is held

### Bottom Center — Action Bar
- 4 active abilities + dodge
- Basic, no clutter

### Bottom Right — Compass + Zone Name
- Simple compass, current zone label

## Companion State Indicators (subtle)
Small icon next to companion portrait in party roster:
- ⚔ = in combat
- 💬 = speaking
- ⚠ = [hidden from player, but triggers when betrayal is imminent — designers only]

## What's NOT on the HUD
- No dialogue history / chat log
- No companion status messages ("Lyra is suspicious")
- No trust value
- No hidden agenda hints
- No "relationship status" widget
