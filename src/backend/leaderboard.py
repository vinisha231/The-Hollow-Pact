"""
LeaderboardService — tracks cross-player companion statistics.
Shows aggregate stats like betrayal rate, average trust at campaign end.
No individual player data exposed.
"""
from __future__ import annotations
import logging
import time
from dataclasses import dataclass
from typing import Optional

import asyncpg

log = logging.getLogger(__name__)


@dataclass
class CompanionStats:
    companion_id: str
    total_campaigns: int
    betrayal_rate: float       # 0-1; % of campaigns ending in hard betrayal
    avg_final_trust: float     # average trust at campaign end
    most_common_betrayal_type: Optional[str]
    avg_session_hours: float


class LeaderboardService:
    def __init__(self, db: asyncpg.Pool):
        self._db = db

    async def get_companion_stats(self, companion_id: str) -> Optional[CompanionStats]:
        row = await self._db.fetchrow(
            """
            SELECT
                COUNT(*) AS total_campaigns,
                AVG(trust_at_trigger::float) AS avg_final_trust,
                COUNT(CASE WHEN betrayal_type != 'none' THEN 1 END)::float / COUNT(*) AS betrayal_rate,
                MODE() WITHIN GROUP (ORDER BY betrayal_type) AS most_common_betrayal_type
            FROM betrayal_log
            WHERE companion_id = $1
            """,
            companion_id,
        )
        if not row:
            return None
        return CompanionStats(
            companion_id=companion_id,
            total_campaigns=row["total_campaigns"],
            betrayal_rate=float(row["betrayal_rate"] or 0),
            avg_final_trust=float(row["avg_final_trust"] or 50),
            most_common_betrayal_type=row["most_common_betrayal_type"],
            avg_session_hours=0.0,  # TODO: join with session_events
        )

    async def global_betrayal_rate(self) -> float:
        row = await self._db.fetchrow(
            "SELECT AVG(CASE WHEN betrayal_type != 'none' THEN 1 ELSE 0 END) AS rate FROM betrayal_log"
        )
        return float(row["rate"] or 0) if row else 0.0
