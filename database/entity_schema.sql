-- Entity Extraction Schema for OSINT Warehouse
-- Week 4: Entity Extraction & Linking
-- SQLite 3 compatible

-- ============================================================================
-- CORE ENTITY TABLES
-- ============================================================================

-- Master entity table
CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Entity Identity
    entity_name TEXT NOT NULL,
    entity_type TEXT NOT NULL,  -- organization, person, location, technology, event
    entity_subtype TEXT,         -- company, university, government, city, country, etc.

    -- Normalization
    canonical_name TEXT NOT NULL,
    name_variants TEXT,          -- JSON array of alternative names

    -- Entity Attributes
    country TEXT,                -- Country code (US, CN, GB, etc.)
    sector TEXT,                 -- Technology, Defense, Academic, Government, etc.
    description TEXT,            -- Brief description

    -- Confidence & Quality
    confidence_score REAL DEFAULT 0.5,  -- 0.0-1.0 confidence in entity identification
    extraction_method TEXT,      -- pattern, ner, manual, external
    verified INTEGER DEFAULT 0,  -- 0=unverified, 1=verified

    -- External IDs
    external_ids TEXT DEFAULT '{}',  -- JSON: {"lei": "...", "duns": "...", etc.}

    -- Statistics
    document_mentions INTEGER DEFAULT 0,
    first_seen TEXT,
    last_seen TEXT,

    -- Metadata
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    UNIQUE(canonical_name, entity_type)
);

CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_entities_canonical ON entities(canonical_name);
CREATE INDEX IF NOT EXISTS idx_entities_country ON entities(country);
CREATE INDEX IF NOT EXISTS idx_entities_sector ON entities(sector);
CREATE INDEX IF NOT EXISTS idx_entities_mentions ON entities(document_mentions DESC);

-- ============================================================================
-- DOCUMENT-ENTITY RELATIONSHIPS
-- ============================================================================

-- Many-to-many relationship between documents and entities
CREATE TABLE IF NOT EXISTS document_entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Relationships
    document_hash TEXT NOT NULL,  -- Foreign key to documents.hash_sha256
    entity_id INTEGER NOT NULL,   -- Foreign key to entities.id

    -- Context
    mention_count INTEGER DEFAULT 1,
    mention_positions TEXT,       -- JSON array of character positions
    context_snippets TEXT,        -- JSON array of surrounding text

    -- Role
    entity_role TEXT,             -- author, subject, partner, competitor, etc.
    prominence TEXT,              -- primary, secondary, mentioned

    -- Confidence
    confidence_score REAL DEFAULT 0.5,
    extraction_method TEXT,       -- pattern, ner, keyword

    -- Metadata
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    UNIQUE(document_hash, entity_id),
    FOREIGN KEY(entity_id) REFERENCES entities(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_doc_entities_document ON document_entities(document_hash);
CREATE INDEX IF NOT EXISTS idx_doc_entities_entity ON document_entities(entity_id);
CREATE INDEX IF NOT EXISTS idx_doc_entities_role ON document_entities(entity_role);
CREATE INDEX IF NOT EXISTS idx_doc_entities_prominence ON document_entities(prominence);

-- ============================================================================
-- ENTITY ALIASES & VARIANTS
-- ============================================================================

-- Entity name aliases (for fuzzy matching)
CREATE TABLE IF NOT EXISTS entity_aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    entity_id INTEGER NOT NULL,
    alias_name TEXT NOT NULL,
    alias_type TEXT,              -- acronym, translation, abbreviation, former_name
    language TEXT,                -- en, zh, etc.

    -- Metadata
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(entity_id) REFERENCES entities(id) ON DELETE CASCADE,
    UNIQUE(entity_id, alias_name)
);

CREATE INDEX IF NOT EXISTS idx_aliases_name ON entity_aliases(alias_name);
CREATE INDEX IF NOT EXISTS idx_aliases_entity ON entity_aliases(entity_id);

-- ============================================================================
-- ENTITY RELATIONSHIPS
-- ============================================================================

-- Relationships between entities (collaborations, ownership, etc.)
CREATE TABLE IF NOT EXISTS entity_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Relationship
    entity_from INTEGER NOT NULL,  -- Foreign key to entities.id
    entity_to INTEGER NOT NULL,    -- Foreign key to entities.id
    relation_type TEXT NOT NULL,   -- collaboration, ownership, partnership, competition, etc.

    -- Context
    supporting_documents TEXT,     -- JSON array of document hashes
    description TEXT,

    -- Temporal
    start_date TEXT,
    end_date TEXT,
    is_active INTEGER DEFAULT 1,

    -- Confidence
    confidence_score REAL DEFAULT 0.5,
    evidence_count INTEGER DEFAULT 0,

    -- Metadata
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(entity_from) REFERENCES entities(id) ON DELETE CASCADE,
    FOREIGN KEY(entity_to) REFERENCES entities(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_relations_from ON entity_relations(entity_from);
CREATE INDEX IF NOT EXISTS idx_relations_to ON entity_relations(entity_to);
CREATE INDEX IF NOT EXISTS idx_relations_type ON entity_relations(relation_type);
CREATE INDEX IF NOT EXISTS idx_relations_active ON entity_relations(is_active);

-- ============================================================================
-- CROSS-REFERENCES TO EXTERNAL DATASETS
-- ============================================================================

-- Links to USPTO, OpenAlex, TED, etc.
CREATE TABLE IF NOT EXISTS entity_cross_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Entity
    entity_id INTEGER NOT NULL,

    -- External Dataset
    external_dataset TEXT NOT NULL,  -- uspto, openalex, ted, gleif, etc.
    external_id TEXT NOT NULL,       -- Patent number, work ID, contract ID, LEI, etc.
    external_record TEXT,            -- JSON: full external record (optional)

    -- Relationship Type
    reference_type TEXT,             -- patent_holder, author, contractor, subsidiary, etc.

    -- Confidence
    confidence_score REAL DEFAULT 0.5,
    match_method TEXT,               -- exact, fuzzy, manual

    -- Metadata
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(entity_id) REFERENCES entities(id) ON DELETE CASCADE,
    UNIQUE(entity_id, external_dataset, external_id)
);

CREATE INDEX IF NOT EXISTS idx_xref_entity ON entity_cross_references(entity_id);
CREATE INDEX IF NOT EXISTS idx_xref_dataset ON entity_cross_references(external_dataset);
CREATE INDEX IF NOT EXISTS idx_xref_external_id ON entity_cross_references(external_id);

-- ============================================================================
-- TECHNOLOGY TAXONOMY
-- ============================================================================

-- Technology classification (for technology entities)
CREATE TABLE IF NOT EXISTS technology_taxonomy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    entity_id INTEGER NOT NULL,

    -- Classification
    domain TEXT NOT NULL,          -- AI, Quantum, Semiconductors, Space, Energy, etc.
    subdomain TEXT,                -- Machine Learning, Quantum Computing, etc.
    keywords TEXT,                 -- JSON array of related keywords

    -- Dual-Use Assessment
    dual_use_potential TEXT,       -- civilian, military, dual_use
    sensitivity_level TEXT,        -- low, medium, high, critical

    -- Strategic Importance
    strategic_importance REAL,     -- 0.0-1.0 score
    china_relevance REAL,          -- 0.0-1.0 score for China focus

    -- Metadata
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(entity_id) REFERENCES entities(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_tech_entity ON technology_taxonomy(entity_id);
CREATE INDEX IF NOT EXISTS idx_tech_domain ON technology_taxonomy(domain);
CREATE INDEX IF NOT EXISTS idx_tech_dual_use ON technology_taxonomy(dual_use_potential);
CREATE INDEX IF NOT EXISTS idx_tech_sensitivity ON technology_taxonomy(sensitivity_level);

-- ============================================================================
-- ENTITY MENTIONS CACHE (for performance)
-- ============================================================================

-- Pre-computed entity mention statistics
CREATE TABLE IF NOT EXISTS entity_mention_stats (
    entity_id INTEGER PRIMARY KEY,

    -- Mention Counts
    total_mentions INTEGER DEFAULT 0,
    document_count INTEGER DEFAULT 0,

    -- By Publisher Type
    thinktank_mentions INTEGER DEFAULT 0,
    archive_mentions INTEGER DEFAULT 0,

    -- By Language
    english_mentions INTEGER DEFAULT 0,
    chinese_mentions INTEGER DEFAULT 0,

    -- By Country
    us_mentions INTEGER DEFAULT 0,
    cn_mentions INTEGER DEFAULT 0,

    -- Temporal
    first_mention_date TEXT,
    last_mention_date TEXT,

    -- Top Co-Mentions (other entities mentioned with this one)
    top_co_entities TEXT,  -- JSON: [{"entity_id": 123, "count": 45}, ...]

    -- Updated
    last_updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(entity_id) REFERENCES entities(id) ON DELETE CASCADE
);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Top organizations by mention count
CREATE VIEW IF NOT EXISTS v_top_organizations AS
SELECT
    e.id,
    e.canonical_name,
    e.country,
    e.sector,
    e.document_mentions,
    COUNT(DISTINCT de.document_hash) as unique_documents,
    SUM(de.mention_count) as total_mentions
FROM entities e
LEFT JOIN document_entities de ON e.id = de.entity_id
WHERE e.entity_type = 'organization'
GROUP BY e.id
ORDER BY total_mentions DESC;

-- View: Top technologies by mention count
CREATE VIEW IF NOT EXISTS v_top_technologies AS
SELECT
    e.id,
    e.canonical_name,
    tt.domain,
    tt.subdomain,
    tt.dual_use_potential,
    e.document_mentions,
    COUNT(DISTINCT de.document_hash) as unique_documents
FROM entities e
LEFT JOIN technology_taxonomy tt ON e.id = tt.entity_id
LEFT JOIN document_entities de ON e.id = de.entity_id
WHERE e.entity_type = 'technology'
GROUP BY e.id
ORDER BY unique_documents DESC;

-- View: Entity network (co-mentions)
CREATE VIEW IF NOT EXISTS v_entity_network AS
SELECT
    de1.entity_id as entity_1,
    de2.entity_id as entity_2,
    COUNT(DISTINCT de1.document_hash) as co_mention_count
FROM document_entities de1
JOIN document_entities de2 ON de1.document_hash = de2.document_hash
WHERE de1.entity_id < de2.entity_id  -- Avoid duplicates
GROUP BY de1.entity_id, de2.entity_id
HAVING co_mention_count >= 2;  -- At least 2 co-mentions

-- View: Cross-dataset entity coverage
CREATE VIEW IF NOT EXISTS v_entity_coverage AS
SELECT
    e.id,
    e.canonical_name,
    e.entity_type,
    COUNT(DISTINCT xr.external_dataset) as external_datasets,
    GROUP_CONCAT(DISTINCT xr.external_dataset) as datasets
FROM entities e
LEFT JOIN entity_cross_references xr ON e.id = xr.entity_id
GROUP BY e.id;

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- ============================================================================

-- Update entity.updated_at on changes
CREATE TRIGGER IF NOT EXISTS trigger_entities_updated
AFTER UPDATE ON entities
BEGIN
    UPDATE entities SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Update entity.document_mentions when document_entities changes
CREATE TRIGGER IF NOT EXISTS trigger_update_mention_count_insert
AFTER INSERT ON document_entities
BEGIN
    UPDATE entities
    SET document_mentions = document_mentions + 1,
        last_seen = CURRENT_TIMESTAMP
    WHERE id = NEW.entity_id;
END;

CREATE TRIGGER IF NOT EXISTS trigger_update_mention_count_delete
AFTER DELETE ON document_entities
BEGIN
    UPDATE entities
    SET document_mentions = MAX(0, document_mentions - 1)
    WHERE id = OLD.entity_id;
END;

-- ============================================================================
-- END OF ENTITY SCHEMA
-- ============================================================================
