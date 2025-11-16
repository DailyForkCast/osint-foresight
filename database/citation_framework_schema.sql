-- ============================================================================
-- COMPREHENSIVE CITATION FRAMEWORK
-- ============================================================================
-- Purpose: Academic/Intelligence-grade source citation and tracking
-- Standards: APA 7th Edition, Chicago Manual of Style compatible
-- Zero-Fabrication: Multiple sources per claim, full provenance tracking
-- ============================================================================

-- ============================================================================
-- CORE CITATIONS TABLE
-- ============================================================================
-- Stores complete bibliographic information for all sources
-- Supports multiple sources per claim with formal citation formats

CREATE TABLE IF NOT EXISTS source_citations (
    citation_id TEXT PRIMARY KEY,

    -- Source Identification
    source_type TEXT NOT NULL,  -- 'news_article', 'government_document', 'academic_paper', 'book', 'press_release', 'treaty', 'database', 'interview'
    source_url TEXT,
    archive_url TEXT,  -- Archive.org or similar permanent URL
    doi TEXT,  -- Digital Object Identifier
    isbn TEXT,  -- For books

    -- Bibliographic Information
    title TEXT NOT NULL,
    subtitle TEXT,
    author TEXT,  -- Comma-separated for multiple authors
    publisher TEXT,
    publication_name TEXT,  -- Newspaper, journal, website name
    publication_date DATE,
    publication_year INTEGER,
    volume TEXT,
    issue TEXT,
    pages TEXT,  -- "45-67" or "A1, A4"
    edition TEXT,

    -- Access Information
    access_date DATE NOT NULL,  -- When we retrieved this source
    last_verified_date DATE,  -- Last time we checked URL still works
    access_method TEXT,  -- 'web', 'database', 'physical_archive', 'foia_request'

    -- Language and Translation
    original_language TEXT DEFAULT 'en',
    translated BOOLEAN DEFAULT 0,
    translator TEXT,

    -- Citation Formats (auto-generated)
    citation_apa TEXT,  -- APA 7th Edition format
    citation_chicago TEXT,  -- Chicago Manual of Style
    citation_mla TEXT,  -- MLA 9th Edition

    -- Reliability Assessment
    source_reliability INTEGER DEFAULT 3,  -- 1=primary official, 2=verified secondary, 3=credible, 4=unverified
    peer_reviewed BOOLEAN DEFAULT 0,
    government_official BOOLEAN DEFAULT 0,

    -- Metadata
    notes TEXT,
    retrieved_by TEXT,  -- Who accessed this source
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- CITATION LINKS TABLE
-- ============================================================================
-- Links citations to records in other tables (many-to-many)
-- Enables multiple sources per claim

CREATE TABLE IF NOT EXISTS citation_links (
    link_id TEXT PRIMARY KEY,
    citation_id TEXT NOT NULL,

    -- What this citation supports (one of these will be populated)
    linked_table TEXT NOT NULL,  -- 'major_acquisitions', 'bilateral_events', etc.
    linked_record_id TEXT NOT NULL,  -- The primary key of the linked record

    -- Specificity
    claim_supported TEXT,  -- Specific claim this citation supports (e.g., "deal value", "date", "entire_record")
    page_reference TEXT,  -- Specific page/section in source
    quote_extract TEXT,  -- Direct quote if applicable

    -- Evidence Quality
    evidence_type TEXT,  -- 'primary', 'secondary', 'tertiary', 'corroborating'
    evidence_strength TEXT DEFAULT 'supporting',  -- 'definitive', 'strong', 'supporting', 'circumstantial'

    -- Conflict Resolution
    conflicts_with TEXT,  -- citation_id of conflicting source, if any
    conflict_resolution TEXT,  -- How conflict was resolved

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (citation_id) REFERENCES source_citations(citation_id)
);

-- ============================================================================
-- ARCHIVE SNAPSHOTS TABLE
-- ============================================================================
-- Tracks when we archived web sources to prevent link rot

CREATE TABLE IF NOT EXISTS source_archives (
    archive_id TEXT PRIMARY KEY,
    citation_id TEXT NOT NULL,

    -- Archive Details
    archive_service TEXT,  -- 'archive_org', 'perma_cc', 'archive_today', 'local_copy'
    archive_url TEXT NOT NULL,
    archive_date DATE NOT NULL,
    archive_status TEXT DEFAULT 'active',  -- 'active', 'failed', 'pending'

    -- Verification
    original_url TEXT NOT NULL,
    original_url_status TEXT,  -- 'active', 'dead', 'paywall', 'moved'
    hash_sha256 TEXT,  -- Hash of archived content for verification

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (citation_id) REFERENCES source_citations(citation_id)
);

-- ============================================================================
-- CITATION METADATA
-- ============================================================================

CREATE TABLE IF NOT EXISTS citation_framework_metadata (
    metadata_key TEXT PRIMARY KEY,
    metadata_value TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR REPLACE INTO citation_framework_metadata VALUES
    ('citation_standard', 'APA 7th Edition', CURRENT_TIMESTAMP),
    ('archive_service', 'archive.org', CURRENT_TIMESTAMP),
    ('minimum_sources_per_claim', '2', CURRENT_TIMESTAMP),
    ('verification_frequency_days', '180', CURRENT_TIMESTAMP),
    ('framework_version', '1.0', CURRENT_TIMESTAMP);

-- ============================================================================
-- VIEWS: Citation Quality Metrics
-- ============================================================================

-- View: Records with insufficient sources
CREATE VIEW IF NOT EXISTS v_insufficient_sources AS
SELECT
    cl.linked_table,
    cl.linked_record_id,
    COUNT(DISTINCT cl.citation_id) as source_count,
    GROUP_CONCAT(DISTINCT sc.source_type) as source_types
FROM citation_links cl
LEFT JOIN source_citations sc ON cl.citation_id = sc.citation_id
GROUP BY cl.linked_table, cl.linked_record_id
HAVING COUNT(DISTINCT cl.citation_id) < 2;

-- View: Citations needing verification
CREATE VIEW IF NOT EXISTS v_citations_need_verification AS
SELECT
    citation_id,
    title,
    source_url,
    last_verified_date,
    julianday('now') - julianday(last_verified_date) as days_since_verified
FROM source_citations
WHERE last_verified_date IS NULL
   OR julianday('now') - julianday(last_verified_date) > 180;

-- View: Citation reliability by record
CREATE VIEW IF NOT EXISTS v_citation_reliability_by_record AS
SELECT
    cl.linked_table,
    cl.linked_record_id,
    COUNT(*) as citation_count,
    AVG(sc.source_reliability) as avg_reliability,
    MIN(sc.source_reliability) as best_reliability,
    SUM(CASE WHEN sc.government_official = 1 THEN 1 ELSE 0 END) as official_sources,
    SUM(CASE WHEN sc.peer_reviewed = 1 THEN 1 ELSE 0 END) as peer_reviewed_sources
FROM citation_links cl
JOIN source_citations sc ON cl.citation_id = sc.citation_id
GROUP BY cl.linked_table, cl.linked_record_id;

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_source_citations_type ON source_citations(source_type);
CREATE INDEX IF NOT EXISTS idx_source_citations_reliability ON source_citations(source_reliability);
CREATE INDEX IF NOT EXISTS idx_source_citations_date ON source_citations(publication_date);
CREATE INDEX IF NOT EXISTS idx_citation_links_record ON citation_links(linked_table, linked_record_id);
CREATE INDEX IF NOT EXISTS idx_citation_links_citation ON citation_links(citation_id);
CREATE INDEX IF NOT EXISTS idx_source_archives_citation ON source_archives(citation_id);

-- ============================================================================
-- HELPER FUNCTIONS (implemented in Python)
-- ============================================================================

-- These would be implemented in Python citation_manager.py:
-- - generate_apa_citation()
-- - generate_chicago_citation()
-- - generate_mla_citation()
-- - archive_url_to_wayback()
-- - verify_citation_accessible()
-- - export_bibliography()

SELECT 'CITATION FRAMEWORK SCHEMA CREATED' as status;
