"""
CrossCompanionSystem — companions form opinions about each other and other
companions' bonded players.

Opinions influence dialogue reactions and spotlight priority.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Dict, Optional

log = logging.getLogger(__name__)


@dataclass
class CompanionOpinion:
    target_companion_id: str
    opinion: int   # -100 (contempt) to +100 (respect)
    notes: list[str] = field(default_factory=list)

    @property
    def label(self) -> str:
        if self.opinion >= 60: return "respect"
        if self.opinion >= 20: return "neutral"
        if self.opinion >= -20: return "wary"
        return "contempt"


class CrossCompanionSystem:
    """
    Tracks one companion's opinions of other companions.
    These are injected into the LLM system prompt as context.
    """

    def __init__(self):
        # outer key: observer companion; inner key: target companion
        self._opinions: Dict[str, Dict[str, CompanionOpinion]] = {}

    def initialise_defaults(self) -> None:
        """Set up canonical starting opinions from lore."""
        # Ossian is suspicious of everyone — he's a former assassin
        self._set("ossian_vex", "brann_ironveil", -10, "He's too rigid. Rigid people get people killed.")
        self._set("ossian_vex", "lyra_nightwhisper", -25, "She's hiding something bigger than usual.")
        # Lyra is warm by default but sensing something from Ossian
        self._set("lyra_nightwhisper", "ossian_vex", -15, "There's a shadow around him. Recent. Heavy.")
        self._set("lyra_nightwhisper", "brann_ironveil", 20, "Honourable. Sad about it.")
        # Brann is professional with everyone to start
        self._set("brann_ironveil", "lyra_nightwhisper", 5, "Useful. Strange. Watching her.")
        self._set("brann_ironveil", "ossian_vex", -5, "He's competent. I don't know what else he is.")

    def update_opinion(
        self, observer: str, target: str, delta: int, note: str
    ) -> None:
        if observer not in self._opinions:
            self._opinions[observer] = {}
        if target not in self._opinions[observer]:
            self._opinions[observer][target] = CompanionOpinion(target, 0)
        op = self._opinions[observer][target]
        op.opinion = max(-100, min(100, op.opinion + delta))
        if note:
            op.notes.append(note)
        log.info(
            "cross_opinion observer=%s target=%s new_value=%d label=%s",
            observer, target, op.opinion, op.label,
        )

    def get_opinion_block(self, observer: str) -> str:
        """Returns text injected into observer's system prompt."""
        opinions = self._opinions.get(observer, {})
        if not opinions:
            return ""
        lines = [
            f"- {target}: {op.label} ({op.notes[-1] if op.notes else 'no specific notes'})"
            for target, op in opinions.items()
        ]
        return "YOUR OPINIONS OF OTHER COMPANIONS:\n" + "\n".join(lines)

    def _set(self, observer: str, target: str, value: int, note: str) -> None:
        if observer not in self._opinions:
            self._opinions[observer] = {}
        self._opinions[observer][target] = CompanionOpinion(target, value, [note])
