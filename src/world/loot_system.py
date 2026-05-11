"""
LootSystem — distributes loot after combat, with companion trust implications.

Companions notice loot decisions. Hoarding is a trust event.
Low-trust companions may quietly pocket items.
"""
from __future__ import annotations
import logging
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

log = logging.getLogger(__name__)


@dataclass
class LootItem:
    item_id: str
    name: str
    gold_value: int
    type: str   # "weapon"|"armour"|"consumable"|"quest"|"coin"
    companion_id_flagged: Optional[str] = None   # companion has interest in this item


@dataclass
class LootResult:
    items: List[LootItem]
    companion_pocketed: Dict[str, LootItem] = field(default_factory=dict)  # companion_id -> item
    trust_events_fired: List[tuple[str, str]] = field(default_factory=list)  # [(companion_id, event)]


class LootSystem:
    def distribute_loot(
        self,
        available: List[LootItem],
        companion_ids: List[str],
        trust_bands: Dict[str, str],
        player_shares_freely: bool = True,
    ) -> LootResult:
        result = LootResult(items=list(available))

        for companion_id in companion_ids:
            band = trust_bands.get(companion_id, "neutral")

            # Hostile/suspicious companions may quietly take consumables
            if band in ("hostile", "suspicious"):
                consumables = [i for i in available if i.type == "consumable"]
                if consumables:
                    taken = random.choice(consumables)
                    if random.random() < (0.7 if band == "hostile" else 0.3):
                        result.companion_pocketed[companion_id] = taken
                        available.remove(taken)
                        log.warning("companion_pocketed id=%s item=%s", companion_id, taken.name)
                        result.trust_events_fired.append((companion_id, "item_hoard"))

            # Check for companion-flagged items
            for item in available:
                if item.companion_id_flagged == companion_id:
                    # Companion is obviously interested — trust event if player keeps it
                    if not player_shares_freely:
                        result.trust_events_fired.append((companion_id, "stole_loot"))
                    else:
                        result.trust_events_fired.append((companion_id, "shared_loot"))

        return result
