"""
Telemetry — structured event logging for game analytics.
Every trust change, betrayal, and dialogue event is logged here.
"""
from __future__ import annotations
import json
import logging
import time
import uuid
from dataclasses import dataclass, asdict
from typing import Any, Optional

log = logging.getLogger(__name__)


@dataclass
class TelemetryEvent:
    event_id: str
    event_type: str
    campaign_id: Optional[str]
    session_id: str
    player_id: Optional[str]
    companion_id: Optional[str]
    payload: dict
    server_time: float

    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)


class TelemetryLogger:
    """
    Wraps a backend sink (Postgres, Datadog, BigQuery, etc).
    Stub implementation logs to Python logger; replace sink in production.
    """

    def __init__(self, sink=None):
        self._sink = sink

    def _emit(self, event: TelemetryEvent) -> None:
        if self._sink:
            self._sink.write(event)
        else:
            log.info("telemetry event_type=%s payload=%s", event.event_type, event.to_json())

    def trust_changed(
        self, session_id: str, campaign_id: str,
        player_id: str, companion_id: str,
        event_type: str, delta: int, trust_after: int, trust_band: str,
    ) -> None:
        self._emit(TelemetryEvent(
            event_id=str(uuid.uuid4()),
            event_type="trust_changed",
            campaign_id=campaign_id,
            session_id=session_id,
            player_id=player_id,
            companion_id=companion_id,
            payload={
                "game_event": event_type,
                "delta": delta,
                "trust_after": trust_after,
                "trust_band": trust_band,
            },
            server_time=time.time(),
        ))

    def betrayal_triggered(
        self, session_id: str, campaign_id: str,
        player_id: str, companion_id: str,
        beat_id: str, betrayal_type: str, trust_at_trigger: int,
    ) -> None:
        self._emit(TelemetryEvent(
            event_id=str(uuid.uuid4()),
            event_type="betrayal_triggered",
            campaign_id=campaign_id,
            session_id=session_id,
            player_id=player_id,
            companion_id=companion_id,
            payload={
                "beat_id": beat_id,
                "betrayal_type": betrayal_type,
                "trust_at_trigger": trust_at_trigger,
            },
            server_time=time.time(),
        ))

    def dialogue_turn(
        self, session_id: str, campaign_id: str,
        player_id: str, companion_id: str,
        latency_ms: float, model_used: str, tokens_used: int,
        intent: str, trust_band: str, injection_flagged: bool,
    ) -> None:
        self._emit(TelemetryEvent(
            event_id=str(uuid.uuid4()),
            event_type="dialogue_turn",
            campaign_id=campaign_id,
            session_id=session_id,
            player_id=player_id,
            companion_id=companion_id,
            payload={
                "latency_ms": latency_ms,
                "model": model_used,
                "tokens": tokens_used,
                "intent": intent,
                "trust_band": trust_band,
                "injection_flagged": injection_flagged,
            },
            server_time=time.time(),
        ))

    def session_ended(
        self, session_id: str, campaign_id: str,
        duration_minutes: float, players: list[str],
    ) -> None:
        self._emit(TelemetryEvent(
            event_id=str(uuid.uuid4()),
            event_type="session_ended",
            campaign_id=campaign_id,
            session_id=session_id,
            player_id=None,
            companion_id=None,
            payload={
                "duration_minutes": duration_minutes,
                "player_count": len(players),
            },
            server_time=time.time(),
        ))
