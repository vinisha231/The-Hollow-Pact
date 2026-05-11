"""
QuestEngine — manages quest lifecycle: discovery, activation, objective tracking, completion.
"""
from __future__ import annotations
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable

from src.world.world_state import WorldState, QuestState

log = logging.getLogger(__name__)


@dataclass
class QuestObjective:
    obj_id: str
    description: str
    optional: bool = False
    completed: bool = False
    trust_on_complete: int = 0   # trust event weight if objective is companion-relevant


@dataclass
class QuestTemplate:
    quest_id: str
    name: str
    giver: str          # NPC id
    zone: str
    description: str
    objectives: List[QuestObjective]
    reward_gold: int
    reward_xp: int
    companion_reactions: Dict[str, str]  # companion_id -> reaction text
    hidden_beats: List[str]             # betrayal beat IDs that can trigger during this quest


QUEST_TEMPLATES: List[QuestTemplate] = [
    QuestTemplate(
        quest_id="q_pale_compass",
        name="The Pale Compass",
        giver="magistrate_aldric",
        zone="hub_saltmere",
        description="Recover the Pale Compass from the Ruins of Varek before the Pale Thread cultists claim it.",
        objectives=[
            QuestObjective("obj_enter_varek", "Reach the Ruins of Varek"),
            QuestObjective("obj_find_vault", "Locate the noble vaults"),
            QuestObjective("obj_defeat_archivist", "Defeat or bypass the Archivist"),
            QuestObjective("obj_retrieve_compass", "Retrieve the Pale Compass"),
            QuestObjective("obj_ironveil_deed", "Find the Ironveil land deed", optional=True, trust_on_complete=15),
        ],
        reward_gold=400,
        reward_xp=800,
        companion_reactions={
            "brann_ironveil": "I've heard of the Varek ruins. The Ironveil family had holdings there, once.",
            "lyra_nightwhisper": "The Pale Compass... I've read about it. It points to things that want to be found.",
            "ossian_vex": "The Pale Thread will have people in there already. We're walking into a hornet's nest.",
        },
        hidden_beats=["act1_treasure_room"],
    ),
    QuestTemplate(
        quest_id="q_thornwood_wolves",
        name="Unquiet Packs",
        giver="ranger_scout_teya",
        zone="hub_saltmere",
        description="The wolf packs in the Thornwood are acting strangely. The ranger scouts want to know why.",
        objectives=[
            QuestObjective("obj_reach_wolf_territory", "Enter wolf territory in the Thornwood"),
            QuestObjective("obj_investigate_den", "Investigate the wolf den"),
            QuestObjective("obj_find_cause", "Discover what's driving the unusual behaviour"),
            QuestObjective("obj_grove_fragment", "Find the First Grove fragment", optional=True, trust_on_complete=10),
        ],
        reward_gold=150,
        reward_xp=300,
        companion_reactions={
            "brann_ironveil": "Wolves don't act without reason. Something's driven them.",
            "lyra_nightwhisper": "...yes. I think I know what this might be. Let's go.",
            "ossian_vex": "Animals. Fine. At least they don't have crossbows.",
        },
        hidden_beats=[],
    ),
]


class QuestEngine:
    def __init__(self, world: WorldState):
        self._world = world
        self._templates = {q.quest_id: q for q in QUEST_TEMPLATES}

    def available_quests(self, zone: str) -> List[QuestTemplate]:
        return [
            t for t in self._templates.values()
            if t.zone == zone
            and t.quest_id not in self._world.quests
        ]

    def accept_quest(self, quest_id: str) -> QuestState:
        template = self._templates.get(quest_id)
        if template is None:
            raise ValueError(f"Unknown quest: {quest_id}")
        state = QuestState(
            quest_id=quest_id,
            name=template.name,
            status="active",
            objectives={obj.obj_id: False for obj in template.objectives},
            notes=[],
        )
        self._world.quests[quest_id] = state
        log.info("quest_accepted id=%s", quest_id)
        return state

    def complete_objective(self, quest_id: str, obj_id: str) -> bool:
        state = self._world.quests.get(quest_id)
        template = self._templates.get(quest_id)
        if not state or not template:
            return False
        if obj_id not in state.objectives:
            return False
        state.objectives[obj_id] = True
        log.info("objective_complete quest=%s obj=%s", quest_id, obj_id)
        self._check_completion(quest_id)
        return True

    def _check_completion(self, quest_id: str) -> None:
        state = self._world.quests[quest_id]
        template = self._templates[quest_id]
        required = [o for o in template.objectives if not o.optional]
        all_done = all(state.objectives.get(o.obj_id, False) for o in required)
        if all_done:
            state.status = "completed"
            log.info("quest_completed id=%s", quest_id)
