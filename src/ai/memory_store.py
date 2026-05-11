"""
MemoryStore — three-tier memory system for companion persistence.

Tiers:
  1. Short-term  — rolling window of last N events (in-prompt)
  2. Episodic    — summarised events in pgvector (retrieved by similarity)
  3. Semantic    — structured world-facts in Postgres (explicit key/value)
"""
from __future__ import annotations
import json
import time
import uuid
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any

import asyncpg
from openai import AsyncOpenAI  # for embeddings only

log = logging.getLogger(__name__)

EMBEDDING_MODEL = "text-embedding-3-small"
SHORT_TERM_WINDOW = 20          # events
EPISODIC_TOP_K = 5              # retrieved memories per turn
SUMMARISE_EVERY_N_EVENTS = 30   # trigger background summarisation


@dataclass
class ShortTermEvent:
    event_id: str
    session_id: str
    timestamp: float
    actor: str        # "player", "companion", "world"
    summary: str      # one-sentence description
    trust_delta: int  # 0 if unrelated to trust


@dataclass
class EpisodicMemory:
    memory_id: str
    companion_id: str
    player_id: str
    created_at: float
    content: str          # prose summary of an episode
    embedding: List[float] = field(default_factory=list, repr=False)
    importance: float = 0.5   # 0-1; boosted for betrayal-relevant events


@dataclass
class SemanticFact:
    fact_id: str
    companion_id: str
    player_id: str
    key: str          # e.g. "player_gave_locket"
    value: str        # e.g. "Ruby gave silver locket in Act 2 Chapter 3"
    updated_at: float


class MemoryStore:
    def __init__(self, db_pool: asyncpg.Pool, openai_client: AsyncOpenAI):
        self._db = db_pool
        self._openai = openai_client
        self._short_term: Dict[str, List[ShortTermEvent]] = {}  # key: f"{companion}:{player}"

    # ── Short-term ────────────────────────────────────────────────────────────

    def push_event(self, companion_id: str, player_id: str, event: ShortTermEvent) -> None:
        key = f"{companion_id}:{player_id}"
        window = self._short_term.setdefault(key, [])
        window.append(event)
        if len(window) > SHORT_TERM_WINDOW:
            window.pop(0)
        if len(window) % SUMMARISE_EVERY_N_EVENTS == 0:
            log.info("summarise_trigger key=%s", key)
            # Background job signals via event bus; not awaited here

    def get_short_term_text(self, companion_id: str, player_id: str) -> str:
        key = f"{companion_id}:{player_id}"
        events = self._short_term.get(key, [])
        if not events:
            return "No recent events."
        lines = [f"- [{e.actor}] {e.summary}" for e in events[-SHORT_TERM_WINDOW:]]
        return "\n".join(lines)

    # ── Episodic ──────────────────────────────────────────────────────────────

    async def store_episodic(self, memory: EpisodicMemory) -> None:
        embedding = await self._embed(memory.content)
        memory.embedding = embedding
        await self._db.execute(
            """
            INSERT INTO episodic_memories
              (memory_id, companion_id, player_id, created_at, content, embedding, importance)
            VALUES ($1,$2,$3,$4,$5,$6::vector,$7)
            """,
            memory.memory_id, memory.companion_id, memory.player_id,
            memory.created_at, memory.content,
            json.dumps(embedding), memory.importance,
        )

    async def retrieve_episodic(
        self, companion_id: str, player_id: str, query: str
    ) -> List[EpisodicMemory]:
        query_emb = await self._embed(query)
        rows = await self._db.fetch(
            """
            SELECT memory_id, companion_id, player_id, created_at, content, importance
            FROM episodic_memories
            WHERE companion_id=$1 AND player_id=$2
            ORDER BY embedding <-> $3::vector
            LIMIT $4
            """,
            companion_id, player_id, json.dumps(query_emb), EPISODIC_TOP_K,
        )
        return [EpisodicMemory(**dict(r), embedding=[]) for r in rows]

    # ── Semantic ──────────────────────────────────────────────────────────────

    async def set_fact(self, fact: SemanticFact) -> None:
        await self._db.execute(
            """
            INSERT INTO semantic_facts (fact_id, companion_id, player_id, key, value, updated_at)
            VALUES ($1,$2,$3,$4,$5,$6)
            ON CONFLICT (companion_id, player_id, key)
            DO UPDATE SET value=EXCLUDED.value, updated_at=EXCLUDED.updated_at
            """,
            fact.fact_id, fact.companion_id, fact.player_id,
            fact.key, fact.value, fact.updated_at,
        )

    async def get_facts(self, companion_id: str, player_id: str) -> Dict[str, str]:
        rows = await self._db.fetch(
            "SELECT key, value FROM semantic_facts WHERE companion_id=$1 AND player_id=$2",
            companion_id, player_id,
        )
        return {r["key"]: r["value"] for r in rows}

    # ── Prompt assembly ───────────────────────────────────────────────────────

    async def build_memory_block(
        self, companion_id: str, player_id: str, current_context: str
    ) -> str:
        short = self.get_short_term_text(companion_id, player_id)
        episodic = await self.retrieve_episodic(companion_id, player_id, current_context)
        facts = await self.get_facts(companion_id, player_id)

        ep_text = "\n".join(f"- {m.content}" for m in episodic) or "None."
        fact_text = "\n".join(f"- {k}: {v}" for k, v in facts.items()) or "None."

        return f"""
RECENT EVENTS (last {SHORT_TERM_WINDOW}):
{short}

MEMORIES (most relevant):
{ep_text}

KNOWN FACTS ABOUT THIS PLAYER:
{fact_text}
""".strip()

    # ── Internal ──────────────────────────────────────────────────────────────

    async def _embed(self, text: str) -> List[float]:
        resp = await self._openai.embeddings.create(
            model=EMBEDDING_MODEL, input=text
        )
        return resp.data[0].embedding
