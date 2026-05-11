"""Tests for IntelSystem."""
import pytest
from src.world.intel_system import IntelSystem, COMPANION_FACTION_CONTACTS


def test_loyal_companion_no_leak():
    system = IntelSystem()
    for _ in range(50):
        result = system.evaluate_leak("ossian_vex", "loyal", "thornwood", COMPANION_FACTION_CONTACTS)
        assert result is None


def test_hostile_companion_may_leak():
    system = IntelSystem()
    leaked = False
    for _ in range(100):
        result = system.evaluate_leak("ossian_vex", "hostile", "thornwood", COMPANION_FACTION_CONTACTS)
        if result is not None:
            leaked = True
            assert result.companion_id == "ossian_vex"
            assert result.faction_tipped == "silent_hand"
            break
    assert leaked


def test_no_contacts_no_leak():
    system = IntelSystem()
    contacts = {"brann_ironveil": None}
    for _ in range(50):
        result = system.evaluate_leak("brann_ironveil", "hostile", "varek", contacts)
        assert result is None


def test_leak_has_effect(capsys):
    system = IntelSystem()
    leaked = None
    for _ in range(100):
        result = system.evaluate_leak("ossian_vex", "hostile", "thornwood", COMPANION_FACTION_CONTACTS)
        if result:
            leaked = result
            break
    if leaked:
        assert leaked.effect in ("reinforced_patrols", "ambush_removed", "prices_raised")
