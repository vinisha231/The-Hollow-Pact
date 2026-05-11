"""Tests for NPCRegistry."""
import pytest
from src.world.npc_registry import NPCRegistry, NPC_DATA


@pytest.fixture
def registry():
    return NPCRegistry()


def test_get_existing_npc(registry):
    npc = registry.get("magistrate_aldric")
    assert npc is not None
    assert npc.name == "Magistrate Aldric"


def test_get_nonexistent_npc(registry):
    assert registry.get("fake_npc") is None


def test_npcs_in_zone(registry):
    npcs = registry.in_zone("hub_saltmere")
    ids = [n.npc_id for n in npcs]
    assert "magistrate_aldric" in ids
    assert "innkeeper_rova" in ids


def test_default_dialogue_line(registry):
    npc = registry.get("magistrate_aldric")
    line = npc.get_line("neutral", set())
    assert line is not None
    assert "Pale Thread" in line


def test_conditional_dialogue_on_flag(registry):
    npc = registry.get("magistrate_aldric")
    line = npc.get_line("neutral", {"q_pale_compass_completed"})
    assert "Compass" in line


def test_companion_reaction_exists(registry):
    npc = registry.get("magistrate_aldric")
    assert "brann_ironveil" in npc.companion_reactions
