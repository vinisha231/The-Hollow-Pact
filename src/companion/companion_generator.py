"""
CompanionGenerator — generates novel companion personas using LLM.
Used for live-ops seasonal companions; reviewed by writers before shipping.
"""
from __future__ import annotations
import json
import logging
import uuid
from dataclasses import dataclass
from typing import Optional

import anthropic

from src.ai.companion_persona import (
    CompanionPersona, PersonalityVector, HiddenAgenda, LoyaltyStance
)

log = logging.getLogger(__name__)

GENERATION_MODEL = "claude-opus-4-7"
MAX_TOKENS = 2000


@dataclass
class GenerationRequest:
    archetype_concept: str    # e.g. "a merchant who secretly works for the villain"
    setting_notes: str        # relevant world context
    personality_hints: str    # optional designer guidance
    voice_id: str             # ElevenLabs voice ID assigned externally


class CompanionGenerator:
    """
    Generates a complete companion persona from a concept brief.
    Output is always reviewed by a writer before shipping.
    """

    def __init__(self, claude: anthropic.AsyncAnthropic):
        self._claude = claude

    async def generate(self, req: GenerationRequest) -> CompanionPersona:
        prompt = self._build_prompt(req)
        resp = await self._claude.messages.create(
            model=GENERATION_MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        return self._parse_response(resp.content[0].text, req.voice_id)

    def _build_prompt(self, req: GenerationRequest) -> str:
        return f"""
You are a narrative designer creating an AI companion for The Hollow Pact, a video game.

CONCEPT:
{req.archetype_concept}

WORLD CONTEXT:
{req.setting_notes}

DESIGNER NOTES:
{req.personality_hints}

Generate a complete companion persona as JSON with this exact structure:
{{
  "name": "string",
  "archetype": "string (snake_case)",
  "personality": {{
    "warmth": 0-100,
    "ambition": 0-100,
    "honesty": 0-100,
    "courage": 0-100,
    "deception_tolerance": 0-100,
    "loyalty_threshold": 0-100
  }},
  "stance": "steadfast|conditional|mercenary|enigmatic",
  "agendas": [
    {{
      "id": "unique_snake_case",
      "label": "short_label",
      "description": "Private description of the secret goal. 2-3 sentences.",
      "priority": 1,
      "reveal_condition": "When this should be revealed",
      "completion_condition": "How it ends"
    }}
  ],
  "backstory": "2-3 paragraph backstory",
  "speech_patterns": ["5 example dialogue lines that only this character would say"],
  "taboos": ["3-5 topics they refuse to discuss"]
}}

Write only the JSON. No preamble.
""".strip()

    def _parse_response(self, text: str, voice_id: str) -> CompanionPersona:
        data = json.loads(text)
        companion_id = f"generated_{data['archetype']}_{str(uuid.uuid4())[:8]}"
        return CompanionPersona(
            companion_id=companion_id,
            name=data["name"],
            archetype=data["archetype"],
            voice_id=voice_id,
            personality=PersonalityVector(**data["personality"]),
            stance=LoyaltyStance(data["stance"]),
            agendas=[HiddenAgenda.from_dict({**a, "completed": False}) for a in data["agendas"]],
            backstory=data["backstory"],
            speech_patterns=data["speech_patterns"],
            taboos=data["taboos"],
        )
