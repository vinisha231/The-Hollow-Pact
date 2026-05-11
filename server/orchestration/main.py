"""
AI Orchestration Service — FastAPI app.
Receives game events from the dedicated server and calls companion AI.
"""
from __future__ import annotations
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

import anthropic
import asyncpg
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
from pydantic import BaseModel
import redis.asyncio as aioredis

from src.ai import (
    ConversationOrchestrator, OrchestratorInput,
    TrustEngine, MemoryStore, InjectionGuard, MemorySummariser,
)
from src.companion.companion_loader import CompanionLoader

log = logging.getLogger(__name__)

# ── App state ─────────────────────────────────────────────────────────────

_db_pool: Optional[asyncpg.Pool] = None
_redis: Optional[aioredis.Redis] = None
_orchestrator: Optional[ConversationOrchestrator] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _db_pool, _redis, _orchestrator

    _db_pool = await asyncpg.create_pool(os.environ["DATABASE_URL"])
    _redis = aioredis.from_url(os.environ["REDIS_URL"])

    openai_client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
    claude_client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    memory = MemoryStore(_db_pool, openai_client)
    trust = TrustEngine()
    guard = InjectionGuard()

    _orchestrator = ConversationOrchestrator(memory, trust, guard, claude_client)

    # Pre-load all companion archetypes
    loader = CompanionLoader()
    for archetype_id in loader.list_archetypes():
        persona = loader.load(archetype_id, "default")
        _orchestrator.register_companion(persona)

    log.info("orchestration_service_ready")
    yield

    await _db_pool.close()
    await _redis.aclose()


app = FastAPI(title="Hollow Pact — AI Orchestration", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)


# ── Request models ────────────────────────────────────────────────────────

class DialogueRequest(BaseModel):
    session_id: str
    companion_id: str
    player_id: str
    raw_text: str
    world_state: dict
    combat_active: bool = False


class TrustEventRequest(BaseModel):
    companion_id: str
    player_id: str
    event_type: str
    session_id: str
    override_delta: Optional[int] = None


# ── Routes ────────────────────────────────────────────────────────────────

@app.post("/dialogue")
async def dialogue(req: DialogueRequest):
    if _orchestrator is None:
        raise HTTPException(503, "Service not ready")
    inp = OrchestratorInput(**req.model_dump())
    result = await _orchestrator.process(inp)
    return {
        "dialogue": result.dialogue,
        "intent": result.intent,
        "intent_target": result.intent_target,
        "trust_band": result.trust_band,
        "latency_ms": round(result.latency_ms, 1),
    }


@app.post("/trust_event")
async def trust_event(req: TrustEventRequest):
    if _orchestrator is None:
        raise HTTPException(503, "Service not ready")
    state = _orchestrator.get_trust_state(req.companion_id, req.player_id)
    trust = _orchestrator._trust
    band, betrayal = trust.record_event(
        state, req.event_type, req.session_id, req.override_delta
    )
    return {
        "trust_band": band.value,
        "trust_value": state.value,
        "betrayal_unlocked": betrayal,
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
