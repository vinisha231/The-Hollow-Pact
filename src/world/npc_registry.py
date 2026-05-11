"""
NPCRegistry — non-companion characters in the world.
Static NPCs have fixed dialogue; interactive NPCs can respond to party actions.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class NPCDialogueLine:
    condition: str   # "always" | flag_name | trust_band condition
    line: str
    trust_event: Optional[str] = None   # fires on saying this line


@dataclass
class NPC:
    npc_id: str
    name: str
    role: str        # "merchant" | "quest_giver" | "innkeeper" | "enemy_ally"
    zone: str
    faction: str
    dialogue: List[NPCDialogueLine]
    companion_reactions: Dict[str, str] = field(default_factory=dict)

    def get_line(self, trust_band: str, flags: set[str]) -> Optional[str]:
        """Returns the first applicable dialogue line given context."""
        for dl in self.dialogue:
            if dl.condition == "always":
                return dl.line
            if dl.condition == trust_band:
                return dl.line
            if dl.condition in flags:
                return dl.line
        return None


NPC_DATA = [
    NPC(
        npc_id="magistrate_aldric",
        name="Magistrate Aldric",
        role="quest_giver",
        zone="hub_saltmere",
        faction="saltmere_council",
        dialogue=[
            NPCDialogueLine("always", "The Pale Thread moves closer to the city walls every week. I need capable hands."),
            NPCDialogueLine("q_pale_compass_completed", "You've retrieved the Compass. Saltmere owes you a debt."),
        ],
        companion_reactions={
            "brann_ironveil": "The Magistrate is careful. That either means he's honest or he's hiding something significant.",
            "ossian_vex": "He's paying us. That's enough.",
        },
    ),
    NPC(
        npc_id="innkeeper_rova",
        name="Rova Thale",
        role="innkeeper",
        zone="hub_saltmere",
        faction="saltmere_neutral",
        dialogue=[
            NPCDialogueLine("always", "Rooms are three silver. Meals are included. Don't cause trouble."),
            NPCDialogueLine("helped_villager", "You helped old Petur at the gate. Meals on the house tonight."),
        ],
        companion_reactions={
            "lyra_nightwhisper": "She knows more than she admits. Innkeepers always do.",
        },
    ),
    NPC(
        npc_id="ferry_captain_das",
        name="Captain Das",
        role="ferry_operator",
        zone="hub_saltmere",
        faction="saltmere_neutral",
        dialogue=[
            NPCDialogueLine("always", "Three silvers to Ashfall. I don't wait."),
            NPCDialogueLine("ashfall_completed", "You made it back. Not many do, lately."),
        ],
        companion_reactions={
            "brann_ironveil": "He crossed the Pale River during the Cinderwar. Knows the crossing better than anyone.",
        },
    ),
]


class NPCRegistry:
    def __init__(self, data=NPC_DATA):
        self._npcs: Dict[str, NPC] = {n.npc_id: n for n in data}

    def get(self, npc_id: str) -> Optional[NPC]:
        return self._npcs.get(npc_id)

    def in_zone(self, zone: str) -> List[NPC]:
        return [n for n in self._npcs.values() if n.zone == zone]
