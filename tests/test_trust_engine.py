"""Tests for TrustEngine."""
import pytest
from src.ai.trust_engine import TrustEngine, TrustState, TrustBand


def make_state(value: int = 50) -> TrustState:
    s = TrustState(companion_id="brann", player_id="player1")
    s.value = value
    return s


def test_initial_band_neutral():
    state = make_state(50)
    assert state.band == TrustBand.NEUTRAL


def test_trust_increases():
    engine = TrustEngine()
    state = make_state(50)
    band, betrayal = engine.record_event(state, "kept_promise", "sess1")
    assert state.value == 58
    assert not betrayal


def test_trust_decreases():
    engine = TrustEngine()
    state = make_state(50)
    engine.record_event(state, "broke_promise", "sess1")
    assert state.value == 35


def test_trust_clamped_at_zero():
    engine = TrustEngine()
    state = make_state(5)
    engine.record_event(state, "humiliated_companion", "sess1")
    assert state.value == 0


def test_trust_clamped_at_100():
    engine = TrustEngine()
    state = make_state(98)
    engine.record_event(state, "kept_promise", "sess1")
    assert state.value == 100


def test_betrayal_triggered_below_threshold():
    engine = TrustEngine(persona_loyalty_threshold=25)
    state = make_state(30)
    band, betrayal = engine.record_event(state, "abandoned_companion", "sess1")
    assert state.value == 10
    assert betrayal is True
    assert state.betrayal_triggered is True


def test_betrayal_only_triggers_once():
    engine = TrustEngine(persona_loyalty_threshold=25)
    state = make_state(30)
    _, first = engine.record_event(state, "abandoned_companion", "sess1")
    state.value = 30  # manually reset trust for next event
    state.betrayal_triggered = True  # already triggered
    _, second = engine.record_event(state, "abandoned_companion", "sess1")
    assert first is True
    assert second is False


def test_tone_directive_devoted():
    engine = TrustEngine()
    state = make_state(90)
    directive = engine.get_llm_tone_directive(state)
    assert "loyal" in directive.lower() or "devoted" in directive.lower()


def test_tone_directive_hostile():
    engine = TrustEngine()
    state = make_state(10)
    directive = engine.get_llm_tone_directive(state)
    assert "cold" in directive.lower() or "contempt" in directive.lower()


def test_event_history_appended():
    engine = TrustEngine()
    state = make_state(50)
    engine.record_event(state, "shared_loot", "sess1")
    engine.record_event(state, "lied_to_companion", "sess1")
    assert len(state.events) == 2
    assert state.events[0].reason == "shared_loot"
    assert state.events[1].reason == "lied_to_companion"
