"""Tests for CompanionSelfModel."""
from src.ai.self_model import CompanionSelfModel


def test_record_event_appends():
    model = CompanionSelfModel("brann")
    model.record_event("hesitated at the crossroads")
    assert len(model.records) == 1
    assert model.records[0].event == "hesitated at the crossroads"


def test_net_trend_stable_by_default():
    model = CompanionSelfModel("brann")
    assert model.net_trust_trend == "stable"


def test_net_trend_improving():
    model = CompanionSelfModel("brann")
    model.total_trust_gained = 80
    model.total_trust_lost = 10
    assert model.net_trust_trend == "improving"


def test_net_trend_deteriorating():
    model = CompanionSelfModel("brann")
    model.total_trust_gained = 5
    model.total_trust_lost = 60
    assert model.net_trust_trend == "deteriorating"


def test_prompt_summary_includes_sessions():
    model = CompanionSelfModel("brann")
    model.total_sessions = 7
    summary = model.to_prompt_summary()
    assert "7" in summary


def test_player_involved_flag():
    model = CompanionSelfModel("brann")
    model.record_event("solo action", player_involved=False)
    assert model.records[0].player_was_involved is False
