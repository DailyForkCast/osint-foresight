-- =============================================================================
-- Document Entities Table - Enhanced for NER
-- SQLite compatible
-- Version: 2.0 - Enhanced for spaCy NER and entity linking
-- =============================================================================

-- Drop existing table if upgrading
DROP TABLE IF EXISTS document_entities;

-- Enhanced document_entities table
CREATE TABLE document_entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Document reference
    document_id INTEGER NOT NULL,
    document_hash TEXT NOT NULL,

    -- Entity information
    entity_text TEXT NOT NULL,              -- Raw entity text as found in document
    entity_type TEXT NOT NULL,              -- ORG, PERSON, GPE, DATE, MONEY, PRODUCT, TECH, etc.
    entity_canonical TEXT NOT NULL,         -- Normalized form for matching (lowercase, no punctuation)

    -- NER metadata
    confidence REAL DEFAULT 1.0,            -- NER confidence score (0.0-1.0)
    position_start INTEGER,                 -- Character offset in document (start)
    position_end INTEGER,                   -- Character offset in document (end)
    sentence_context TEXT,                  -- Surrounding sentence for validation

    -- Cross-reference links (JSON arrays of matched IDs)
    matched_uspto_entities TEXT,            -- JSON: ["huawei_tech_co", "huawei_invest"]
    matched_openalex_authors TEXT,          -- JSON: ["A1234567890", "A9876543210"]
    matched_ted_contractors TEXT,           -- JSON: ["contractor_id_1", "contractor_id_2"]
    matched_usaspending_recipients TEXT,    -- JSON: ["recipient_id_1"]

    -- Fuzzy matching metadata
    match_confidence REAL DEFAULT 0.0,      -- Fuzzy match confidence (0.0-1.0)
    match_method TEXT,                      -- exact, fuzzy, manual
    verified_match INTEGER DEFAULT 0,       -- Human-verified match

    -- Technology domain classification
    tech_domains TEXT,                      -- JSON: ["semiconductors", "quantum"]

    -- Timestamps
    extracted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    matched_at TEXT,
    verified_at TEXT,

    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_entities_document_id ON document_entities(document_id);
CREATE INDEX idx_entities_document_hash ON document_entities(document_hash);
CREATE INDEX idx_entities_text ON document_entities(entity_text);
CREATE INDEX idx_entities_canonical ON document_entities(entity_canonical);
CREATE INDEX idx_entities_type ON document_entities(entity_type);
CREATE INDEX idx_entities_confidence ON document_entities(confidence);

-- Composite indexes for common queries
CREATE INDEX idx_entities_doc_type ON document_entities(document_id, entity_type);
CREATE INDEX idx_entities_type_canonical ON document_entities(entity_type, entity_canonical);

-- Full-text search on entity text
CREATE VIRTUAL TABLE IF NOT EXISTS entity_fts USING fts5(
    entity_text,
    entity_canonical,
    content=document_entities,
    content_rowid=id
);

-- Trigger to keep FTS index in sync
CREATE TRIGGER entity_fts_insert AFTER INSERT ON document_entities BEGIN
    INSERT INTO entity_fts(rowid, entity_text, entity_canonical)
    VALUES (new.id, new.entity_text, new.entity_canonical);
END;

CREATE TRIGGER entity_fts_update AFTER UPDATE ON document_entities BEGIN
    INSERT INTO entity_fts(entity_fts, rowid, entity_text, entity_canonical)
    VALUES ('delete', old.id, old.entity_text, old.entity_canonical);
    INSERT INTO entity_fts(rowid, entity_text, entity_canonical)
    VALUES (new.id, new.entity_text, new.entity_canonical);
END;

CREATE TRIGGER entity_fts_delete AFTER DELETE ON document_entities BEGIN
    INSERT INTO entity_fts(entity_fts, rowid, entity_text, entity_canonical)
    VALUES ('delete', old.id, old.entity_text, old.entity_canonical);
END;

-- =============================================================================
-- Useful views
-- =============================================================================

-- View: Most mentioned organizations
CREATE VIEW IF NOT EXISTS top_organizations AS
SELECT
    entity_canonical,
    entity_text,
    COUNT(DISTINCT document_id) as doc_count,
    COUNT(*) as mention_count,
    AVG(confidence) as avg_confidence
FROM document_entities
WHERE entity_type = 'ORG'
GROUP BY entity_canonical
ORDER BY doc_count DESC;

-- View: Cross-referenced entities (have matches in other systems)
CREATE VIEW IF NOT EXISTS cross_referenced_entities AS
SELECT
    entity_canonical,
    entity_text,
    entity_type,
    COUNT(DISTINCT document_id) as doc_count,
    SUM(CASE WHEN matched_uspto_entities IS NOT NULL THEN 1 ELSE 0 END) as uspto_matches,
    SUM(CASE WHEN matched_openalex_authors IS NOT NULL THEN 1 ELSE 0 END) as openalex_matches,
    SUM(CASE WHEN matched_ted_contractors IS NOT NULL THEN 1 ELSE 0 END) as ted_matches,
    SUM(CASE WHEN matched_usaspending_recipients IS NOT NULL THEN 1 ELSE 0 END) as usaspending_matches
FROM document_entities
GROUP BY entity_canonical
HAVING uspto_matches > 0 OR openalex_matches > 0 OR ted_matches > 0 OR usaspending_matches > 0
ORDER BY doc_count DESC;

-- View: Entity co-occurrence (entities mentioned in same documents)
CREATE VIEW IF NOT EXISTS entity_cooccurrence AS
SELECT
    e1.entity_canonical as entity1,
    e2.entity_canonical as entity2,
    COUNT(DISTINCT e1.document_id) as cooccurrence_count
FROM document_entities e1
JOIN document_entities e2 ON e1.document_id = e2.document_id
WHERE e1.entity_canonical < e2.entity_canonical  -- Avoid duplicates
    AND e1.entity_type IN ('ORG', 'PERSON')
    AND e2.entity_type IN ('ORG', 'PERSON')
GROUP BY e1.entity_canonical, e2.entity_canonical
HAVING cooccurrence_count >= 3
ORDER BY cooccurrence_count DESC;

-- =============================================================================
-- Schema complete
-- =============================================================================
