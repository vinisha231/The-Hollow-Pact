"""
CampaignSaveService — serialises and restores full campaign state.
Structured fields in Postgres; binary blobs in S3.
"""
from __future__ import annotations
import json
import logging
import time
import uuid
from dataclasses import dataclass, asdict
from typing import Optional

import asyncpg
import boto3

from src.world.world_state import WorldState
from src.ai.trust_engine import TrustState

log = logging.getLogger(__name__)

S3_BUCKET = "hollow-pact-saves"


@dataclass
class CampaignSave:
    save_id: str
    campaign_id: str
    session_number: int
    world_state: WorldState
    trust_states: dict[str, TrustState]   # key: f"{companion}:{player}"
    created_at: float
    checksum: str


class CampaignSaveService:
    def __init__(self, db_pool: asyncpg.Pool, s3_client):
        self._db = db_pool
        self._s3 = s3_client

    async def save(self, save: CampaignSave) -> str:
        """Persist campaign save. Returns save_id."""
        world_json = json.dumps(save.world_state.to_dict())
        trust_json = json.dumps({
            k: asdict(v) for k, v in save.trust_states.items()
        })

        # Store large blobs in S3
        s3_key = f"campaigns/{save.campaign_id}/{save.save_id}.json"
        blob = json.dumps({
            "world": save.world_state.to_dict(),
            "trust": {k: asdict(v) for k, v in save.trust_states.items()},
        })
        self._s3.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=blob.encode(),
            ContentType="application/json",
        )

        # Store metadata in Postgres
        await self._db.execute(
            """
            INSERT INTO campaign_saves
              (save_id, campaign_id, session_number, s3_key, act, created_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            save.save_id, save.campaign_id, save.session_number,
            s3_key, save.world_state.act, save.created_at,
        )
        log.info("campaign_saved id=%s campaign=%s session=%d",
                 save.save_id, save.campaign_id, save.session_number)
        return save.save_id

    async def load_latest(self, campaign_id: str) -> Optional[CampaignSave]:
        row = await self._db.fetchrow(
            """
            SELECT save_id, campaign_id, session_number, s3_key, created_at
            FROM campaign_saves
            WHERE campaign_id=$1
            ORDER BY created_at DESC
            LIMIT 1
            """,
            campaign_id,
        )
        if row is None:
            return None
        return await self._load_from_s3(dict(row))

    async def _load_from_s3(self, meta: dict) -> CampaignSave:
        obj = self._s3.get_object(Bucket=S3_BUCKET, Key=meta["s3_key"])
        data = json.loads(obj["Body"].read())
        world = WorldState.from_dict(data["world"])
        trust = {
            k: TrustState(**v) for k, v in data["trust"].items()
        }
        return CampaignSave(
            save_id=meta["save_id"],
            campaign_id=meta["campaign_id"],
            session_number=meta["session_number"],
            world_state=world,
            trust_states=trust,
            created_at=meta["created_at"],
            checksum="",
        )
