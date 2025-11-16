-- U.S. Government Documents Collection Schema
-- Supports Tech Sweep (5-year) and China Sweep (15-year) automated collections

-- ============================================================================
-- Main Documents Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS usgov_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Core identifiers
    doc_uuid TEXT UNIQUE NOT NULL,
    hash_sha256 TEXT UNIQUE,
    doc_number TEXT,  -- Public Law #, GAO-##-###, FR-####-#####, R####, IF####

    -- Metadata
    title TEXT NOT NULL,
    document_type TEXT NOT NULL CHECK(document_type IN (
        'law','regulation','rule','notice','determination','directive',
        'report','testimony','strategy','white_paper','issue_paper',
        'nonpaper','treaty','mou','roadmap','posture_statement',
        'hearing','committee_print','fact_sheet','readout','assessment'
    )),
    publisher_org TEXT NOT NULL,
    publisher_type TEXT CHECK(publisher_type IN (
        'government','congress','independent_agency'
    )),
    agency_bureau TEXT,  -- DOC/BIS, DOD/DARPA, Whitehouse/OSTP

    -- Dates
    publication_date DATE NOT NULL,
    year INTEGER,
    month INTEGER,
    day INTEGER,

    -- URLs and files
    canonical_url TEXT NOT NULL,
    download_url TEXT,
    saved_path TEXT,
    file_ext TEXT,
    file_size_bytes INTEGER,
    pages INTEGER,

    -- Content
    summary TEXT,
    executive_summary TEXT,
    key_findings TEXT,
    authors TEXT,
    citation_suggested TEXT,
    language TEXT DEFAULT 'en',

    -- Classification
    collection TEXT CHECK(collection IN ('tech_sweep','china_sweep','general')),
    sweep_date DATE,  -- When collected

    -- Special identifiers
    rin TEXT,  -- Regulation Identifier Number
    docket_id TEXT,
    fr_doc_number TEXT,  -- Federal Register Document Number
    cfr_citation TEXT,
    public_law_number TEXT,
    treaty_tias_ref TEXT,
    gao_report_number TEXT,
    crs_report_number TEXT,

    -- China-specific fields
    china_focus_flag BOOLEAN DEFAULT 0,
    country_pair_json TEXT,  -- JSON: {"us":"USA","partner":"Japan","context":"China"}
    sanctions_list_ref TEXT,
    entity_list_ref TEXT,
    meeting_or_visit TEXT,

    -- QA and processing
    extraction_ok BOOLEAN,
    extraction_notes TEXT,
    qa_issues TEXT,  -- JSON array of issues
    evidence_quality TEXT CHECK(evidence_quality IN ('STRONG','MODERATE','WEAK')),

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_usgov_doc_type ON usgov_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_usgov_publisher ON usgov_documents(publisher_org);
CREATE INDEX IF NOT EXISTS idx_usgov_agency ON usgov_documents(agency_bureau);
CREATE INDEX IF NOT EXISTS idx_usgov_date ON usgov_documents(publication_date);
CREATE INDEX IF NOT EXISTS idx_usgov_year ON usgov_documents(year);
CREATE INDEX IF NOT EXISTS idx_usgov_collection ON usgov_documents(collection);
CREATE INDEX IF NOT EXISTS idx_usgov_china_flag ON usgov_documents(china_focus_flag);
CREATE INDEX IF NOT EXISTS idx_usgov_hash ON usgov_documents(hash_sha256);
CREATE INDEX IF NOT EXISTS idx_usgov_doc_number ON usgov_documents(doc_number);

-- ============================================================================
-- Document Topics (Many-to-Many)
-- ============================================================================

CREATE TABLE IF NOT EXISTS usgov_document_topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_uuid TEXT NOT NULL,
    topic TEXT NOT NULL,
    subtopic TEXT,
    confidence REAL DEFAULT 1.0,
    detected_by TEXT,  -- 'keyword', 'classifier', 'manual'
    FOREIGN KEY (doc_uuid) REFERENCES usgov_documents(doc_uuid) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_usgov_topics_doc ON usgov_document_topics(doc_uuid);
CREATE INDEX IF NOT EXISTS idx_usgov_topics_topic ON usgov_document_topics(topic);
CREATE INDEX IF NOT EXISTS idx_usgov_topics_subtopic ON usgov_document_topics(subtopic);

-- ============================================================================
-- Sweep Run Metadata
-- ============================================================================

CREATE TABLE IF NOT EXISTS usgov_sweep_runs (
    run_id TEXT PRIMARY KEY,
    sweep_type TEXT NOT NULL CHECK(sweep_type IN ('tech_sweep','china_sweep')),
    run_date DATE NOT NULL,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_seconds INTEGER,

    -- Date window
    window_start_date DATE,
    window_end_date DATE,
    window_years INTEGER,

    -- Counts
    total_collected INTEGER DEFAULT 0,
    unique_documents INTEGER DEFAULT 0,
    duplicates_found INTEGER DEFAULT 0,

    -- By document type
    laws_count INTEGER DEFAULT 0,
    regulations_count INTEGER DEFAULT 0,
    reports_count INTEGER DEFAULT 0,
    testimonies_count INTEGER DEFAULT 0,
    strategies_count INTEGER DEFAULT 0,
    treaties_count INTEGER DEFAULT 0,

    -- QA metrics
    valid_urls_count INTEGER DEFAULT 0,
    valid_urls_pct REAL,
    with_direct_file_count INTEGER DEFAULT 0,
    with_direct_file_pct REAL,
    duplicate_rate_pct REAL,
    qa_pass_rate_pct REAL,
    qa_issues_count INTEGER DEFAULT 0,

    -- Status
    status TEXT CHECK(status IN ('running','completed','failed','partial')) DEFAULT 'running',
    error_log TEXT,

    -- Output paths
    export_path TEXT,
    memo_path TEXT,

    -- Metadata
    sources_queried TEXT,  -- JSON array
    top_agencies TEXT,  -- JSON array
    top_topics TEXT,  -- JSON array

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sweep_runs_type ON usgov_sweep_runs(sweep_type);
CREATE INDEX IF NOT EXISTS idx_sweep_runs_date ON usgov_sweep_runs(run_date);
CREATE INDEX IF NOT EXISTS idx_sweep_runs_status ON usgov_sweep_runs(status);

-- ============================================================================
-- Source Collection Log (Track per-source performance)
-- ============================================================================

CREATE TABLE IF NOT EXISTS usgov_source_collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    source_name TEXT NOT NULL,
    source_type TEXT CHECK(source_type IN ('api','scrape','rss')),

    -- Timing
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_seconds INTEGER,

    -- Results
    records_found INTEGER DEFAULT 0,
    records_collected INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,

    -- Status
    status TEXT CHECK(status IN ('success','partial','failed')) DEFAULT 'success',
    error_message TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES usgov_sweep_runs(run_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_source_collections_run ON usgov_source_collections(run_id);
CREATE INDEX IF NOT EXISTS idx_source_collections_source ON usgov_source_collections(source_name);

-- ============================================================================
-- QA Issues Log
-- ============================================================================

CREATE TABLE IF NOT EXISTS usgov_qa_issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    doc_uuid TEXT,  -- NULL if issue is with collection, not specific doc
    issue_type TEXT NOT NULL CHECK(issue_type IN (
        'dead_link','missing_metadata','enum_unmapped',
        'out_of_window','duplicate','extraction_failed',
        'invalid_date','missing_file','hash_collision'
    )),
    severity TEXT CHECK(severity IN ('critical','high','medium','low')) DEFAULT 'medium',
    description TEXT,
    resolved BOOLEAN DEFAULT 0,
    resolution_notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES usgov_sweep_runs(run_id) ON DELETE CASCADE,
    FOREIGN KEY (doc_uuid) REFERENCES usgov_documents(doc_uuid) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_qa_issues_run ON usgov_qa_issues(run_id);
CREATE INDEX IF NOT EXISTS idx_qa_issues_type ON usgov_qa_issues(issue_type);
CREATE INDEX IF NOT EXISTS idx_qa_issues_severity ON usgov_qa_issues(severity);
CREATE INDEX IF NOT EXISTS idx_qa_issues_resolved ON usgov_qa_issues(resolved);

-- ============================================================================
-- Controlled Vocabularies (Reference tables)
-- ============================================================================

CREATE TABLE IF NOT EXISTS usgov_controlled_topics (
    topic TEXT PRIMARY KEY,
    category TEXT,  -- 'technology', 'policy', 'geography'
    description TEXT,
    aliases TEXT,  -- JSON array of alternative terms
    active BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS usgov_controlled_agencies (
    agency_code TEXT PRIMARY KEY,  -- 'DOC/BIS', 'DOD/DARPA'
    full_name TEXT NOT NULL,
    agency_type TEXT,
    parent_agency TEXT,
    active BOOLEAN DEFAULT 1
);

-- ============================================================================
-- Deduplication Cache
-- ============================================================================

CREATE TABLE IF NOT EXISTS usgov_dedup_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_doc_uuid TEXT NOT NULL,
    duplicate_doc_uuid TEXT NOT NULL,
    similarity_score REAL,
    match_type TEXT CHECK(match_type IN ('hash','title','content')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (canonical_doc_uuid) REFERENCES usgov_documents(doc_uuid),
    FOREIGN KEY (duplicate_doc_uuid) REFERENCES usgov_documents(doc_uuid)
);

CREATE INDEX IF NOT EXISTS idx_dedup_canonical ON usgov_dedup_cache(canonical_doc_uuid);
CREATE INDEX IF NOT EXISTS idx_dedup_duplicate ON usgov_dedup_cache(duplicate_doc_uuid);

-- ============================================================================
-- Views for Common Queries
-- ============================================================================

-- Recent Tech Sweep documents
CREATE VIEW IF NOT EXISTS v_recent_tech_sweep AS
SELECT
    d.*,
    GROUP_CONCAT(dt.topic, ', ') as topics
FROM usgov_documents d
LEFT JOIN usgov_document_topics dt ON d.doc_uuid = dt.doc_uuid
WHERE d.collection = 'tech_sweep'
    AND d.publication_date >= date('now', '-5 years')
GROUP BY d.doc_uuid
ORDER BY d.publication_date DESC;

-- Recent China-related documents
CREATE VIEW IF NOT EXISTS v_recent_china_sweep AS
SELECT
    d.*,
    GROUP_CONCAT(dt.topic, ', ') as topics
FROM usgov_documents d
LEFT JOIN usgov_document_topics dt ON d.doc_uuid = dt.doc_uuid
WHERE d.china_focus_flag = 1
    AND d.publication_date >= date('now', '-15 years')
GROUP BY d.doc_uuid
ORDER BY d.publication_date DESC;

-- QA Dashboard
CREATE VIEW IF NOT EXISTS v_qa_dashboard AS
SELECT
    sr.run_id,
    sr.sweep_type,
    sr.run_date,
    sr.status,
    sr.total_collected,
    sr.unique_documents,
    sr.valid_urls_pct,
    sr.with_direct_file_pct,
    sr.duplicate_rate_pct,
    sr.qa_pass_rate_pct,
    COUNT(DISTINCT qi.id) as total_qa_issues,
    SUM(CASE WHEN qi.severity = 'critical' THEN 1 ELSE 0 END) as critical_issues,
    SUM(CASE WHEN qi.severity = 'high' THEN 1 ELSE 0 END) as high_issues,
    SUM(CASE WHEN qi.resolved = 1 THEN 1 ELSE 0 END) as resolved_issues
FROM usgov_sweep_runs sr
LEFT JOIN usgov_qa_issues qi ON sr.run_id = qi.run_id
GROUP BY sr.run_id
ORDER BY sr.run_date DESC;

-- Top Agencies by Document Count
CREATE VIEW IF NOT EXISTS v_top_agencies AS
SELECT
    agency_bureau,
    publisher_org,
    COUNT(*) as doc_count,
    COUNT(CASE WHEN collection = 'tech_sweep' THEN 1 END) as tech_sweep_count,
    COUNT(CASE WHEN collection = 'china_sweep' THEN 1 END) as china_sweep_count,
    MAX(publication_date) as latest_doc_date
FROM usgov_documents
WHERE agency_bureau IS NOT NULL
GROUP BY agency_bureau, publisher_org
ORDER BY doc_count DESC;
