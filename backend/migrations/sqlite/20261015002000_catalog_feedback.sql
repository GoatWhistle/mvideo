-- migrate:up
CREATE TABLE catalog_configuration (
    id INTEGER PRIMARY KEY CONSTRAINT catalog_singleton CHECK (id = 1),
    version TEXT NOT NULL,
    payload TEXT NOT NULL
);
CREATE TABLE corrections (
    id TEXT PRIMARY KEY,
    fingerprint TEXT NOT NULL,
    source_hash TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    brand TEXT NOT NULL,
    attribute TEXT NOT NULL,
    value TEXT NOT NULL,
    key TEXT NOT NULL,
    quote TEXT NOT NULL,
    start INTEGER NOT NULL,
    end INTEGER NOT NULL,
    learn_alias INTEGER NOT NULL CONSTRAINT alias_boolean CHECK (learn_alias IN (0, 1)),
    created_at TEXT NOT NULL,
    revoked INTEGER NOT NULL DEFAULT 0 CONSTRAINT revoked_boolean CHECK (revoked IN (0, 1)),
    version INTEGER NOT NULL DEFAULT 1 CONSTRAINT positive_version CHECK (version > 0),
    CONSTRAINT valid_span CHECK (start >= 0 AND end > start)
);
CREATE UNIQUE INDEX active_card_attribute ON corrections(source_hash, category_id, attribute)
    WHERE revoked = 0;
CREATE INDEX scoped_alias ON corrections(category_id, brand, attribute) WHERE learn_alias = 1 AND revoked = 0;

-- migrate:down
DROP TABLE corrections;
DROP TABLE catalog_configuration;
