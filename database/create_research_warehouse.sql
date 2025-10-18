-- Research Data Warehouse for OSINT Foresight
-- Following playbook architecture with bronze/silver/gold layers
-- Integrates: EPO, OpenAIRE, CORDIS, TED, USPTO, SEC EDGAR, USASpending, OpenSanctions, GLEIF

-- =====================================================
-- SCHEMA CREATION
-- =====================================================

-- Raw layer (bronze) - immutable source dumps
CREATE SCHEMA IF NOT EXISTS raw_epo;
CREATE SCHEMA IF NOT EXISTS raw_openaire;
CREATE SCHEMA IF NOT EXISTS raw_cordis;
CREATE SCHEMA IF NOT EXISTS raw_ted;
CREATE SCHEMA IF NOT EXISTS raw_uspto;
CREATE SCHEMA IF NOT EXISTS raw_sec;
CREATE SCHEMA IF NOT EXISTS raw_usaspending;
CREATE SCHEMA IF NOT EXISTS raw_gleif;
CREATE SCHEMA IF NOT EXISTS raw_opensanctions;

-- Staging layer (silver) - typed/cleaned per-source
CREATE SCHEMA IF NOT EXISTS stage_epo;
CREATE SCHEMA IF NOT EXISTS stage_openaire;
CREATE SCHEMA IF NOT EXISTS stage_cordis;
CREATE SCHEMA IF NOT EXISTS stage_ted;
CREATE SCHEMA IF NOT EXISTS stage_uspto;
CREATE SCHEMA IF NOT EXISTS stage_sec;
CREATE SCHEMA IF NOT EXISTS stage_usaspending;
CREATE SCHEMA IF NOT EXISTS stage_gleif;
CREATE SCHEMA IF NOT EXISTS stage_opensanctions;

-- Core layer (gold) - conformed model
CREATE SCHEMA IF NOT EXISTS core;

-- Mart layer - analyst-friendly views
CREATE SCHEMA IF NOT EXISTS marts_china;
CREATE SCHEMA IF NOT EXISTS marts_risk;
CREATE SCHEMA IF NOT EXISTS marts_supply;
CREATE SCHEMA IF NOT EXISTS marts_tech;
CREATE SCHEMA IF NOT EXISTS marts_exec;

-- Operations
CREATE SCHEMA IF NOT EXISTS ops;

-- =====================================================
-- CORE DIMENSIONS
-- =====================================================

-- Country dimension
CREATE TABLE IF NOT EXISTS core.dim_country (
    iso2 CHAR(2) PRIMARY KEY,
    iso3 CHAR(3) UNIQUE,
    name TEXT NOT NULL,
    region TEXT,
    is_eu BOOLEAN DEFAULT FALSE,
    is_nato BOOLEAN DEFAULT FALSE,
    is_five_eyes BOOLEAN DEFAULT FALSE,
    is_prc_aligned BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Organization dimension (universities, research institutes)
CREATE TABLE IF NOT EXISTS core.dim_org (
    ror_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    name_normalized TEXT,
    country CHAR(2) REFERENCES core.dim_country(iso2),
    org_type TEXT, -- university, research_institute, government, etc.
    is_chinese BOOLEAN DEFAULT FALSE,
    is_european BOOLEAN DEFAULT FALSE,
    risk_level TEXT, -- CRITICAL, HIGH, MEDIUM, LOW
    wikipedia_url TEXT,
    grid_id TEXT,
    isni TEXT,
    fundref_id TEXT,
    active_from DATE DEFAULT CURRENT_DATE,
    active_to DATE,
    source_system TEXT,
    retrieved_at TIMESTAMPTZ DEFAULT NOW()
);

-- Company dimension with SCD-2 for tracking changes
CREATE TABLE IF NOT EXISTS core.dim_company (
    lei TEXT NOT NULL,
    name TEXT NOT NULL,
    name_normalized TEXT,
    country CHAR(2) REFERENCES core.dim_country(iso2),
    registry_id TEXT,
    is_chinese BOOLEAN DEFAULT FALSE,
    is_european BOOLEAN DEFAULT FALSE,
    is_sanctioned BOOLEAN DEFAULT FALSE,
    risk_level TEXT,
    ultimate_parent_lei TEXT,
    active_from DATE DEFAULT CURRENT_DATE,
    active_to DATE,
    is_current BOOLEAN DEFAULT TRUE,
    source_system TEXT,
    retrieved_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY(lei, active_from)
);

-- Person dimension
CREATE TABLE IF NOT EXISTS core.dim_person (
    orcid TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    name_normalized TEXT,
    primary_org TEXT REFERENCES core.dim_org(ror_id),
    country CHAR(2) REFERENCES core.dim_country(iso2),
    h_index INTEGER,
    citation_count INTEGER,
    is_thousand_talents BOOLEAN DEFAULT FALSE,
    risk_flag BOOLEAN DEFAULT FALSE,
    source_system TEXT,
    retrieved_at TIMESTAMPTZ DEFAULT NOW()
);

-- Technology/Product dimension
CREATE TABLE IF NOT EXISTS core.dim_technology (
    tech_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT, -- AI, quantum, semiconductor, biotech, etc.
    subcategory TEXT,
    is_critical BOOLEAN DEFAULT FALSE,
    is_dual_use BOOLEAN DEFAULT FALSE,
    export_control_level TEXT,
    hs6 TEXT,
    cpc_codes TEXT[],
    ipc_codes TEXT[],
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Place dimension
CREATE TABLE IF NOT EXISTS core.dim_place (
    un_locode TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    country CHAR(2) REFERENCES core.dim_country(iso2),
    lat NUMERIC(9,6),
    lon NUMERIC(9,6),
    place_type TEXT, -- port, airport, city, etc.
    alt_names TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sanctions lists dimension
CREATE TABLE IF NOT EXISTS core.dim_sanction_list (
    list_id TEXT PRIMARY KEY,
    source TEXT NOT NULL, -- OFAC, EU, UN, etc.
    label TEXT,
    list_type TEXT,
    updated_at TIMESTAMPTZ,
    url TEXT
);

-- =====================================================
-- CROSSWALKS AND RELATIONSHIPS
-- =====================================================

-- Organization to company mapping
CREATE TABLE IF NOT EXISTS core.x_org_company (
    ror_id TEXT REFERENCES core.dim_org(ror_id),
    lei TEXT,
    confidence NUMERIC(3,2),
    source TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY(ror_id, lei)
);

-- Ownership relationships (company hierarchy)
CREATE TABLE IF NOT EXISTS core.edge_ownership (
    child_lei TEXT NOT NULL,
    parent_lei TEXT NOT NULL,
    pct NUMERIC(5,2),
    rel_type TEXT, -- direct, ultimate, JV, subsidiary
    valid_from DATE NOT NULL,
    valid_to DATE,
    source_system TEXT,
    PRIMARY KEY(child_lei, parent_lei, valid_from)
);

-- Collaboration network
CREATE TABLE IF NOT EXISTS core.edge_collaboration (
    entity1_id TEXT NOT NULL,
    entity1_type TEXT NOT NULL, -- org, company, person
    entity2_id TEXT NOT NULL,
    entity2_type TEXT NOT NULL,
    collaboration_type TEXT, -- research, patent, commercial, funding
    strength NUMERIC(5,2),
    first_collab DATE,
    last_collab DATE,
    total_collabs INTEGER DEFAULT 1,
    is_china_related BOOLEAN DEFAULT FALSE,
    PRIMARY KEY(entity1_id, entity1_type, entity2_id, entity2_type)
);

-- Sanctions hits
CREATE TABLE IF NOT EXISTS core.hit_sanction (
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    list_id TEXT REFERENCES core.dim_sanction_list(list_id),
    match_score NUMERIC(3,2),
    effective_from DATE,
    effective_to DATE,
    reason TEXT,
    PRIMARY KEY(entity_type, entity_id, list_id, effective_from)
);

-- =====================================================
-- FACT TABLES
-- =====================================================

-- Patent facts
CREATE TABLE IF NOT EXISTS core.f_patent (
    app_id TEXT PRIMARY KEY,
    family_id TEXT,
    title TEXT,
    abstract TEXT,
    ipc_codes TEXT[],
    cpc_codes TEXT[],
    applicant_lei TEXT,
    applicant_ror TEXT,
    applicant_name TEXT,
    inventor_orcids TEXT[],
    filing_date DATE,
    grant_date DATE,
    priority_date DATE,
    publication_date DATE,
    status TEXT,
    kind TEXT,
    country CHAR(2),
    is_china_related BOOLEAN DEFAULT FALSE,
    tech_category TEXT,
    citation_count INTEGER DEFAULT 0,
    family_size INTEGER DEFAULT 1,
    -- Provenance
    source_system TEXT,
    source_url TEXT,
    retrieved_at TIMESTAMPTZ DEFAULT NOW(),
    sha256 TEXT
);

-- Research publication facts
CREATE TABLE IF NOT EXISTS core.f_publication (
    pub_id TEXT PRIMARY KEY,
    doi TEXT UNIQUE,
    title TEXT NOT NULL,
    abstract TEXT,
    authors TEXT[],
    author_orcids TEXT[],
    affiliations TEXT[],
    affiliation_rors TEXT[],
    publication_date DATE,
    journal TEXT,
    conference TEXT,
    keywords TEXT[],
    field_of_study TEXT,
    citation_count INTEGER DEFAULT 0,
    is_open_access BOOLEAN DEFAULT FALSE,
    is_china_collab BOOLEAN DEFAULT FALSE,
    china_author_count INTEGER DEFAULT 0,
    eu_author_count INTEGER DEFAULT 0,
    -- Provenance
    source_system TEXT,
    source_url TEXT,
    retrieved_at TIMESTAMPTZ DEFAULT NOW(),
    sha256 TEXT
);

-- Procurement/contract facts
CREATE TABLE IF NOT EXISTS core.f_procurement_award (
    award_id TEXT PRIMARY KEY,
    buyer_ror TEXT,
    buyer_name TEXT,
    buyer_country CHAR(2),
    vendor_lei TEXT,
    vendor_name TEXT,
    vendor_country CHAR(2),
    cpv TEXT,
    title TEXT,
    description TEXT,
    award_date DATE,
    start_date DATE,
    end_date DATE,
    value NUMERIC,
    currency CHAR(3),
    delivery_locode TEXT,
    is_framework BOOLEAN DEFAULT FALSE,
    is_china_related BOOLEAN DEFAULT FALSE,
    risk_score NUMERIC(3,2),
    -- Provenance
    source_system TEXT,
    source_url TEXT,
    retrieved_at TIMESTAMPTZ DEFAULT NOW(),
    sha256 TEXT
);

-- Grant/funding facts
CREATE TABLE IF NOT EXISTS core.f_grant (
    grant_id TEXT PRIMARY KEY,
    funder_ror TEXT,
    funder_name TEXT,
    recipient_ror TEXT,
    recipient_name TEXT,
    pi_orcid TEXT,
    pi_name TEXT,
    call_id TEXT,
    program TEXT,
    title TEXT,
    abstract TEXT,
    amount NUMERIC,
    currency CHAR(3),
    start_date DATE,
    end_date DATE,
    keywords TEXT[],
    tech_areas TEXT[],
    is_china_collab BOOLEAN DEFAULT FALSE,
    -- Provenance
    source_system TEXT,
    source_url TEXT,
    retrieved_at TIMESTAMPTZ DEFAULT NOW(),
    sha256 TEXT
);

-- Standards participation facts
CREATE TABLE IF NOT EXISTS core.f_standard (
    event_id TEXT PRIMARY KEY,
    std_body TEXT,
    working_group TEXT,
    doc_id TEXT,
    org_ror TEXT,
    person_orcid TEXT,
    person_name TEXT,
    role TEXT,
    contribution_date DATE,
    standard_name TEXT,
    tech_area TEXT,
    is_china_participant BOOLEAN DEFAULT FALSE,
    -- Provenance
    source_system TEXT,
    retrieved_at TIMESTAMPTZ DEFAULT NOW()
);

-- Investment/M&A facts
CREATE TABLE IF NOT EXISTS core.f_investment (
    deal_id TEXT PRIMARY KEY,
    investor_lei TEXT,
    investor_name TEXT,
    target_lei TEXT,
    target_name TEXT,
    deal_type TEXT, -- acquisition, minority, JV, etc.
    amount NUMERIC,
    currency CHAR(3),
    stake_pct NUMERIC(5,2),
    announcement_date DATE,
    close_date DATE,
    tech_sector TEXT,
    is_china_investor BOOLEAN DEFAULT FALSE,
    cfius_review BOOLEAN DEFAULT FALSE,
    -- Provenance
    source_system TEXT,
    source_url TEXT,
    retrieved_at TIMESTAMPTZ DEFAULT NOW()
);

-- Intelligence events (alerts, discoveries)
CREATE TABLE IF NOT EXISTS core.f_intelligence_event (
    event_id TEXT PRIMARY KEY,
    event_type TEXT, -- discovery, alert, anomaly, etc.
    severity TEXT, -- CRITICAL, HIGH, MEDIUM, LOW
    title TEXT,
    description TEXT,
    entities_involved TEXT[],
    detected_date DATE,
    confidence_score NUMERIC(3,2),
    false_positive BOOLEAN DEFAULT FALSE,
    analyst_notes TEXT,
    -- Provenance
    source_system TEXT,
    detection_method TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- OPERATIONS TABLES
-- =====================================================

-- Load tracking
CREATE TABLE IF NOT EXISTS ops.load_log (
    load_id SERIAL PRIMARY KEY,
    dataset TEXT NOT NULL,
    file_path TEXT,
    file_hash TEXT,
    row_count INTEGER,
    loaded_at TIMESTAMPTZ DEFAULT NOW(),
    load_duration_seconds INTEGER,
    status TEXT,
    error_message TEXT,
    loaded_by TEXT DEFAULT CURRENT_USER
);

-- Entity resolution matches
CREATE TABLE IF NOT EXISTS ops.entity_matches (
    match_id SERIAL PRIMARY KEY,
    entity_type TEXT NOT NULL,
    name_raw TEXT NOT NULL,
    matched_id TEXT,
    match_score NUMERIC(3,2),
    match_method TEXT,
    decided_by TEXT,
    decided_at TIMESTAMPTZ DEFAULT NOW(),
    is_verified BOOLEAN DEFAULT FALSE,
    notes TEXT,
    UNIQUE(entity_type, name_raw)
);

-- Manual verifications
CREATE TABLE IF NOT EXISTS ops.manual_checks (
    check_id SERIAL PRIMARY KEY,
    entity_type TEXT,
    entity_id TEXT,
    check_type TEXT,
    source TEXT,
    result TEXT,
    checked_by TEXT,
    checked_at TIMESTAMPTZ DEFAULT NOW(),
    evidence_url TEXT,
    notes TEXT
);

-- Policy and terms tracking
CREATE TABLE IF NOT EXISTS ops.policy_notes (
    source TEXT PRIMARY KEY,
    tos_url TEXT,
    allowed_use TEXT,
    restrictions TEXT,
    requires_attribution BOOLEAN DEFAULT TRUE,
    last_reviewed TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Company indexes
CREATE INDEX IF NOT EXISTS idx_company_country ON core.dim_company(country) WHERE is_current = TRUE;
CREATE INDEX IF NOT EXISTS idx_company_chinese ON core.dim_company(is_chinese) WHERE is_current = TRUE;
CREATE INDEX IF NOT EXISTS idx_company_parent ON core.dim_company(ultimate_parent_lei) WHERE is_current = TRUE;

-- Organization indexes
CREATE INDEX IF NOT EXISTS idx_org_country ON core.dim_org(country);
CREATE INDEX IF NOT EXISTS idx_org_chinese ON core.dim_org(is_chinese);
CREATE INDEX IF NOT EXISTS idx_org_risk ON core.dim_org(risk_level);

-- Patent indexes
CREATE INDEX IF NOT EXISTS idx_patent_filing ON core.f_patent(filing_date);
CREATE INDEX IF NOT EXISTS idx_patent_applicant_lei ON core.f_patent(applicant_lei);
CREATE INDEX IF NOT EXISTS idx_patent_applicant_ror ON core.f_patent(applicant_ror);
CREATE INDEX IF NOT EXISTS idx_patent_china ON core.f_patent(is_china_related);
CREATE INDEX IF NOT EXISTS idx_patent_tech ON core.f_patent(tech_category);

-- Publication indexes
CREATE INDEX IF NOT EXISTS idx_pub_date ON core.f_publication(publication_date);
CREATE INDEX IF NOT EXISTS idx_pub_china ON core.f_publication(is_china_collab);
CREATE INDEX IF NOT EXISTS idx_pub_field ON core.f_publication(field_of_study);

-- Procurement indexes
CREATE INDEX IF NOT EXISTS idx_proc_date ON core.f_procurement_award(award_date);
CREATE INDEX IF NOT EXISTS idx_proc_vendor ON core.f_procurement_award(vendor_lei);
CREATE INDEX IF NOT EXISTS idx_proc_buyer ON core.f_procurement_award(buyer_ror);
CREATE INDEX IF NOT EXISTS idx_proc_china ON core.f_procurement_award(is_china_related);

-- Collaboration indexes
CREATE INDEX IF NOT EXISTS idx_collab_china ON core.edge_collaboration(is_china_related);
CREATE INDEX IF NOT EXISTS idx_collab_entity1 ON core.edge_collaboration(entity1_id, entity1_type);
CREATE INDEX IF NOT EXISTS idx_collab_entity2 ON core.edge_collaboration(entity2_id, entity2_type);

-- =====================================================
-- MATERIALIZED VIEWS FOR ANALYSIS
-- =====================================================

-- China exposure by vendor
CREATE MATERIALIZED VIEW IF NOT EXISTS marts_china.mv_vendor_exposure AS
SELECT
    c.lei,
    c.name,
    c.country,
    c.ultimate_parent_lei,
    COUNT(DISTINCT p.award_id) as total_awards,
    SUM(p.value) as total_value,
    COUNT(DISTINCT p.award_id) FILTER (WHERE p.is_china_related) as china_awards,
    SUM(p.value) FILTER (WHERE p.is_china_related) as china_value,
    BOOL_OR(c.is_chinese) as is_chinese_entity,
    BOOL_OR(s.entity_id IS NOT NULL) as is_sanctioned,
    MAX(p.award_date) as latest_award
FROM core.dim_company c
LEFT JOIN core.f_procurement_award p ON p.vendor_lei = c.lei
LEFT JOIN core.hit_sanction s ON s.entity_id = c.lei AND s.entity_type = 'company'
WHERE c.is_current = TRUE
GROUP BY c.lei, c.name, c.country, c.ultimate_parent_lei;

CREATE INDEX IF NOT EXISTS idx_mv_vendor_lei ON marts_china.mv_vendor_exposure(lei);
CREATE INDEX IF NOT EXISTS idx_mv_vendor_chinese ON marts_china.mv_vendor_exposure(is_chinese_entity);

-- China research collaboration network
CREATE MATERIALIZED VIEW IF NOT EXISTS marts_china.mv_research_network AS
SELECT
    o.ror_id,
    o.name as org_name,
    o.country,
    o.org_type,
    COUNT(DISTINCT p.pub_id) as total_pubs,
    COUNT(DISTINCT p.pub_id) FILTER (WHERE p.is_china_collab) as china_collabs,
    AVG(p.china_author_count) FILTER (WHERE p.is_china_collab) as avg_china_authors,
    ARRAY_AGG(DISTINCT p.field_of_study) FILTER (WHERE p.is_china_collab) as china_collab_fields,
    MAX(p.publication_date) FILTER (WHERE p.is_china_collab) as latest_china_collab
FROM core.dim_org o
JOIN core.f_publication p ON o.ror_id = ANY(p.affiliation_rors)
GROUP BY o.ror_id, o.name, o.country, o.org_type
HAVING COUNT(DISTINCT p.pub_id) FILTER (WHERE p.is_china_collab) > 0;

CREATE INDEX IF NOT EXISTS idx_mv_research_ror ON marts_china.mv_research_network(ror_id);
CREATE INDEX IF NOT EXISTS idx_mv_research_collabs ON marts_china.mv_research_network(china_collabs DESC);

-- Technology transfer risk assessment
CREATE MATERIALIZED VIEW IF NOT EXISTS marts_risk.mv_tech_transfer_risk AS
WITH patent_risk AS (
    SELECT
        applicant_ror as entity_id,
        'org' as entity_type,
        COUNT(*) as patent_count,
        COUNT(*) FILTER (WHERE is_china_related) as china_patents,
        ARRAY_AGG(DISTINCT tech_category) as tech_areas
    FROM core.f_patent
    WHERE filing_date >= CURRENT_DATE - INTERVAL '3 years'
    GROUP BY applicant_ror
),
pub_risk AS (
    SELECT
        unnest(affiliation_rors) as entity_id,
        COUNT(*) as pub_count,
        COUNT(*) FILTER (WHERE is_china_collab) as china_pubs
    FROM core.f_publication
    WHERE publication_date >= CURRENT_DATE - INTERVAL '3 years'
    GROUP BY entity_id
)
SELECT
    COALESCE(pt.entity_id, pb.entity_id) as entity_id,
    o.name,
    o.country,
    COALESCE(pt.patent_count, 0) as recent_patents,
    COALESCE(pt.china_patents, 0) as china_patents,
    COALESCE(pb.pub_count, 0) as recent_pubs,
    COALESCE(pb.china_pubs, 0) as china_pubs,
    pt.tech_areas,
    CASE
        WHEN COALESCE(pt.china_patents, 0) > 10 OR COALESCE(pb.china_pubs, 0) > 50 THEN 'CRITICAL'
        WHEN COALESCE(pt.china_patents, 0) > 5 OR COALESCE(pb.china_pubs, 0) > 20 THEN 'HIGH'
        WHEN COALESCE(pt.china_patents, 0) > 0 OR COALESCE(pb.china_pubs, 0) > 10 THEN 'MEDIUM'
        ELSE 'LOW'
    END as risk_level
FROM patent_risk pt
FULL OUTER JOIN pub_risk pb ON pt.entity_id = pb.entity_id
LEFT JOIN core.dim_org o ON o.ror_id = COALESCE(pt.entity_id, pb.entity_id);

-- =====================================================
-- UTILITY FUNCTIONS
-- =====================================================

-- Get ultimate parent company
CREATE OR REPLACE FUNCTION core.get_ultimate_parent(p_lei TEXT)
RETURNS TABLE(lei TEXT, name TEXT, country CHAR(2))
LANGUAGE SQL AS $$
    WITH RECURSIVE ownership_chain AS (
        SELECT c.lei, c.name, c.country, e.parent_lei, 1 as depth
        FROM core.dim_company c
        LEFT JOIN core.edge_ownership e ON e.child_lei = c.lei
            AND NOW() BETWEEN e.valid_from AND COALESCE(e.valid_to, 'infinity'::DATE)
        WHERE c.lei = p_lei AND c.is_current = TRUE

        UNION ALL

        SELECT c2.lei, c2.name, c2.country, e2.parent_lei, depth + 1
        FROM ownership_chain oc
        JOIN core.edge_ownership e2 ON e2.child_lei = oc.parent_lei
            AND NOW() BETWEEN e2.valid_from AND COALESCE(e2.valid_to, 'infinity'::DATE)
        JOIN core.dim_company c2 ON c2.lei = e2.child_lei AND c2.is_current = TRUE
        WHERE depth < 10 -- Prevent infinite loops
    )
    SELECT lei, name, country
    FROM ownership_chain
    ORDER BY depth DESC
    LIMIT 1;
$$;

-- Check if entity has China connection
CREATE OR REPLACE FUNCTION core.has_china_connection(
    p_entity_id TEXT,
    p_entity_type TEXT
)
RETURNS BOOLEAN
LANGUAGE SQL AS $$
    SELECT EXISTS (
        SELECT 1
        FROM core.edge_collaboration
        WHERE (entity1_id = p_entity_id AND entity1_type = p_entity_type)
           OR (entity2_id = p_entity_id AND entity2_type = p_entity_type)
        AND is_china_related = TRUE
    );
$$;

-- =====================================================
-- AUDIT TRIGGERS
-- =====================================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION core.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update timestamp to key tables
CREATE TRIGGER update_company_timestamp BEFORE UPDATE ON core.dim_company
    FOR EACH ROW EXECUTE FUNCTION core.update_timestamp();

CREATE TRIGGER update_org_timestamp BEFORE UPDATE ON core.dim_org
    FOR EACH ROW EXECUTE FUNCTION core.update_timestamp();

-- =====================================================
-- INITIAL DATA LOADS
-- =====================================================

-- Load critical countries
INSERT INTO core.dim_country (iso2, iso3, name, is_eu, is_nato, is_prc_aligned) VALUES
('CN', 'CHN', 'China', FALSE, FALSE, TRUE),
('US', 'USA', 'United States', FALSE, TRUE, FALSE),
('DE', 'DEU', 'Germany', TRUE, TRUE, FALSE),
('FR', 'FRA', 'France', TRUE, TRUE, FALSE),
('IT', 'ITA', 'Italy', TRUE, TRUE, FALSE),
('GB', 'GBR', 'United Kingdom', FALSE, TRUE, FALSE),
('NL', 'NLD', 'Netherlands', TRUE, TRUE, FALSE),
('ES', 'ESP', 'Spain', TRUE, TRUE, FALSE),
('PL', 'POL', 'Poland', TRUE, TRUE, FALSE),
('SE', 'SWE', 'Sweden', TRUE, FALSE, FALSE),
('RU', 'RUS', 'Russia', FALSE, FALSE, TRUE),
('KP', 'PRK', 'North Korea', FALSE, FALSE, TRUE),
('IR', 'IRN', 'Iran', FALSE, FALSE, TRUE)
ON CONFLICT (iso2) DO NOTHING;

-- Load critical technology categories
INSERT INTO core.dim_technology (tech_id, name, category, is_critical, is_dual_use) VALUES
('AI_ML', 'Artificial Intelligence & Machine Learning', 'AI', TRUE, TRUE),
('QUANTUM', 'Quantum Computing', 'Computing', TRUE, TRUE),
('SEMICONDUCTOR', 'Semiconductors & Microelectronics', 'Electronics', TRUE, TRUE),
('5G_6G', '5G/6G Communications', 'Telecommunications', TRUE, TRUE),
('HYPERSONIC', 'Hypersonic Systems', 'Aerospace', TRUE, TRUE),
('BIOTECH', 'Biotechnology & Synthetic Biology', 'Biology', TRUE, TRUE),
('NUCLEAR', 'Nuclear Technology', 'Energy', TRUE, TRUE),
('CYBER', 'Cybersecurity & Encryption', 'Computing', TRUE, TRUE),
('SPACE', 'Space Technology', 'Aerospace', TRUE, TRUE),
('AUTONOMOUS', 'Autonomous Systems & Robotics', 'AI', TRUE, TRUE)
ON CONFLICT (tech_id) DO NOTHING;

-- =====================================================
-- GRANT PERMISSIONS (adjust for your environment)
-- =====================================================

-- GRANT USAGE ON SCHEMA core TO analyst_role;
-- GRANT SELECT ON ALL TABLES IN SCHEMA core TO analyst_role;
-- GRANT SELECT ON ALL TABLES IN SCHEMA marts_china TO analyst_role;
-- GRANT SELECT ON ALL TABLES IN SCHEMA marts_risk TO analyst_role;

-- =====================================================
-- FINAL SETUP MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE 'Research Data Warehouse created successfully!';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Run data import scripts for each source';
    RAISE NOTICE '2. Execute entity resolution procedures';
    RAISE NOTICE '3. Refresh materialized views';
    RAISE NOTICE '4. Verify crosswalks and relationships';
END $$;
