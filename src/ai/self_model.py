"""
SelfModel — companion's model of itself and its own history.

Separate from the world model; this is what the companion "knows"
about its own past actions, decisions, and emotional arc.
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SelfRecord:
    """A moment the companion remembers about itself."""
    timestamp: float
    event: str                    # "made a decision", "was afraid", "succeeded"
    emotional_weight: float       # 0-1
    player_was_involved: bool


@dataclass
class CompanionSelfModel:
    companion_id: str
    total_sessions: int = 0
    total_trust_gained: int = 0
    total_trust_lost: int = 0
    times_healed_player: int = 0
    times_refused_order: int = 0
    times_acted_against_agenda: int = 0
    records: List[SelfRecord] = field(default_factory=list)

    def record_event(
        self, event: str, weight: float = 0.5, player_involved: bool = True
    ) -> None:
        self.records.append(SelfRecord(
            timestamp=time.time(),
            event=event,
            emotional_weight=weight,
            player_was_involved=player_involved,
        ))

    def to_prompt_summary(self) -> str:
        """Short self-awareness block for system prompt injection."""
        return (
            f"SELF-KNOWLEDGE: You have spent {self.total_sessions} sessions with this player. "
            f"You have healed them {self.times_healed_player} times. "
            f"You have refused {self.times_refused_order} orders. "
        )

    @property
    def net_trust_trend(self) -> str:
        if self.total_trust_gained > self.total_trust_lost + 20:
            return "improving"
        if self.total_trust_lost > self.total_trust_gained + 20:
            return "deteriorating"
        return "stable"
