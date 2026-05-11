CREATE TABLE IF NOT EXISTS campaign_saves (
    save_id         UUID PRIMARY KEY,
    campaign_id     UUID NOT NULL,
    session_number  INTEGER NOT NULL,
    s3_key          TEXT NOT NULL,
    act             INTEGER NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_campaign_saves_campaign ON campaign_saves(campaign_id, created_at DESC);
