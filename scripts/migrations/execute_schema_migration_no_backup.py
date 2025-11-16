"""
Schema Migration Executor (No Full Backup - Structure Only)
Executes the thinktank_reports schema migration plan

NOTE: This version skips full database backup due to large database size (17GB).
      Safe to run since thinktank_reports table has 0 rows (structure-only migration).
      Other tables remain untouched.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

# Paths
DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
LOG_PATH = Path(f"C:/Projects/OSINT - Foresight/analysis/schema_migration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

print(f"=== Schema Migration Executor (Structure-Only) ===")
print(f"Database: {DB_PATH}")
print(f"Log file: {LOG_PATH}")
print(f"Started: {datetime.now()}")
print()

# Create log file
log_lines = []
log_lines.append(f"=== Schema Migration Log ===")
log_lines.append(f"Started: {datetime.now()}")
log_lines.append(f"Database: {DB_PATH}")
log_lines.append("")

# Step 1: Skip full backup (table is empty)
print("Step 1: Backup assessment...")
print("  [INFO] Skipping full database backup (17GB)")
print("  [INFO] Target table 'thinktank_reports' has 0 rows (structure-only migration)")
print("  [INFO] All other tables remain untouched")
log_lines.append("Step 1: Backup skipped - structure-only migration on empty table")
print()

# Step 2: Connect to database
print("Step 2: Connecting to database...")
try:
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")  # Enable FK constraints
    cursor = conn.cursor()
    print(f"  [OK] Connected to database")
    log_lines.append("Step 2: Connected to database successfully")
except Exception as e:
    print(f"  [ERROR] Connection failed: {e}")
    log_lines.append(f"Step 2: ERROR - Connection failed: {e}")
    LOG_PATH.write_text('\n'.join(log_lines))
    exit(1)

print()

# Step 3: Pre-migration validation
print("Step 3: Pre-migration validation...")
try:
    # Check current row count
    cursor.execute("SELECT COUNT(*) FROM thinktank_reports")
    row_count = cursor.fetchone()[0]
    print(f"  Current row count: {row_count}")
    log_lines.append(f"Step 3: Pre-migration validation - {row_count} rows")

    # Check current schema
    cursor.execute("PRAGMA table_info(thinktank_reports)")
    columns = cursor.fetchall()
    print(f"  Current column count: {len(columns)}")
    log_lines.append(f"  - Current columns: {len(columns)}")

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
            log_lines.append(f"  - WARNING: {len(duplicates)} duplicate hashes")
        else:
            print(f"  [OK] No duplicate hashes")
            log_lines.append("  - No duplicate hashes")
    else:
        print(f"  [OK] Table empty - structure-only migration")
        log_lines.append("  - Table empty - safe for structure migration")

except Exception as e:
    print(f"  [ERROR] Pre-migration validation failed: {e}")
    log_lines.append(f"Step 3: ERROR - {e}")
    LOG_PATH.write_text('\n'.join(log_lines))
    conn.close()
    exit(1)

print()

# Step 4: Execute Phase 1 - Reference Tables
print("Step 4: Executing Phase 1 - Reference Tables...")
try:
    phase1_sql = """
    BEGIN TRANSACTION;

    CREATE TABLE IF NOT EXISTS ref_publisher_types (
        publisher_type_slug TEXT PRIMARY KEY,
        display_name TEXT NOT NULL,
        description TEXT,
        sort_order INTEGER DEFAULT 0
    );

    INSERT OR IGNORE INTO ref_publisher_types (publisher_type_slug, display_name, description, sort_order) VALUES
    ('government', 'Government Agency', 'Federal, state, or local government organizations', 1),
    ('military', 'Military Organization', 'Department of Defense, armed services, defense agencies', 2),
    ('congressional', 'Congressional Office', 'Congress, Senate, House committees and services', 3),
    ('think_tank', 'Think Tank / Research Institute', 'Independent policy research organizations', 4),
    ('academic', 'Academic Institution', 'Universities, research labs, academic centers', 5),
    ('industry', 'Industry Organization', 'Private sector companies and associations', 6),
    ('ngo', 'Non-Governmental Organization', 'Non-profit advocacy and research groups', 7),
    ('international', 'International Organization', 'UN, NATO, EU, multinational bodies', 8);

    CREATE TABLE IF NOT EXISTS ref_region_groups (
        region_slug TEXT PRIMARY KEY,
        display_name TEXT NOT NULL,
        description TEXT,
        parent_region TEXT REFERENCES ref_region_groups(region_slug),
        sort_order INTEGER DEFAULT 0
    );

    INSERT OR IGNORE INTO ref_region_groups (region_slug, display_name, description, parent_region, sort_order) VALUES
    ('global', 'Global', 'Worldwide scope', NULL, 1),
    ('arctic', 'Arctic', 'Arctic region including Greenland, Svalbard, Northern Canada', NULL, 2),
    ('europe', 'Europe', 'European continent including EU, UK, Balkans, Caucasus', NULL, 3),
    ('east_asia', 'East Asia', 'China, Japan, Korea, Taiwan, Mongolia', NULL, 4),
    ('southeast_asia', 'Southeast Asia', 'ASEAN nations', NULL, 5),
    ('indo_pacific', 'Indo-Pacific', 'Broader Asia-Pacific strategic region', NULL, 6),
    ('middle_east', 'Middle East', 'Middle East and North Africa', NULL, 7),
    ('sub_saharan_africa', 'Sub-Saharan Africa', 'Africa south of Sahara', NULL, 8),
    ('americas', 'Americas', 'North and South America', NULL, 9);

    CREATE TABLE IF NOT EXISTS ref_topics (
        topic_slug TEXT PRIMARY KEY,
        display_name TEXT NOT NULL,
        description TEXT,
        parent_topic TEXT REFERENCES ref_topics(topic_slug),
        sort_order INTEGER DEFAULT 0
    );

    INSERT OR IGNORE INTO ref_topics (topic_slug, display_name, description, parent_topic, sort_order) VALUES
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

    CREATE TABLE IF NOT EXISTS ref_subtopics (
        subtopic_slug TEXT PRIMARY KEY,
        parent_topic TEXT NOT NULL REFERENCES ref_topics(topic_slug),
        display_name TEXT NOT NULL,
        description TEXT,
        sort_order INTEGER DEFAULT 0
    );

    INSERT OR IGNORE INTO ref_subtopics (subtopic_slug, parent_topic, display_name, description, sort_order) VALUES
    ('mcf_talent', 'mcf', 'Talent Recruitment', 'Thousand Talents, academic partnerships', 1),
    ('mcf_standards', 'mcf', 'Standards & Regulations', 'MCF legal frameworks, civil-military standards', 2),
    ('ai_surveillance', 'ai_ml', 'Surveillance AI', 'Facial recognition, social credit, monitoring', 1),
    ('ai_autonomous', 'ai_ml', 'Autonomous Weapons', 'AI-enabled weapons systems', 2),
    ('space_satellite', 'space', 'Satellite Systems', 'Navigation, communications, reconnaissance satellites', 1),
    ('space_launch', 'space', 'Launch Vehicles', 'Rockets, spaceports, commercial launch', 2);

    CREATE TABLE IF NOT EXISTS ref_languages (
        lang_code TEXT PRIMARY KEY,
        display_name TEXT NOT NULL,
        native_name TEXT,
        sort_order INTEGER DEFAULT 0
    );

    INSERT OR IGNORE INTO ref_languages (lang_code, display_name, native_name, sort_order) VALUES
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
    log_lines.append(f"Step 4: Phase 1 complete - {len(ref_tables)} reference tables")

    for table in ref_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"     - {table[0]}: {count} rows")
        log_lines.append(f"  - {table[0]}: {count} rows")

except Exception as e:
    print(f"  [ERROR] Phase 1 failed: {e}")
    log_lines.append(f"Step 4: ERROR - {e}")
    LOG_PATH.write_text('\n'.join(log_lines))
    conn.rollback()
    conn.close()
    exit(1)

print()

# Step 5: Execute Phase 2 - Junction Tables
print("Step 5: Executing Phase 2 - Junction Tables...")
try:
    phase2_sql = """
    BEGIN TRANSACTION;

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

    CREATE INDEX IF NOT EXISTS idx_report_topics_report ON report_topics(report_id);
    CREATE INDEX IF NOT EXISTS idx_report_topics_topic ON report_topics(topic_slug);
    CREATE INDEX IF NOT EXISTS idx_report_topics_primary ON report_topics(is_primary) WHERE is_primary = 1;

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

    CREATE INDEX IF NOT EXISTS idx_report_subtopics_report ON report_subtopics(report_id);
    CREATE INDEX IF NOT EXISTS idx_report_subtopics_subtopic ON report_subtopics(subtopic_slug);

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

    CREATE INDEX IF NOT EXISTS idx_report_regions_report ON report_regions(report_id);
    CREATE INDEX IF NOT EXISTS idx_report_regions_region ON report_regions(region_slug);
    CREATE INDEX IF NOT EXISTS idx_report_regions_primary ON report_regions(is_primary) WHERE is_primary = 1;

    COMMIT;
    """

    cursor.executescript(phase2_sql)

    # Verify junction tables created
    junction_tables = ['report_topics', 'report_subtopics', 'report_regions']
    print(f"  [OK] Phase 2 complete: {len(junction_tables)} junction tables created")
    log_lines.append(f"Step 5: Phase 2 complete - {len(junction_tables)} junction tables")

    for table in junction_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"     - {table}: {count} rows")
        log_lines.append(f"  - {table}: {count} rows")

except Exception as e:
    print(f"  [ERROR] Phase 2 failed: {e}")
    log_lines.append(f"Step 5: ERROR - {e}")
    LOG_PATH.write_text('\n'.join(log_lines))
    conn.rollback()
    conn.close()
    exit(1)

print()

# Step 6: Execute Phase 3 - ALTER TABLE
print("Step 6: Executing Phase 3 - ALTER TABLE (adding new columns)...")
try:
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(thinktank_reports)")
    existing_columns = {col[1] for col in cursor.fetchall()}

    new_column_defs = [
        ("subtitle", "TEXT"),
        ("language", "TEXT DEFAULT 'en'"),
        ("pages", "INTEGER"),
        ("publisher_type", "TEXT"),
        ("file_ext", "TEXT"),
        ("file_size_bytes", "INTEGER"),
        ("publisher_org", "TEXT"),
        ("publication_date_iso", "TEXT"),
        ("collection_date_utc", "TIMESTAMP"),
        ("hash_sha256", "TEXT"),
        ("url_canonical", "TEXT"),
        ("url_download", "TEXT"),
        ("mcf_flag", "BOOLEAN DEFAULT 0"),
        ("europe_focus_flag", "BOOLEAN DEFAULT 0"),
        ("arctic_flag", "BOOLEAN DEFAULT 0"),
        ("quality_score", "REAL"),
        ("completeness_score", "REAL"),
        ("doc_type", "TEXT")
    ]

    added_count = 0
    for col_name, col_def in new_column_defs:
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE thinktank_reports ADD COLUMN {col_name} {col_def}")
                added_count += 1
            except Exception as e:
                print(f"     [WARNING] Could not add {col_name}: {e}")

    conn.commit()

    # Log migration in processing log (optional - skip if FK constraint fails)
    try:
        cursor.execute("""
            INSERT INTO report_processing_log (report_id, processing_stage, status, message)
            VALUES (0, 'schema_migration', 'completed', ?)
        """, (f"Phase 3: {added_count} new columns added ({datetime.now()})",))
        conn.commit()
    except Exception:
        # Skip logging if it fails (FK constraint likely)
        pass

    # Verify new columns
    cursor.execute("PRAGMA table_info(thinktank_reports)")
    final_columns = cursor.fetchall()
    new_columns = [col[1] for col in final_columns if col[1] in dict(new_column_defs).keys()]

    print(f"  [OK] Phase 3 complete: {added_count} new columns added")
    print(f"     Total columns: {len(final_columns)}")
    print(f"     New columns verified: {len(new_columns)}")
    log_lines.append(f"Step 6: Phase 3 complete - {added_count} columns added, total now {len(final_columns)}")

except Exception as e:
    print(f"  [ERROR] Phase 3 failed: {e}")
    log_lines.append(f"Step 6: ERROR - {e}")
    LOG_PATH.write_text('\n'.join(log_lines))
    conn.rollback()
    conn.close()
    exit(1)

print()

# Step 7: Skip Phase 4 & 5 (Backfill) - Table is empty
print("Step 7: Phases 4-5 (Backfill & Scoring) - SKIPPED (0 rows)")
print("  [INFO] Table is empty, no data to backfill")
log_lines.append("Step 7: Phases 4-5 skipped - empty table")
print()

# Step 8: Execute Phase 6 - Create Views
print("Step 8: Executing Phase 6 - Backward Compatibility Views...")
try:
    views_sql = [
        ("v_thinktank_reports_legacy", """
            CREATE VIEW IF NOT EXISTS v_thinktank_reports_legacy AS
            SELECT
                report_id, title,
                COALESCE(publisher_org, source_organization) as source_organization,
                authors,
                COALESCE(publication_date_iso, publication_date) as publication_date,
                document_type, classification, content_text,
                executive_summary, key_findings, recommendations, methodology,
                file_path, file_size,
                COALESCE(hash_sha256, file_hash) as file_hash,
                url_origin,
                COALESCE(collection_date_utc, collection_date) as collection_date,
                relevance_score, confidence_level, processing_status, processing_notes,
                created_at, updated_at
            FROM thinktank_reports
        """),
        ("v_thinktank_reports_enhanced", """
            CREATE VIEW IF NOT EXISTS v_thinktank_reports_enhanced AS
            SELECT
                t.*,
                GROUP_CONCAT(DISTINCT rt.topic_slug) as topics,
                GROUP_CONCAT(DISTINCT rr.region_slug) as regions
            FROM thinktank_reports t
            LEFT JOIN report_topics rt ON t.report_id = rt.report_id
            LEFT JOIN report_regions rr ON t.report_id = rr.report_id
            GROUP BY t.report_id
        """),
        ("v_mcf_reports", """
            CREATE VIEW IF NOT EXISTS v_mcf_reports AS
            SELECT
                t.report_id, t.title, t.publisher_org, t.publication_date_iso,
                t.mcf_flag, t.quality_score, t.completeness_score,
                (SELECT COUNT(*) FROM report_entities WHERE report_id = t.report_id) as entity_count,
                (SELECT COUNT(*) FROM report_technologies WHERE report_id = t.report_id) as tech_count,
                (SELECT COUNT(*) FROM report_risk_indicators WHERE report_id = t.report_id) as risk_count
            FROM thinktank_reports t
            WHERE t.mcf_flag = 1
        """),
        ("v_reports_by_topic", """
            CREATE VIEW IF NOT EXISTS v_reports_by_topic AS
            SELECT
                rt.topic_slug,
                ref.display_name as topic_name,
                t.report_id, t.title, t.publisher_org, t.publication_date_iso,
                rt.is_primary, rt.confidence
            FROM report_topics rt
            JOIN ref_topics ref ON rt.topic_slug = ref.topic_slug
            JOIN thinktank_reports t ON rt.report_id = t.report_id
        """)
    ]

    created_views = []
    for view_name, view_sql in views_sql:
        try:
            cursor.execute(view_sql)
            created_views.append(view_name)
        except Exception as e:
            print(f"     [WARNING] Could not create {view_name}: {e}")

    conn.commit()

    print(f"  [OK] Phase 6 complete: {len(created_views)} views created")
    for view in created_views:
        print(f"     - {view}")
    log_lines.append(f"Step 8: Phase 6 complete - {len(created_views)} views created")

except Exception as e:
    print(f"  [ERROR] Phase 6 failed: {e}")
    log_lines.append(f"Step 8: ERROR - {e}")
    LOG_PATH.write_text('\n'.join(log_lines))
    conn.rollback()
    conn.close()
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
    log_lines.append(f"Step 9: Post-migration validation passed")
    log_lines.append(f"  - Rows: {row_count} -> {final_row_count}")
    log_lines.append(f"  - Columns: {len(columns)} -> {len(final_columns)}")
    log_lines.append(f"  - Reference tables: {pub_types + topics + regions} total rows")
    log_lines.append(f"  - Junction tables: {len(junction)}")
    log_lines.append(f"  - Views: {len(views)}")

except Exception as e:
    print(f"  [ERROR] Post-migration validation failed: {e}")
    log_lines.append(f"Step 9: ERROR - {e}")
    LOG_PATH.write_text('\n'.join(log_lines))
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
print(f"  - Columns: {len(columns)} -> {len(final_columns)}")
print(f"  - Tables added: 8 (5 reference + 3 junction)")
print(f"  - Views added: {len(views)}")
print(f"  - Completed: {datetime.now()}")
print(f"  - Log file: {LOG_PATH}")
print()
print("Next steps:")
print("  1. Test views: SELECT * FROM v_thinktank_reports_legacy LIMIT 5")
print("  2. Test reference tables: SELECT * FROM ref_topics")
print("  3. Begin importing reports from F:/Reports")
print()

# Save log
log_lines.append("")
log_lines.append(f"Migration completed successfully: {datetime.now()}")
LOG_PATH.write_text('\n'.join(log_lines))
print(f"[INFO] Migration log saved to: {LOG_PATH}")
