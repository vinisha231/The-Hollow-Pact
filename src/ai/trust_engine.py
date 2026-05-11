"""
TrustEngine — tracks the hidden trust value between companion and player.
Never exposed directly; influences dialogue tone and betrayal branches.
"""
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum
import time
import logging

log = logging.getLogger(__name__)


class TrustBand(Enum):
    """Coarse bands used by the LLM to modulate dialogue tone."""
    DEVOTED = "devoted"         # 80-100
    LOYAL = "loyal"             # 60-79
    NEUTRAL = "neutral"         # 40-59
    SUSPICIOUS = "suspicious"   # 20-39
    HOSTILE = "hostile"         # 0-19


@dataclass
class TrustEvent:
    timestamp: float
    delta: int           # positive = trust gained, negative = trust lost
    reason: str          # human-readable, logged for analytics
    session_id: str


@dataclass
class TrustState:
    companion_id: str
    player_id: str
    value: int = 50          # starts neutral
    events: List[TrustEvent] = field(default_factory=list)
    betrayal_triggered: bool = False

    @property
    def band(self) -> TrustBand:
        if self.value >= 80:
            return TrustBand.DEVOTED
        if self.value >= 60:
            return TrustBand.LOYAL
        if self.value >= 40:
            return TrustBand.NEUTRAL
        if self.value >= 20:
            return TrustBand.SUSPICIOUS
        return TrustBand.HOSTILE

    def apply(self, delta: int, reason: str, session_id: str) -> None:
        self.value = max(0, min(100, self.value + delta))
        self.events.append(TrustEvent(
            timestamp=time.time(),
            delta=delta,
            reason=reason,
            session_id=session_id,
        ))
        log.info(
            "trust_change companion=%s player=%s delta=%+d reason=%r new_value=%d band=%s",
            self.companion_id, self.player_id, delta, reason,
            self.value, self.band.value,
        )


class TrustEngine:
    """
    Central authority for trust mutations.
    Separate from TrustState so rules live in one place.
    """

    # (event_type, delta) map — designer-tunable
    EVENT_WEIGHTS: dict = {
        "kept_promise": +8,
        "broke_promise": -15,
        "defended_companion": +10,
        "abandoned_companion": -20,
        "shared_loot": +5,
        "stole_loot": -12,
        "agreed_with_companion": +3,
        "dismissed_companion_idea": -4,
        "helped_villager": +2,
        "harmed_villager": -8,
        "lied_to_companion": -10,
        "confided_in_companion": +6,
        "completed_companion_quest": +15,
        "blocked_companion_agenda": -18,
        "humiliated_companion": -25,
        "complimented_companion": +2,
    }

    def __init__(self, persona_loyalty_threshold: int = 20):
        self.loyalty_threshold = persona_loyalty_threshold

    def record_event(
        self,
        state: TrustState,
        event_type: str,
        session_id: str,
        override_delta: Optional[int] = None,
    ) -> Tuple[TrustBand, bool]:
        """
        Apply a named trust event.
        Returns (new_band, betrayal_just_triggered).
        """
        delta = override_delta if override_delta is not None \
            else self.EVENT_WEIGHTS.get(event_type, 0)

        was_above_threshold = state.value > self.loyalty_threshold
        state.apply(delta, event_type, session_id)
        crossed_threshold = was_above_threshold and state.value <= self.loyalty_threshold

        if crossed_threshold and not state.betrayal_triggered:
            state.betrayal_triggered = True
            log.warning(
                "BETRAYAL_UNLOCKED companion=%s player=%s",
                state.companion_id, state.player_id,
            )
            return state.band, True

        return state.band, False

    def get_llm_tone_directive(self, state: TrustState) -> str:
        """Returns a short string injected into the LLM prompt each turn."""
        directives = {
            TrustBand.DEVOTED: "You are deeply loyal and openly affectionate.",
            TrustBand.LOYAL: "You trust this person and are cooperative.",
            TrustBand.NEUTRAL: "You are professional but guarded.",
            TrustBand.SUSPICIOUS: "You are wary and give clipped, careful responses.",
            TrustBand.HOSTILE: "You are cold, contemptuous, and look for exits.",
        }
        return directives[state.band]
