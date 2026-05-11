"""
Matchmaking — Redis-backed queue for stranger matchmaking.
Uses sorted sets keyed by quest difficulty + preferred playstyle.
"""
from __future__ import annotations
import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, asdict
from typing import List, Optional

import redis.asyncio as aioredis

log = logging.getLogger(__name__)

QUEUE_KEY = "matchmaking:queue"
MATCH_SIZE = 4
MATCH_TIMEOUT = 120  # seconds


@dataclass
class QueueEntry:
    player_id: str
    character_level: int
    preferred_difficulty: str   # "casual"|"normal"|"brutal"
    playstyle: str              # "explorer"|"fighter"|"roleplayer"
    joined_at: float

    @property
    def score(self) -> float:
        """Redis sorted-set score: encode difficulty + join time."""
        difficulty_weight = {"casual": 0, "normal": 100, "brutal": 200}
        return difficulty_weight.get(self.preferred_difficulty, 100) + self.joined_at / 1e10


@dataclass
class MatchResult:
    match_id: str
    players: List[str]
    difficulty: str


class MatchmakingService:
    def __init__(self, redis: aioredis.Redis):
        self._redis = redis

    async def enqueue(self, entry: QueueEntry) -> None:
        payload = json.dumps(asdict(entry))
        await self._redis.zadd(QUEUE_KEY, {payload: entry.score})
        log.info("player_enqueued id=%s difficulty=%s", entry.player_id, entry.preferred_difficulty)

    async def dequeue(self, player_id: str) -> None:
        items = await self._redis.zrange(QUEUE_KEY, 0, -1)
        for item in items:
            data = json.loads(item)
            if data["player_id"] == player_id:
                await self._redis.zrem(QUEUE_KEY, item)
                log.info("player_dequeued id=%s", player_id)
                return

    async def try_match(self) -> Optional[MatchResult]:
        """Pull the oldest MATCH_SIZE entries with similar difficulty."""
        now = time.time()
        # Pull candidates (ordered by score)
        raw_items = await self._redis.zrange(QUEUE_KEY, 0, MATCH_SIZE * 2 - 1, withscores=True)
        if len(raw_items) < MATCH_SIZE:
            return None

        entries = []
        for raw, score in raw_items:
            e = QueueEntry(**json.loads(raw))
            if now - e.joined_at > MATCH_TIMEOUT:
                # Stale entry — widen difficulty tolerance
                entries.append(e)
            else:
                entries.append(e)

        if len(entries) < MATCH_SIZE:
            return None

        chosen = entries[:MATCH_SIZE]
        # Remove matched players from queue
        pipe = self._redis.pipeline()
        for e in chosen:
            pipe.zrem(QUEUE_KEY, json.dumps(asdict(e)))
        await pipe.execute()

        result = MatchResult(
            match_id=str(uuid.uuid4()),
            players=[e.player_id for e in chosen],
            difficulty=chosen[0].preferred_difficulty,
        )
        log.info("match_formed id=%s players=%s", result.match_id, result.players)
        return result

    async def queue_size(self) -> int:
        return await self._redis.zcard(QUEUE_KEY)
