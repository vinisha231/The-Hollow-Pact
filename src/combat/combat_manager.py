"""
CombatManager — coordinates a single combat encounter.
Manages enemy spawns, companion AI ticks, and betrayal beat evaluation.
"""
from __future__ import annotations
import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .behavior_tree import build_companion_bt, CombatContext, BTStatus
from .betrayal_triggers import BetrayalTriggerSystem, BetrayalDecision
from src.ai.trust_engine import TrustState, TrustBand

log = logging.getLogger(__name__)

BT_TICK_RATE = 0.1   # seconds; 10 ticks/second per companion


@dataclass
class EnemyState:
    enemy_id: str
    enemy_type: str
    hp: float
    position: tuple[float, float, float]
    alive: bool = True


@dataclass
class CombatState:
    encounter_id: str
    zone_id: str
    beat_id: str
    enemies: Dict[str, EnemyState] = field(default_factory=dict)
    companion_contexts: Dict[str, CombatContext] = field(default_factory=dict)
    started_at: float = field(default_factory=time.time)
    ended_at: Optional[float] = None
    player_ids: List[str] = field(default_factory=list)


class CombatManager:
    def __init__(self, betrayal_system: BetrayalTriggerSystem):
        self._betrayal = betrayal_system
        self._behavior_trees: Dict[str, object] = {}   # companion_id -> BT root

    def register_companion(self, companion_id: str) -> None:
        self._behavior_trees[companion_id] = build_companion_bt()

    async def run_combat_loop(
        self,
        state: CombatState,
        trust_states: Dict[str, TrustState],
        on_betrayal_triggered=None,
    ) -> None:
        """
        Main async loop. Ticks all companion BTs at BT_TICK_RATE.
        Evaluates betrayal at the encounter's narrative beat.
        """
        log.info("combat_start encounter=%s zone=%s", state.encounter_id, state.zone_id)

        # Check betrayal on encounter start
        for companion_id, trust in trust_states.items():
            decision = self._betrayal.evaluate(
                state.beat_id, companion_id, trust.value, trust.band
            )
            if decision.triggered:
                log.warning("betrayal_at_combat_start companion=%s", companion_id)
                if on_betrayal_triggered:
                    await on_betrayal_triggered(companion_id, decision)
                # Inject LLM override into companion context
                ctx = state.companion_contexts.get(companion_id)
                if ctx:
                    ctx.llm_override = decision.betrayal_type.value
                return

        while any(e.alive for e in state.enemies.values()):
            for companion_id, bt in self._behavior_trees.items():
                ctx = state.companion_contexts.get(companion_id)
                if ctx and ctx.llm_override != "betray":
                    # Update context with current trust band
                    trust = trust_states.get(companion_id)
                    if trust:
                        ctx.trust_band = trust.band.value
                    bt.tick(ctx)

            await asyncio.sleep(BT_TICK_RATE)

            # Re-evaluate betrayal mid-combat (for mid-boss beats)
            for companion_id, trust in trust_states.items():
                decision = self._betrayal.evaluate(
                    f"{state.beat_id}_midcombat", companion_id, trust.value, trust.band
                )
                if decision.triggered and on_betrayal_triggered:
                    await on_betrayal_triggered(companion_id, decision)

        state.ended_at = time.time()
        duration = state.ended_at - state.started_at
        log.info("combat_ended encounter=%s duration=%.1fs", state.encounter_id, duration)
