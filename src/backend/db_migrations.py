"""
Database migration runner.
Applies SQL migrations in order; tracks applied migrations in a migrations table.
"""
from __future__ import annotations
import asyncio
import logging
import os
from pathlib import Path

import asyncpg

log = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).parents[2] / "server" / "orchestration" / "db" / "migrations"


async def run_migrations(pool: asyncpg.Pool) -> None:
    await pool.execute("""
        CREATE TABLE IF NOT EXISTS migrations (
            id SERIAL PRIMARY KEY,
            filename TEXT NOT NULL UNIQUE,
            applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)

    applied = {r["filename"] for r in await pool.fetch("SELECT filename FROM migrations")}
    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql")) if MIGRATIONS_DIR.exists() else []

    for path in migration_files:
        if path.name in applied:
            continue
        sql = path.read_text()
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(sql)
                await conn.execute("INSERT INTO migrations (filename) VALUES ($1)", path.name)
        log.info("migration_applied: %s", path.name)
