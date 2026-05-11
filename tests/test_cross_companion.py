"""Tests for CrossCompanionSystem."""
import pytest
from src.multiplayer.cross_companion import CrossCompanionSystem, CompanionOpinion


@pytest.fixture
def system():
    s = CrossCompanionSystem()
    s.initialise_defaults()
    return s


def test_defaults_set_ossian_suspicious_of_lyra(system):
    block = system.get_opinion_block("ossian_vex")
    assert "lyra_nightwhisper" in block


def test_opinion_update_changes_value(system):
    system.update_opinion("brann_ironveil", "lyra_nightwhisper", 30, "She healed me when she didn't have to.")
    block = system.get_opinion_block("brann_ironveil")
    assert "lyra_nightwhisper" in block


def test_opinion_clamped_at_100(system):
    system.update_opinion("brann_ironveil", "ossian_vex", 200, "somehow amazing")
    opinions = system._opinions["brann_ironveil"]["ossian_vex"]
    assert opinions.opinion <= 100


def test_opinion_clamped_at_minus_100(system):
    system.update_opinion("ossian_vex", "brann_ironveil", -200, "worst")
    opinions = system._opinions["ossian_vex"]["brann_ironveil"]
    assert opinions.opinion >= -100


def test_unknown_observer_returns_empty(system):
    block = system.get_opinion_block("nonexistent_companion")
    assert block == ""


def test_opinion_label_wary():
    op = CompanionOpinion("target", -15)
    assert op.label == "wary"


def test_opinion_label_respect():
    op = CompanionOpinion("target", 80)
    assert op.label == "respect"
