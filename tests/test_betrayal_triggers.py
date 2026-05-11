"""Tests for BetrayalTriggerSystem."""
import pytest
from src.combat.betrayal_triggers import BetrayalTriggerSystem, BetrayalType
from src.ai.trust_engine import TrustBand


def test_no_betrayal_above_threshold():
    system = BetrayalTriggerSystem()
    result = system.evaluate("act1_treasure_room", "brann", 50, TrustBand.NEUTRAL)
    assert not result.triggered
    assert result.betrayal_type == BetrayalType.NONE


def test_betrayal_triggered_below_threshold():
    system = BetrayalTriggerSystem()
    result = system.evaluate("act1_treasure_room", "brann", 25, TrustBand.HOSTILE)
    assert result.triggered
    assert result.betrayal_type == BetrayalType.STEAL_MACGUFFIN


def test_hard_betrayal_only_once():
    system = BetrayalTriggerSystem()
    system.evaluate("act1_treasure_room", "brann", 25, TrustBand.HOSTILE)
    result2 = system.evaluate("act1_treasure_room", "brann", 10, TrustBand.HOSTILE)
    assert not result2.triggered


def test_act2_midboss_turn_hostile():
    system = BetrayalTriggerSystem()
    result = system.evaluate("act2_midboss", "ossian", 15, TrustBand.HOSTILE)
    assert result.triggered
    assert result.betrayal_type == BetrayalType.TURN_HOSTILE


def test_soft_sandbag_can_retrigger():
    system = BetrayalTriggerSystem()
    r1 = system.evaluate("soft_any_combat", "lyra", 20, TrustBand.SUSPICIOUS)
    r2 = system.evaluate("soft_any_combat", "lyra", 20, TrustBand.SUSPICIOUS)
    assert r1.triggered
    assert r2.triggered  # soft betrayal is not one-shot


def test_unknown_beat_returns_safe():
    system = BetrayalTriggerSystem()
    result = system.evaluate("nonexistent_beat", "brann", 0, TrustBand.HOSTILE)
    assert not result.triggered


def test_beat_has_telegraph_hints():
    system = BetrayalTriggerSystem()
    result = system.evaluate("act1_treasure_room", "brann", 25, TrustBand.HOSTILE)
    assert result.beat is not None
    assert len(result.beat.telegraphed_by) > 0
