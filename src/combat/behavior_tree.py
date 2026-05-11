"""
CompanionBehaviorTree — frame-by-frame combat AI for companions.

The LLM is NOT in this hot path. It only injects override nodes at
narrative moments. The behavior tree handles second-by-second decisions.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Callable
from enum import Enum
import logging

log = logging.getLogger(__name__)


class BTStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    RUNNING = "running"


@dataclass
class CombatContext:
    companion_id: str
    companion_hp: float        # 0-100
    companion_mana: float      # 0-100
    nearest_enemy_dist: float  # world units
    nearest_enemy_hp: float
    nearest_ally_hp: float
    nearest_ally_dist: float
    trust_band: str            # "devoted"|"loyal"|"neutral"|"suspicious"|"hostile"
    llm_override: Optional[str] = None  # set by orchestrator
    llm_override_target: Optional[str] = None


class BTNode:
    def tick(self, ctx: CombatContext) -> BTStatus:
        raise NotImplementedError


class Sequence(BTNode):
    """All children must succeed."""
    def __init__(self, children: List[BTNode]):
        self.children = children

    def tick(self, ctx: CombatContext) -> BTStatus:
        for child in self.children:
            status = child.tick(ctx)
            if status != BTStatus.SUCCESS:
                return status
        return BTStatus.SUCCESS


class Selector(BTNode):
    """First succeeding child wins."""
    def __init__(self, children: List[BTNode]):
        self.children = children

    def tick(self, ctx: CombatContext) -> BTStatus:
        for child in self.children:
            status = child.tick(ctx)
            if status == BTStatus.SUCCESS:
                return BTStatus.SUCCESS
        return BTStatus.FAILURE


class Condition(BTNode):
    def __init__(self, predicate: Callable[[CombatContext], bool], label: str = ""):
        self.predicate = predicate
        self.label = label

    def tick(self, ctx: CombatContext) -> BTStatus:
        return BTStatus.SUCCESS if self.predicate(ctx) else BTStatus.FAILURE


class Action(BTNode):
    def __init__(self, action_fn: Callable[[CombatContext], None], label: str = ""):
        self.action_fn = action_fn
        self.label = label

    def tick(self, ctx: CombatContext) -> BTStatus:
        try:
            self.action_fn(ctx)
            return BTStatus.SUCCESS
        except Exception as exc:
            log.error("bt_action_error label=%s: %s", self.label, exc)
            return BTStatus.FAILURE


# ── Pre-built action callbacks (stubs; real ones live in Unity C#) ─────────

def _flee(ctx: CombatContext) -> None:
    log.info("companion_flee id=%s", ctx.companion_id)

def _attack_nearest(ctx: CombatContext) -> None:
    log.info("companion_attack id=%s", ctx.companion_id)

def _heal_ally(ctx: CombatContext) -> None:
    log.info("companion_heal_ally id=%s", ctx.companion_id)

def _use_ability(ctx: CombatContext) -> None:
    log.info("companion_ability id=%s", ctx.companion_id)

def _sandbag(ctx: CombatContext) -> None:
    """Low-trust soft betrayal — companion performs suboptimal moves."""
    log.warning("companion_sandbagging id=%s trust=%s", ctx.companion_id, ctx.trust_band)

def _apply_llm_override(ctx: CombatContext) -> None:
    log.info("companion_llm_override id=%s intent=%s", ctx.companion_id, ctx.llm_override)


# ── Companion behavior tree ────────────────────────────────────────────────

def build_companion_bt() -> BTNode:
    """
    Constructs the default companion combat behavior tree.
    Priority (top to bottom):
      1. LLM hard override (betray, flee per story beat)
      2. Self-preservation (flee if critically low HP)
      3. Sandbag if trust is hostile
      4. Heal ally if critically low
      5. Use ability if available
      6. Attack nearest enemy
    """
    return Selector([
        # 1. LLM hard override
        Sequence([
            Condition(lambda c: c.llm_override is not None, "has_override"),
            Action(_apply_llm_override, "apply_override"),
        ]),

        # 2. Self-preservation
        Sequence([
            Condition(lambda c: c.companion_hp < 15, "critical_hp"),
            Action(_flee, "flee"),
        ]),

        # 3. Sandbag if hostile trust
        Sequence([
            Condition(lambda c: c.trust_band == "hostile", "is_hostile"),
            Action(_sandbag, "sandbag"),
        ]),

        # 4. Heal nearby ally
        Sequence([
            Condition(lambda c: c.nearest_ally_hp < 25, "ally_critical"),
            Condition(lambda c: c.nearest_ally_dist < 15, "ally_in_range"),
            Condition(lambda c: c.companion_mana >= 20, "has_mana"),
            Action(_heal_ally, "heal_ally"),
        ]),

        # 5. Use ability
        Sequence([
            Condition(lambda c: c.companion_mana >= 40, "ability_mana"),
            Condition(lambda c: c.nearest_enemy_dist < 20, "enemy_in_range"),
            Action(_use_ability, "use_ability"),
        ]),

        # 6. Default: attack
        Action(_attack_nearest, "attack_nearest"),
    ])
