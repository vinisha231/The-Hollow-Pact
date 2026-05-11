"""
IntelSystem — soft betrayal: low-trust companions leak party intel to factions.

A suspicious companion might tip off a bandit faction before the party enters a zone,
leading to reinforced patrols, removed ambush opportunities, or locked doors.
"""
from __future__ import annotations
import logging
import random
from dataclasses import dataclass
from typing import Optional

log = logging.getLogger(__name__)


@dataclass
class IntelLeak:
    companion_id: str
    faction_tipped: str
    zone_id: str
    effect: str    # "reinforced_patrols"|"ambush_removed"|"door_locked"|"prices_raised"
    discovered_by_player: bool = False


class IntelSystem:
    def evaluate_leak(
        self,
        companion_id: str,
        trust_band: str,
        current_zone: str,
        companion_faction_contacts: dict[str, str],
    ) -> Optional[IntelLeak]:
        """
        Returns an IntelLeak if the companion decides to tip off a faction.
        Only fires at zone transitions.
        """
        if trust_band not in ("suspicious", "hostile"):
            return None

        leak_probability = 0.15 if trust_band == "suspicious" else 0.4
        if random.random() > leak_probability:
            return None

        faction = companion_faction_contacts.get(companion_id)
        if not faction:
            return None

        effects = ["reinforced_patrols", "ambush_removed", "prices_raised"]
        effect = random.choice(effects)

        log.warning(
            "intel_leaked companion=%s faction=%s zone=%s effect=%s",
            companion_id, faction, current_zone, effect,
        )
        return IntelLeak(companion_id, faction, current_zone, effect)


COMPANION_FACTION_CONTACTS: dict[str, str] = {
    "ossian_vex": "silent_hand",
    "brann_ironveil": None,    # no faction contacts
    "lyra_nightwhisper": "forest_court",
}
