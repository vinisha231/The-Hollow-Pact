"""
AuthService — player identity, Steam/Epic SDK bridging, JWT issuance.
Platform-agnostic: each platform passes its own auth token for verification.
"""
from __future__ import annotations
import hashlib
import hmac
import json
import logging
import os
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import jwt  # PyJWT

log = logging.getLogger(__name__)

JWT_SECRET = os.environ.get("JWT_SECRET", "CHANGE_ME_IN_PRODUCTION")
JWT_ALGORITHM = "HS256"
JWT_TTL = 86400  # 24 hours


class Platform(Enum):
    STEAM = "steam"
    EPIC = "epic"
    ANONYMOUS = "anonymous"   # dev/testing only


@dataclass
class PlayerIdentity:
    player_id: str
    display_name: str
    platform: Platform
    platform_id: str
    created_at: float
    last_seen: float


@dataclass
class AuthResult:
    success: bool
    player_id: Optional[str]
    jwt_token: Optional[str]
    error: Optional[str]


class AuthService:
    def __init__(self, db_pool):
        self._db = db_pool

    async def authenticate_steam(self, steam_ticket: str, steam_id: str) -> AuthResult:
        """
        Validate a Steam session ticket via the Steam Web API.
        In production: POST to https://api.steampowered.com/ISteamUserAuth/AuthenticateUserTicket/v1/
        """
        # Stub — real implementation calls Steam Web API
        if not steam_ticket or not steam_id:
            return AuthResult(False, None, None, "missing ticket or id")

        player_id = await self._upsert_player(steam_id, Platform.STEAM, f"Steam_{steam_id[-6:]}")
        token = self._issue_jwt(player_id, Platform.STEAM)
        return AuthResult(True, player_id, token, None)

    async def authenticate_epic(self, epic_access_token: str) -> AuthResult:
        """Validate an Epic Online Services access token."""
        if not epic_access_token:
            return AuthResult(False, None, None, "missing token")
        # Stub — real: GET https://api.epicgames.dev/epic/oauth/v2/userInfo
        platform_id = hashlib.sha256(epic_access_token.encode()).hexdigest()[:16]
        player_id = await self._upsert_player(platform_id, Platform.EPIC, f"Adventurer_{platform_id[:6]}")
        token = self._issue_jwt(player_id, Platform.EPIC)
        return AuthResult(True, player_id, token, None)

    async def authenticate_anonymous(self, device_fingerprint: str) -> AuthResult:
        """Dev-only anonymous auth. Disabled in production builds."""
        if os.environ.get("ENV") == "production":
            return AuthResult(False, None, None, "anonymous auth disabled in production")
        player_id = await self._upsert_player(device_fingerprint, Platform.ANONYMOUS, "Wanderer")
        token = self._issue_jwt(player_id, Platform.ANONYMOUS)
        return AuthResult(True, player_id, token, None)

    def verify_jwt(self, token: str) -> Optional[dict]:
        try:
            return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def _issue_jwt(self, player_id: str, platform: Platform) -> str:
        payload = {
            "sub": player_id,
            "platform": platform.value,
            "iat": int(time.time()),
            "exp": int(time.time()) + JWT_TTL,
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    async def _upsert_player(self, platform_id: str, platform: Platform, display_name: str) -> str:
        row = await self._db.fetchrow(
            "SELECT player_id FROM players WHERE platform_id=$1 AND platform=$2",
            platform_id, platform.value,
        )
        if row:
            await self._db.execute(
                "UPDATE players SET last_seen=NOW() WHERE player_id=$1", str(row["player_id"])
            )
            return str(row["player_id"])

        player_id = str(uuid.uuid4())
        await self._db.execute(
            """INSERT INTO players (player_id, display_name, platform, platform_id, created_at, last_seen)
               VALUES ($1, $2, $3, $4, NOW(), NOW())""",
            player_id, display_name, platform.value, platform_id,
        )
        log.info("player_created id=%s platform=%s", player_id, platform.value)
        return player_id
