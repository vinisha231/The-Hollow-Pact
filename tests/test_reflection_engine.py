"""Tests for ReflectionEngine parsing."""
import pytest
from src.ai.reflection_engine import ReflectionEngine


def test_parse_reflection_basic():
    text = """EMOTIONAL_STATE: cold contempt
OBSERVATIONS:
- Player abandoned me in the Thornwood fight
- Player lied about the loot split
- Player dismissed my concern about the shrine
BETRAYAL_RISK: high
SUMMARY: This session confirmed my suspicions. Trust is nearly gone."""
    
    result = ReflectionEngine._parse_reflection("brann", "player1", text)
    assert result.emotional_state == "cold contempt"
    assert len(result.key_observations) == 3
    assert result.betrayal_risk == "high"
    assert "Trust is nearly gone" in result.session_summary


def test_parse_reflection_none_risk():
    text = """EMOTIONAL_STATE: guarded optimism
OBSERVATIONS:
- Player kept their promise about the merchant
BETRAYAL_RISK: none
SUMMARY: A promising session. Perhaps I was wrong about them."""
    
    result = ReflectionEngine._parse_reflection("lyra", "player1", text)
    assert result.betrayal_risk == "none"
    assert result.emotional_state == "guarded optimism"


def test_parse_reflection_malformed_graceful():
    text = "Something completely unstructured that doesn't match the format at all"
    result = ReflectionEngine._parse_reflection("ossian", "player1", text)
    # Should not raise; should return defaults
    assert result.companion_id == "ossian"
    assert result.player_id == "player1"
    assert result.betrayal_risk == "none"
