"""
SessionManager — creates and tracks multiplayer party sessions.
Integrates with Hathora for on-demand dedicated server allocation.
"""
from __future__ import annotations
import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

log = logging.getLogger(__name__)

MAX_PLAYERS = 4


class SessionState(Enum):
    LOBBY = "lobby"
    IN_QUEST = "in_quest"
    IN_COMBAT = "in_combat"
    RETURNING_TO_HUB = "returning_to_hub"
    ENDED = "ended"


@dataclass
class PlayerSlot:
    slot_id: int           # 0-3
    player_id: Optional[str] = None
    character_id: Optional[str] = None
    companion_id: Optional[str] = None
    connected: bool = False
    is_host: bool = False


@dataclass
class PartySession:
    session_id: str
    campaign_id: str
    hathora_room_id: Optional[str]
    state: SessionState
    slots: List[PlayerSlot] = field(default_factory=lambda: [
        PlayerSlot(slot_id=i) for i in range(MAX_PLAYERS)
    ])
    created_at: float = field(default_factory=time.time)
    server_url: Optional[str] = None

    @property
    def player_count(self) -> int:
        return sum(1 for s in self.slots if s.player_id is not None)

    @property
    def host_slot(self) -> Optional[PlayerSlot]:
        return next((s for s in self.slots if s.is_host), None)

    def add_player(self, player_id: str, character_id: str, companion_id: str) -> PlayerSlot:
        for slot in self.slots:
            if slot.player_id is None:
                slot.player_id = player_id
                slot.character_id = character_id
                slot.companion_id = companion_id
                slot.connected = True
                if self.player_count == 1:
                    slot.is_host = True
                log.info("player_joined session=%s player=%s slot=%d", self.session_id, player_id, slot.slot_id)
                return slot
        raise ValueError("Session is full")

    def remove_player(self, player_id: str) -> None:
        for slot in self.slots:
            if slot.player_id == player_id:
                was_host = slot.is_host
                slot.player_id = None
                slot.character_id = None
                slot.companion_id = None
                slot.connected = False
                slot.is_host = False
                log.info("player_left session=%s player=%s", self.session_id, player_id)
                if was_host:
                    self._reassign_host()
                return

    def _reassign_host(self) -> None:
        for slot in self.slots:
            if slot.player_id is not None:
                slot.is_host = True
                log.info("host_reassigned session=%s new_host=%s", self.session_id, slot.player_id)
                return


class SessionManager:
    def __init__(self, hathora_app_id: str, hathora_token: str):
        self._app_id = hathora_app_id
        self._token = hathora_token
        self._sessions: Dict[str, PartySession] = {}

    async def create_session(self, campaign_id: str) -> PartySession:
        session_id = str(uuid.uuid4())
        room_id = await self._allocate_hathora_room(session_id)
        session = PartySession(
            session_id=session_id,
            campaign_id=campaign_id,
            hathora_room_id=room_id,
            state=SessionState.LOBBY,
        )
        self._sessions[session_id] = session
        log.info("session_created id=%s campaign=%s room=%s", session_id, campaign_id, room_id)
        return session

    async def get_session(self, session_id: str) -> Optional[PartySession]:
        return self._sessions.get(session_id)

    async def end_session(self, session_id: str) -> None:
        session = self._sessions.get(session_id)
        if session:
            session.state = SessionState.ENDED
            await self._release_hathora_room(session.hathora_room_id)
            del self._sessions[session_id]

    async def _allocate_hathora_room(self, session_id: str) -> str:
        # Real implementation: POST to Hathora rooms API
        # Stub for now
        return f"hathora_room_{session_id[:8]}"

    async def _release_hathora_room(self, room_id: Optional[str]) -> None:
        if room_id:
            log.info("hathora_room_released id=%s", room_id)
