-- ============================================================================
-- COMPREHENSIVE BILATERAL RELATIONS DATABASE SCHEMA
-- ============================================================================
-- Purpose: Track multi-dimensional China bilateral relationships across 81 countries
-- Coverage: Diplomatic, Economic, Cultural, Academic, Security, Infrastructure
-- Created: 2025-10-22
-- Version: 1.0
-- ============================================================================

-- ============================================================================
-- CORE TABLES: Foundational bilateral tracking
-- ============================================================================

-- Master country configuration and relationship metadata
CREATE TABLE IF NOT EXISTS bilateral_countries (
    country_code TEXT PRIMARY KEY,  -- ISO 3166-1 alpha-2 (DE, FR, IT, etc.)
    country_name TEXT NOT NULL,
    country_name_chinese TEXT,
    diplomatic_normalization_date DATE,  -- When official relations established
    current_relationship_status TEXT,  -- 'strategic_partnership', 'comprehensive_partnership', 'normal', 'strained', 'no_relations'
    relationship_tier TEXT,  -- 'tier_1_gateway', 'tier_2_high_penetration', 'tier_3_major_economy'
    bri_participation_status TEXT,  -- 'full_participant', 'partial', 'observer', 'declined', 'unclear'
    bri_mou_signed_date DATE,
    eu_member BOOLEAN DEFAULT 0,
    nato_member BOOLEAN DEFAULT 0,
    five_eyes BOOLEAN DEFAULT 0,
    notes TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Comprehensive bilateral events timeline
CREATE TABLE IF NOT EXISTS bilateral_events (
    event_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    event_date DATE NOT NULL,
    event_year INTEGER,  -- Denormalized for easy querying
    event_type TEXT NOT NULL,  -- 'diplomatic_visit', 'agreement', 'controversy', 'sanction', 'policy_shift', 'crisis', 'cooperation'
    event_category TEXT NOT NULL,  -- 'diplomatic', 'economic', 'security', 'cultural', 'technology', 'political'
    event_title TEXT NOT NULL,
    event_description TEXT,
    importance_tier INTEGER DEFAULT 3,  -- 1=critical, 2=important, 3=notable, 4=minor
    chinese_official TEXT,
    chinese_position TEXT,
    foreign_official TEXT,
    foreign_position TEXT,
    location TEXT,
    outcomes TEXT,  -- JSON array of outcomes
    agreements_signed TEXT,  -- JSON array of agreement IDs
    sentiment TEXT,  -- 'positive', 'neutral', 'negative', 'mixed'
    strategic_significance TEXT,
    source_url TEXT,
    source_type TEXT,  -- 'official_statement', 'treaty', 'news', 'academic', 'government_report'
    source_reliability INTEGER DEFAULT 3,  -- 1=primary official, 2=verified secondary, 3=credible news, 4=unverified
    verification_status TEXT DEFAULT 'unverified',  -- 'verified', 'unverified', 'disputed', 'requires_review'
    related_event_ids TEXT,  -- JSON array linking related events
    tags TEXT,  -- JSON array for flexible categorization
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- ============================================================================
-- DIPLOMATIC DIMENSION
-- ============================================================================

-- High-level diplomatic visits and meetings
CREATE TABLE IF NOT EXISTS diplomatic_visits (
    visit_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    visit_date DATE NOT NULL,
    visit_year INTEGER,
    visit_type TEXT NOT NULL,  -- 'state_visit', 'official_visit', 'working_visit', 'summit', 'ministerial', 'virtual_meeting'
    direction TEXT NOT NULL,  -- 'to_china', 'from_china', 'third_country'
    chinese_official TEXT NOT NULL,
    chinese_position TEXT NOT NULL,
    chinese_institution TEXT,
    foreign_official TEXT NOT NULL,
    foreign_position TEXT NOT NULL,
    foreign_institution TEXT,
    location_city TEXT,
    location_country TEXT,
    duration_days INTEGER,
    delegation_size INTEGER,
    visit_purpose TEXT,
    outcomes_summary TEXT,
    agreements_signed INTEGER DEFAULT 0,
    joint_statement_issued BOOLEAN DEFAULT 0,
    joint_statement_url TEXT,
    press_conference BOOLEAN DEFAULT 0,
    media_coverage_intensity TEXT,  -- 'high', 'medium', 'low'
    significance_score INTEGER,  -- 1-10 subjective assessment
    predecessor_visit_id TEXT,  -- Links to previous visit in series
    follow_up_visit_id TEXT,  -- Links to subsequent visit
    source_url TEXT,
    source_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- Diplomatic posts and consular presence
CREATE TABLE IF NOT EXISTS diplomatic_posts (
    post_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    post_type TEXT NOT NULL,  -- 'embassy', 'consulate_general', 'consulate', 'representative_office', 'trade_office'
    post_name TEXT NOT NULL,
    location_city TEXT NOT NULL,
    location_region TEXT,  -- State/province within country
    opening_date DATE,
    closure_date DATE,
    status TEXT DEFAULT 'active',  -- 'active', 'closed', 'suspended', 'planned'
    ambassador_name TEXT,
    ambassador_start_date DATE,
    staff_count INTEGER,
    consular_jurisdiction TEXT,  -- Areas/regions covered
    services_offered TEXT,  -- JSON array
    website_url TEXT,
    controversy_notes TEXT,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- Bilateral agreements, treaties, and MOUs
CREATE TABLE IF NOT EXISTS bilateral_agreements (
    agreement_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    agreement_type TEXT NOT NULL,  -- 'treaty', 'mou', 'protocol', 'joint_statement', 'strategic_partnership', 'framework_agreement'
    agreement_category TEXT NOT NULL,  -- 'trade', 'investment', 'technology', 'defense', 'cultural', 'education', 'legal', 'environmental'
    agreement_title TEXT NOT NULL,
    agreement_title_chinese TEXT,
    signing_date DATE,
    signing_location TEXT,
    entry_into_force_date DATE,
    expiration_date DATE,
    renewal_date DATE,
    status TEXT DEFAULT 'active',  -- 'active', 'expired', 'suspended', 'terminated', 'pending_ratification'
    chinese_signatory TEXT,
    chinese_signatory_position TEXT,
    foreign_signatory TEXT,
    foreign_signatory_position TEXT,
    agreement_summary TEXT,
    key_provisions TEXT,  -- JSON array
    strategic_importance TEXT,
    related_agreements TEXT,  -- JSON array of agreement_ids
    treaty_text_url TEXT,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- ============================================================================
-- ECONOMIC DIMENSION
-- ============================================================================

-- Annual bilateral trade statistics
CREATE TABLE IF NOT EXISTS bilateral_trade (
    trade_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    year INTEGER NOT NULL,
    trade_direction TEXT NOT NULL,  -- 'export_to_china', 'import_from_china', 'total_bilateral'
    trade_value_usd REAL,
    trade_value_local_currency REAL,
    currency_code TEXT,
    goods_category TEXT,  -- 'all', or specific HS code categories
    goods_category_name TEXT,
    hs_code TEXT,  -- Harmonized System code if specific
    sector TEXT,  -- 'machinery', 'electronics', 'automotive', 'chemicals', etc.
    trade_volume_quantity REAL,  -- Physical quantity if applicable
    trade_volume_unit TEXT,  -- 'tonnes', 'units', etc.
    percentage_of_total_trade REAL,  -- What % of country's total trade
    year_over_year_change REAL,  -- Percentage change from previous year
    trade_balance REAL,  -- Positive = surplus with China, negative = deficit
    source TEXT NOT NULL,  -- 'destatis', 'un_comtrade', 'wto', 'national_statistics'
    source_url TEXT,
    data_quality TEXT DEFAULT 'verified',  -- 'verified', 'estimated', 'preliminary', 'disputed'
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code),
    UNIQUE(country_code, year, trade_direction, goods_category, hs_code)
);

-- Investment flows and major transactions
CREATE TABLE IF NOT EXISTS bilateral_investments (
    investment_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    transaction_date DATE,
    announcement_date DATE,
    completion_date DATE,
    year INTEGER,
    investment_direction TEXT NOT NULL,  -- 'chinese_into_country', 'country_into_china'
    investment_type TEXT NOT NULL,  -- 'acquisition', 'merger', 'greenfield', 'brownfield', 'joint_venture', 'portfolio', 'real_estate'
    investor_entity TEXT NOT NULL,
    investor_entity_type TEXT,  -- 'soe', 'private', 'sovereign_wealth_fund', 'state_backed'
    investor_country TEXT,
    target_entity TEXT NOT NULL,
    target_entity_type TEXT,
    target_country TEXT,
    sector TEXT NOT NULL,  -- 'technology', 'manufacturing', 'energy', 'finance', 'real_estate', etc.
    subsector TEXT,
    deal_value_usd REAL,
    deal_value_reported_currency REAL,
    currency_code TEXT,
    ownership_percentage REAL,
    deal_status TEXT,  -- 'completed', 'announced', 'pending_approval', 'blocked', 'abandoned'
    government_approval_required BOOLEAN,
    government_approval_status TEXT,  -- 'approved', 'blocked', 'approved_with_conditions', 'under_review'
    blocking_reason TEXT,
    strategic_asset BOOLEAN DEFAULT 0,  -- Is target considered strategic/critical?
    technology_transfer_involved BOOLEAN DEFAULT 0,
    dual_use_concerns BOOLEAN DEFAULT 0,
    national_security_review BOOLEAN DEFAULT 0,
    jobs_created INTEGER,
    jobs_lost INTEGER,
    strategic_significance TEXT,
    controversy_notes TEXT,
    source TEXT,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- Major Chinese acquisitions of foreign companies (detailed tracking)
CREATE TABLE IF NOT EXISTS major_acquisitions (
    acquisition_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    target_company TEXT NOT NULL,
    target_sector TEXT NOT NULL,
    target_technology_area TEXT,
    chinese_acquirer TEXT NOT NULL,
    acquirer_type TEXT,  -- 'soe', 'private', 'soe_backed'
    acquisition_date DATE,
    announcement_date DATE,
    deal_value_usd REAL,
    ownership_acquired_percentage REAL,
    deal_structure TEXT,  -- 'full_acquisition', 'majority_stake', 'minority_stake', 'merger'
    financing_structure TEXT,
    strategic_rationale TEXT,
    technology_acquired TEXT,  -- Description of key tech/IP
    market_access_gained TEXT,
    employees_at_acquisition INTEGER,
    pre_acquisition_revenue_usd REAL,
    government_review_process TEXT,
    approval_conditions TEXT,
    political_controversy BOOLEAN DEFAULT 0,
    media_attention_level TEXT,  -- 'high', 'medium', 'low'
    post_acquisition_performance TEXT,
    integration_status TEXT,
    related_investments TEXT,  -- JSON array of related investment_ids
    source TEXT,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- Currency agreements and financial cooperation
CREATE TABLE IF NOT EXISTS financial_cooperation (
    cooperation_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    cooperation_type TEXT NOT NULL,  -- 'currency_swap', 'clearing_bank', 'rmb_hub', 'financial_dialogue', 'tax_treaty'
    agreement_date DATE,
    effective_date DATE,
    expiration_date DATE,
    agreement_title TEXT,
    agreement_value_usd REAL,
    agreement_value_rmb REAL,
    cooperation_details TEXT,
    institutions_involved TEXT,  -- JSON array
    strategic_purpose TEXT,
    utilization_amount REAL,  -- How much has been used
    status TEXT DEFAULT 'active',
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- ============================================================================
-- INFRASTRUCTURE & BRI DIMENSION
-- ============================================================================

-- Infrastructure projects and BRI investments
CREATE TABLE IF NOT EXISTS infrastructure_projects (
    project_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    project_name TEXT NOT NULL,
    project_type TEXT NOT NULL,  -- 'port', 'railway', 'road', 'airport', 'telecom', 'energy', 'industrial_park', 'logistics_hub'
    project_category TEXT,  -- 'transport', 'energy', 'digital', 'industrial'
    bri_affiliated BOOLEAN DEFAULT 0,
    bri_corridor TEXT,  -- Which BRI corridor/initiative
    project_location TEXT,
    project_description TEXT,
    chinese_entity TEXT,
    chinese_entity_type TEXT,  -- 'soe', 'private', 'consortium'
    local_partner_entity TEXT,
    other_partners TEXT,  -- JSON array
    announcement_date DATE,
    groundbreaking_date DATE,
    completion_date DATE,
    expected_completion_date DATE,
    project_status TEXT,  -- 'proposed', 'approved', 'under_construction', 'completed', 'suspended', 'cancelled'
    project_value_usd REAL,
    chinese_investment_usd REAL,
    financing_structure TEXT,  -- 'loan', 'grant', 'equity', 'mixed'
    lending_institution TEXT,  -- 'China Development Bank', 'AIIB', 'Silk Road Fund', etc.
    loan_terms TEXT,
    ownership_structure TEXT,
    equity_percentage REAL,
    concession_period_years INTEGER,
    strategic_importance TEXT,
    dual_use_concerns BOOLEAN DEFAULT 0,
    security_concerns TEXT,
    debt_sustainability_concerns BOOLEAN DEFAULT 0,
    environmental_concerns TEXT,
    local_opposition BOOLEAN DEFAULT 0,
    controversy_notes TEXT,
    related_projects TEXT,  -- JSON array of project_ids
    source TEXT,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- Telecom infrastructure and 5G deployment
CREATE TABLE IF NOT EXISTS telecom_infrastructure (
    deployment_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    technology TEXT NOT NULL,  -- '5g', '4g', 'fiber_optic', 'submarine_cable', 'satellite'
    chinese_vendor TEXT NOT NULL,  -- 'huawei', 'zte', 'china_mobile', 'china_telecom', etc.
    deployment_type TEXT,  -- 'network_equipment', 'core_network', 'ran', 'backhaul', 'handsets'
    deployment_scope TEXT,  -- 'nationwide', 'regional', 'urban', 'rural', 'pilot'
    carrier_operator TEXT,  -- Local telecom carrier
    announcement_date DATE,
    deployment_start_date DATE,
    deployment_status TEXT,  -- 'planned', 'deployed', 'banned', 'restricted', 'phased_out'
    contract_value_usd REAL,
    network_coverage_percentage REAL,
    ban_date DATE,
    ban_reason TEXT,
    phase_out_deadline DATE,
    replacement_vendor TEXT,
    security_concerns TEXT,
    government_decision TEXT,
    political_context TEXT,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- ============================================================================
-- CULTURAL & PEOPLE-TO-PEOPLE DIMENSION
-- ============================================================================

-- Sister city and subnational partnerships
CREATE TABLE IF NOT EXISTS sister_relationships (
    relationship_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    relationship_type TEXT NOT NULL,  -- 'sister_city', 'sister_province', 'sister_region', 'friendship_city', 'partnership_city'
    foreign_city TEXT,
    foreign_region TEXT,  -- State/province in foreign country
    chinese_city TEXT,
    chinese_province TEXT,
    establishment_date DATE,
    establishment_year INTEGER,
    agreement_renewal_date DATE,
    relationship_status TEXT DEFAULT 'active',  -- 'active', 'suspended', 'terminated', 'inactive'
    suspension_date DATE,
    suspension_reason TEXT,
    termination_date DATE,
    termination_reason TEXT,
    cooperation_areas TEXT,  -- JSON array: 'trade', 'culture', 'education', 'tourism', 'technology'
    exchange_programs TEXT,  -- Description of active programs
    annual_exchanges INTEGER,
    memorandum_url TEXT,
    managing_organization TEXT,
    controversy_notes TEXT,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- Cultural institutions (Confucius Institutes, cultural centers, etc.)
CREATE TABLE IF NOT EXISTS cultural_institutions (
    institution_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    institution_type TEXT NOT NULL,  -- 'confucius_institute', 'confucius_classroom', 'cultural_center', 'china_house', 'education_office'
    institution_name TEXT NOT NULL,
    host_institution TEXT,  -- University or organization hosting
    host_institution_type TEXT,  -- 'university', 'school', 'community_organization', 'independent'
    location_city TEXT NOT NULL,
    location_region TEXT,
    street_address TEXT,
    established_date DATE,
    established_year INTEGER,
    closure_date DATE,
    closure_year INTEGER,
    status TEXT DEFAULT 'active',  -- 'active', 'closed', 'suspended', 'rebranded'
    closure_reason TEXT,
    chinese_director TEXT,
    foreign_director TEXT,
    staff_count INTEGER,
    chinese_staff_count INTEGER,
    funding_source TEXT,  -- 'hanban', 'chinese_embassy', 'mixed', 'self_funded'
    annual_budget_usd REAL,
    students_enrolled INTEGER,
    programs_offered TEXT,  -- JSON array
    academic_freedom_concerns BOOLEAN DEFAULT 0,
    controversy_timeline TEXT,
    media_coverage TEXT,
    government_scrutiny BOOLEAN DEFAULT 0,
    rebranding_details TEXT,  -- If renamed to language center, etc.
    successor_institution TEXT,
    website_url TEXT,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- Education exchanges and student flows
CREATE TABLE IF NOT EXISTS education_exchanges (
    exchange_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    year INTEGER NOT NULL,
    direction TEXT NOT NULL,  -- 'to_china', 'from_china'
    student_count INTEGER NOT NULL,
    student_level TEXT,  -- 'undergraduate', 'graduate', 'phd', 'postdoc', 'exchange', 'language', 'vocational', 'short_term'
    field_of_study TEXT,  -- 'stem', 'social_sciences', 'humanities', 'business', 'language', 'mixed'
    scholarship_recipients INTEGER,
    scholarship_program TEXT,  -- 'chinese_government', 'confucius_institute', 'bilateral', 'self_funded'
    top_sending_institutions TEXT,  -- JSON array
    top_receiving_institutions TEXT,  -- JSON array
    average_duration_months REAL,
    percentage_of_total_students REAL,  -- % of all international students
    year_over_year_change REAL,
    source TEXT NOT NULL,  -- 'daad', 'unesco', 'moe', 'national_statistics'
    source_url TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code),
    UNIQUE(country_code, year, direction, student_level)
);

-- Academic partnerships and exchange agreements (university level)
CREATE TABLE IF NOT EXISTS academic_partnerships (
    partnership_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    foreign_institution TEXT NOT NULL,
    foreign_institution_type TEXT,  -- 'university', 'research_institute', 'academy'
    chinese_institution TEXT NOT NULL,
    chinese_institution_type TEXT,
    partnership_type TEXT NOT NULL,  -- 'mou', 'joint_program', 'joint_research_center', 'dual_degree', 'exchange_program', 'joint_lab'
    agreement_date DATE,
    agreement_year INTEGER,
    expiration_date DATE,
    status TEXT DEFAULT 'active',
    cooperation_areas TEXT,  -- JSON array of research/education areas
    joint_degrees_offered TEXT,  -- JSON array
    student_exchange_quota INTEGER,
    faculty_exchange BOOLEAN DEFAULT 0,
    joint_research_projects INTEGER,
    joint_publications INTEGER,
    funding_amount_usd REAL,
    funding_source TEXT,
    strategic_concerns BOOLEAN DEFAULT 0,
    technology_transfer_concerns BOOLEAN DEFAULT 0,
    military_involvement BOOLEAN DEFAULT 0,
    controversy_notes TEXT,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- ============================================================================
-- TECHNOLOGY & RESEARCH DIMENSION
-- ============================================================================

-- Technology cooperation agreements and joint R&D
CREATE TABLE IF NOT EXISTS technology_cooperation (
    cooperation_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    cooperation_type TEXT NOT NULL,  -- 'joint_research', 'technology_transfer', 'standards_cooperation', 'innovation_center', 'tech_park'
    technology_area TEXT NOT NULL,  -- 'ai', 'quantum', 'semiconductors', 'biotech', '5g', 'ev', 'renewable_energy', etc.
    agreement_title TEXT,
    agreement_date DATE,
    agreement_year INTEGER,
    foreign_entity TEXT,
    foreign_entity_type TEXT,  -- 'government', 'university', 'company', 'research_institute'
    chinese_entity TEXT,
    chinese_entity_type TEXT,
    cooperation_scope TEXT,
    strategic_importance TEXT,  -- 'critical', 'high', 'medium', 'low'
    dual_use_potential BOOLEAN DEFAULT 0,
    export_control_applicable BOOLEAN DEFAULT 0,
    funding_amount_usd REAL,
    expected_outcomes TEXT,
    actual_outcomes TEXT,
    status TEXT DEFAULT 'active',
    controversy_notes TEXT,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- Standards cooperation and influence in international bodies
CREATE TABLE IF NOT EXISTS standards_cooperation (
    standard_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    standards_body TEXT NOT NULL,  -- 'iso', 'iec', 'itu', '3gpp', 'etsi', national bodies
    technology_domain TEXT NOT NULL,  -- '5g', '6g', 'iot', 'ai', 'quantum', etc.
    standard_number TEXT,
    standard_title TEXT,
    proposal_date DATE,
    adoption_date DATE,
    chinese_involvement_level TEXT,  -- 'leading', 'contributing', 'participating', 'observer'
    chinese_representatives TEXT,  -- JSON array
    foreign_representatives TEXT,  -- JSON array
    voting_outcome TEXT,
    strategic_significance TEXT,
    geopolitical_context TEXT,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- ============================================================================
-- MEDIA & INFORMATION DIMENSION
-- ============================================================================

-- Chinese state media presence and operations
CREATE TABLE IF NOT EXISTS media_presence (
    presence_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    media_organization TEXT NOT NULL,  -- 'xinhua', 'cgtn', 'peoples_daily', 'china_daily', 'cri'
    organization_type TEXT,  -- 'news_agency', 'broadcaster', 'newspaper', 'digital_platform', 'radio'
    presence_type TEXT,  -- 'bureau', 'correspondent', 'distribution_deal', 'content_partnership', 'broadcasting_license'
    location_city TEXT,
    establishment_date DATE,
    closure_date DATE,
    status TEXT DEFAULT 'active',
    staff_count INTEGER,
    local_staff_count INTEGER,
    chinese_staff_count INTEGER,
    distribution_reach TEXT,  -- Description of audience/reach
    content_type TEXT,  -- 'news', 'documentaries', 'entertainment', 'propaganda', 'mixed'
    local_partnerships TEXT,  -- JSON array of local media partners
    regulatory_status TEXT,  -- 'licensed', 'registered_foreign_agent', 'unrestricted', 'restricted', 'banned'
    controversy_notes TEXT,
    government_concerns TEXT,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- Media cooperation agreements and content deals
CREATE TABLE IF NOT EXISTS media_cooperation (
    cooperation_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    chinese_media_entity TEXT NOT NULL,
    foreign_media_entity TEXT NOT NULL,
    cooperation_type TEXT,  -- 'content_sharing', 'joint_production', 'training', 'technology_transfer', 'distribution_deal'
    agreement_date DATE,
    cooperation_scope TEXT,
    strategic_purpose TEXT,
    controversy BOOLEAN DEFAULT 0,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- ============================================================================
-- SECURITY & DEFENSE DIMENSION
-- ============================================================================

-- Security and defense cooperation/incidents
CREATE TABLE IF NOT EXISTS security_cooperation (
    cooperation_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    cooperation_type TEXT NOT NULL,  -- 'military_exchange', 'defense_dialogue', 'joint_exercise', 'port_visit', 'defense_industry', 'peacekeeping'
    event_date DATE,
    event_year INTEGER,
    event_title TEXT,
    event_description TEXT,
    chinese_military_branch TEXT,  -- 'pla', 'plan', 'plaaf', 'plarf', 'strategic_support_force'
    foreign_military_branch TEXT,
    location TEXT,
    participants_count INTEGER,
    cooperation_areas TEXT,  -- JSON array
    equipment_involved TEXT,
    strategic_significance TEXT,
    nato_concerns BOOLEAN DEFAULT 0,
    allied_concerns BOOLEAN DEFAULT 0,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- Espionage incidents and security concerns
CREATE TABLE IF NOT EXISTS security_incidents (
    incident_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    incident_date DATE,
    incident_year INTEGER,
    incident_type TEXT NOT NULL,  -- 'espionage', 'cyber_attack', 'influence_operation', 'intellectual_property_theft', 'sabotage', 'disinformation'
    incident_title TEXT,
    incident_description TEXT,
    chinese_actors TEXT,  -- Identified or suspected actors
    actor_affiliation TEXT,  -- 'mss', 'pla', 'state_company', 'contracted_hackers', 'unknown'
    target_sector TEXT,
    target_organizations TEXT,  -- JSON array
    information_stolen TEXT,
    damage_assessment TEXT,
    attribution_confidence TEXT,  -- 'confirmed', 'high_confidence', 'suspected', 'alleged'
    public_disclosure_date DATE,
    disclosing_entity TEXT,  -- Who revealed the incident
    government_response TEXT,
    sanctions_imposed BOOLEAN DEFAULT 0,
    arrests_made INTEGER DEFAULT 0,
    indictments_issued INTEGER DEFAULT 0,
    diplomatic_protest BOOLEAN DEFAULT 0,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- Export control decisions and technology restrictions
CREATE TABLE IF NOT EXISTS export_controls (
    control_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    decision_date DATE,
    decision_year INTEGER,
    control_type TEXT NOT NULL,  -- 'export_ban', 'license_requirement', 'entity_list', 'end_use_control', 'catch_all'
    technology_area TEXT NOT NULL,
    specific_products TEXT,  -- JSON array
    chinese_entities_affected TEXT,  -- JSON array
    control_scope TEXT,  -- 'comprehensive', 'limited', 'case_by_case'
    legal_basis TEXT,
    strategic_rationale TEXT,
    coordination_with_allies BOOLEAN DEFAULT 0,
    allied_coordination_details TEXT,
    chinese_response TEXT,
    economic_impact TEXT,
    effectiveness_assessment TEXT,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- ============================================================================
-- LEGAL & REGULATORY DIMENSION
-- ============================================================================

-- Legal framework and treaties
CREATE TABLE IF NOT EXISTS legal_framework (
    framework_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    framework_type TEXT NOT NULL,  -- 'extradition_treaty', 'mutual_legal_assistance', 'tax_treaty', 'investment_protection', 'arbitration'
    framework_title TEXT NOT NULL,
    signing_date DATE,
    entry_into_force_date DATE,
    status TEXT DEFAULT 'active',
    key_provisions TEXT,  -- JSON array
    utilization_cases INTEGER DEFAULT 0,
    controversy BOOLEAN DEFAULT 0,
    controversy_details TEXT,
    treaty_text_url TEXT,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- Regulatory decisions affecting Chinese entities
CREATE TABLE IF NOT EXISTS regulatory_decisions (
    decision_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    decision_date DATE,
    decision_year INTEGER,
    regulatory_body TEXT NOT NULL,
    decision_type TEXT NOT NULL,  -- 'approval', 'rejection', 'conditional_approval', 'investigation', 'fine', 'ban', 'restriction'
    affected_entity TEXT NOT NULL,
    entity_type TEXT,  -- 'company', 'app', 'product', 'investment', 'service'
    sector TEXT,
    decision_summary TEXT,
    legal_basis TEXT,
    concerns_cited TEXT,  -- 'national_security', 'data_privacy', 'competition', 'consumer_protection', 'public_health'
    conditions_imposed TEXT,
    fine_amount_usd REAL,
    appeal_status TEXT,
    appeal_outcome TEXT,
    precedent_setting BOOLEAN DEFAULT 0,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- ============================================================================
-- POLICY & STRATEGIC DOCUMENTS
-- ============================================================================

-- National strategy documents and policy papers
CREATE TABLE IF NOT EXISTS policy_documents (
    document_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    document_type TEXT NOT NULL,  -- 'national_strategy', 'white_paper', 'parliamentary_report', 'government_review', 'policy_guideline'
    document_title TEXT NOT NULL,
    issuing_body TEXT NOT NULL,
    publication_date DATE,
    publication_year INTEGER,
    document_scope TEXT,  -- 'comprehensive_china_strategy', 'sector_specific', 'regional', 'threat_assessment'
    key_themes TEXT,  -- JSON array
    policy_recommendations TEXT,  -- JSON array
    risk_assessment TEXT,
    stance_on_china TEXT,  -- 'cooperative', 'competitive', 'adversarial', 'mixed', 'systemic_rival'
    policy_shift_indicator BOOLEAN DEFAULT 0,  -- Marks significant policy changes
    previous_policy_document TEXT,  -- Links to previous version
    document_url TEXT,
    document_text TEXT,  -- Full text if available
    summary TEXT,
    media_reaction TEXT,
    chinese_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- ============================================================================
-- LINKING TABLES: Connect to existing OSINT data
-- ============================================================================

-- Links bilateral events to existing academic collaborations
CREATE TABLE IF NOT EXISTS bilateral_academic_links (
    link_id TEXT PRIMARY KEY,
    event_id TEXT,
    country_code TEXT NOT NULL,
    openalex_work_id TEXT,  -- Links to OpenAlex papers
    arxiv_id TEXT,  -- Links to arXiv papers
    cordis_project_id TEXT,  -- Links to CORDIS projects
    collaboration_date DATE,
    collaboration_type TEXT,
    strategic_significance TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES bilateral_events(event_id),
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- Links bilateral events to procurement/contracts
CREATE TABLE IF NOT EXISTS bilateral_procurement_links (
    link_id TEXT PRIMARY KEY,
    event_id TEXT,
    investment_id TEXT,
    country_code TEXT NOT NULL,
    ted_contract_id TEXT,  -- Links to TED contracts
    usaspending_award_id TEXT,  -- Links to USAspending
    contract_date DATE,
    contract_value_usd REAL,
    strategic_significance TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES bilateral_events(event_id),
    FOREIGN KEY (investment_id) REFERENCES bilateral_investments(investment_id),
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- Links bilateral events to patents
CREATE TABLE IF NOT EXISTS bilateral_patent_links (
    link_id TEXT PRIMARY KEY,
    event_id TEXT,
    cooperation_id TEXT,
    country_code TEXT NOT NULL,
    uspto_patent_number TEXT,
    epo_patent_number TEXT,
    wipo_patent_number TEXT,
    patent_filing_date DATE,
    technology_area TEXT,
    strategic_significance TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES bilateral_events(event_id),
    FOREIGN KEY (cooperation_id) REFERENCES technology_cooperation(cooperation_id),
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- Links bilateral entities to corporate ownership (GLEIF)
CREATE TABLE IF NOT EXISTS bilateral_corporate_links (
    link_id TEXT PRIMARY KEY,
    investment_id TEXT,
    acquisition_id TEXT,
    country_code TEXT NOT NULL,
    gleif_lei TEXT,  -- Legal Entity Identifier
    chinese_entity TEXT,
    foreign_entity TEXT,
    relationship_type TEXT,  -- 'ownership', 'subsidiary', 'joint_venture', 'supplier', 'customer'
    ownership_percentage REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (investment_id) REFERENCES bilateral_investments(investment_id),
    FOREIGN KEY (acquisition_id) REFERENCES major_acquisitions(acquisition_id),
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- Links to sanctions and entity lists
CREATE TABLE IF NOT EXISTS bilateral_sanctions_links (
    link_id TEXT PRIMARY KEY,
    event_id TEXT,
    incident_id TEXT,
    country_code TEXT NOT NULL,
    sanctioned_entity TEXT,
    sanction_type TEXT,
    sanction_date DATE,
    opensanctions_id TEXT,  -- Links to OpenSanctions data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES bilateral_events(event_id),
    FOREIGN KEY (incident_id) REFERENCES security_incidents(incident_id),
    FOREIGN KEY (country_code) REFERENCES bilateral_countries(country_code)
);

-- ============================================================================
-- ANALYTICAL VIEWS: Pre-computed aggregations
-- ============================================================================

-- Country relationship intensity score view
CREATE VIEW IF NOT EXISTS v_country_relationship_intensity AS
SELECT
    bc.country_code,
    bc.country_name,
    bc.current_relationship_status,
    bc.bri_participation_status,
    COUNT(DISTINCT be.event_id) as total_events,
    COUNT(DISTINCT dv.visit_id) as diplomatic_visits,
    COUNT(DISTINCT ba.agreement_id) as bilateral_agreements,
    COUNT(DISTINCT bi.investment_id) as investments,
    SUM(bi.deal_value_usd) as total_investment_usd,
    COUNT(DISTINCT sr.relationship_id) as sister_cities,
    COUNT(DISTINCT ci.institution_id) as cultural_institutions,
    COUNT(DISTINCT ip.project_id) as infrastructure_projects,
    COUNT(DISTINCT si.incident_id) as security_incidents
FROM bilateral_countries bc
LEFT JOIN bilateral_events be ON bc.country_code = be.country_code
LEFT JOIN diplomatic_visits dv ON bc.country_code = dv.country_code
LEFT JOIN bilateral_agreements ba ON bc.country_code = ba.agreement_id
LEFT JOIN bilateral_investments bi ON bc.country_code = bi.country_code
LEFT JOIN sister_relationships sr ON bc.country_code = sr.country_code
LEFT JOIN cultural_institutions ci ON bc.country_code = ci.country_code
LEFT JOIN infrastructure_projects ip ON bc.country_code = ip.country_code
LEFT JOIN security_incidents si ON bc.country_code = si.country_code
GROUP BY bc.country_code;

-- Annual relationship trends view
CREATE VIEW IF NOT EXISTS v_annual_relationship_trends AS
SELECT
    country_code,
    year,
    COUNT(*) as events_count,
    SUM(CASE WHEN sentiment = 'positive' THEN 1 ELSE 0 END) as positive_events,
    SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) as negative_events,
    AVG(importance_tier) as avg_importance
FROM (
    SELECT country_code, event_year as year, sentiment, importance_tier FROM bilateral_events
    UNION ALL
    SELECT country_code, visit_year as year, 'positive' as sentiment, 2 as importance_tier FROM diplomatic_visits
    UNION ALL
    SELECT country_code, year, 'neutral' as sentiment, 3 as importance_tier FROM bilateral_investments
)
GROUP BY country_code, year
ORDER BY country_code, year;

-- Technology cooperation intensity by country
CREATE VIEW IF NOT EXISTS v_technology_cooperation_intensity AS
SELECT
    bc.country_code,
    bc.country_name,
    COUNT(DISTINCT tc.cooperation_id) as cooperation_agreements,
    COUNT(DISTINCT CASE WHEN tc.dual_use_potential = 1 THEN tc.cooperation_id END) as dual_use_projects,
    COUNT(DISTINCT ap.partnership_id) as academic_partnerships,
    COUNT(DISTINCT bal.openalex_work_id) as collaborative_papers,
    COUNT(DISTINCT bpl.uspto_patent_number) as collaborative_patents
FROM bilateral_countries bc
LEFT JOIN technology_cooperation tc ON bc.country_code = tc.country_code
LEFT JOIN academic_partnerships ap ON bc.country_code = ap.country_code
LEFT JOIN bilateral_academic_links bal ON bc.country_code = bal.country_code
LEFT JOIN bilateral_patent_links bpl ON bc.country_code = bpl.country_code
GROUP BY bc.country_code;

-- Investment patterns by sector
CREATE VIEW IF NOT EXISTS v_investment_by_sector AS
SELECT
    country_code,
    sector,
    COUNT(*) as investment_count,
    SUM(deal_value_usd) as total_value_usd,
    AVG(deal_value_usd) as avg_value_usd,
    SUM(CASE WHEN strategic_asset = 1 THEN 1 ELSE 0 END) as strategic_acquisitions,
    SUM(CASE WHEN deal_status = 'blocked' THEN 1 ELSE 0 END) as blocked_deals
FROM bilateral_investments
WHERE deal_value_usd IS NOT NULL
GROUP BY country_code, sector;

-- ============================================================================
-- PERFORMANCE INDEXES
-- ============================================================================

-- Core tables primary indexes
CREATE INDEX IF NOT EXISTS idx_bilateral_events_country_date ON bilateral_events(country_code, event_date);
CREATE INDEX IF NOT EXISTS idx_bilateral_events_type ON bilateral_events(event_type);
CREATE INDEX IF NOT EXISTS idx_bilateral_events_year ON bilateral_events(event_year);
CREATE INDEX IF NOT EXISTS idx_bilateral_events_importance ON bilateral_events(importance_tier);

CREATE INDEX IF NOT EXISTS idx_diplomatic_visits_country_date ON diplomatic_visits(country_code, visit_date);
CREATE INDEX IF NOT EXISTS idx_diplomatic_visits_year ON diplomatic_visits(visit_year);

CREATE INDEX IF NOT EXISTS idx_bilateral_agreements_country ON bilateral_agreements(country_code);
CREATE INDEX IF NOT EXISTS idx_bilateral_agreements_type ON bilateral_agreements(agreement_type);
CREATE INDEX IF NOT EXISTS idx_bilateral_agreements_status ON bilateral_agreements(status);

CREATE INDEX IF NOT EXISTS idx_bilateral_trade_country_year ON bilateral_trade(country_code, year);
CREATE INDEX IF NOT EXISTS idx_bilateral_trade_direction ON bilateral_trade(trade_direction);
CREATE INDEX IF NOT EXISTS idx_bilateral_trade_sector ON bilateral_trade(sector);

CREATE INDEX IF NOT EXISTS idx_bilateral_investments_country_year ON bilateral_investments(country_code, year);
CREATE INDEX IF NOT EXISTS idx_bilateral_investments_direction ON bilateral_investments(investment_direction);
CREATE INDEX IF NOT EXISTS idx_bilateral_investments_sector ON bilateral_investments(sector);
CREATE INDEX IF NOT EXISTS idx_bilateral_investments_status ON bilateral_investments(deal_status);

CREATE INDEX IF NOT EXISTS idx_major_acquisitions_country ON major_acquisitions(country_code);
CREATE INDEX IF NOT EXISTS idx_major_acquisitions_sector ON major_acquisitions(target_sector);
CREATE INDEX IF NOT EXISTS idx_major_acquisitions_date ON major_acquisitions(acquisition_date);

CREATE INDEX IF NOT EXISTS idx_infrastructure_projects_country ON infrastructure_projects(country_code);
CREATE INDEX IF NOT EXISTS idx_infrastructure_projects_type ON infrastructure_projects(project_type);
CREATE INDEX IF NOT EXISTS idx_infrastructure_projects_bri ON infrastructure_projects(bri_affiliated);
CREATE INDEX IF NOT EXISTS idx_infrastructure_projects_status ON infrastructure_projects(project_status);

CREATE INDEX IF NOT EXISTS idx_sister_relationships_country ON sister_relationships(country_code);
CREATE INDEX IF NOT EXISTS idx_sister_relationships_status ON sister_relationships(relationship_status);

CREATE INDEX IF NOT EXISTS idx_cultural_institutions_country ON cultural_institutions(country_code);
CREATE INDEX IF NOT EXISTS idx_cultural_institutions_type ON cultural_institutions(institution_type);
CREATE INDEX IF NOT EXISTS idx_cultural_institutions_status ON cultural_institutions(status);

CREATE INDEX IF NOT EXISTS idx_education_exchanges_country_year ON education_exchanges(country_code, year);
CREATE INDEX IF NOT EXISTS idx_education_exchanges_direction ON education_exchanges(direction);

CREATE INDEX IF NOT EXISTS idx_academic_partnerships_country ON academic_partnerships(country_code);
CREATE INDEX IF NOT EXISTS idx_academic_partnerships_type ON academic_partnerships(partnership_type);

CREATE INDEX IF NOT EXISTS idx_technology_cooperation_country ON technology_cooperation(country_code);
CREATE INDEX IF NOT EXISTS idx_technology_cooperation_area ON technology_cooperation(technology_area);

CREATE INDEX IF NOT EXISTS idx_security_incidents_country_year ON security_incidents(country_code, incident_year);
CREATE INDEX IF NOT EXISTS idx_security_incidents_type ON security_incidents(incident_type);

CREATE INDEX IF NOT EXISTS idx_policy_documents_country_year ON policy_documents(country_code, publication_year);

-- Linking tables indexes
CREATE INDEX IF NOT EXISTS idx_bilateral_academic_links_country ON bilateral_academic_links(country_code);
CREATE INDEX IF NOT EXISTS idx_bilateral_academic_links_event ON bilateral_academic_links(event_id);

CREATE INDEX IF NOT EXISTS idx_bilateral_procurement_links_country ON bilateral_procurement_links(country_code);
CREATE INDEX IF NOT EXISTS idx_bilateral_procurement_links_event ON bilateral_procurement_links(event_id);

CREATE INDEX IF NOT EXISTS idx_bilateral_patent_links_country ON bilateral_patent_links(country_code);
CREATE INDEX IF NOT EXISTS idx_bilateral_patent_links_event ON bilateral_patent_links(event_id);

CREATE INDEX IF NOT EXISTS idx_bilateral_corporate_links_country ON bilateral_corporate_links(country_code);
CREATE INDEX IF NOT EXISTS idx_bilateral_corporate_links_investment ON bilateral_corporate_links(investment_id);

CREATE INDEX IF NOT EXISTS idx_bilateral_sanctions_links_country ON bilateral_sanctions_links(country_code);
CREATE INDEX IF NOT EXISTS idx_bilateral_sanctions_links_event ON bilateral_sanctions_links(event_id);

-- ============================================================================
-- METADATA AND VERSION TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS bilateral_schema_metadata (
    metadata_key TEXT PRIMARY KEY,
    metadata_value TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR REPLACE INTO bilateral_schema_metadata VALUES
    ('schema_version', '1.0', CURRENT_TIMESTAMP),
    ('schema_created', '2025-10-22', CURRENT_TIMESTAMP),
    ('total_tables', '40', CURRENT_TIMESTAMP),
    ('total_views', '4', CURRENT_TIMESTAMP),
    ('coverage_countries', '81', CURRENT_TIMESTAMP),
    ('status', 'production_ready', CURRENT_TIMESTAMP);

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
