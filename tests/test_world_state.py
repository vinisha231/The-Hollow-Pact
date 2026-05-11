"""Tests for WorldState."""
import pytest
from src.world.world_state import WorldState, QuestState, EntityState, CampaignFlags
import json


def make_world():
    return WorldState(
        campaign_id="test_campaign",
        current_zone="hub_saltmere",
        time_of_day="day",
        act=1,
        session_number=1,
    )


def test_initial_state():
    world = make_world()
    assert world.act == 1
    assert world.current_zone == "hub_saltmere"


def test_advance_time_cycles():
    world = make_world()
    world.time_of_day = "night"
    world.advance_time()
    assert world.time_of_day == "dawn"


def test_advance_time_day_to_dusk():
    world = make_world()
    world.advance_time()
    assert world.time_of_day == "dusk"


def test_prompt_snapshot_is_valid_json():
    world = make_world()
    snapshot = world.to_prompt_snapshot()
    data = json.loads(snapshot)
    assert "zone" in data
    assert "time" in data
    assert "act" in data


def test_prompt_snapshot_includes_active_quests():
    world = make_world()
    world.quests["q1"] = QuestState(
        quest_id="q1", name="The Pale Compass",
        status="active", objectives={}, notes=[],
    )
    snapshot = json.loads(world.to_prompt_snapshot())
    assert "Pale Compass" in snapshot["active_quests"]


def test_prompt_snapshot_excludes_completed_quests():
    world = make_world()
    world.quests["q1"] = QuestState(
        quest_id="q1", name="Old Quest",
        status="completed", objectives={}, notes=[],
    )
    snapshot = json.loads(world.to_prompt_snapshot())
    assert "Old Quest" not in snapshot["active_quests"]


def test_campaign_flag_set_and_check():
    flags = CampaignFlags()
    flags.set("ironveil_deed_found")
    assert flags.check("ironveil_deed_found") is True
    assert flags.check("other_flag") is False


def test_dict_roundtrip():
    world = make_world()
    world.quests["q1"] = QuestState("q1", "Quest One", "active", {}, [])
    d = world.to_dict()
    restored = WorldState.from_dict(d)
    assert restored.campaign_id == world.campaign_id
    assert "q1" in restored.quests
