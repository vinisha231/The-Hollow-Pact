CREATE TABLE IF NOT EXISTS players (
    player_id   UUID PRIMARY KEY,
    display_name TEXT NOT NULL,
    platform    TEXT NOT NULL,
    platform_id TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (platform, platform_id)
);
