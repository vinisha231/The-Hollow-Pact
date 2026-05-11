"""
PromptBuilder — assembles the full system prompt for each companion turn.

Centralises prompt construction so token counts can be audited and optimised.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .companion_persona import CompanionPersona
from .trust_engine import TrustEngine, TrustState


@dataclass
class PromptComponents:
    persona_block: str
    trust_directive: str
    world_snapshot: str
    memory_block: str
    total_estimated_tokens: int


class PromptBuilder:
    # Rough token estimates per block (for budget tracking)
    TOKENS = {
        "persona": 600,
        "trust_directive": 30,
        "world_snapshot": 80,
        "memory_short": 400,
        "memory_episodic": 250,
        "memory_facts": 150,
        "response_format": 50,
    }

    def __init__(self, trust_engine: TrustEngine):
        self._trust = trust_engine

    def build(
        self,
        persona: CompanionPersona,
        trust_state: TrustState,
        world_snapshot: str,
        memory_block: str,
    ) -> str:
        tone = self._trust.get_llm_tone_directive(trust_state)
        total_tokens = sum(self.TOKENS.values())

        return f"""
{persona.system_prompt_block}

CURRENT EMOTIONAL REGISTER:
{tone}

WORLD STATE:
{world_snapshot}

MEMORY:
{memory_block}

RESPONSE FORMAT (always JSON):
{{
  "dialogue": "<1-3 sentences, in character>",
  "intent": "<idle|attack|flee|refuse_order|betray>",
  "intent_target": "<entity ID or null>"
}}
""".strip()

    def estimate_tokens(self, persona: CompanionPersona, memory_block: str, world_snapshot: str) -> int:
        """Rough token count estimate for cost modelling."""
        persona_tokens = len(persona.system_prompt_block) // 4
        memory_tokens = len(memory_block) // 4
        world_tokens = len(world_snapshot) // 4
        return persona_tokens + memory_tokens + world_tokens + self.TOKENS["response_format"]

    def audit_prompt(self, persona: CompanionPersona) -> dict:
        """Returns a breakdown of token usage by block."""
        return {
            "persona_estimated": len(persona.system_prompt_block) // 4,
            "agendas": sum(len(a.description) for a in persona.agendas) // 4,
            "speech_patterns": sum(len(p) for p in persona.speech_patterns) // 4,
            "backstory": len(persona.backstory) // 4,
            "taboos": sum(len(t) for t in persona.taboos) // 4,
        }
