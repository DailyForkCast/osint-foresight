-- Semiconductor Data Integration Schema
-- Purpose: Integrate WSTS market data, SIA industry metrics, and comprehensive taxonomy
-- Database: osint_master.db (F:/OSINT_WAREHOUSE/)
-- Created: 2025-11-02
-- Zero Fabrication Protocol: All data sourced from verified reports

-- ============================================================================
-- 1. SEMICONDUCTOR MARKET DATA (WSTS)
-- ============================================================================

-- Historical billings data from WSTS (1986-2025)
CREATE TABLE IF NOT EXISTS semiconductor_market_billings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    region TEXT NOT NULL, -- 'Americas', 'Europe', 'Japan', 'Asia Pacific', 'Worldwide'

    -- Monthly data (USD thousands)
    january REAL,
    february REAL,
    march REAL,
    april REAL,
    may REAL,
    june REAL,
    july REAL,
    august REAL,
    september REAL,
    october REAL,
    november REAL,
    december REAL,

    -- Quarterly data (USD thousands)
    q1 REAL,
    q2 REAL,
    q3 REAL,
    q4 REAL,

    -- Annual total (USD thousands)
    total_year REAL,

    -- Metadata
    source TEXT DEFAULT 'WSTS-Historical-Billings-Report-Aug2025.xlsx',
    data_type TEXT DEFAULT 'actual', -- 'actual' or '3mma' (3-month moving average)
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(year, region, data_type)
);

-- Index for time-series queries
CREATE INDEX IF NOT EXISTS idx_billings_year_region ON semiconductor_market_billings(year, region);
CREATE INDEX IF NOT EXISTS idx_billings_region_year ON semiconductor_market_billings(region, year);

-- ============================================================================
-- 2. SIA INDUSTRY METRICS
-- ============================================================================

-- US semiconductor industry metrics from SIA
CREATE TABLE IF NOT EXISTS semiconductor_industry_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    metric_category TEXT NOT NULL, -- 'market', 'rd', 'employment', 'manufacturing', etc.
    metric_name TEXT NOT NULL,
    metric_value REAL,
    metric_unit TEXT, -- 'USD billions', 'percent', 'count', etc.
    metric_description TEXT,

    -- Metadata
    source TEXT DEFAULT 'SIA-State-of-the-Industry-Report-2025.pdf',
    source_page TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(year, metric_category, metric_name)
);

-- Index for metric queries
CREATE INDEX IF NOT EXISTS idx_metrics_year_category ON semiconductor_industry_metrics(year, metric_category);

-- ============================================================================
-- 3. MARKET SEGMENTS
-- ============================================================================

-- Semiconductor market segments (Computing/AI, Communications, Automotive, etc.)
CREATE TABLE IF NOT EXISTS semiconductor_market_segments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    segment_name TEXT NOT NULL, -- 'computing_ai', 'communications', 'automotive', etc.
    market_share REAL, -- Percentage
    segment_description TEXT,

    -- Metadata
    source TEXT DEFAULT 'SIA-State-of-the-Industry-Report-2025.pdf',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(year, segment_name)
);

-- ============================================================================
-- 4. SUPPLY CHAIN VALUE ADDED (REGIONAL)
-- ============================================================================

-- Regional contributions to semiconductor value chain
CREATE TABLE IF NOT EXISTS semiconductor_supply_chain_regional (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    region TEXT NOT NULL, -- 'united_states', 'china', 'taiwan', 'south_korea', 'japan', 'europe'
    value_chain_stage TEXT NOT NULL, -- 'design', 'manufacturing', 'equipment', 'materials'
    percentage REAL, -- Percentage contribution

    -- Metadata
    source TEXT DEFAULT 'SIA-State-of-the-Industry-Report-2025.pdf',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(year, region, value_chain_stage)
);

-- Index for supply chain queries
CREATE INDEX IF NOT EXISTS idx_supply_chain_region ON semiconductor_supply_chain_regional(region, value_chain_stage);

-- ============================================================================
-- 5. TECHNOLOGY TAXONOMY
-- ============================================================================

-- Comprehensive technology taxonomy (technologies, sub-technologies, applications)
CREATE TABLE IF NOT EXISTS semiconductor_technology_taxonomy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL, -- 'upstream', 'core_manufacturing', 'downstream', 'equipment', 'research'
    subcategory TEXT, -- e.g., 'critical_minerals', 'process_nodes', 'computing_ai'
    technology_name TEXT NOT NULL,
    technology_description TEXT,

    -- Attributes (JSON for flexibility)
    attributes TEXT, -- JSON: supply_chain_risk, market_share, strategic_importance, etc.

    -- Metadata
    source TEXT DEFAULT 'semiconductor_comprehensive_taxonomy.json',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(category, subcategory, technology_name)
);

-- Index for taxonomy queries
CREATE INDEX IF NOT EXISTS idx_taxonomy_category ON semiconductor_technology_taxonomy(category, subcategory);

-- ============================================================================
-- 6. CRITICAL MINERALS
-- ============================================================================

-- Critical minerals for semiconductor manufacturing
CREATE TABLE IF NOT EXISTS semiconductor_critical_minerals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mineral_name TEXT NOT NULL UNIQUE,
    mineral_description TEXT,
    primary_use TEXT, -- e.g., 'gallium arsenide substrates', 'EUV lithography'

    -- Supply chain risk
    supply_chain_risk TEXT, -- 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    primary_suppliers TEXT, -- JSON array of countries
    china_market_share REAL, -- Percentage if China dominates supply

    -- Strategic importance
    strategic_importance TEXT, -- 'CRITICAL', 'HIGH', 'MEDIUM'
    substitution_difficulty TEXT, -- 'Very difficult', 'Difficult', 'Possible'

    -- Metadata
    source TEXT DEFAULT 'semiconductor_comprehensive_taxonomy.json',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 7. EQUIPMENT SUPPLIERS
-- ============================================================================

-- Semiconductor equipment suppliers and market shares
CREATE TABLE IF NOT EXISTS semiconductor_equipment_suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_type TEXT NOT NULL, -- 'lithography', 'deposition', 'etch', etc.
    supplier_name TEXT NOT NULL,
    supplier_country TEXT,
    market_share REAL, -- Percentage
    technology_focus TEXT, -- e.g., 'EUV monopoly', 'PECVD leader'

    -- Strategic importance
    strategic_importance TEXT, -- 'CRITICAL', 'HIGH', 'MEDIUM'

    -- Metadata
    source TEXT DEFAULT 'semiconductor_comprehensive_taxonomy.json',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(equipment_type, supplier_name)
);

-- Index for equipment queries
CREATE INDEX IF NOT EXISTS idx_equipment_type ON semiconductor_equipment_suppliers(equipment_type);

-- ============================================================================
-- 8. RESEARCH AREAS
-- ============================================================================

-- Semiconductor research focus areas
CREATE TABLE IF NOT EXISTS semiconductor_research_areas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    research_area TEXT NOT NULL UNIQUE,
    description TEXT,
    subcategories TEXT, -- JSON array of sub-areas

    -- Strategic importance
    strategic_importance TEXT, -- 'CRITICAL', 'HIGH', 'MEDIUM'
    timeframe TEXT, -- '2-5 years', '5-10 years', '10+ years'

    -- Key players
    leading_countries TEXT, -- JSON array
    leading_companies TEXT, -- JSON array

    -- Metadata
    source TEXT DEFAULT 'semiconductor_comprehensive_taxonomy.json',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 9. GEOPOLITICAL FACTORS (CHIPS ACT, EXPORT CONTROLS)
-- ============================================================================

-- Policy and geopolitical factors affecting semiconductor industry
CREATE TABLE IF NOT EXISTS semiconductor_geopolitical_factors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    factor_type TEXT NOT NULL, -- 'policy', 'export_control', 'investment', 'strategic_initiative'
    factor_name TEXT NOT NULL,
    description TEXT,

    -- Financial impact
    funding_amount REAL, -- USD billions if applicable
    funding_breakdown TEXT, -- JSON if multiple components

    -- Geographic scope
    countries_affected TEXT, -- JSON array

    -- Metadata
    source TEXT DEFAULT 'SIA-State-of-the-Industry-Report-2025.pdf',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(year, factor_type, factor_name)
);

-- ============================================================================
-- 10. INTEGRATION WITH EXISTING ETO TABLES
-- ============================================================================

-- Link table to connect new taxonomy with existing ETO semiconductor tables
CREATE TABLE IF NOT EXISTS semiconductor_eto_taxonomy_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    taxonomy_id INTEGER,
    eto_table TEXT, -- 'eto_semiconductor_inputs', 'eto_semiconductor_providers', etc.
    eto_record_id INTEGER,
    link_type TEXT, -- 'material', 'equipment', 'process', 'supplier'

    -- Metadata
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (taxonomy_id) REFERENCES semiconductor_technology_taxonomy(id),
    UNIQUE(taxonomy_id, eto_table, eto_record_id)
);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Latest market data by region
CREATE VIEW IF NOT EXISTS v_semiconductor_market_latest AS
SELECT
    year,
    region,
    total_year,
    q1, q2, q3, q4
FROM semiconductor_market_billings
WHERE data_type = 'actual'
ORDER BY year DESC,
    CASE region
        WHEN 'Worldwide' THEN 1
        WHEN 'Asia Pacific' THEN 2
        WHEN 'Americas' THEN 3
        WHEN 'Europe' THEN 4
        WHEN 'Japan' THEN 5
    END;

-- View: US market metrics summary
CREATE VIEW IF NOT EXISTS v_us_semiconductor_metrics AS
SELECT
    year,
    metric_category,
    metric_name,
    metric_value,
    metric_unit,
    metric_description
FROM semiconductor_industry_metrics
ORDER BY year DESC, metric_category, metric_name;

-- View: Critical supply chain risks
CREATE VIEW IF NOT EXISTS v_critical_supply_chain_risks AS
SELECT
    mineral_name,
    primary_use,
    supply_chain_risk,
    primary_suppliers,
    china_market_share,
    strategic_importance
FROM semiconductor_critical_minerals
WHERE supply_chain_risk IN ('CRITICAL', 'HIGH')
ORDER BY
    CASE supply_chain_risk
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH' THEN 2
    END,
    mineral_name;

-- ============================================================================
-- COMMENTS AND DOCUMENTATION
-- ============================================================================

-- Schema Notes:
-- 1. All tables include source attribution for Zero Fabrication Protocol compliance
-- 2. Uses JSON fields for flexible attribute storage where appropriate
-- 3. Indexes created on frequently queried columns for performance
-- 4. Views created for common analytical queries
-- 5. Integration points with existing ETO tables via link table
-- 6. Time-series data (WSTS) optimized for temporal queries
-- 7. Taxonomy structure supports hierarchical categorization
-- 8. Supply chain risk assessment built into critical tables
