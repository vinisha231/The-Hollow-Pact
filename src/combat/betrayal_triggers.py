"""
BetrayalTriggers — decides when a low-trust companion acts against the party.

Soft betrayals: suboptimal moves, intel leaks, item hoarding.
Hard betrayals: turns hostile, flees with macguffin, becomes antagonist NPC.

Triggered at narrative beats, not randomly.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from src.ai.trust_engine import TrustBand

log = logging.getLogger(__name__)


class BetrayalType(Enum):
    NONE = "none"
    SANDBAG = "sandbag"              # Soft: underperforms in combat
    INTEL_LEAK = "intel_leak"        # Soft: tips off enemy faction
    ITEM_HOARD = "item_hoard"        # Soft: keeps loot from party
    MISSED_HEAL = "missed_heal"      # Soft: "accidentally" fails to heal
    DESERT = "desert"                # Hard: leaves party permanently
    STEAL_MACGUFFIN = "steal_macguffin"  # Hard: takes key item and flees
    TURN_HOSTILE = "turn_hostile"    # Hard: fights the party
    SUMMON_ENEMIES = "summon_enemies"  # Hard: calls in hostile faction


@dataclass
class NarrativeBeat:
    """A defined story moment where betrayal can trigger."""
    beat_id: str
    label: str
    description: str
    requires_trust_below: int     # hard threshold
    betrayal_type: BetrayalType
    telegraphed_by: List[str]     # dialogue hints that preceded this


DEFINED_BEATS: List[NarrativeBeat] = [
    NarrativeBeat(
        beat_id="act1_treasure_room",
        label="Act 1 — Treasure Room",
        description="Party reaches the treasure room at end of Act 1.",
        requires_trust_below=30,
        betrayal_type=BetrayalType.STEAL_MACGUFFIN,
        telegraphed_by=[
            "Companion grew unusually interested in the map earlier",
            "Companion asked about the vault's exact location twice",
            "Companion went quiet after learning the artifact's value",
        ],
    ),
    NarrativeBeat(
        beat_id="act2_midboss",
        label="Act 2 — Mid-Boss",
        description="Party is mid-fight with the Act 2 boss.",
        requires_trust_below=20,
        betrayal_type=BetrayalType.TURN_HOSTILE,
        telegraphed_by=[
            "Companion has been hostile in dialogue for several sessions",
            "Companion missed two critical heals in the previous dungeon",
            "Companion had a private meeting with the villain's herald",
        ],
    ),
    NarrativeBeat(
        beat_id="act1_escape",
        label="Act 1 — Escape Sequence",
        description="Party is fleeing and split across zones.",
        requires_trust_below=35,
        betrayal_type=BetrayalType.DESERT,
        telegraphed_by=[
            "Companion has been distant since the merchant incident",
            "Companion packed extra supplies before the dungeon",
        ],
    ),
    NarrativeBeat(
        beat_id="soft_any_combat",
        label="Any combat — Sandbag",
        description="Ongoing soft betrayal in any combat encounter.",
        requires_trust_below=25,
        betrayal_type=BetrayalType.SANDBAG,
        telegraphed_by=[
            "Companion aims slightly off-target",
            "Companion's timing on abilities is suspiciously poor",
        ],
    ),
]


@dataclass
class BetrayalDecision:
    triggered: bool
    betrayal_type: BetrayalType
    beat: Optional[NarrativeBeat]
    message: str   # log / analytics message


class BetrayalTriggerSystem:
    def __init__(self):
        self._beats = {b.beat_id: b for b in DEFINED_BEATS}
        self._triggered_hard: set[str] = set()  # campaign-persistent

    def evaluate(
        self,
        beat_id: str,
        companion_id: str,
        trust_value: int,
        trust_band: TrustBand,
    ) -> BetrayalDecision:
        beat = self._beats.get(beat_id)
        if beat is None:
            return BetrayalDecision(False, BetrayalType.NONE, None, "unknown beat")

        already_triggered = beat_id in self._triggered_hard
        if already_triggered:
            return BetrayalDecision(False, BetrayalType.NONE, beat, "already triggered")

        should_trigger = trust_value < beat.requires_trust_below
        if not should_trigger:
            return BetrayalDecision(False, BetrayalType.NONE, beat, "trust above threshold")

        hard = beat.betrayal_type not in {BetrayalType.SANDBAG, BetrayalType.MISSED_HEAL}
        if hard:
            self._triggered_hard.add(beat_id)

        log.warning(
            "BETRAYAL companion=%s beat=%s type=%s trust=%d",
            companion_id, beat_id, beat.betrayal_type.value, trust_value,
        )

        return BetrayalDecision(
            triggered=True,
            betrayal_type=beat.betrayal_type,
            beat=beat,
            message=f"companion {companion_id} betrayal at {beat_id}",
        )
