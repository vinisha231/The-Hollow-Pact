-- The Hollow Pact — Database Schema
-- Postgres with pgvector extension

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Campaigns ────────────────────────────────────────────────────────────

CREATE TABLE campaigns (
    campaign_id     UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    act             INTEGER NOT NULL DEFAULT 1,
    session_count   INTEGER NOT NULL DEFAULT 0,
    state           TEXT NOT NULL DEFAULT 'active',
    world_state     JSONB NOT NULL DEFAULT '{}'
);

-- ── Characters ────────────────────────────────────────────────────────────

CREATE TABLE characters (
    character_id    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    player_id       UUID NOT NULL,
    campaign_id     UUID REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    class           TEXT NOT NULL,
    level           INTEGER NOT NULL DEFAULT 1,
    stats           JSONB NOT NULL DEFAULT '{}',
    inventory       JSONB NOT NULL DEFAULT '[]',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_characters_player ON characters(player_id);
CREATE INDEX idx_characters_campaign ON characters(campaign_id);

-- ── Companion state ───────────────────────────────────────────────────────

CREATE TABLE companion_states (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companion_id    TEXT NOT NULL,
    player_id       UUID NOT NULL,
    campaign_id     UUID REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    trust_value     INTEGER NOT NULL DEFAULT 50,
    betrayal_triggered BOOLEAN NOT NULL DEFAULT FALSE,
    agenda_progress JSONB NOT NULL DEFAULT '{}',
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (companion_id, player_id, campaign_id)
);

-- ── Episodic memory ───────────────────────────────────────────────────────

CREATE TABLE episodic_memories (
    memory_id       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companion_id    TEXT NOT NULL,
    player_id       UUID NOT NULL,
    campaign_id     UUID REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    content         TEXT NOT NULL,
    embedding       vector(1536),
    importance      REAL NOT NULL DEFAULT 0.5
);

CREATE INDEX idx_episodic_companion_player
    ON episodic_memories(companion_id, player_id);
CREATE INDEX idx_episodic_embedding
    ON episodic_memories USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- ── Semantic facts ────────────────────────────────────────────────────────

CREATE TABLE semantic_facts (
    fact_id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companion_id    TEXT NOT NULL,
    player_id       UUID NOT NULL,
    campaign_id     UUID REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    key             TEXT NOT NULL,
    value           TEXT NOT NULL,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (companion_id, player_id, key)
);

-- ── Trust event log (analytics) ───────────────────────────────────────────

CREATE TABLE trust_events (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companion_id    TEXT NOT NULL,
    player_id       UUID NOT NULL,
    campaign_id     UUID,
    session_id      UUID NOT NULL,
    event_type      TEXT NOT NULL,
    delta           INTEGER NOT NULL,
    trust_after     INTEGER NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_trust_events_companion ON trust_events(companion_id, player_id);
CREATE INDEX idx_trust_events_session ON trust_events(session_id);

-- ── Betrayal log ──────────────────────────────────────────────────────────

CREATE TABLE betrayal_log (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companion_id    TEXT NOT NULL,
    player_id       UUID NOT NULL,
    campaign_id     UUID,
    beat_id         TEXT NOT NULL,
    betrayal_type   TEXT NOT NULL,
    trust_at_trigger INTEGER NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
