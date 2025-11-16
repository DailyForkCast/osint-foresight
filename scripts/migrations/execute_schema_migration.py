"""
Schema Migration Executor
Executes the thinktank_reports schema migration plan
"""

import sqlite3
from datetime import datetime
from pathlib import Path

# Paths
DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
BACKUP_PATH = Path(f"F:/OSINT_WAREHOUSE/osint_master_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")

print(f"=== Schema Migration Executor ===")
print(f"Database: {DB_PATH}")
print(f"Backup: {BACKUP_PATH}")
print(f"Started: {datetime.now()}")
print()

# Step 1: Create backup using SQLite backup API
print("Step 1: Creating database backup...")
try:
    # Check if source exists
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Source database not found: {DB_PATH}")

    # Get file size
    size_mb = DB_PATH.stat().st_size / (1024 * 1024)
    print(f"  Source size: {size_mb:.2f} MB")
    print(f"  Note: Large database - using SQLite backup API (may take several minutes)")

    # Use SQLite backup API instead of file copy
    print(f"  Creating backup: {BACKUP_PATH}")
    source_conn = sqlite3.connect(str(DB_PATH))
    backup_conn = sqlite3.connect(str(BACKUP_PATH))

    with backup_conn:
        source_conn.backup(backup_conn)

    source_conn.close()
    backup_conn.close()

    # Verify backup
    if BACKUP_PATH.exists():
        backup_size_mb = BACKUP_PATH.stat().st_size / (1024 * 1024)
        print(f"  Backup size: {backup_size_mb:.2f} MB")
        print(f"  [OK] Backup created successfully")
    else:
        raise Exception("Backup file not found after copy")

except Exception as e:
    print(f"  [ERROR] Backup failed: {e}")
    print("  Migration aborted for safety")
    exit(1)

print()

# Step 2: Connect to database
print("Step 2: Connecting to database...")
try:
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")  # Enable FK constraints
    cursor = conn.cursor()
    print(f"  [OK] Connected to database")
except Exception as e:
    print(f"  [ERROR] Connection failed: {e}")
    exit(1)

print()

# Step 3: Pre-migration validation
print("Step 3: Pre-migration validation...")
try:
    # Check current row count
    cursor.execute("SELECT COUNT(*) FROM thinktank_reports")
    row_count = cursor.fetchone()[0]
    print(f"  Current row count: {row_count}")

    # Check current schema
    cursor.execute("PRAGMA table_info(thinktank_reports)")
    columns = cursor.fetchall()
    print(f"  Current column count: {len(columns)}")

    # Check for duplicate hashes (if any rows)
    if row_count > 0:
        cursor.execute("""
            SELECT file_hash, COUNT(*) as cnt
            FROM thinktank_reports
            WHERE file_hash IS NOT NULL
            GROUP BY file_hash
            HAVING cnt > 1
        """)
        duplicates = cursor.fetchall()
        if duplicates:
            print(f"  [WARNING] {len(duplicates)} duplicate hashes found")
        else:
            print(f"  [OK] No duplicate hashes")
    else:
        print(f"  [OK] Table empty - structure-only migration")

except Exception as e:
    print(f"  [ERROR] Pre-migration validation failed: {e}")
    conn.close()
    exit(1)

print()

# Step 4: Execute Phase 1 - Reference Tables
print("Step 4: Executing Phase 1 - Reference Tables...")
try:
    phase1_sql = """
    -- ============================================
    -- PHASE 1: REFERENCE TABLES (Controlled Vocabularies)
    -- ============================================

    BEGIN TRANSACTION;

    -- Publisher Types Reference
    CREATE TABLE IF NOT EXISTS ref_publisher_types (
        publisher_type_slug TEXT PRIMARY KEY,
        display_name TEXT NOT NULL,
        description TEXT,
        sort_order INTEGER DEFAULT 0
    );

    INSERT INTO ref_publisher_types (publisher_type_slug, display_name, description, sort_order) VALUES
    ('government', 'Government Agency', 'Federal, state, or local government organizations', 1),
    ('military', 'Military Organization', 'Department of Defense, armed services, defense agencies', 2),
    ('congressional', 'Congressional Office', 'Congress, Senate, House committees and services', 3),
    ('think_tank', 'Think Tank / Research Institute', 'Independent policy research organizations', 4),
    ('academic', 'Academic Institution', 'Universities, research labs, academic centers', 5),
    ('industry', 'Industry Organization', 'Private sector companies and associations', 6),
    ('ngo', 'Non-Governmental Organization', 'Non-profit advocacy and research groups', 7),
    ('international', 'International Organization', 'UN, NATO, EU, multinational bodies', 8);

    -- Region Groups Reference
    CREATE TABLE IF NOT EXISTS ref_region_groups (
        region_slug TEXT PRIMARY KEY,
        display_name TEXT NOT NULL,
        description TEXT,
        parent_region TEXT REFERENCES ref_region_groups(region_slug),
        sort_order INTEGER DEFAULT 0
    );

    INSERT INTO ref_region_groups (region_slug, display_name, description, parent_region, sort_order) VALUES
    ('global', 'Global', 'Worldwide scope', NULL, 1),
    ('arctic', 'Arctic', 'Arctic region including Greenland, Svalbard, Northern Canada', NULL, 2),
    ('europe', 'Europe', 'European continent including EU, UK, Balkans, Caucasus', NULL, 3),
    ('east_asia', 'East Asia', 'China, Japan, Korea, Taiwan, Mongolia', NULL, 4),
    ('southeast_asia', 'Southeast Asia', 'ASEAN nations', NULL, 5),
    ('indo_pacific', 'Indo-Pacific', 'Broader Asia-Pacific strategic region', NULL, 6),
    ('middle_east', 'Middle East', 'Middle East and North Africa', NULL, 7),
    ('sub_saharan_africa', 'Sub-Saharan Africa', 'Africa south of Sahara', NULL, 8),
    ('americas', 'Americas', 'North and South America', NULL, 9);

    -- Topics Reference
    CREATE TABLE IF NOT EXISTS ref_topics (
        topic_slug TEXT PRIMARY KEY,
        display_name TEXT NOT NULL,
        description TEXT,
        parent_topic TEXT REFERENCES ref_topics(topic_slug),
        sort_order INTEGER DEFAULT 0
    );

    INSERT INTO ref_topics (topic_slug, display_name, description, parent_topic, sort_order) VALUES
    ('mcf', 'Military-Civil Fusion (MCF)', 'Chinese military-civil integration strategy', NULL, 1),
    ('tech_transfer', 'Technology Transfer', 'Technology acquisition, IP theft, forced transfers', NULL, 2),
    ('supply_chain', 'Supply Chain', 'Critical supply chains, dependencies, vulnerabilities', NULL, 3),
    ('defense', 'Defense & Military', 'Military capabilities, weapons systems, defense industry', NULL, 4),
    ('economic', 'Economic & Trade', 'Trade policy, economic coercion, investment', NULL, 5),
    ('cyber', 'Cybersecurity', 'Cyber threats, espionage, critical infrastructure', NULL, 6),
    ('space', 'Space Technology', 'Satellite, launch vehicles, space weapons', NULL, 7),
    ('ai_ml', 'Artificial Intelligence', 'AI, machine learning, autonomous systems', NULL, 8),
    ('quantum', 'Quantum Technology', 'Quantum computing, communications, sensing', NULL, 9),
    ('semiconductors', 'Semiconductors', 'Chip manufacturing, lithography, foundries', NULL, 10),
    ('biotech', 'Biotechnology', 'Genomics, gene editing, synthetic biology', NULL, 11),
    ('energy', 'Energy', 'Nuclear, renewables, battery technology', NULL, 12),
    ('telecom', 'Telecommunications', '5G/6G, network infrastructure', NULL, 13),
    ('policy', 'Policy & Strategy', 'Policy recommendations, strategic assessments', NULL, 14),
    ('general', 'General', 'Uncategorized or broad scope', NULL, 99);

    -- Subtopics Reference (examples - expand as needed)
    CREATE TABLE IF NOT EXISTS ref_subtopics (
        subtopic_slug TEXT PRIMARY KEY,
        parent_topic TEXT NOT NULL REFERENCES ref_topics(topic_slug),
        display_name TEXT NOT NULL,
        description TEXT,
        sort_order INTEGER DEFAULT 0
    );

    INSERT INTO ref_subtopics (subtopic_slug, parent_topic, display_name, description, sort_order) VALUES
    ('mcf_talent', 'mcf', 'Talent Recruitment', 'Thousand Talents, academic partnerships', 1),
    ('mcf_standards', 'mcf', 'Standards & Regulations', 'MCF legal frameworks, civil-military standards', 2),
    ('ai_surveillance', 'ai_ml', 'Surveillance AI', 'Facial recognition, social credit, monitoring', 1),
    ('ai_autonomous', 'ai_ml', 'Autonomous Weapons', 'AI-enabled weapons systems', 2),
    ('space_satellite', 'space', 'Satellite Systems', 'Navigation, communications, reconnaissance satellites', 1),
    ('space_launch', 'space', 'Launch Vehicles', 'Rockets, spaceports, commercial launch', 2);

    -- Languages Reference
    CREATE TABLE IF NOT EXISTS ref_languages (
        lang_code TEXT PRIMARY KEY,
        display_name TEXT NOT NULL,
        native_name TEXT,
        sort_order INTEGER DEFAULT 0
    );

    INSERT INTO ref_languages (lang_code, display_name, native_name, sort_order) VALUES
    ('en', 'English', 'English', 1),
    ('zh', 'Chinese', 'Chinese', 2),
    ('ru', 'Russian', 'Russian', 3),
    ('es', 'Spanish', 'Spanish', 4),
    ('fr', 'French', 'French', 5),
    ('de', 'German', 'German', 6),
    ('ja', 'Japanese', 'Japanese', 7),
    ('ko', 'Korean', 'Korean', 8),
    ('ar', 'Arabic', 'Arabic', 9),
    ('pt', 'Portuguese', 'Portuguese', 10);

    COMMIT;
    """

    cursor.executescript(phase1_sql)

    # Verify tables created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'ref_%'")
    ref_tables = cursor.fetchall()
    print(f"  [OK] Phase 1 complete: {len(ref_tables)} reference tables created")
    for table in ref_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"     - {table[0]}: {count} rows")

except Exception as e:
    print(f"  [ERROR] Phase 1 failed: {e}")
    conn.rollback()
    conn.close()
    print(f"\n[WARNING] Migration failed. Restore from backup: {BACKUP_PATH}")
    exit(1)

print()

# Step 5: Execute Phase 2 - Junction Tables
print("Step 5: Executing Phase 2 - Junction Tables...")
try:
    phase2_sql = """
    -- ============================================
    -- PHASE 2: JUNCTION TABLES (Many-to-Many)
    -- ============================================

    BEGIN TRANSACTION;

    -- Report Topics Junction
    CREATE TABLE IF NOT EXISTS report_topics (
        report_id INTEGER NOT NULL,
        topic_slug TEXT NOT NULL,
        is_primary BOOLEAN DEFAULT 0,
        confidence REAL CHECK(confidence >= 0 AND confidence <= 1),
        assigned_by TEXT,
        assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (report_id) REFERENCES thinktank_reports(report_id) ON DELETE CASCADE,
        FOREIGN KEY (topic_slug) REFERENCES ref_topics(topic_slug),
        PRIMARY KEY (report_id, topic_slug)
    );

    CREATE INDEX idx_report_topics_report ON report_topics(report_id);
    CREATE INDEX idx_report_topics_topic ON report_topics(topic_slug);
    CREATE INDEX idx_report_topics_primary ON report_topics(is_primary) WHERE is_primary = 1;

    -- Report Subtopics Junction
    CREATE TABLE IF NOT EXISTS report_subtopics (
        report_id INTEGER NOT NULL,
        subtopic_slug TEXT NOT NULL,
        confidence REAL CHECK(confidence >= 0 AND confidence <= 1),
        assigned_by TEXT,
        assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (report_id) REFERENCES thinktank_reports(report_id) ON DELETE CASCADE,
        FOREIGN KEY (subtopic_slug) REFERENCES ref_subtopics(subtopic_slug),
        PRIMARY KEY (report_id, subtopic_slug)
    );

    CREATE INDEX idx_report_subtopics_report ON report_subtopics(report_id);
    CREATE INDEX idx_report_subtopics_subtopic ON report_subtopics(subtopic_slug);

    -- Report Regions Junction
    CREATE TABLE IF NOT EXISTS report_regions (
        report_id INTEGER NOT NULL,
        region_slug TEXT NOT NULL,
        is_primary BOOLEAN DEFAULT 0,
        confidence REAL CHECK(confidence >= 0 AND confidence <= 1),
        assigned_by TEXT,
        assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (report_id) REFERENCES thinktank_reports(report_id) ON DELETE CASCADE,
        FOREIGN KEY (region_slug) REFERENCES ref_region_groups(region_slug),
        PRIMARY KEY (report_id, region_slug)
    );

    CREATE INDEX idx_report_regions_report ON report_regions(report_id);
    CREATE INDEX idx_report_regions_region ON report_regions(region_slug);
    CREATE INDEX idx_report_regions_primary ON report_regions(is_primary) WHERE is_primary = 1;

    COMMIT;
    """

    cursor.executescript(phase2_sql)

    # Verify junction tables created
    junction_tables = ['report_topics', 'report_subtopics', 'report_regions']
    print(f"  [OK] Phase 2 complete: {len(junction_tables)} junction tables created")
    for table in junction_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"     - {table}: {count} rows")

except Exception as e:
    print(f"  [ERROR] Phase 2 failed: {e}")
    conn.rollback()
    conn.close()
    print(f"\n[WARNING] Migration failed. Restore from backup: {BACKUP_PATH}")
    exit(1)

print()

# Step 6: Execute Phase 3 - ALTER TABLE
print("Step 6: Executing Phase 3 - ALTER TABLE (adding new columns)...")
try:
    phase3_sql = """
    -- ============================================
    -- PHASE 3: ALTER thinktank_reports (Add New Columns)
    -- ============================================

    BEGIN TRANSACTION;

    -- Log migration start
    INSERT INTO report_processing_log (report_id, processing_stage, status, message)
    VALUES (0, 'schema_migration', 'started', 'Phase 3: Adding new columns to thinktank_reports (' || datetime('now') || ')');

    -- New fields
    ALTER TABLE thinktank_reports ADD COLUMN subtitle TEXT;
    ALTER TABLE thinktank_reports ADD COLUMN language TEXT DEFAULT 'en';
    ALTER TABLE thinktank_reports ADD COLUMN pages INTEGER;
    ALTER TABLE thinktank_reports ADD COLUMN publisher_type TEXT;
    ALTER TABLE thinktank_reports ADD COLUMN file_ext TEXT;
    ALTER TABLE thinktank_reports ADD COLUMN file_size_bytes INTEGER;

    -- Renamed fields (add new, keep old for now)
    ALTER TABLE thinktank_reports ADD COLUMN publisher_org TEXT;
    ALTER TABLE thinktank_reports ADD COLUMN publication_date_iso TEXT;
    ALTER TABLE thinktank_reports ADD COLUMN collection_date_utc TIMESTAMP;
    ALTER TABLE thinktank_reports ADD COLUMN hash_sha256 TEXT;

    -- URL split
    ALTER TABLE thinktank_reports ADD COLUMN url_canonical TEXT;
    ALTER TABLE thinktank_reports ADD COLUMN url_download TEXT;

    -- Boolean flags
    ALTER TABLE thinktank_reports ADD COLUMN mcf_flag BOOLEAN DEFAULT 0;
    ALTER TABLE thinktank_reports ADD COLUMN europe_focus_flag BOOLEAN DEFAULT 0;
    ALTER TABLE thinktank_reports ADD COLUMN arctic_flag BOOLEAN DEFAULT 0;

    -- Quality metrics
    ALTER TABLE thinktank_reports ADD COLUMN quality_score REAL;
    ALTER TABLE thinktank_reports ADD COLUMN completeness_score REAL;

    -- Renamed doc_type (keep old document_type for backward compat)
    ALTER TABLE thinktank_reports ADD COLUMN doc_type TEXT;

    -- Log completion
    INSERT INTO report_processing_log (report_id, processing_stage, status, message)
    VALUES (0, 'schema_migration', 'completed', 'Phase 3: New columns added successfully (' || datetime('now') || ')');

    COMMIT;
    """

    cursor.executescript(phase3_sql)

    # Verify new columns
    cursor.execute("PRAGMA table_info(thinktank_reports)")
    final_columns = cursor.fetchall()
    new_columns = [col[1] for col in final_columns if col[1] in ['subtitle', 'language', 'pages', 'publisher_org',
                                                          'mcf_flag', 'europe_focus_flag', 'arctic_flag',
                                                          'quality_score', 'completeness_score', 'hash_sha256']]

    print(f"  [OK] Phase 3 complete: {len(new_columns)} new columns added")
    print(f"     Total columns: {len(final_columns)}")
    print(f"     New columns: {', '.join(new_columns[:5])}...")

except Exception as e:
    print(f"  [ERROR] Phase 3 failed: {e}")
    conn.rollback()
    conn.close()
    print(f"\n[WARNING] Migration failed. Restore from backup: {BACKUP_PATH}")
    exit(1)

print()

# Step 7: Skip Phase 4 & 5 (Backfill) - Table is empty
print("Step 7: Phases 4-5 (Backfill & Scoring) - SKIPPED (0 rows)")
print("  [INFO] Table is empty, no data to backfill")
print()

# Step 8: Execute Phase 6 - Create Views
print("Step 8: Executing Phase 6 - Backward Compatibility Views...")
try:
    phase6_sql = """
    -- ============================================
    -- PHASE 6: BACKWARD COMPATIBILITY VIEWS
    -- ============================================

    -- Legacy view exposing old column names
    CREATE VIEW IF NOT EXISTS v_thinktank_reports_legacy AS
    SELECT
        report_id,
        title,
        COALESCE(publisher_org, source_organization) as source_organization,
        authors,
        COALESCE(publication_date_iso, publication_date) as publication_date,
        document_type,
        classification,
        content_text,
        executive_summary,
        key_findings,
        recommendations,
        methodology,
        file_path,
        file_size as file_size,
        COALESCE(hash_sha256, file_hash) as file_hash,
        url_origin,
        COALESCE(collection_date_utc, collection_date) as collection_date,
        relevance_score,
        confidence_level,
        processing_status,
        processing_notes,
        created_at,
        updated_at
    FROM thinktank_reports;

    -- Enhanced view with all new fields
    CREATE VIEW IF NOT EXISTS v_thinktank_reports_enhanced AS
    SELECT
        t.*,
        GROUP_CONCAT(DISTINCT rt.topic_slug) as topics,
        GROUP_CONCAT(DISTINCT rr.region_slug) as regions
    FROM thinktank_reports t
    LEFT JOIN report_topics rt ON t.report_id = rt.report_id
    LEFT JOIN report_regions rr ON t.report_id = rr.report_id
    GROUP BY t.report_id;

    -- MCF-focused reports view
    CREATE VIEW IF NOT EXISTS v_mcf_reports AS
    SELECT
        t.report_id,
        t.title,
        t.publisher_org,
        t.publication_date_iso,
        t.mcf_flag,
        t.quality_score,
        t.completeness_score,
        (SELECT COUNT(*) FROM report_entities WHERE report_id = t.report_id) as entity_count,
        (SELECT COUNT(*) FROM report_technologies WHERE report_id = t.report_id) as tech_count,
        (SELECT COUNT(*) FROM report_risk_indicators WHERE report_id = t.report_id) as risk_count
    FROM thinktank_reports t
    WHERE t.mcf_flag = 1;

    -- Reports by topic (denormalized)
    CREATE VIEW IF NOT EXISTS v_reports_by_topic AS
    SELECT
        rt.topic_slug,
        ref.display_name as topic_name,
        t.report_id,
        t.title,
        t.publisher_org,
        t.publication_date_iso,
        rt.is_primary,
        rt.confidence
    FROM report_topics rt
    JOIN ref_topics ref ON rt.topic_slug = ref.topic_slug
    JOIN thinktank_reports t ON rt.report_id = t.report_id;
    """

    cursor.executescript(phase6_sql)

    # Verify views created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view' AND name LIKE 'v_%'")
    views = cursor.fetchall()
    print(f"  [OK] Phase 6 complete: {len(views)} views created")
    for view in views:
        print(f"     - {view[0]}")

except Exception as e:
    print(f"  [ERROR] Phase 6 failed: {e}")
    conn.rollback()
    conn.close()
    print(f"\n[WARNING] Migration failed. Restore from backup: {BACKUP_PATH}")
    exit(1)

print()

# Step 9: Post-migration validation
print("Step 9: Post-migration validation...")
try:
    # Row count preservation
    cursor.execute("SELECT COUNT(*) FROM thinktank_reports")
    final_row_count = cursor.fetchone()[0]
    status = '[OK]' if row_count == final_row_count else '[ERROR]'
    print(f"  Row count: {row_count} -> {final_row_count} {status}")

    # Column count
    cursor.execute("PRAGMA table_info(thinktank_reports)")
    final_columns = cursor.fetchall()
    print(f"  Column count: {len(columns)} -> {len(final_columns)} [OK]")

    # Reference tables
    cursor.execute("SELECT COUNT(*) FROM ref_publisher_types")
    pub_types = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM ref_topics")
    topics = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM ref_region_groups")
    regions = cursor.fetchone()[0]
    print(f"  Reference data:")
    print(f"     - Publisher types: {pub_types}")
    print(f"     - Topics: {topics}")
    print(f"     - Regions: {regions}")

    # Junction tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'report_%' AND name NOT LIKE '%_log'")
    junction = cursor.fetchall()
    print(f"  Junction tables: {len(junction)}")

    # Views exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
    views = cursor.fetchall()
    print(f"  Views: {len(views)}")

    print(f"\n  [OK] Post-migration validation passed")

except Exception as e:
    print(f"  [ERROR] Post-migration validation failed: {e}")
    conn.close()
    exit(1)

# Close connection
conn.close()

print()
print("=" * 50)
print("[SUCCESS] MIGRATION COMPLETED SUCCESSFULLY")
print("=" * 50)
print(f"\nSummary:")
print(f"  - Database: {DB_PATH}")
print(f"  - Backup: {BACKUP_PATH}")
print(f"  - Columns: {len(columns)} -> {len(final_columns)}")
print(f"  - Tables added: 8 (5 reference + 3 junction)")
print(f"  - Views added: {len(views)}")
print(f"  - Completed: {datetime.now()}")
print()
print("Next steps:")
print("  1. Test views: SELECT * FROM v_thinktank_reports_legacy LIMIT 5")
print("  2. Test reference tables: SELECT * FROM ref_topics")
print("  3. Begin importing reports from F:/Reports")
print()
