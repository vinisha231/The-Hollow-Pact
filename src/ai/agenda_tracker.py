"""
AgendaTracker — monitors companion hidden agenda progress.

Evaluates world events against agenda completion/reveal conditions.
Fires events when conditions are met.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

from .companion_persona import CompanionPersona, HiddenAgenda
from src.world.world_state import WorldState

log = logging.getLogger(__name__)


@dataclass
class AgendaEvent:
    companion_id: str
    agenda_id: str
    event_type: str   # "reveal_hint" | "partial_reveal" | "completed" | "failed"
    description: str


class AgendaTracker:
    """
    Checks world state and campaign flags against agenda conditions.
    Called after major world events (entering a new zone, completing a quest, etc.)
    """

    def evaluate(
        self,
        persona: CompanionPersona,
        world: WorldState,
        player_id: str,
    ) -> List[AgendaEvent]:
        events = []
        for agenda in persona.agendas:
            if agenda.completed:
                continue
            event = self._check_agenda(agenda, persona.companion_id, world)
            if event:
                events.append(event)
        return events

    def _check_agenda(
        self,
        agenda: HiddenAgenda,
        companion_id: str,
        world: WorldState,
    ) -> Optional[AgendaEvent]:
        # Check completion
        if self._condition_met(agenda.completion_condition, world):
            log.info("agenda_completed companion=%s id=%s", companion_id, agenda.id)
            return AgendaEvent(
                companion_id=companion_id,
                agenda_id=agenda.id,
                event_type="completed",
                description=f"Agenda '{agenda.label}' completed.",
            )

        # Check reveal
        if self._condition_met(agenda.reveal_condition, world):
            log.info("agenda_reveal_triggered companion=%s id=%s", companion_id, agenda.id)
            return AgendaEvent(
                companion_id=companion_id,
                agenda_id=agenda.id,
                event_type="partial_reveal",
                description=f"Hint surfaced for agenda '{agenda.label}'.",
            )

        return None

    @staticmethod
    def _condition_met(condition: str, world: WorldState) -> bool:
        """
        Simple condition evaluator.
        Real implementation: structured condition format parsed from JSON.
        Stub: checks for flag names mentioned in the condition string.
        """
        words = condition.lower().split()
        for flag in world.flags.flags:
            if flag.lower() in condition.lower():
                return world.flags.check(flag)
        return False
