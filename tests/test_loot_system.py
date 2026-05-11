"""Tests for LootSystem."""
from src.world.loot_system import LootSystem, LootItem


def make_items():
    return [
        LootItem("sword_01", "Iron Sword", 50, "weapon"),
        LootItem("bandage_01", "Bandage", 5, "consumable"),
        LootItem("coin_01", "Gold Coins", 30, "coin"),
    ]


def test_all_items_returned_at_loyal_trust():
    system = LootSystem()
    items = make_items()
    result = system.distribute_loot(items, ["brann"], {"brann": "loyal"}, True)
    assert len(result.companion_pocketed) == 0


def test_hostile_companion_may_pocket_consumable():
    system = LootSystem()
    # Run many times to account for randomness
    pocketed_at_least_once = False
    for _ in range(30):
        items = make_items()
        result = system.distribute_loot(items, ["brann"], {"brann": "hostile"}, True)
        if "brann" in result.companion_pocketed:
            pocketed_at_least_once = True
            assert result.companion_pocketed["brann"].type == "consumable"
            break
    assert pocketed_at_least_once


def test_shared_loot_trust_event_when_flagged_item_given():
    system = LootSystem()
    items = [LootItem("amulet_01", "Family Amulet", 100, "weapon", companion_id_flagged="brann")]
    result = system.distribute_loot(items, ["brann"], {"brann": "loyal"}, player_shares_freely=True)
    assert ("brann", "shared_loot") in result.trust_events_fired


def test_stole_loot_event_when_flagged_item_kept():
    system = LootSystem()
    items = [LootItem("amulet_01", "Family Amulet", 100, "weapon", companion_id_flagged="brann")]
    result = system.distribute_loot(items, ["brann"], {"brann": "loyal"}, player_shares_freely=False)
    assert ("brann", "stole_loot") in result.trust_events_fired
