"""Tests for MatchmakingService."""
import asyncio
import json
import time
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.multiplayer.matchmaking import MatchmakingService, QueueEntry


def make_entry(player_id: str, difficulty: str = "normal") -> QueueEntry:
    return QueueEntry(
        player_id=player_id,
        character_level=5,
        preferred_difficulty=difficulty,
        playstyle="fighter",
        joined_at=time.time(),
    )


@pytest.mark.asyncio
async def test_enqueue_calls_zadd():
    redis = AsyncMock()
    service = MatchmakingService(redis)
    entry = make_entry("p1")
    await service.enqueue(entry)
    redis.zadd.assert_called_once()


@pytest.mark.asyncio
async def test_not_enough_players_returns_none():
    redis = AsyncMock()
    redis.zrange = AsyncMock(return_value=[
        (json.dumps({"player_id": "p1", "character_level": 1,
                     "preferred_difficulty": "normal", "playstyle": "fighter",
                     "joined_at": time.time()}), 1.0),
        (json.dumps({"player_id": "p2", "character_level": 1,
                     "preferred_difficulty": "normal", "playstyle": "fighter",
                     "joined_at": time.time()}), 2.0),
    ])
    service = MatchmakingService(redis)
    result = await service.try_match()
    assert result is None


@pytest.mark.asyncio
async def test_four_players_match():
    entries = [
        {"player_id": f"p{i}", "character_level": 5,
         "preferred_difficulty": "normal", "playstyle": "fighter",
         "joined_at": time.time()}
        for i in range(4)
    ]
    redis = AsyncMock()
    redis.zrange = AsyncMock(return_value=[
        (json.dumps(e), float(i)) for i, e in enumerate(entries)
    ])
    pipe = AsyncMock()
    redis.pipeline = MagicMock(return_value=pipe)
    pipe.__aenter__ = AsyncMock(return_value=pipe)
    pipe.__aexit__ = AsyncMock(return_value=None)
    pipe.execute = AsyncMock(return_value=[1, 1, 1, 1])
    service = MatchmakingService(redis)
    result = await service.try_match()
    assert result is not None
    assert len(result.players) == 4
