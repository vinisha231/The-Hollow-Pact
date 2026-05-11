"""
AbilitySystem — companion special abilities.
Each companion archetype has 3 active abilities.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class AbilityType(Enum):
    ATTACK = "attack"
    HEAL = "heal"
    BUFF = "buff"
    DEBUFF = "debuff"
    MOBILITY = "mobility"


@dataclass
class Ability:
    ability_id: str
    name: str
    type: AbilityType
    mana_cost: int
    cooldown_seconds: float
    range_units: float
    trust_required: int = 0   # min trust to use (some abilities require loyalty)
    description: str = ""


COMPANION_ABILITIES: Dict[str, List[Ability]] = {
    "brann_ironveil": [
        Ability("shield_wall", "Shield Wall", AbilityType.BUFF, 30, 15.0, 8.0,
                description="Raise shield to reduce party damage by 30% for 5s"),
        Ability("challenge", "Challenge", AbilityType.DEBUFF, 20, 10.0, 15.0,
                description="Force nearest enemy to target Brann for 4s"),
        Ability("rallying_strike", "Rallying Strike", AbilityType.ATTACK, 40, 20.0, 5.0,
                trust_required=50,
                description="Powerful strike; heals nearest ally for 20% of damage dealt"),
    ],
    "lyra_nightwhisper": [
        Ability("grove_mend", "Grove Mend", AbilityType.HEAL, 35, 8.0, 12.0,
                description="Heal target for 40% max HP over 6s"),
        Ability("thornwall", "Thornwall", AbilityType.DEBUFF, 25, 12.0, 20.0,
                description="Summon thorns that slow and damage enemies passing through"),
        Ability("nature_call", "Nature's Call", AbilityType.ATTACK, 50, 30.0, 25.0,
                trust_required=60,
                description="Call a beast companion for 15s (only at high trust)"),
    ],
    "ossian_vex": [
        Ability("shadow_step", "Shadow Step", AbilityType.MOBILITY, 20, 6.0, 30.0,
                description="Teleport behind target enemy, brief stealth"),
        Ability("exploit_weakness", "Exploit Weakness", AbilityType.DEBUFF, 15, 8.0, 20.0,
                description="Mark enemy — all party damage increased by 20% for 8s"),
        Ability("shadow_mark", "Shadow Mark", AbilityType.ATTACK, 40, 20.0, 35.0,
                trust_required=40,
                description="Delayed poison: enemy takes 80 damage after 3s"),
    ],
}
