"""
SpotlightSystem — manages which companion gets to speak in a multi-human party.

In a 4-player party, up to 4 AI companions could all try to respond simultaneously.
The spotlight system ensures only one companion speaks per window,
with priority given to the bonded companion and context-relevant ones.
"""
from __future__ import annotations
import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

log = logging.getLogger(__name__)

SPOTLIGHT_WINDOW_SECONDS = 5.0
COMBAT_SILENCE = True  # companions emit barks only during active combat


@dataclass
class SpotlightSlot:
    companion_id: str
    player_id: str           # bonded player
    last_spoke_at: float = 0.0
    priority_boost: float = 0.0   # temporary; set when companion is directly addressed


@dataclass
class SpotlightRequest:
    companion_id: str
    player_id: str
    trigger: str          # "direct_address"|"world_event"|"emotional_trigger"|"idle"
    urgency: float        # 0-1; 1 = must speak now


class SpotlightSystem:
    """
    Decides which companion speaks next.
    Only one companion speaks per SPOTLIGHT_WINDOW_SECONDS.
    """

    def __init__(self):
        self._slots: Dict[str, SpotlightSlot] = {}
        self._current_speaker: Optional[str] = None
        self._window_end: float = 0.0

    def register_companion(self, companion_id: str, player_id: str) -> None:
        self._slots[companion_id] = SpotlightSlot(companion_id, player_id)

    def request_spotlight(self, req: SpotlightRequest) -> bool:
        """
        Returns True if this companion gets the spotlight.
        Returns False if another companion is speaking or window hasn't expired.
        """
        now = time.monotonic()
        slot = self._slots.get(req.companion_id)
        if slot is None:
            return False

        # Hard block: another companion currently speaking
        if self._current_speaker and self._current_speaker != req.companion_id:
            if now < self._window_end:
                return False

        # Hard block: this companion spoke too recently
        if now - slot.last_spoke_at < SPOTLIGHT_WINDOW_SECONDS and req.urgency < 0.9:
            return False

        # Direct address always wins
        if req.trigger == "direct_address":
            self._grant(req.companion_id, now)
            return True

        # Score all pending requests if multiple want to speak
        score = self._score(req, now)
        if score > 0.5:
            self._grant(req.companion_id, now)
            return True

        return False

    def release_spotlight(self, companion_id: str) -> None:
        if self._current_speaker == companion_id:
            self._current_speaker = None
            log.debug("spotlight_released id=%s", companion_id)

    def _grant(self, companion_id: str, now: float) -> None:
        self._current_speaker = companion_id
        self._window_end = now + SPOTLIGHT_WINDOW_SECONDS
        slot = self._slots[companion_id]
        slot.last_spoke_at = now
        slot.priority_boost = 0.0
        log.debug("spotlight_granted id=%s", companion_id)

    def _score(self, req: SpotlightRequest, now: float) -> float:
        slot = self._slots.get(req.companion_id)
        if not slot:
            return 0.0
        silence_bonus = min(1.0, (now - slot.last_spoke_at) / 60.0)  # up to 1 min
        urgency = req.urgency
        boost = slot.priority_boost
        return (silence_bonus * 0.4 + urgency * 0.5 + boost * 0.1)
