"""
MimicSystem — the Echo Mimic enemy type.

Mimics sample from the companion bark library and play them as their
own attack dialogue, trying to confuse players into attacking their companions.
"""
from __future__ import annotations
import random
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional
import json
from pathlib import Path

log = logging.getLogger(__name__)

BARK_LIBRARY_PATH = Path(__file__).parents[1] / "audio" / "bark_library.json"


@dataclass
class MimicSpawnConfig:
    mimic_id: str
    target_companion_id: str   # which companion it mimics
    spawn_zone: str
    confusion_radius: float    # how close mimic needs to be to trigger confusion


class MimicSystem:
    def __init__(self):
        with BARK_LIBRARY_PATH.open() as f:
            data = json.load(f)
        self._bark_library: Dict[str, Dict[str, List[str]]] = data["barks"]

    def get_mimic_bark(self, companion_id: str, bark_type: str) -> Optional[str]:
        """Returns a bark line the mimic will speak, sampled from the companion's library."""
        companion_barks = self._bark_library.get(companion_id)
        if not companion_barks:
            return None
        type_barks = companion_barks.get(bark_type, companion_barks.get("attack", []))
        if not type_barks:
            return None
        return random.choice(type_barks)

    def mimic_attack_sequence(
        self, mimic: MimicSpawnConfig, player_facing_companion: bool
    ) -> Dict:
        """
        Returns combat instructions for a mimic attack.
        If player is currently facing their companion, mimic attacks from behind.
        """
        bark = self.get_mimic_bark(mimic.target_companion_id, "attack")
        return {
            "mimic_id": mimic.id if hasattr(mimic, 'id') else mimic.mimic_id,
            "spoke_line": bark,
            "attack_from_behind": player_facing_companion,
            "confusion_active": True,
            "hint": "A mimic is impersonating your companion",
        }

    def spawn_mimics_for_zone(self, zone_id: str, active_companions: List[str]) -> List[MimicSpawnConfig]:
        """
        For the Gilded Dirge (act2), spawn one mimic per active companion.
        """
        if zone_id != "cursed_opera_house":
            return []
        return [
            MimicSpawnConfig(
                mimic_id=f"mimic_{c}_{zone_id}",
                target_companion_id=c,
                spawn_zone=zone_id,
                confusion_radius=12.0,
            )
            for c in active_companions
        ]
