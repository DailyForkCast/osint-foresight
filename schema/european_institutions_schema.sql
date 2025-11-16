-- European Institutional Intelligence Framework
-- Purpose: Track decision-makers, policies, and debates on China/US relations, technology, security
-- Coverage: 42 European countries + regional organizations
-- Created: 2025-10-26

-- ============================================================================
-- CORE INSTITUTION REGISTRY
-- ============================================================================

CREATE TABLE IF NOT EXISTS european_institutions (
    institution_id TEXT PRIMARY KEY,
    institution_name TEXT NOT NULL,
    institution_name_native TEXT,
    institution_type TEXT NOT NULL, -- ministry, agency, council, commission, parliament, regulator
    jurisdiction_level TEXT NOT NULL, -- national, regional, eu, nato, multilateral
    country_code TEXT, -- ISO 3166-1 alpha-2 (NULL for regional orgs)
    parent_organization TEXT, -- EU Commission directorate, ministry department

    -- Contact & Web Presence
    official_website TEXT,
    press_office_url TEXT,
    publications_url TEXT,
    legislation_url TEXT,

    -- Focus Areas (JSON array)
    policy_domains TEXT, -- ["foreign_affairs", "defense", "technology", "trade", "security"]
    china_relevance INTEGER, -- 0-100 score
    us_relevance INTEGER, -- 0-100 score
    tech_relevance INTEGER, -- 0-100 score

    -- Metadata
    established_date TEXT,
    budget_eur REAL,
    staff_count INTEGER,
    status TEXT DEFAULT 'active', -- active, merged, dissolved

    -- Collection tracking
    last_scraped TEXT,
    collection_frequency TEXT, -- daily, weekly, monthly
    scraper_status TEXT, -- operational, needs_review, manual_only

    -- Source verification
    source_verified_date TEXT,
    verified_by TEXT,
    notes TEXT,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INSTITUTIONAL SUBDIVISIONS (Directorates, Departments, Units)
-- ============================================================================

CREATE TABLE IF NOT EXISTS institution_subdivisions (
    subdivision_id TEXT PRIMARY KEY,
    institution_id TEXT NOT NULL,
    subdivision_name TEXT NOT NULL,
    subdivision_type TEXT, -- directorate, department, unit, division, bureau

    -- Leadership
    head_name TEXT,
    head_title TEXT,

    -- Focus
    policy_focus TEXT, -- Specific policy area (e.g., "China Affairs", "Export Controls")
    description TEXT,

    -- Contact
    contact_email TEXT,
    website_url TEXT,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (institution_id) REFERENCES european_institutions(institution_id)
);

-- ============================================================================
-- KEY PERSONNEL (Decision-makers, Ministers, Directors)
-- ============================================================================

CREATE TABLE IF NOT EXISTS institutional_personnel (
    person_id TEXT PRIMARY KEY,
    institution_id TEXT NOT NULL,
    subdivision_id TEXT,

    -- Identity
    full_name TEXT NOT NULL,
    title TEXT NOT NULL, -- Minister, State Secretary, Director-General, Ambassador
    role_type TEXT, -- political, civil_servant, military, diplomatic

    -- Position details
    position_start_date TEXT,
    position_end_date TEXT,
    is_current INTEGER DEFAULT 1,

    -- Background
    political_party TEXT,
    previous_positions TEXT, -- JSON array
    education TEXT,
    expertise_areas TEXT, -- JSON array: ["china_policy", "cybersecurity", "trade"]

    -- Public presence
    official_bio_url TEXT,
    twitter_handle TEXT,
    linkedin_url TEXT,

    -- Statements tracking
    statement_count INTEGER DEFAULT 0,
    last_statement_date TEXT,
    china_stance TEXT, -- hawkish, moderate, accommodating, unknown

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (institution_id) REFERENCES european_institutions(institution_id),
    FOREIGN KEY (subdivision_id) REFERENCES institution_subdivisions(subdivision_id)
);

-- ============================================================================
-- POLICY DOCUMENTS & PUBLICATIONS
-- ============================================================================

CREATE TABLE IF NOT EXISTS institutional_publications (
    publication_id TEXT PRIMARY KEY,
    institution_id TEXT NOT NULL,
    subdivision_id TEXT,

    -- Document metadata
    title TEXT NOT NULL,
    title_english TEXT,
    document_type TEXT NOT NULL, -- white_paper, strategy, law, regulation, report, speech, press_release
    publication_date TEXT NOT NULL,

    -- Content
    summary TEXT,
    full_text TEXT,
    language TEXT,
    page_count INTEGER,

    -- URLs & Access
    official_url TEXT,
    pdf_url TEXT,
    archived_url TEXT, -- Wayback Machine
    local_file_path TEXT,

    -- Topical relevance
    mentions_china INTEGER DEFAULT 0,
    mentions_us INTEGER DEFAULT 0,
    mentions_russia INTEGER DEFAULT 0,
    china_sentiment TEXT, -- positive, neutral, negative, mixed

    -- Technology topics (JSON array)
    technology_topics TEXT, -- ["semiconductors", "AI", "5G", "quantum"]
    security_topics TEXT, -- ["cyber", "espionage", "investment_screening", "export_controls"]

    -- Policy impact
    legal_status TEXT, -- draft, enacted, repealed
    legal_citation TEXT, -- Official gazette reference
    supersedes_doc_id TEXT, -- Previous version

    -- Collection tracking
    extraction_method TEXT, -- manual, automated, api
    extraction_quality INTEGER, -- 0-100
    needs_review INTEGER DEFAULT 0,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (institution_id) REFERENCES european_institutions(institution_id)
);

-- ============================================================================
-- LEGISLATIVE & REGULATORY FRAMEWORK
-- ============================================================================

CREATE TABLE IF NOT EXISTS european_legislation (
    legislation_id TEXT PRIMARY KEY,
    institution_id TEXT NOT NULL,
    country_code TEXT,

    -- Legal identification
    official_title TEXT NOT NULL,
    official_number TEXT, -- Law number, regulation number
    legal_type TEXT, -- law, decree, regulation, directive, decision

    -- Dates
    proposal_date TEXT,
    enactment_date TEXT,
    effective_date TEXT,
    expiry_date TEXT,

    -- Content
    summary TEXT,
    scope TEXT, -- What does this regulate?

    -- China/Tech relevance
    china_specific INTEGER DEFAULT 0, -- 1 if specifically targets China
    technology_sector TEXT, -- semiconductors, telecoms, AI, etc.
    security_rationale TEXT, -- Why was this passed? (national security, economic security)

    -- Implementation
    implementing_body TEXT, -- Which institution enforces this?
    penalties TEXT, -- What are the consequences?

    -- Related documents
    official_gazette_url TEXT,
    eur_lex_id TEXT, -- For EU legislation

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (institution_id) REFERENCES european_institutions(institution_id)
);

-- ============================================================================
-- PARLIAMENTARY ACTIVITIES (Debates, Questions, Hearings)
-- ============================================================================

CREATE TABLE IF NOT EXISTS parliamentary_activities (
    activity_id TEXT PRIMARY KEY,
    institution_id TEXT NOT NULL, -- Parliament institution
    country_code TEXT,

    -- Activity details
    activity_type TEXT, -- debate, question, hearing, committee_meeting, vote
    activity_date TEXT NOT NULL,
    chamber TEXT, -- lower, upper, joint, committee
    committee_name TEXT,

    -- Content
    topic TEXT NOT NULL,
    description TEXT,
    transcript_url TEXT,
    video_url TEXT,

    -- Participants
    participants TEXT, -- JSON array of MPs, ministers

    -- China/Tech relevance
    china_mentioned INTEGER DEFAULT 0,
    china_focus INTEGER DEFAULT 0, -- Primary topic vs. mentioned
    technology_focus TEXT,
    security_focus TEXT,

    -- Outcomes
    outcome TEXT, -- resolution_passed, law_proposed, minister_questioned
    follow_up_actions TEXT,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (institution_id) REFERENCES european_institutions(institution_id)
);

-- ============================================================================
-- OFFICIAL STATEMENTS & PRESS RELEASES
-- ============================================================================

CREATE TABLE IF NOT EXISTS institutional_statements (
    statement_id TEXT PRIMARY KEY,
    institution_id TEXT NOT NULL,
    person_id TEXT, -- Who made the statement

    -- Statement details
    statement_date TEXT NOT NULL,
    statement_type TEXT, -- press_release, speech, interview, testimony, tweet
    title TEXT,
    content TEXT NOT NULL,

    -- Context
    event_name TEXT, -- Conference, hearing where statement was made
    audience TEXT, -- Public, parliament, closed-door

    -- China/Tech stance
    china_mentioned INTEGER DEFAULT 0,
    china_stance TEXT, -- critical, supportive, neutral
    policy_area TEXT, -- trade, security, technology, human_rights

    -- Sentiment analysis
    sentiment_score REAL, -- -1 to 1
    key_phrases TEXT, -- JSON array of important quotes

    -- Media coverage
    media_coverage_count INTEGER DEFAULT 0,

    -- URLs
    official_url TEXT,
    transcript_url TEXT,
    video_url TEXT,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (institution_id) REFERENCES european_institutions(institution_id),
    FOREIGN KEY (person_id) REFERENCES institutional_personnel(person_id)
);

-- ============================================================================
-- INTERAGENCY COORDINATION (Who works with whom)
-- ============================================================================

CREATE TABLE IF NOT EXISTS institutional_relationships (
    relationship_id TEXT PRIMARY KEY,
    institution_a_id TEXT NOT NULL,
    institution_b_id TEXT NOT NULL,

    -- Relationship details
    relationship_type TEXT, -- coordination, oversight, advisory, reporting
    formalized INTEGER, -- 1 if formal MoU, 0 if informal

    -- Collaboration areas
    coordination_topics TEXT, -- JSON array
    joint_publications INTEGER DEFAULT 0,

    -- Temporal
    relationship_start TEXT,
    relationship_end TEXT,
    is_active INTEGER DEFAULT 1,

    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (institution_a_id) REFERENCES european_institutions(institution_id),
    FOREIGN KEY (institution_b_id) REFERENCES european_institutions(institution_id)
);

-- ============================================================================
-- CROSS-REFERENCES TO EXISTING DATA
-- ============================================================================

CREATE TABLE IF NOT EXISTS institution_entity_links (
    link_id TEXT PRIMARY KEY,
    institution_id TEXT NOT NULL,

    -- Links to existing OSINT data
    linked_entity_type TEXT, -- ted_contract, academic_partnership, patent, conference
    linked_entity_id TEXT,
    linked_entity_name TEXT,

    -- Relationship context
    relationship_nature TEXT, -- regulator, funder, participant, oversight
    relationship_date TEXT,

    -- Evidence
    evidence_url TEXT,
    evidence_description TEXT,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (institution_id) REFERENCES european_institutions(institution_id)
);

-- ============================================================================
-- INTELLIGENCE ASSESSMENTS (Analyst insights)
-- ============================================================================

CREATE TABLE IF NOT EXISTS institutional_intelligence (
    assessment_id TEXT PRIMARY KEY,
    institution_id TEXT NOT NULL,
    assessment_date TEXT NOT NULL,

    -- Assessment
    china_policy_position TEXT, -- hawkish, moderate, accommodating
    china_policy_trend TEXT, -- hardening, softening, stable
    influence_level TEXT, -- high, medium, low (how much influence on national policy)

    -- Key findings
    recent_actions TEXT, -- What have they done recently?
    notable_statements TEXT,
    policy_shifts TEXT,

    -- Strategic context
    alignment_with_eu TEXT, -- aligned, divergent, mixed
    alignment_with_nato TEXT,
    alignment_with_us TEXT,

    -- Risk assessment
    vulnerability_to_china_influence INTEGER, -- 0-100
    vulnerability_factors TEXT,

    -- Analyst notes
    analyst_name TEXT,
    confidence_level INTEGER, -- 0-100
    sources_consulted TEXT,
    next_review_date TEXT,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (institution_id) REFERENCES european_institutions(institution_id)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_institutions_country ON european_institutions(country_code);
CREATE INDEX IF NOT EXISTS idx_institutions_type ON european_institutions(institution_type);
CREATE INDEX IF NOT EXISTS idx_institutions_china_relevance ON european_institutions(china_relevance);

CREATE INDEX IF NOT EXISTS idx_publications_institution ON institutional_publications(institution_id);
CREATE INDEX IF NOT EXISTS idx_publications_date ON institutional_publications(publication_date);
CREATE INDEX IF NOT EXISTS idx_publications_china ON institutional_publications(mentions_china);
CREATE INDEX IF NOT EXISTS idx_publications_type ON institutional_publications(document_type);

CREATE INDEX IF NOT EXISTS idx_personnel_institution ON institutional_personnel(institution_id);
CREATE INDEX IF NOT EXISTS idx_personnel_current ON institutional_personnel(is_current);

CREATE INDEX IF NOT EXISTS idx_statements_institution ON institutional_statements(institution_id);
CREATE INDEX IF NOT EXISTS idx_statements_date ON institutional_statements(statement_date);
CREATE INDEX IF NOT EXISTS idx_statements_person ON institutional_statements(person_id);

CREATE INDEX IF NOT EXISTS idx_legislation_country ON european_legislation(country_code);
CREATE INDEX IF NOT EXISTS idx_legislation_china ON european_legislation(china_specific);

CREATE INDEX IF NOT EXISTS idx_parliamentary_date ON parliamentary_activities(activity_date);
CREATE INDEX IF NOT EXISTS idx_parliamentary_china ON parliamentary_activities(china_focus);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Active China-focused institutions
CREATE VIEW IF NOT EXISTS v_china_focused_institutions AS
SELECT
    i.institution_id,
    i.institution_name,
    i.country_code,
    i.institution_type,
    i.china_relevance,
    i.official_website,
    COUNT(DISTINCT p.publication_id) as china_publications,
    COUNT(DISTINCT s.statement_id) as china_statements
FROM european_institutions i
LEFT JOIN institutional_publications p ON i.institution_id = p.institution_id AND p.mentions_china = 1
LEFT JOIN institutional_statements s ON i.institution_id = s.institution_id AND s.china_mentioned = 1
WHERE i.status = 'active'
  AND i.china_relevance >= 50
GROUP BY i.institution_id
ORDER BY i.china_relevance DESC;

-- Current decision-makers on China policy
CREATE VIEW IF NOT EXISTS v_china_policy_decision_makers AS
SELECT
    p.person_id,
    p.full_name,
    p.title,
    p.china_stance,
    i.institution_name,
    i.country_code,
    p.position_start_date,
    p.statement_count,
    p.last_statement_date
FROM institutional_personnel p
JOIN european_institutions i ON p.institution_id = i.institution_id
WHERE p.is_current = 1
  AND i.china_relevance >= 50
ORDER BY p.last_statement_date DESC;

-- Recent China-relevant legislation
CREATE VIEW IF NOT EXISTS v_recent_china_legislation AS
SELECT
    l.legislation_id,
    l.official_title,
    l.country_code,
    l.legal_type,
    l.enactment_date,
    l.technology_sector,
    l.security_rationale,
    i.institution_name as enacting_body
FROM european_legislation l
JOIN european_institutions i ON l.institution_id = i.institution_id
WHERE l.china_specific = 1
   OR l.official_title LIKE '%China%'
   OR l.security_rationale LIKE '%China%'
ORDER BY l.enactment_date DESC;
