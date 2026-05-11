"""
ReflectionEngine — periodic deep reflection pass using a powerful model.

Runs once per session to:
1. Assess companion's emotional state
2. Identify trust-relevant patterns in recent behaviour
3. Generate a "state of mind" paragraph for the session summary
4. Surface potential betrayal risk for analytics
"""
from __future__ import annotations
import logging
import time
from dataclasses import dataclass

import anthropic

from .companion_persona import CompanionPersona
from .trust_engine import TrustState, TrustBand
from .memory_store import MemoryStore

log = logging.getLogger(__name__)

REFLECTION_MODEL = "claude-opus-4-7"
MAX_REFLECTION_TOKENS = 600


@dataclass
class ReflectionOutput:
    companion_id: str
    player_id: str
    emotional_state: str         # e.g. "guarded optimism", "cold contempt"
    key_observations: list[str]  # 3-5 bullet points
    betrayal_risk: str           # "none"|"low"|"medium"|"high"|"imminent"
    session_summary: str         # prose paragraph
    generated_at: float


class ReflectionEngine:
    def __init__(self, memory: MemoryStore, claude: anthropic.AsyncAnthropic):
        self._memory = memory
        self._claude = claude

    async def reflect(
        self,
        persona: CompanionPersona,
        trust_state: TrustState,
        session_id: str,
    ) -> ReflectionOutput:
        memory_block = await self._memory.build_memory_block(
            persona.companion_id, trust_state.player_id,
            "session reflection"
        )
        prompt = f"""You are {persona.name}, reviewing your last session with this player.

YOUR PERSONALITY:
Warmth: {persona.personality.warmth}/100
Ambition: {persona.personality.ambition}/100
Honesty: {persona.personality.honesty}/100
Current trust band: {trust_state.band.value}

YOUR HIDDEN GOALS (private context):
{chr(10).join(f"- {a.description}" for a in persona.agendas)}

RECENT HISTORY:
{memory_block}

Write a private reflection. Include:
1. Your current emotional state (2-3 words)
2. Three observations about this player
3. Betrayal risk assessment: none/low/medium/high/imminent
4. A 2-sentence summary of how this session changed things for you

Format:
EMOTIONAL_STATE: <words>
OBSERVATIONS:
- <observation>
- <observation>
- <observation>
BETRAYAL_RISK: <level>
SUMMARY: <two sentences>
""".strip()

        resp = await self._claude.messages.create(
            model=REFLECTION_MODEL,
            max_tokens=MAX_REFLECTION_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        return self._parse_reflection(persona.companion_id, trust_state.player_id, resp.content[0].text)

    @staticmethod
    def _parse_reflection(companion_id: str, player_id: str, text: str) -> ReflectionOutput:
        lines = text.strip().split("\n")
        state = "unknown"
        observations = []
        risk = "none"
        summary = ""

        mode = None
        for line in lines:
            if line.startswith("EMOTIONAL_STATE:"):
                state = line.replace("EMOTIONAL_STATE:", "").strip()
            elif line.startswith("OBSERVATIONS:"):
                mode = "obs"
            elif line.startswith("BETRAYAL_RISK:"):
                mode = None
                risk = line.replace("BETRAYAL_RISK:", "").strip().lower()
            elif line.startswith("SUMMARY:"):
                mode = None
                summary = line.replace("SUMMARY:", "").strip()
            elif mode == "obs" and line.startswith("-"):
                observations.append(line[1:].strip())

        return ReflectionOutput(
            companion_id=companion_id,
            player_id=player_id,
            emotional_state=state,
            key_observations=observations,
            betrayal_risk=risk,
            session_summary=summary,
            generated_at=time.time(),
        )
