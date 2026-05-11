"""
WorldStateManager — authoritative server-side world state.
Serialised to Postgres; snapshot injected into LLM prompts each turn.
"""
from __future__ import annotations
import json
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any


@dataclass
class QuestState:
    quest_id: str
    name: str
    status: str     # "available"|"active"|"completed"|"failed"
    objectives: Dict[str, bool]  # objective_id -> completed
    notes: List[str]  # narrative notes accumulated during quest


@dataclass
class EntityState:
    entity_id: str
    name: str
    alive: bool = True
    location_zone: str = ""
    faction: str = ""
    relationship: str = "neutral"  # "allied"|"neutral"|"hostile"
    known_to_party: bool = True


@dataclass
class CampaignFlags:
    """One-shot boolean flags set by scripted events."""
    flags: Dict[str, bool] = field(default_factory=dict)

    def set(self, flag: str) -> None:
        self.flags[flag] = True

    def check(self, flag: str) -> bool:
        return self.flags.get(flag, False)


@dataclass
class WorldState:
    campaign_id: str
    current_zone: str
    time_of_day: str          # "dawn"|"day"|"dusk"|"night"
    act: int                  # 1-3
    session_number: int
    quests: Dict[str, QuestState] = field(default_factory=dict)
    entities: Dict[str, EntityState] = field(default_factory=dict)
    flags: CampaignFlags = field(default_factory=CampaignFlags)
    updated_at: float = field(default_factory=time.time)

    def to_prompt_snapshot(self) -> str:
        """Compact world snapshot for LLM injection (keep it small)."""
        active_quests = [
            q for q in self.quests.values() if q.status == "active"
        ]
        quest_text = ", ".join(q.name for q in active_quests) or "none"
        known_hostiles = [
            e.name for e in self.entities.values()
            if e.relationship == "hostile" and e.known_to_party and e.alive
        ]
        return json.dumps({
            "zone": self.current_zone,
            "time": self.time_of_day,
            "act": self.act,
            "active_quests": quest_text,
            "known_hostiles": known_hostiles,
        }, indent=2)

    def advance_time(self) -> None:
        order = ["dawn", "day", "dusk", "night"]
        idx = order.index(self.time_of_day) if self.time_of_day in order else 1
        self.time_of_day = order[(idx + 1) % len(order)]
        self.updated_at = time.time()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "WorldState":
        data = dict(data)
        data["flags"] = CampaignFlags(data.get("flags", {}).get("flags", {}))
        data["quests"] = {k: QuestState(**v) for k, v in data.get("quests", {}).items()}
        data["entities"] = {k: EntityState(**v) for k, v in data.get("entities", {}).items()}
        return cls(**data)
