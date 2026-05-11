"""
TokenBudgetLimiter — per-player hourly token budget to prevent cost runaway.
Implemented as a sliding window in Redis.
"""
from __future__ import annotations
import logging
import time
from typing import Optional

import redis.asyncio as aioredis

log = logging.getLogger(__name__)

DEFAULT_HOURLY_BUDGET = 50_000   # tokens
WINDOW_SECONDS = 3600


class TokenBudgetLimiter:
    def __init__(self, redis: aioredis.Redis, hourly_budget: int = DEFAULT_HOURLY_BUDGET):
        self._redis = redis
        self._budget = hourly_budget

    async def check_and_consume(
        self,
        player_id: str,
        estimated_tokens: int,
    ) -> tuple[bool, int]:
        """
        Returns (allowed, remaining_budget).
        Deducts estimated_tokens from the player's hourly budget.
        """
        key = f"token_budget:{player_id}:{self._window_key()}"
        pipe = self._redis.pipeline()
        pipe.incrby(key, estimated_tokens)
        pipe.expire(key, WINDOW_SECONDS)
        results = await pipe.execute()
        total_used = results[0]
        remaining = max(0, self._budget - total_used)

        if total_used > self._budget:
            log.warning("budget_exceeded player=%s used=%d budget=%d", player_id, total_used, self._budget)
            return False, 0

        return True, remaining

    async def get_usage(self, player_id: str) -> int:
        key = f"token_budget:{player_id}:{self._window_key()}"
        val = await self._redis.get(key)
        return int(val) if val else 0

    def _window_key(self) -> int:
        return int(time.time()) // WINDOW_SECONDS
