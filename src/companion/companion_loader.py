"""
CompanionLoader — loads and validates companion archetypes from JSON.
Generates campaign-specific instances with seeded randomisation.
"""
from __future__ import annotations
import json
import random
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from src.ai.companion_persona import (
    CompanionPersona, PersonalityVector, HiddenAgenda, LoyaltyStance
)


ARCHETYPES_PATH = Path(__file__).parent / "archetypes.json"


class CompanionLoader:
    def __init__(self, archetypes_path: Path = ARCHETYPES_PATH):
        with archetypes_path.open() as f:
            data = json.load(f)
        self._archetypes: List[dict] = data["companions"]

    def list_archetypes(self) -> List[str]:
        return [c["companion_id"] for c in self._archetypes]

    def load(
        self,
        archetype_id: str,
        campaign_id: str,
        seed: Optional[int] = None,
    ) -> CompanionPersona:
        """
        Loads an archetype and applies light per-campaign variation
        to personality sliders (±5) so companions feel slightly different
        across playthroughs without changing their core identity.
        """
        base = next(
            (c for c in self._archetypes if c["companion_id"] == archetype_id), None
        )
        if base is None:
            raise ValueError(f"Unknown archetype: {archetype_id!r}")

        rng = random.Random(seed or hash(campaign_id + archetype_id))
        personality_raw = {
            k: max(0, min(100, v + rng.randint(-5, 5)))
            for k, v in base["personality"].items()
        }

        return CompanionPersona(
            companion_id=f"{archetype_id}_{campaign_id[:8]}",
            name=base["name"],
            archetype=base["archetype"],
            voice_id=base["voice_id"],
            personality=PersonalityVector(**personality_raw),
            stance=LoyaltyStance(base["stance"]),
            agendas=[HiddenAgenda.from_dict(a) for a in base["agendas"]],
            backstory=base["backstory"],
            speech_patterns=base["speech_patterns"],
            taboos=base["taboos"],
        )

    def random_companion(self, campaign_id: str, exclude: List[str] = None) -> CompanionPersona:
        exclude = exclude or []
        choices = [c for c in self._archetypes if c["companion_id"] not in exclude]
        if not choices:
            raise ValueError("No available companions")
        chosen = random.choice(choices)
        return self.load(chosen["companion_id"], campaign_id)
