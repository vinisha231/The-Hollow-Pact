"""Tests for CompanionBehaviorTree."""
import pytest
from src.combat.behavior_tree import build_companion_bt, CombatContext, BTStatus


def default_ctx(**kwargs) -> CombatContext:
    defaults = dict(
        companion_id="brann",
        companion_hp=80.0,
        companion_mana=60.0,
        nearest_enemy_dist=10.0,
        nearest_enemy_hp=50.0,
        nearest_ally_hp=70.0,
        nearest_ally_dist=8.0,
        trust_band="loyal",
        llm_override=None,
        llm_override_target=None,
    )
    defaults.update(kwargs)
    return CombatContext(**defaults)


def test_default_attack_returns_success():
    bt = build_companion_bt()
    ctx = default_ctx()
    status = bt.tick(ctx)
    assert status == BTStatus.SUCCESS


def test_critical_hp_triggers_flee():
    actions_taken = []

    import src.combat.behavior_tree as btmod
    original_flee = btmod._flee

    def mock_flee(ctx):
        actions_taken.append("flee")

    btmod._flee = mock_flee
    try:
        bt = build_companion_bt()
        ctx = default_ctx(companion_hp=10.0)
        bt.tick(ctx)
        assert "flee" in actions_taken
    finally:
        btmod._flee = original_flee


def test_llm_override_takes_priority():
    actions_taken = []

    import src.combat.behavior_tree as btmod
    original = btmod._apply_llm_override

    def mock_override(ctx):
        actions_taken.append("override")

    btmod._apply_llm_override = mock_override
    try:
        bt = build_companion_bt()
        ctx = default_ctx(llm_override="betray", llm_override_target="player1")
        bt.tick(ctx)
        assert "override" in actions_taken
    finally:
        btmod._apply_llm_override = original


def test_hostile_trust_sandbags():
    actions_taken = []

    import src.combat.behavior_tree as btmod
    original = btmod._sandbag

    def mock_sandbag(ctx):
        actions_taken.append("sandbag")

    btmod._sandbag = mock_sandbag
    try:
        bt = build_companion_bt()
        ctx = default_ctx(trust_band="hostile", companion_hp=80.0)
        bt.tick(ctx)
        assert "sandbag" in actions_taken
    finally:
        btmod._sandbag = original
