-- Technology Events & Conferences Intelligence Schema
-- Tracks conferences, expos, trade shows where dual-use tech is discussed/marketed
-- Temporal scope: 2015-2035 (10 years historical + 10 years forward)

-- Core events table
CREATE TABLE IF NOT EXISTS technology_events (
    event_id TEXT PRIMARY KEY,
    event_name TEXT NOT NULL,
    event_series TEXT,  -- e.g., "Mobile World Congress" (recurring annual event)
    edition TEXT,  -- e.g., "MWC 2024", "47th Annual"
    event_type TEXT,  -- conference, expo, trade_show, symposium, workshop, summit, forum
    technology_domain TEXT,  -- maps to our 12 strategic domains
    start_date DATE,
    end_date DATE,
    location_city TEXT,
    location_country TEXT,
    location_country_code TEXT,  -- ISO 2-letter
    venue TEXT,
    organizer_name TEXT,
    organizer_type TEXT,  -- industry_association, commercial, academic, government, military, ngo
    organizer_country TEXT,
    website_url TEXT,
    archived_url TEXT,  -- Wayback Machine URL if historical
    expected_attendance INTEGER,
    actual_attendance INTEGER,
    exhibitor_count INTEGER,
    speaker_count INTEGER,

    -- Strategic indicators
    dual_use_indicator BOOLEAN DEFAULT 0,  -- potential military applications
    military_participation BOOLEAN DEFAULT 0,  -- defense contractors/military present
    government_sponsored BOOLEAN DEFAULT 0,
    china_participation_confirmed BOOLEAN DEFAULT 0,
    china_sponsored BOOLEAN DEFAULT 0,
    event_scope TEXT,  -- international, regional, national, bilateral

    -- Security classifications
    export_controlled_topics BOOLEAN DEFAULT 0,  -- ITAR/EAR/EU dual-use topics
    clearance_required BOOLEAN DEFAULT 0,

    -- Metadata
    data_source TEXT,  -- website, wayback, manual, api
    data_quality TEXT,  -- complete, partial, minimal
    last_updated TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Event participants (sponsors, exhibitors, speakers, attendees)
CREATE TABLE IF NOT EXISTS event_participants (
    participant_id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL,
    entity_name TEXT NOT NULL,
    entity_normalized TEXT,  -- standardized name for matching
    entity_type TEXT,  -- sponsor, exhibitor, speaker, attendee, organizer, partner
    entity_country TEXT,
    entity_country_code TEXT,

    -- Chinese entity detection
    chinese_entity BOOLEAN DEFAULT 0,
    chinese_entity_type TEXT,  -- soe, private, university, research_institute, military
    pla_affiliated BOOLEAN DEFAULT 0,
    entity_list_status TEXT,  -- BIS entity list, SDN, etc.

    -- Participation details
    participation_role TEXT,  -- e.g., "Gold Sponsor", "Keynote Speaker", "Exhibitor"
    booth_number TEXT,
    booth_size TEXT,  -- for exhibitors
    speaking_topics TEXT,  -- for speakers
    session_ids TEXT,  -- comma-separated session IDs
    sponsorship_level TEXT,  -- platinum, gold, silver, bronze, supporter
    sponsorship_amount_usd REAL,

    -- Strategic assessment
    technology_focus TEXT,  -- what tech they're promoting/discussing
    products_displayed TEXT,
    dual_use_products BOOLEAN DEFAULT 0,
    networking_focus TEXT,  -- recruiting, partnerships, sales, research

    -- Metadata
    data_source TEXT,
    verification_status TEXT,  -- confirmed, inferred, unverified
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (event_id) REFERENCES technology_events(event_id)
);

-- Event programs (sessions, panels, workshops)
CREATE TABLE IF NOT EXISTS event_programs (
    program_id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL,
    session_title TEXT NOT NULL,
    session_type TEXT,  -- keynote, panel, technical_session, workshop, demo, exhibition
    session_date DATE,
    session_time TEXT,
    session_duration_minutes INTEGER,
    track TEXT,  -- conference track (e.g., "Quantum Hardware", "AI Ethics")

    -- Content
    session_abstract TEXT,
    speakers TEXT,  -- comma-separated or JSON
    moderator TEXT,
    panelists TEXT,
    topics TEXT,  -- comma-separated topic keywords
    technology_keywords TEXT,  -- extracted tech terms

    -- Strategic relevance
    strategic_relevance TEXT,  -- HIGH/MEDIUM/LOW based on tech domain
    dual_use_content BOOLEAN DEFAULT 0,
    export_control_relevant BOOLEAN DEFAULT 0,
    chinese_speakers BOOLEAN DEFAULT 0,
    chinese_companies_mentioned BOOLEAN DEFAULT 0,

    -- Metadata
    recording_url TEXT,
    slides_url TEXT,
    paper_doi TEXT,  -- if academic conference
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (event_id) REFERENCES technology_events(event_id)
);

-- Event intelligence summaries
CREATE TABLE IF NOT EXISTS event_intelligence (
    intelligence_id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL,

    -- Participation metrics
    chinese_entities_count INTEGER DEFAULT 0,
    european_entities_count INTEGER DEFAULT 0,
    us_entities_count INTEGER DEFAULT 0,
    total_entities_count INTEGER DEFAULT 0,

    -- Entity type breakdown
    chinese_sponsors_count INTEGER DEFAULT 0,
    chinese_exhibitors_count INTEGER DEFAULT 0,
    chinese_speakers_count INTEGER DEFAULT 0,

    -- Content analysis
    dual_use_sessions_count INTEGER DEFAULT 0,
    strategic_tech_sessions_count INTEGER DEFAULT 0,

    -- Key observations
    key_observations TEXT,  -- Analyst notes
    notable_chinese_entities TEXT,  -- High-profile attendees
    strategic_partnerships_observed TEXT,
    technology_showcased TEXT,

    -- Risk assessment
    risk_indicators TEXT,  -- Technology transfer risks identified
    risk_score INTEGER,  -- 0-100
    recommendations TEXT,

    -- Temporal comparisons
    yoy_chinese_participation_change REAL,  -- year-over-year % change
    trend_analysis TEXT,

    -- Metadata
    analyst_name TEXT,
    analysis_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (event_id) REFERENCES technology_events(event_id)
);

-- Event series tracking (for recurring conferences)
CREATE TABLE IF NOT EXISTS event_series (
    series_id TEXT PRIMARY KEY,
    series_name TEXT NOT NULL,
    frequency TEXT,  -- annual, biennial, quarterly
    typical_month TEXT,  -- usual timing
    typical_location TEXT,
    organizer TEXT,
    technology_domain TEXT,
    first_edition_year INTEGER,
    latest_edition_year INTEGER,
    total_editions INTEGER,

    -- Strategic importance
    importance_tier INTEGER,  -- 1=critical, 2=important, 3=notable
    strategic_rationale TEXT,

    -- Tracking
    monitoring_status TEXT,  -- active, inactive, discontinued
    last_scraped_date DATE,
    next_edition_expected_date DATE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Relationships: Events to our existing entities
CREATE TABLE IF NOT EXISTS event_entity_links (
    link_id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL,
    entity_id TEXT,  -- links to openalex_entities, ted contractors, etc.
    entity_source TEXT,  -- openalex, ted, patents, manual
    link_type TEXT,  -- sponsor, speaker, exhibitor
    confidence REAL,  -- 0.0-1.0 matching confidence
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (event_id) REFERENCES technology_events(event_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_events_date ON technology_events(start_date);
CREATE INDEX IF NOT EXISTS idx_events_domain ON technology_events(technology_domain);
CREATE INDEX IF NOT EXISTS idx_events_country ON technology_events(location_country_code);
CREATE INDEX IF NOT EXISTS idx_events_china_participation ON technology_events(china_participation_confirmed);

CREATE INDEX IF NOT EXISTS idx_participants_event ON event_participants(event_id);
CREATE INDEX IF NOT EXISTS idx_participants_chinese ON event_participants(chinese_entity);
CREATE INDEX IF NOT EXISTS idx_participants_entity ON event_participants(entity_normalized);

CREATE INDEX IF NOT EXISTS idx_programs_event ON event_programs(event_id);
CREATE INDEX IF NOT EXISTS idx_programs_date ON event_programs(session_date);
CREATE INDEX IF NOT EXISTS idx_programs_strategic ON event_programs(strategic_relevance);

CREATE INDEX IF NOT EXISTS idx_intelligence_event ON event_intelligence(event_id);
