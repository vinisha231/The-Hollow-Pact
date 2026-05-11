"""Tests for CompanionLoader."""
import pytest
from src.companion.companion_loader import CompanionLoader
from src.ai.companion_persona import LoyaltyStance


@pytest.fixture
def loader():
    return CompanionLoader()


def test_list_archetypes(loader):
    archetypes = loader.list_archetypes()
    assert "brann_ironveil" in archetypes
    assert "lyra_nightwhisper" in archetypes
    assert "ossian_vex" in archetypes


def test_load_brann(loader):
    persona = loader.load("brann_ironveil", "campaign_abc")
    assert persona.name == "Brann Ironveil"
    assert persona.archetype == "disgraced_knight"
    assert len(persona.agendas) >= 1


def test_load_unknown_archetype(loader):
    with pytest.raises(ValueError, match="Unknown archetype"):
        loader.load("nonexistent_companion", "campaign_abc")


def test_personality_variance_between_campaigns(loader):
    p1 = loader.load("brann_ironveil", "campaign_aaa", seed=1)
    p2 = loader.load("brann_ironveil", "campaign_bbb", seed=2)
    # personality may differ but should be within ±5 of base
    assert abs(p1.personality.warmth - p2.personality.warmth) <= 10


def test_personality_clamped(loader):
    persona = loader.load("brann_ironveil", "campaign_test", seed=42)
    for attr in vars(persona.personality).values():
        assert 0 <= attr <= 100


def test_same_seed_same_result(loader):
    p1 = loader.load("brann_ironveil", "campaign_x", seed=99)
    p2 = loader.load("brann_ironveil", "campaign_x", seed=99)
    assert p1.personality.warmth == p2.personality.warmth


def test_random_companion_returns_persona(loader):
    persona = loader.random_companion("campaign_test")
    assert persona.name


def test_random_companion_excludes(loader):
    for _ in range(20):
        persona = loader.random_companion("campaign_test", exclude=["brann_ironveil"])
        assert persona.archetype != "disgraced_knight"
