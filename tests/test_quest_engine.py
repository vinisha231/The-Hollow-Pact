"""Tests for QuestEngine."""
import pytest
from src.world.world_state import WorldState
from src.world.quest_engine import QuestEngine


def make_engine(zone="hub_saltmere"):
    world = WorldState(
        campaign_id="test", current_zone=zone,
        time_of_day="day", act=1, session_number=1,
    )
    return QuestEngine(world), world


def test_available_quests_in_zone():
    engine, _ = make_engine("hub_saltmere")
    quests = engine.available_quests("hub_saltmere")
    ids = [q.quest_id for q in quests]
    assert "q_pale_compass" in ids


def test_accept_quest_adds_to_world():
    engine, world = make_engine()
    engine.accept_quest("q_pale_compass")
    assert "q_pale_compass" in world.quests


def test_accept_unknown_quest_raises():
    engine, _ = make_engine()
    with pytest.raises(ValueError):
        engine.accept_quest("q_nonexistent")


def test_complete_objective():
    engine, world = make_engine()
    engine.accept_quest("q_pale_compass")
    result = engine.complete_objective("q_pale_compass", "obj_enter_varek")
    assert result is True
    assert world.quests["q_pale_compass"].objectives["obj_enter_varek"] is True


def test_quest_completes_when_required_objectives_done():
    engine, world = make_engine()
    engine.accept_quest("q_pale_compass")
    required_ids = ["obj_enter_varek", "obj_find_vault", "obj_defeat_archivist", "obj_retrieve_compass"]
    for obj_id in required_ids:
        engine.complete_objective("q_pale_compass", obj_id)
    assert world.quests["q_pale_compass"].status == "completed"


def test_optional_objective_doesnt_complete_quest():
    engine, world = make_engine()
    engine.accept_quest("q_pale_compass")
    engine.complete_objective("q_pale_compass", "obj_ironveil_deed")  # optional
    assert world.quests["q_pale_compass"].status == "active"


def test_completed_quest_not_in_available():
    engine, world = make_engine()
    engine.accept_quest("q_pale_compass")
    quests = engine.available_quests("hub_saltmere")
    ids = [q.quest_id for q in quests]
    assert "q_pale_compass" not in ids
