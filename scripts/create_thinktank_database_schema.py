#!/usr/bin/env python3
"""
Create comprehensive database schema for think tank reports
Integrates with existing OSINT warehouse at F:/OSINT_WAREHOUSE/osint_master.db
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

def create_thinktank_schema(db_path="F:/OSINT_WAREHOUSE/osint_master.db"):
    """Create comprehensive schema for think tank report storage and analysis"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    # Main think tank reports table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS thinktank_reports (
        report_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        source_organization TEXT NOT NULL,
        authors TEXT,
        publication_date DATE,
        collection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        file_path TEXT UNIQUE,
        file_hash TEXT UNIQUE,
        file_size INTEGER,
        url_origin TEXT,
        document_type TEXT CHECK(document_type IN ('report', 'brief', 'testimony', 'analysis', 'white_paper', 'policy_paper', 'research_note')),
        classification TEXT CHECK(classification IN ('MCF', 'TECH_TRANSFER', 'SUPPLY_CHAIN', 'DEFENSE', 'ECONOMIC', 'CYBER', 'SPACE', 'AI_ML', 'GENERAL')),
        content_text TEXT,
        executive_summary TEXT,
        key_findings TEXT,
        recommendations TEXT,
        methodology TEXT,
        relevance_score REAL CHECK(relevance_score >= 0 AND relevance_score <= 10),
        confidence_level TEXT CHECK(confidence_level IN ('HIGH', 'MEDIUM', 'LOW', 'UNCERTAIN')),
        processing_status TEXT DEFAULT 'pending' CHECK(processing_status IN ('pending', 'processing', 'completed', 'failed', 'partial')),
        processing_notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Entity mentions in reports
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS report_entities (
        entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER NOT NULL,
        entity_type TEXT NOT NULL CHECK(entity_type IN ('company', 'technology', 'person', 'organization', 'program', 'location', 'event', 'law_regulation')),
        entity_name TEXT NOT NULL,
        entity_chinese_name TEXT,
        mention_count INTEGER DEFAULT 1,
        first_mention_page INTEGER,
        context_snippets TEXT,
        sentiment TEXT CHECK(sentiment IN ('positive', 'negative', 'neutral', 'threat', 'opportunity')),
        risk_level TEXT CHECK(risk_level IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'MINIMAL')),
        confidence REAL CHECK(confidence >= 0 AND confidence <= 1),
        FOREIGN KEY (report_id) REFERENCES thinktank_reports(report_id) ON DELETE CASCADE,
        UNIQUE(report_id, entity_type, entity_name)
    )
    """)

    # Technology areas identified
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS report_technologies (
        tech_id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER NOT NULL,
        technology_category TEXT NOT NULL,
        specific_technology TEXT NOT NULL,
        maturity_level TEXT CHECK(maturity_level IN ('research', 'development', 'demonstration', 'deployment', 'operational')),
        dual_use_flag BOOLEAN DEFAULT 0,
        military_application TEXT,
        civilian_application TEXT,
        china_capability_assessment TEXT,
        us_capability_assessment TEXT,
        technology_gap TEXT,
        timeline_projection TEXT,
        FOREIGN KEY (report_id) REFERENCES thinktank_reports(report_id) ON DELETE CASCADE
    )
    """)

    # Risk indicators and warnings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS report_risk_indicators (
        risk_id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER NOT NULL,
        risk_category TEXT NOT NULL CHECK(risk_category IN ('technology_transfer', 'ip_theft', 'supply_chain', 'investment', 'espionage', 'cyber', 'influence', 'military')),
        risk_description TEXT NOT NULL,
        severity TEXT CHECK(severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
        likelihood TEXT CHECK(likelihood IN ('CERTAIN', 'LIKELY', 'POSSIBLE', 'UNLIKELY')),
        timeframe TEXT,
        affected_sectors TEXT,
        recommended_actions TEXT,
        evidence_quality TEXT CHECK(evidence_quality IN ('STRONG', 'MODERATE', 'WEAK', 'SPECULATIVE')),
        FOREIGN KEY (report_id) REFERENCES thinktank_reports(report_id) ON DELETE CASCADE
    )
    """)

    # Cross-references to other data sources
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS report_cross_references (
        xref_id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER NOT NULL,
        source_type TEXT NOT NULL CHECK(source_type IN ('CORDIS', 'SEC_EDGAR', 'USPTO', 'TED', 'OPENALEX', 'USASPENDING', 'OPENSANCTIONS', 'GLEIF')),
        source_record_id TEXT NOT NULL,
        reference_type TEXT CHECK(reference_type IN ('confirms', 'contradicts', 'extends', 'related')),
        confidence REAL CHECK(confidence >= 0 AND confidence <= 1),
        validation_notes TEXT,
        FOREIGN KEY (report_id) REFERENCES thinktank_reports(report_id) ON DELETE CASCADE
    )
    """)

    # Report relationships and citations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS report_relationships (
        relationship_id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_report_id INTEGER NOT NULL,
        target_report_id INTEGER NOT NULL,
        relationship_type TEXT CHECK(relationship_type IN ('cites', 'cited_by', 'updates', 'supersedes', 'contradicts', 'supports')),
        relationship_strength TEXT CHECK(relationship_strength IN ('strong', 'moderate', 'weak')),
        FOREIGN KEY (source_report_id) REFERENCES thinktank_reports(report_id) ON DELETE CASCADE,
        FOREIGN KEY (target_report_id) REFERENCES thinktank_reports(report_id) ON DELETE CASCADE,
        UNIQUE(source_report_id, target_report_id, relationship_type)
    )
    """)

    # Extracted data points and statistics
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS report_data_points (
        datapoint_id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER NOT NULL,
        data_type TEXT NOT NULL,
        data_value TEXT NOT NULL,
        data_unit TEXT,
        data_year INTEGER,
        data_source TEXT,
        confidence_interval TEXT,
        notes TEXT,
        FOREIGN KEY (report_id) REFERENCES thinktank_reports(report_id) ON DELETE CASCADE
    )
    """)

    # Policy recommendations tracking
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS report_recommendations (
        rec_id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER NOT NULL,
        recommendation_type TEXT CHECK(recommendation_type IN ('policy', 'legislative', 'regulatory', 'operational', 'research', 'investment')),
        recommendation_text TEXT NOT NULL,
        target_audience TEXT,
        priority_level TEXT CHECK(priority_level IN ('IMMEDIATE', 'HIGH', 'MEDIUM', 'LOW')),
        implementation_status TEXT CHECK(implementation_status IN ('not_started', 'under_consideration', 'partial', 'implemented', 'rejected')),
        related_entities TEXT,
        FOREIGN KEY (report_id) REFERENCES thinktank_reports(report_id) ON DELETE CASCADE
    )
    """)

    # Source organizations metadata
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS thinktank_sources (
        source_id INTEGER PRIMARY KEY AUTOINCREMENT,
        organization_name TEXT UNIQUE NOT NULL,
        organization_type TEXT CHECK(organization_type IN ('government', 'think_tank', 'academic', 'industry', 'ngo', 'international')),
        country TEXT,
        website TEXT,
        bias_assessment TEXT CHECK(bias_assessment IN ('neutral', 'hawkish', 'dovish', 'balanced', 'unknown')),
        credibility_score REAL CHECK(credibility_score >= 0 AND credibility_score <= 10),
        specialization TEXT,
        notes TEXT
    )
    """)

    # Processing log for audit trail
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS report_processing_log (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER NOT NULL,
        processing_stage TEXT NOT NULL,
        status TEXT CHECK(status IN ('started', 'completed', 'failed', 'skipped')),
        message TEXT,
        error_details TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (report_id) REFERENCES thinktank_reports(report_id) ON DELETE CASCADE
    )
    """)

    # Create indexes for performance
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_reports_source ON thinktank_reports(source_organization)",
        "CREATE INDEX IF NOT EXISTS idx_reports_date ON thinktank_reports(publication_date)",
        "CREATE INDEX IF NOT EXISTS idx_reports_classification ON thinktank_reports(classification)",
        "CREATE INDEX IF NOT EXISTS idx_reports_status ON thinktank_reports(processing_status)",
        "CREATE INDEX IF NOT EXISTS idx_entities_name ON report_entities(entity_name)",
        "CREATE INDEX IF NOT EXISTS idx_entities_type ON report_entities(entity_type)",
        "CREATE INDEX IF NOT EXISTS idx_entities_risk ON report_entities(risk_level)",
        "CREATE INDEX IF NOT EXISTS idx_tech_category ON report_technologies(technology_category)",
        "CREATE INDEX IF NOT EXISTS idx_risk_severity ON report_risk_indicators(severity)",
        "CREATE INDEX IF NOT EXISTS idx_xref_source ON report_cross_references(source_type)"
    ]

    for index in indexes:
        cursor.execute(index)

    # Create useful views
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS v_high_risk_entities AS
    SELECT DISTINCT
        e.entity_name,
        e.entity_type,
        e.risk_level,
        COUNT(DISTINCT e.report_id) as report_mentions,
        GROUP_CONCAT(DISTINCT r.source_organization) as sources
    FROM report_entities e
    JOIN thinktank_reports r ON e.report_id = r.report_id
    WHERE e.risk_level IN ('CRITICAL', 'HIGH')
    GROUP BY e.entity_name, e.entity_type
    ORDER BY report_mentions DESC
    """)

    cursor.execute("""
    CREATE VIEW IF NOT EXISTS v_technology_consensus AS
    SELECT
        t.technology_category,
        t.specific_technology,
        COUNT(DISTINCT t.report_id) as report_count,
        AVG(CASE WHEN t.dual_use_flag = 1 THEN 1 ELSE 0 END) as dual_use_percentage,
        GROUP_CONCAT(DISTINCT r.source_organization) as reporting_orgs
    FROM report_technologies t
    JOIN thinktank_reports r ON t.report_id = r.report_id
    GROUP BY t.technology_category, t.specific_technology
    HAVING report_count > 1
    ORDER BY report_count DESC
    """)

    cursor.execute("""
    CREATE VIEW IF NOT EXISTS v_recent_critical_risks AS
    SELECT
        r.title,
        r.source_organization,
        r.publication_date,
        ri.risk_category,
        ri.risk_description,
        ri.severity,
        ri.likelihood
    FROM thinktank_reports r
    JOIN report_risk_indicators ri ON r.report_id = ri.report_id
    WHERE ri.severity = 'CRITICAL'
    AND r.publication_date >= date('now', '-6 months')
    ORDER BY r.publication_date DESC
    """)

    # Create triggers for updated_at
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS update_report_timestamp
    AFTER UPDATE ON thinktank_reports
    BEGIN
        UPDATE thinktank_reports SET updated_at = CURRENT_TIMESTAMP
        WHERE report_id = NEW.report_id;
    END
    """)

    conn.commit()

    print(f"[SUCCESS] Database schema created successfully at {db_path}")
    print("\nTables created:")
    print("  - thinktank_reports (main document storage)")
    print("  - report_entities (companies, people, organizations)")
    print("  - report_technologies (tech areas and assessments)")
    print("  - report_risk_indicators (threats and warnings)")
    print("  - report_cross_references (validation with other sources)")
    print("  - report_relationships (document connections)")
    print("  - report_data_points (extracted statistics)")
    print("  - report_recommendations (policy suggestions)")
    print("  - thinktank_sources (organization metadata)")
    print("  - report_processing_log (audit trail)")
    print("\nViews created:")
    print("  - v_high_risk_entities")
    print("  - v_technology_consensus")
    print("  - v_recent_critical_risks")

    return conn

if __name__ == "__main__":
    # Check if database directory exists
    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
    if not db_path.parent.exists():
        print(f"Creating directory: {db_path.parent}")
        db_path.parent.mkdir(parents=True, exist_ok=True)

    # Create schema
    conn = create_thinktank_schema(str(db_path))

    # Show current statistics
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM thinktank_reports WHERE processing_status = 'completed'")
    report_count = cursor.fetchone()[0]
    print(f"\nCurrent database contains {report_count} processed reports")

    conn.close()
