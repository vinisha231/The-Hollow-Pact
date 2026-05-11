"""
Matchmaking microservice — standalone FastAPI app.
Handles player queuing and match formation independently of the AI service.
"""
from __future__ import annotations
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.multiplayer.matchmaking import MatchmakingService, QueueEntry

log = logging.getLogger(__name__)

_redis: Optional[aioredis.Redis] = None
_service: Optional[MatchmakingService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _redis, _service
    _redis = aioredis.from_url(os.environ["REDIS_URL"])
    _service = MatchmakingService(_redis)
    # Start background match-formation loop
    asyncio.create_task(_match_loop())
    log.info("matchmaking_service_ready")
    yield
    await _redis.aclose()


app = FastAPI(title="Hollow Pact — Matchmaking", lifespan=lifespan)


class EnqueueRequest(BaseModel):
    player_id: str
    character_level: int
    preferred_difficulty: str
    playstyle: str


class DequeueRequest(BaseModel):
    player_id: str


@app.post("/queue")
async def enqueue(req: EnqueueRequest):
    from src.multiplayer.matchmaking import QueueEntry
    import time
    entry = QueueEntry(
        player_id=req.player_id,
        character_level=req.character_level,
        preferred_difficulty=req.preferred_difficulty,
        playstyle=req.playstyle,
        joined_at=time.time(),
    )
    await _service.enqueue(entry)
    size = await _service.queue_size()
    return {"queued": True, "queue_size": size}


@app.delete("/queue/{player_id}")
async def dequeue(player_id: str):
    await _service.dequeue(player_id)
    return {"dequeued": True}


@app.get("/queue/size")
async def queue_size():
    size = await _service.queue_size()
    return {"queue_size": size}


@app.get("/health")
async def health():
    return {"status": "ok"}


async def _match_loop():
    """Background loop that attempts to form matches every second."""
    while True:
        try:
            result = await _service.try_match()
            if result:
                log.info("match_formed id=%s players=%s", result.match_id, result.players)
                # TODO: Notify players and spin up Hathora instance
        except Exception as exc:
            log.error("match_loop_error: %s", exc)
        await asyncio.sleep(1.0)
