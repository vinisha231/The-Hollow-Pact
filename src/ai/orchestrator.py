"""
ConversationOrchestrator — central pipeline for companion AI turns.

Pipeline:
  raw_input → guard → memory_retrieval → prompt_build → LLM → intent_parse → output
"""
from __future__ import annotations
import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass
from typing import Optional

import anthropic

from .companion_persona import CompanionPersona
from .trust_engine import TrustEngine, TrustState
from .memory_store import MemoryStore, ShortTermEvent
from .injection_guard import InjectionGuard

log = logging.getLogger(__name__)

DIALOGUE_MODEL = "claude-sonnet-4-6"
REFLECTION_MODEL = "claude-opus-4-7"   # for periodic deep reflection passes
MAX_DIALOGUE_TOKENS = 512
RETRY_LIMIT = 2


@dataclass
class OrchestratorInput:
    session_id: str
    companion_id: str
    player_id: str
    raw_text: str          # already transcribed from STT
    world_state: dict      # injected by game server
    combat_active: bool


@dataclass
class OrchestratorOutput:
    dialogue: str           # final spoken line
    intent: str             # "idle"|"attack"|"flee"|"refuse_order"|"betray"
    intent_target: Optional[str]  # enemy ID or None
    trust_band: str
    latency_ms: float


class ConversationOrchestrator:
    def __init__(
        self,
        memory: MemoryStore,
        trust: TrustEngine,
        guard: InjectionGuard,
        claude: anthropic.AsyncAnthropic,
    ):
        self._memory = memory
        self._trust = trust
        self._guard = guard
        self._claude = claude
        self._personas: dict[str, CompanionPersona] = {}
        self._trust_states: dict[str, TrustState] = {}

    def register_companion(self, persona: CompanionPersona) -> None:
        self._personas[persona.companion_id] = persona

    def get_trust_state(self, companion_id: str, player_id: str) -> TrustState:
        key = f"{companion_id}:{player_id}"
        if key not in self._trust_states:
            self._trust_states[key] = TrustState(
                companion_id=companion_id, player_id=player_id
            )
        return self._trust_states[key]

    async def process(self, inp: OrchestratorInput) -> OrchestratorOutput:
        t0 = time.monotonic()
        persona = self._personas[inp.companion_id]
        trust_state = self.get_trust_state(inp.companion_id, inp.player_id)

        # 1. Injection guard
        clean_text, flagged = self._guard.sanitise(inp.raw_text)
        if flagged:
            log.warning("injection_flagged session=%s text=%r", inp.session_id, inp.raw_text)

        # 2. Memory retrieval
        memory_block = await self._memory.build_memory_block(
            inp.companion_id, inp.player_id, clean_text
        )

        # 3. Build prompt
        system = self._build_system(persona, trust_state, inp.world_state, memory_block)
        user_msg = clean_text if clean_text else "[Player is silent]"

        # 4. LLM call with retry
        raw_response = await self._call_llm(system, user_msg, inp.combat_active)

        # 5. Parse structured output
        dialogue, intent, intent_target = self._parse_response(raw_response)

        # 6. Push to short-term memory
        self._memory.push_event(
            inp.companion_id, inp.player_id,
            ShortTermEvent(
                event_id=str(uuid.uuid4()),
                session_id=inp.session_id,
                timestamp=time.time(),
                actor="player",
                summary=clean_text[:120],
                trust_delta=0,
            ),
        )

        latency = (time.monotonic() - t0) * 1000
        return OrchestratorOutput(
            dialogue=dialogue,
            intent=intent,
            intent_target=intent_target,
            trust_band=trust_state.band.value,
            latency_ms=latency,
        )

    def _build_system(
        self,
        persona: CompanionPersona,
        trust_state: TrustState,
        world_state: dict,
        memory_block: str,
    ) -> str:
        tone = self._trust.get_llm_tone_directive(trust_state)
        world_text = json.dumps(world_state, indent=2)
        return f"""
{persona.system_prompt_block}

CURRENT TRUST TONE:
{tone}

WORLD STATE:
{world_text}

MEMORY:
{memory_block}

RESPONSE FORMAT — always respond with JSON:
{{
  "dialogue": "<what you say aloud, 1-3 sentences, in character>",
  "intent": "<one of: idle, attack, flee, refuse_order, betray>",
  "intent_target": "<entity ID or null>"
}}
""".strip()

    async def _call_llm(self, system: str, user_msg: str, combat: bool) -> str:
        model = DIALOGUE_MODEL  # use fast model for combat
        for attempt in range(RETRY_LIMIT + 1):
            try:
                msg = await self._claude.messages.create(
                    model=model,
                    max_tokens=MAX_DIALOGUE_TOKENS,
                    system=system,
                    messages=[{"role": "user", "content": user_msg}],
                )
                return msg.content[0].text
            except Exception as exc:
                if attempt == RETRY_LIMIT:
                    log.error("llm_failed after %d attempts: %s", RETRY_LIMIT, exc)
                    return '{"dialogue": "...", "intent": "idle", "intent_target": null}'
                await asyncio.sleep(0.2 * (attempt + 1))

    @staticmethod
    def _parse_response(raw: str) -> tuple[str, str, Optional[str]]:
        try:
            data = json.loads(raw)
            return (
                data.get("dialogue", "..."),
                data.get("intent", "idle"),
                data.get("intent_target"),
            )
        except json.JSONDecodeError:
            log.warning("non_json_response: %r", raw[:200])
            return raw[:300], "idle", None
