"""Tests for COMPANION_ABILITIES."""
from src.combat.ability_system import COMPANION_ABILITIES, AbilityType


def test_brann_has_three_abilities():
    assert len(COMPANION_ABILITIES["brann_ironveil"]) == 3


def test_lyra_has_heal_ability():
    abilities = COMPANION_ABILITIES["lyra_nightwhisper"]
    heals = [a for a in abilities if a.type == AbilityType.HEAL]
    assert len(heals) >= 1


def test_ossian_has_mobility():
    abilities = COMPANION_ABILITIES["ossian_vex"]
    mobility = [a for a in abilities if a.type == AbilityType.MOBILITY]
    assert len(mobility) >= 1


def test_trust_gated_abilities_exist():
    all_abilities = [a for abilities in COMPANION_ABILITIES.values() for a in abilities]
    gated = [a for a in all_abilities if a.trust_required > 0]
    assert len(gated) >= 3


def test_ability_mana_costs_positive():
    for companion_id, abilities in COMPANION_ABILITIES.items():
        for ability in abilities:
            assert ability.mana_cost > 0, f"{companion_id}.{ability.ability_id} has zero mana cost"
