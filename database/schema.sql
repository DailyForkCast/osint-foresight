-- =============================================================================
-- OSINT Foresight Master Database Schema
-- PostgreSQL 14+
-- Version: 1.0
-- Date: 2025-10-13
-- =============================================================================

-- Drop existing tables (for clean reinstall)
DROP TABLE IF EXISTS document_keywords CASCADE;
DROP TABLE IF EXISTS document_entities CASCADE;
DROP TABLE IF EXISTS document_topics CASCADE;
DROP TABLE IF EXISTS documents CASCADE;

-- =============================================================================
-- MAIN DOCUMENTS TABLE
-- =============================================================================

CREATE TABLE documents (
    -- Primary Key
    id BIGSERIAL PRIMARY KEY,

    -- Document Identity
    document_id VARCHAR(255) UNIQUE,  -- Optional external ID
    hash_sha256 VARCHAR(64) NOT NULL UNIQUE,  -- Deduplication key
    text_hash_sha256 VARCHAR(64),  -- Content-only hash

    -- Document Classification
    document_type VARCHAR(50) NOT NULL,  -- policy, report, paper, etc.

    -- Publisher Information
    publisher_org TEXT NOT NULL,
    publisher_type VARCHAR(50) NOT NULL,  -- government, think_tank, academic, etc.
    publisher_country CHAR(2),  -- ISO 3166-1 alpha-2
    publisher_domain VARCHAR(255),
    verified_publisher BOOLEAN DEFAULT FALSE,

    -- Date Information
    publication_date DATE NOT NULL,
    publication_date_iso VARCHAR(10) NOT NULL,  -- YYYY-MM-DD string
    date_source VARCHAR(100),
    date_confidence VARCHAR(20),  -- low, medium, high
    last_modified TIMESTAMPTZ,

    -- Content
    title TEXT NOT NULL,
    title_en TEXT,  -- English translation if original is non-English
    description TEXT,
    content_text TEXT NOT NULL,
    content_length INTEGER NOT NULL,
    language CHAR(2) NOT NULL,  -- ISO 639-1

    -- File Metadata
    file_size_bytes BIGINT,
    file_format VARCHAR(50),  -- html, pdf, xml, json, etc.
    canonical_url TEXT NOT NULL,

    -- Provenance
    discovery_method VARCHAR(100),  -- api, rss, scrape, etc.
    discovery_timestamp TIMESTAMPTZ,
    fetch_url TEXT NOT NULL,
    archive_url TEXT,
    archive_timestamp TIMESTAMPTZ,
    mirror_source_type VARCHAR(50),  -- direct, wayback, mirror_service
    safe_access_validated BOOLEAN DEFAULT TRUE,
    blocked_domain_detected BOOLEAN DEFAULT FALSE,

    -- Extraction Metadata
    extraction_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    extraction_ok BOOLEAN DEFAULT FALSE,
    qa_passed BOOLEAN DEFAULT FALSE,
    redteam_reviewed BOOLEAN DEFAULT FALSE,
    verified_safe_source BOOLEAN DEFAULT FALSE,
    reliability_weight FLOAT DEFAULT 0.5 CHECK (reliability_weight >= 0.0 AND reliability_weight <= 1.0),
    duplicate_detected BOOLEAN DEFAULT FALSE,
    duplicate_of VARCHAR(64),  -- Reference to hash_sha256 of original

    -- Collection Metadata
    collection_run_id VARCHAR(255),
    collector_name VARCHAR(100) NOT NULL,
    collector_version VARCHAR(20) NOT NULL,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Extensions (JSONB for flexibility)
    extensions JSONB DEFAULT '{}'::jsonb,

    -- Constraints
    CONSTRAINT valid_date_confidence CHECK (date_confidence IN ('low', 'medium', 'high')),
    CONSTRAINT valid_mirror_source CHECK (mirror_source_type IN ('direct', 'wayback', 'mirror_service')),
    CONSTRAINT duplicate_logic CHECK (
        (duplicate_detected = FALSE) OR
        (duplicate_detected = TRUE AND duplicate_of IS NOT NULL)
    ),
    CONSTRAINT qa_logic CHECK (
        (qa_passed = FALSE) OR
        (qa_passed = TRUE AND extraction_ok = TRUE)
    )
);

-- =============================================================================
-- DOCUMENT TOPICS (Many-to-Many)
-- =============================================================================

CREATE TABLE document_topics (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    topic VARCHAR(100) NOT NULL,
    topic_type VARCHAR(20) DEFAULT 'primary' CHECK (topic_type IN ('primary', 'secondary')),

    UNIQUE(document_id, topic)
);

-- =============================================================================
-- DOCUMENT KEYWORDS (Many-to-Many)
-- =============================================================================

CREATE TABLE document_keywords (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    keyword VARCHAR(255) NOT NULL,

    UNIQUE(document_id, keyword)
);

-- =============================================================================
-- DOCUMENT ENTITIES (Many-to-Many)
-- =============================================================================

CREATE TABLE document_entities (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    entity_name VARCHAR(500) NOT NULL,
    entity_type VARCHAR(100),  -- organization, person, location, etc.

    UNIQUE(document_id, entity_name)
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Primary lookup indexes
CREATE INDEX idx_documents_hash ON documents(hash_sha256);
CREATE INDEX idx_documents_text_hash ON documents(text_hash_sha256);
CREATE INDEX idx_documents_duplicate_of ON documents(duplicate_of);

-- Query indexes
CREATE INDEX idx_documents_pub_date ON documents(publication_date);
CREATE INDEX idx_documents_publisher_country ON documents(publisher_country);
CREATE INDEX idx_documents_publisher_type ON documents(publisher_type);
CREATE INDEX idx_documents_document_type ON documents(document_type);
CREATE INDEX idx_documents_language ON documents(language);
CREATE INDEX idx_documents_collector ON documents(collector_name);

-- Quality indexes
CREATE INDEX idx_documents_qa_passed ON documents(qa_passed);
CREATE INDEX idx_documents_extraction_ok ON documents(extraction_ok);
CREATE INDEX idx_documents_verified ON documents(verified_safe_source);

-- Provenance indexes
CREATE INDEX idx_documents_mirror_source ON documents(mirror_source_type);
CREATE INDEX idx_documents_blocked_domain ON documents(blocked_domain_detected);

-- Full-text search indexes
CREATE INDEX idx_documents_title_fts ON documents USING GIN(to_tsvector('english', title));
CREATE INDEX idx_documents_content_fts ON documents USING GIN(to_tsvector('english', content_text));

-- Related table indexes
CREATE INDEX idx_topics_document ON document_topics(document_id);
CREATE INDEX idx_topics_topic ON document_topics(topic);
CREATE INDEX idx_keywords_document ON document_keywords(document_id);
CREATE INDEX idx_keywords_keyword ON document_keywords(keyword);
CREATE INDEX idx_entities_document ON document_entities(document_id);
CREATE INDEX idx_entities_name ON document_entities(entity_name);

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

-- View: High-quality documents
CREATE OR REPLACE VIEW high_quality_documents AS
SELECT
    id,
    document_id,
    hash_sha256,
    title,
    publisher_org,
    publisher_country,
    publication_date,
    document_type,
    qa_passed,
    reliability_weight,
    collector_name
FROM documents
WHERE
    qa_passed = TRUE
    AND extraction_ok = TRUE
    AND duplicate_detected = FALSE
    AND reliability_weight >= 0.7;

-- View: Recent documents (last 3 years)
CREATE OR REPLACE VIEW recent_documents AS
SELECT
    id,
    title,
    publisher_org,
    publisher_country,
    publication_date,
    document_type,
    collector_name
FROM documents
WHERE
    publication_date >= CURRENT_DATE - INTERVAL '3 years'
    AND duplicate_detected = FALSE
ORDER BY publication_date DESC;

-- View: Documents by country
CREATE OR REPLACE VIEW documents_by_country AS
SELECT
    publisher_country,
    COUNT(*) as document_count,
    COUNT(DISTINCT publisher_org) as org_count,
    MIN(publication_date) as earliest_date,
    MAX(publication_date) as latest_date
FROM documents
WHERE duplicate_detected = FALSE
GROUP BY publisher_country
ORDER BY document_count DESC;

-- View: Data quality metrics
CREATE OR REPLACE VIEW data_quality_metrics AS
SELECT
    COUNT(*) as total_documents,
    COUNT(CASE WHEN extraction_ok = TRUE THEN 1 END) as extraction_ok_count,
    COUNT(CASE WHEN qa_passed = TRUE THEN 1 END) as qa_passed_count,
    COUNT(CASE WHEN duplicate_detected = TRUE THEN 1 END) as duplicates_count,
    COUNT(CASE WHEN verified_safe_source = TRUE THEN 1 END) as verified_count,
    AVG(reliability_weight) as avg_reliability,
    AVG(content_length) as avg_content_length
FROM documents;

-- =============================================================================
-- UTILITY FUNCTIONS
-- =============================================================================

-- Function: Find duplicates by text hash
CREATE OR REPLACE FUNCTION find_duplicate_by_text_hash(text_hash VARCHAR(64))
RETURNS TABLE (
    id BIGINT,
    hash_sha256 VARCHAR(64),
    title TEXT,
    publication_date DATE,
    collector_name VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.hash_sha256,
        d.title,
        d.publication_date,
        d.collector_name
    FROM documents d
    WHERE d.text_hash_sha256 = text_hash
    ORDER BY d.created_at ASC
    LIMIT 10;
END;
$$ LANGUAGE plpgsql;

-- Function: Get documents by date range
CREATE OR REPLACE FUNCTION get_documents_by_date_range(
    start_date DATE,
    end_date DATE,
    country_code CHAR(2) DEFAULT NULL
)
RETURNS TABLE (
    id BIGINT,
    title TEXT,
    publisher_org TEXT,
    publisher_country CHAR(2),
    publication_date DATE,
    document_type VARCHAR(50)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.title,
        d.publisher_org,
        d.publisher_country,
        d.publication_date,
        d.document_type
    FROM documents d
    WHERE
        d.publication_date BETWEEN start_date AND end_date
        AND (country_code IS NULL OR d.publisher_country = country_code)
        AND d.duplicate_detected = FALSE
    ORDER BY d.publication_date DESC;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- COMMENTS FOR DOCUMENTATION
-- =============================================================================

COMMENT ON TABLE documents IS 'Main documents table storing all collected intelligence documents in unified format';
COMMENT ON COLUMN documents.hash_sha256 IS 'SHA256 hash of entire document for deduplication';
COMMENT ON COLUMN documents.text_hash_sha256 IS 'SHA256 hash of content only for near-duplicate detection';
COMMENT ON COLUMN documents.reliability_weight IS 'Reliability score 0.0-1.0 based on source quality';
COMMENT ON COLUMN documents.extensions IS 'JSONB field for source-specific extensions';

COMMENT ON TABLE document_topics IS 'Topics/categories assigned to documents';
COMMENT ON TABLE document_keywords IS 'Keywords extracted from documents';
COMMENT ON TABLE document_entities IS 'Named entities (organizations, people, etc.) extracted from documents';

-- =============================================================================
-- GRANT PERMISSIONS (adjust usernames as needed)
-- =============================================================================

-- Create app user (adjust as needed)
-- CREATE USER osint_app WITH PASSWORD 'CHANGE_THIS_PASSWORD';

-- Grant permissions
-- GRANT SELECT, INSERT, UPDATE ON documents TO osint_app;
-- GRANT SELECT, INSERT, UPDATE ON document_topics TO osint_app;
-- GRANT SELECT, INSERT, UPDATE ON document_keywords TO osint_app;
-- GRANT SELECT, INSERT, UPDATE ON document_entities TO osint_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO osint_app;

-- =============================================================================
-- COMPLETION
-- =============================================================================

-- Database schema creation complete
-- Version: 1.0
-- Tables: 4 (documents + 3 related tables)
-- Indexes: 20+
-- Views: 4
-- Functions: 2
-- Triggers: 1

-- Next steps:
-- 1. Run this script: psql -U postgres -d osint_foresight < schema.sql
-- 2. Verify tables created: \dt
-- 3. Check indexes: \di
-- 4. Test with sample data
