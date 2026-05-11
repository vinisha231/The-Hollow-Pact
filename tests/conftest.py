"""Shared pytest fixtures."""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.ai.companion_persona import (
    CompanionPersona, PersonalityVector, LoyaltyStance
)
from src.ai.trust_engine import TrustEngine, TrustState


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def brann_persona():
    return CompanionPersona(
        companion_id="brann_test",
        name="Brann Ironveil",
        archetype="disgraced_knight",
        voice_id="v_brann",
        personality=PersonalityVector(
            warmth=35, ambition=60, honesty=75, courage=80,
            deception_tolerance=30, loyalty_threshold=25,
        ),
        stance=LoyaltyStance.CONDITIONAL,
        agendas=[],
        backstory="A disgraced knight seeking redemption.",
        speech_patterns=["Right then.", "I've seen worse."],
        taboos=["Lord Caldrath"],
    )


@pytest.fixture
def trust_engine():
    return TrustEngine(persona_loyalty_threshold=25)


@pytest.fixture
def trust_state():
    return TrustState(companion_id="brann_test", player_id="player1")


@pytest.fixture
def mock_claude():
    client = AsyncMock()
    msg = MagicMock()
    msg.content = [MagicMock(text='{"dialogue": "Right then.", "intent": "idle", "intent_target": null}')]
    client.messages.create = AsyncMock(return_value=msg)
    return client


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def mock_redis():
    return AsyncMock()
