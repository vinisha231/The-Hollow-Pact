"""
MemorySummariser — background job that condenses short-term events into
episodic memories every N events, keeping the long-term store from bloating.
"""
from __future__ import annotations
import asyncio
import logging
import time
import uuid
from typing import List

import anthropic

from .memory_store import MemoryStore, ShortTermEvent, EpisodicMemory

log = logging.getLogger(__name__)

SUMMARISE_MODEL = "claude-haiku-4-5-20251001"
SUMMARISE_INTERVAL_SECONDS = 1800  # 30 minutes


class MemorySummariser:
    def __init__(self, memory: MemoryStore, claude: anthropic.AsyncAnthropic):
        self._memory = memory
        self._claude = claude

    async def summarise_events(
        self,
        companion_id: str,
        player_id: str,
        events: List[ShortTermEvent],
    ) -> EpisodicMemory:
        """Condenses a list of events into a single episodic memory."""
        event_text = "\n".join(
            f"- [{e.actor}] {e.summary}" for e in events
        )
        prompt = f"""
You are summarising gameplay events for a companion AI memory system.
Condense the following events into 2-3 sentences that capture:
1. What happened narratively
2. How the player treated the companion (if relevant)
3. Any important world-state changes

Events:
{event_text}

Write only the summary. No preamble.
""".strip()

        response = await self._claude.messages.create(
            model=SUMMARISE_MODEL,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        summary = response.content[0].text.strip()
        importance = self._score_importance(events)

        memory = EpisodicMemory(
            memory_id=str(uuid.uuid4()),
            companion_id=companion_id,
            player_id=player_id,
            created_at=time.time(),
            content=summary,
            importance=importance,
        )
        await self._memory.store_episodic(memory)
        log.info(
            "episodic_stored companion=%s player=%s importance=%.2f",
            companion_id, player_id, importance,
        )
        return memory

    @staticmethod
    def _score_importance(events: List[ShortTermEvent]) -> float:
        """Higher trust deltas = more important memory."""
        total_delta = sum(abs(e.trust_delta) for e in events)
        return min(1.0, 0.3 + total_delta / 100.0)

    async def run_periodic(self, companion_id: str, player_id: str) -> None:
        """Long-running loop for background summarisation."""
        while True:
            await asyncio.sleep(SUMMARISE_INTERVAL_SECONDS)
            key = f"{companion_id}:{player_id}"
            events = self._memory._short_term.get(key, [])
            if events:
                try:
                    await self.summarise_events(companion_id, player_id, events)
                except Exception as exc:
                    log.error("summarise_error: %s", exc)
