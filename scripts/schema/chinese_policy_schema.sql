-- ==============================================================================
-- CHINESE POLICY & STRATEGY DATABASE SCHEMA
-- ==============================================================================
-- Purpose: Comprehensive tracking of Chinese national strategies, Five Year Plans,
--          Military-Civil Fusion policies, and cross-references to entities/technologies
-- Created: 2025-11-08
-- Compliance: Zero Fabrication Protocol
-- ==============================================================================

-- ==============================================================================
-- I. CORE POLICY DOCUMENTS
-- ==============================================================================

CREATE TABLE IF NOT EXISTS chinese_policy_documents (
    -- Primary identification
    document_id TEXT PRIMARY KEY,  -- Format: cn_policy_<hash> or cn_fyp_14_<section>
    document_type TEXT NOT NULL,   -- fyp_national, fyp_technology, national_strategy, mcf_policy, legislation, implementation_plan

    -- Document metadata
    title_chinese TEXT,
    title_english TEXT NOT NULL,
    document_code TEXT,             -- Official document number (e.g., 国发〔2015〕28号)

    -- Provenance (CRITICAL for Zero Fabrication)
    issuing_body_chinese TEXT,
    issuing_body_english TEXT NOT NULL,  -- e.g., State Council, National People's Congress, Central Military Commission
    publication_date TEXT,          -- ISO format YYYY-MM-DD
    publication_year INTEGER,
    effective_date TEXT,            -- When policy takes effect (may differ from publication)
    expiration_date TEXT,           -- If applicable (e.g., FYP ends 2025)

    -- Source provenance
    source_url_chinese TEXT,        -- Original Chinese government website
    source_url_english TEXT,        -- Official English translation source
    translation_source TEXT,        -- e.g., 'Xinhua Official', 'Georgetown CSET', 'China Law Translate'
    acquired_date TEXT NOT NULL,    -- When we obtained the document

    -- Content
    document_text_chinese TEXT,     -- Full Chinese text
    document_text_english TEXT,     -- Full English translation
    executive_summary TEXT,         -- 1-2 paragraph summary

    -- Structured extraction
    strategic_objectives TEXT,      -- JSON array: Key goals stated in document
    target_metrics TEXT,            -- JSON object: Specific targets (e.g., {"semiconductor_self_sufficiency": "70%", "target_year": "2025"})
    technology_priorities TEXT,     -- JSON array: Technologies explicitly prioritized
    investment_commitments TEXT,    -- JSON object: Funding amounts and sources

    -- Classification
    policy_domain TEXT,             -- industrial, technology, defense, economic, legislative
    technology_areas TEXT,          -- JSON array: semiconductors, AI, quantum, biotech, etc.
    geographic_scope TEXT,          -- national, provincial, pilot_zone

    -- MCF-specific fields
    mcf_relevance TEXT,            -- none, implicit, explicit, core_mcf_document
    mcf_technologies TEXT,          -- JSON array: Dual-use technologies mentioned
    military_applications TEXT,     -- If explicitly mentioned

    -- Cross-reference hooks
    supersedes_document_id TEXT,    -- Previous policy version
    superseded_by_document_id TEXT, -- Newer policy version
    related_documents TEXT,         -- JSON array of related policy IDs

    -- Analysis metadata
    veracity_status TEXT DEFAULT 'verified',  -- verified, official_translation, third_party_translation, excerpt_only
    completeness TEXT DEFAULT 'complete',     -- complete, summary_only, excerpt, pending_full_text
    confidence_level TEXT DEFAULT 'high',     -- high, medium, low (based on source quality)

    -- Audit trail
    created_at TEXT NOT NULL,
    updated_at TEXT,
    verified_by TEXT,               -- Analyst who verified provenance
    notes TEXT,

    FOREIGN KEY (supersedes_document_id) REFERENCES chinese_policy_documents(document_id),
    FOREIGN KEY (superseded_by_document_id) REFERENCES chinese_policy_documents(document_id)
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_chinese_policy_type ON chinese_policy_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_chinese_policy_year ON chinese_policy_documents(publication_year);
CREATE INDEX IF NOT EXISTS idx_chinese_policy_issuing_body ON chinese_policy_documents(issuing_body_english);
CREATE INDEX IF NOT EXISTS idx_chinese_policy_mcf_relevance ON chinese_policy_documents(mcf_relevance);

-- ==============================================================================
-- II. CROSS-REFERENCE TABLES - LINK POLICIES TO REAL-WORLD ENTITIES/TECH
-- ==============================================================================

-- Link Chinese policies to specific entities (SOEs, companies, institutions)
CREATE TABLE IF NOT EXISTS policy_entity_mandates (
    mandate_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Policy side
    policy_document_id TEXT NOT NULL,
    policy_section TEXT,            -- Which section of the policy mentions the entity

    -- Entity side
    entity_id TEXT,                 -- References prc_soe_historical_database or entities table
    entity_name_chinese TEXT,
    entity_name_english TEXT NOT NULL,
    entity_type TEXT,               -- soe, private_company, university, research_institute, military

    -- Nature of mandate
    mandate_type TEXT NOT NULL,     -- funding_recipient, target_entity, implementing_agency, pilot_enterprise
    mandate_description TEXT,       -- What the entity is directed/funded to do

    -- Financials (if specified)
    funding_amount_rmb REAL,        -- In RMB (元)
    funding_amount_usd REAL,        -- Converted to USD for comparison
    funding_source TEXT,            -- e.g., 'National IC Fund Phase II', 'State Council Special Fund'
    funding_period_start TEXT,
    funding_period_end TEXT,

    -- Evidence
    evidence_type TEXT,             -- explicit_mention, implementation_announcement, funding_award
    evidence_text_chinese TEXT,     -- Actual quote from policy
    evidence_text_english TEXT,
    source_page_number TEXT,        -- For long documents

    -- Compliance tracking
    compliance_status TEXT,         -- not_started, in_progress, completed, failed, unknown
    compliance_notes TEXT,          -- Track whether entity actually executed mandate

    created_at TEXT NOT NULL,

    FOREIGN KEY (policy_document_id) REFERENCES chinese_policy_documents(document_id)
);

CREATE INDEX IF NOT EXISTS idx_policy_entity_mandates_policy ON policy_entity_mandates(policy_document_id);
CREATE INDEX IF NOT EXISTS idx_policy_entity_mandates_entity ON policy_entity_mandates(entity_id);
CREATE INDEX IF NOT EXISTS idx_policy_entity_mandates_type ON policy_entity_mandates(mandate_type);

-- Link Chinese policies to technology domains
CREATE TABLE IF NOT EXISTS policy_technology_priorities (
    priority_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Policy side
    policy_document_id TEXT NOT NULL,
    policy_section TEXT,

    -- Technology classification
    technology_domain TEXT NOT NULL,  -- semiconductors, AI, quantum, biotech, aerospace, etc.
    technology_subdomain TEXT,        -- e.g., domain=AI, subdomain=computer_vision
    chinese_classification TEXT,      -- Chinese government's own tech classification

    -- Priority level
    priority_tier TEXT,               -- strategic, important, general
    priority_rank INTEGER,            -- 1, 2, 3... (if policy ranks technologies)

    -- Targets
    development_target TEXT,          -- Text description of goal
    target_metrics TEXT,              -- JSON: {"self_sufficiency": "70%", "global_share": "25%"}
    target_date TEXT,

    -- Investment
    allocated_funding_rmb REAL,
    allocated_funding_usd REAL,

    -- Cross-reference to international classifications
    cpc_codes TEXT,                   -- JSON array: Relevant patent CPC codes
    openalex_topics TEXT,             -- JSON array: Matching OpenAlex topic IDs
    european_tech_domain TEXT,        -- Equivalent EU tech domain from our policy_documents

    created_at TEXT NOT NULL,

    FOREIGN KEY (policy_document_id) REFERENCES chinese_policy_documents(document_id)
);

CREATE INDEX IF NOT EXISTS idx_policy_tech_priorities_policy ON policy_technology_priorities(policy_document_id);
CREATE INDEX IF NOT EXISTS idx_policy_tech_priorities_domain ON policy_technology_priorities(technology_domain);
CREATE INDEX IF NOT EXISTS idx_policy_tech_priorities_tier ON policy_technology_priorities(priority_tier);

-- ==============================================================================
-- III. POLICY INTERACTION MATRIX - CHINA ↔ EUROPE/US
-- ==============================================================================

-- Track how policies interact: Chinese offensive strategies vs. European/US defensive responses
CREATE TABLE IF NOT EXISTS policy_interactions (
    interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Chinese policy side
    chinese_policy_id TEXT NOT NULL,
    chinese_policy_title TEXT,
    chinese_policy_date TEXT,

    -- Foreign policy side
    foreign_policy_id TEXT,         -- May reference policy_documents table (European) or new US policy table
    foreign_country_code TEXT,      -- EU, US, GB, etc.
    foreign_policy_title TEXT,
    foreign_policy_date TEXT,

    -- Interaction type
    interaction_type TEXT NOT NULL, -- response_defensive, counter_investment, regulatory_barrier, cooperation_framework
    temporal_relationship TEXT,     -- chinese_first, foreign_first, simultaneous, cyclical

    -- Time gap analysis
    first_policy_date TEXT,
    second_policy_date TEXT,
    days_between INTEGER,

    -- Competitive analysis
    chinese_investment_rmb REAL,
    foreign_investment_usd REAL,
    technology_domain TEXT,         -- What they're competing over

    -- Description
    interaction_description TEXT,   -- How the policies interact
    strategic_implications TEXT,    -- Analysis of what this means

    -- Evidence
    evidence_citations TEXT,        -- JSON array: Supporting evidence

    created_at TEXT NOT NULL,

    FOREIGN KEY (chinese_policy_id) REFERENCES chinese_policy_documents(document_id),
    FOREIGN KEY (foreign_policy_id) REFERENCES policy_documents(document_id)
);

CREATE INDEX IF NOT EXISTS idx_policy_interactions_chinese ON policy_interactions(chinese_policy_id);
CREATE INDEX IF NOT EXISTS idx_policy_interactions_foreign ON policy_interactions(foreign_policy_id);
CREATE INDEX IF NOT EXISTS idx_policy_interactions_type ON policy_interactions(interaction_type);
CREATE INDEX IF NOT EXISTS idx_policy_interactions_tech ON policy_interactions(technology_domain);

-- ==============================================================================
-- IV. FIVE YEAR PLAN SPECIFICS - STRUCTURED TRACKING
-- ==============================================================================

-- Five Year Plans deserve their own detailed tracking structure
CREATE TABLE IF NOT EXISTS five_year_plan_chapters (
    chapter_id TEXT PRIMARY KEY,    -- fyp_14_ch3 (14th FYP, Chapter 3)

    plan_period TEXT NOT NULL,      -- 13th (2016-2020), 14th (2021-2025), 15th (2026-2030)
    plan_type TEXT,                 -- national, provincial, sectoral

    chapter_number INTEGER,
    chapter_title_chinese TEXT,
    chapter_title_english TEXT,

    -- Content
    chapter_text_chinese TEXT,
    chapter_text_english TEXT,
    key_objectives TEXT,            -- JSON array

    -- Technology/industry focus
    technology_domains TEXT,        -- JSON array
    target_industries TEXT,         -- JSON array

    -- Metrics
    quantitative_targets TEXT,      -- JSON object: All numerical targets in this chapter

    -- Cross-references
    implementing_policies TEXT,     -- JSON array: Policies that implement this chapter
    responsible_agencies TEXT,      -- JSON array: Government bodies responsible

    parent_document_id TEXT,        -- Links to main FYP document

    created_at TEXT NOT NULL,

    FOREIGN KEY (parent_document_id) REFERENCES chinese_policy_documents(document_id)
);

-- Track progress on Five Year Plan targets
CREATE TABLE IF NOT EXISTS fyp_target_tracking (
    tracking_id INTEGER PRIMARY KEY AUTOINCREMENT,

    chapter_id TEXT NOT NULL,
    target_description TEXT NOT NULL,

    -- Target specification
    baseline_value REAL,
    baseline_year INTEGER,
    target_value REAL,
    target_year INTEGER,
    measurement_unit TEXT,          -- percent, billion_rmb, million_units, etc.

    -- Progress tracking
    current_value REAL,
    current_as_of_date TEXT,
    progress_percentage REAL,       -- (current - baseline) / (target - baseline) * 100
    on_track_status TEXT,           -- ahead, on_track, behind, failed, unknown

    -- Evidence of progress
    data_source TEXT,               -- Where we got current_value (official stats, third-party estimate)
    source_url TEXT,
    source_date TEXT,
    confidence TEXT,                -- high, medium, low (based on data source reliability)

    notes TEXT,
    updated_at TEXT,

    FOREIGN KEY (chapter_id) REFERENCES five_year_plan_chapters(chapter_id)
);

-- ==============================================================================
-- V. MCF-SPECIFIC TABLES - MILITARY-CIVIL FUSION TRACKING
-- ==============================================================================

-- Track MCF-designated enterprises and institutions
CREATE TABLE IF NOT EXISTS mcf_designated_entities (
    designation_id INTEGER PRIMARY KEY AUTOINCREMENT,

    entity_id TEXT,                 -- Link to main entities database
    entity_name_chinese TEXT,
    entity_name_english TEXT NOT NULL,

    -- MCF designation
    designation_type TEXT,          -- mcf_demonstration_enterprise, mcf_pilot_zone, mcf_research_center
    designation_date TEXT,
    designating_authority TEXT,     -- Which government body granted MCF status
    designation_document_id TEXT,   -- Link to policy that designated them

    -- Status
    designation_status TEXT,        -- active, suspended, revoked, unknown

    -- Capabilities
    dual_use_technologies TEXT,     -- JSON array: Technologies they work on
    military_applications TEXT,     -- Documented military uses
    civilian_applications TEXT,     -- Documented civilian uses

    -- Integration metrics
    military_revenue_percentage REAL,
    civilian_revenue_percentage REAL,
    cross_domain_projects TEXT,     -- JSON array: Projects spanning military/civilian

    -- Evidence
    source_url TEXT,
    source_document TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT,

    FOREIGN KEY (designation_document_id) REFERENCES chinese_policy_documents(document_id)
);

CREATE INDEX IF NOT EXISTS idx_mcf_designated_entities_type ON mcf_designated_entities(designation_type);
CREATE INDEX IF NOT EXISTS idx_mcf_designated_entities_status ON mcf_designated_entities(designation_status);

-- ==============================================================================
-- VI. THINK TANK & SECONDARY ANALYSIS - TRACKED SEPARATELY
-- ==============================================================================

-- Secondary analysis by Western think tanks - SEPARATE from primary sources
CREATE TABLE IF NOT EXISTS chinese_policy_analysis (
    analysis_id TEXT PRIMARY KEY,

    -- What's being analyzed
    analyzed_policy_id TEXT,        -- Links to chinese_policy_documents
    analyzed_topic TEXT,            -- If not a specific policy

    -- Who did the analysis
    analyst_organization TEXT NOT NULL,  -- MERICS, CSET, CSIS, ASPI, Brookings, etc.
    analyst_names TEXT,             -- Individual researchers
    publication_title TEXT NOT NULL,
    publication_date TEXT,
    publication_url TEXT,

    -- Content
    executive_summary TEXT,
    key_findings TEXT,              -- JSON array
    analytical_conclusions TEXT,    -- JSON array

    -- CRITICAL: Distinguish facts from analysis
    factual_content TEXT,           -- Documented facts cited in the analysis
    analytical_content TEXT,        -- Expert opinions/interpretations

    -- Quality assessment
    source_quality TEXT,            -- authoritative, credible, questionable
    citation_quality TEXT,          -- well_cited, partial_citation, opinion_based

    -- Flags
    is_primary_source BOOLEAN DEFAULT 0,  -- Almost always FALSE for think tank reports
    contains_translation BOOLEAN,   -- Does it include Chinese policy translations?

    created_at TEXT NOT NULL,

    FOREIGN KEY (analyzed_policy_id) REFERENCES chinese_policy_documents(document_id)
);

CREATE INDEX IF NOT EXISTS idx_chinese_policy_analysis_org ON chinese_policy_analysis(analyst_organization);
CREATE INDEX IF NOT EXISTS idx_chinese_policy_analysis_policy ON chinese_policy_analysis(analyzed_policy_id);

-- ==============================================================================
-- VII. SOURCE TRACKING - PROVENANCE FOR ZERO FABRICATION
-- ==============================================================================

CREATE TABLE IF NOT EXISTS chinese_policy_sources (
    source_id INTEGER PRIMARY KEY AUTOINCREMENT,

    source_name TEXT NOT NULL,      -- 'State Council Website', 'Georgetown CSET', 'Xinhua English'
    source_type TEXT NOT NULL,      -- official_chinese, official_translation, academic_translation, think_tank
    source_url_base TEXT,           -- Base URL

    reliability_tier TEXT,          -- tier1_official, tier2_verified_translation, tier3_third_party
    language TEXT,                  -- zh, en, both

    access_method TEXT,             -- public_web, academic_subscription, purchased, archived
    last_accessed TEXT,
    accessibility_status TEXT,      -- accessible, requires_vpn, requires_subscription, archived_only

    notes TEXT,
    created_at TEXT NOT NULL
);

-- Link documents to their sources (many-to-many: one document may have Chinese + English sources)
CREATE TABLE IF NOT EXISTS document_source_links (
    link_id INTEGER PRIMARY KEY AUTOINCREMENT,

    document_id TEXT NOT NULL,
    source_id INTEGER NOT NULL,

    source_url_specific TEXT,       -- Specific URL for this document
    acquisition_date TEXT NOT NULL,
    acquired_by TEXT,               -- Who obtained it

    version_type TEXT,              -- original_chinese, official_english, third_party_translation
    completeness TEXT,              -- complete_document, excerpt, summary

    verification_status TEXT,       -- verified, pending_verification, unverified
    verified_by TEXT,
    verified_date TEXT,

    notes TEXT,

    FOREIGN KEY (document_id) REFERENCES chinese_policy_documents(document_id),
    FOREIGN KEY (source_id) REFERENCES chinese_policy_sources(source_id)
);

-- ==============================================================================
-- VIII. ENHANCED MCF TABLES - EXPAND EXISTING INFRASTRUCTURE
-- ==============================================================================

-- The existing mcf_documents table will be migrated/merged with chinese_policy_documents
-- The existing empty tables will be populated:

-- mcf_sources → chinese_policy_sources (expanded version above)
-- mcf_document_entities → policy_entity_mandates (expanded version above)
-- mcf_document_technologies → policy_technology_priorities (expanded version above)

-- New taxonomy table for MCF technologies
CREATE TABLE IF NOT EXISTS mcf_technology_taxonomy (
    taxonomy_id INTEGER PRIMARY KEY AUTOINCREMENT,

    technology_name_chinese TEXT,
    technology_name_english TEXT NOT NULL,

    -- Classification
    technology_category TEXT,       -- core, important, emerging
    dual_use_classification TEXT,   -- explicit_dual_use, implicit_dual_use, civilian_primary, military_primary

    -- Cross-references
    cpc_codes TEXT,                 -- JSON array: Patent classification codes
    openalex_topics TEXT,           -- JSON array: Academic research topics
    bis_control_classification TEXT, -- US export control classification

    -- MCF relevance
    mcf_priority_level TEXT,        -- strategic, important, general
    military_applications TEXT,      -- JSON array
    civilian_applications TEXT,      -- JSON array

    -- Policy references
    mentioned_in_policies TEXT,     -- JSON array of policy_document_ids
    first_mentioned_date TEXT,

    description TEXT,
    created_at TEXT NOT NULL
);

-- ==============================================================================
-- IX. VIEWS FOR COMMON QUERIES
-- ==============================================================================

-- View: All 14th Five Year Plan content
CREATE VIEW IF NOT EXISTS view_14th_fyp AS
SELECT
    d.document_id,
    d.title_english,
    d.document_type,
    d.publication_date,
    d.strategic_objectives,
    d.technology_priorities,
    d.investment_commitments,
    c.chapter_title_english,
    c.key_objectives
FROM chinese_policy_documents d
LEFT JOIN five_year_plan_chapters c ON d.document_id = c.parent_document_id
WHERE d.document_type LIKE 'fyp_%'
  AND d.title_english LIKE '%14th%'
ORDER BY d.publication_date, c.chapter_number;

-- View: MCF entities and their policy mandates
CREATE VIEW IF NOT EXISTS view_mcf_entity_mandates AS
SELECT
    m.entity_name_english,
    m.designation_type,
    m.designation_date,
    p.title_english as policy_title,
    pm.mandate_type,
    pm.mandate_description,
    pm.funding_amount_usd
FROM mcf_designated_entities m
LEFT JOIN policy_entity_mandates pm ON m.entity_id = pm.entity_id
LEFT JOIN chinese_policy_documents p ON pm.policy_document_id = p.document_id
ORDER BY m.designation_date DESC;

-- View: China-Europe policy competition by technology
CREATE VIEW IF NOT EXISTS view_china_europe_tech_competition AS
SELECT
    pi.technology_domain,
    cp.title_english as chinese_policy,
    cp.publication_date as chinese_date,
    cp.investment_commitments as chinese_investment,
    ep.document_title as european_policy,
    ep.publication_date as european_date,
    pi.foreign_investment_usd as european_investment,
    pi.days_between,
    pi.interaction_type
FROM policy_interactions pi
JOIN chinese_policy_documents cp ON pi.chinese_policy_id = cp.document_id
JOIN policy_documents ep ON pi.foreign_policy_id = ep.document_id
WHERE pi.technology_domain IS NOT NULL
ORDER BY pi.technology_domain, cp.publication_date;

-- ==============================================================================
-- X. MIGRATION NOTES
-- ==============================================================================

-- The existing mcf_documents table (26 records) should be:
-- 1. Reviewed for primary vs. secondary sources
-- 2. Primary Chinese documents → migrated to chinese_policy_documents
-- 3. Western analysis (USCC, ASPI) → migrated to chinese_policy_analysis
-- 4. Source tracking → populate chinese_policy_sources

-- Empty tables to be retired after migration:
-- - mcf_document_entities → policy_entity_mandates (this schema)
-- - mcf_document_technologies → policy_technology_priorities (this schema)
-- - mcf_sources → chinese_policy_sources (this schema)
-- - mcf_technologies → mcf_technology_taxonomy (this schema)

-- ==============================================================================
-- SCHEMA COMPLETE - READY FOR ETL IMPLEMENTATION
-- ==============================================================================
-- Next steps:
-- 1. Create ETL scripts to populate these tables
-- 2. Acquire Chinese policy documents (Priority 1 list from audit)
-- 3. Build cross-reference linking scripts
-- 4. Create query/analysis tools
-- ==============================================================================
