#!/usr/bin/env python3
"""
Companies House UK Integration Script
Merges UK company data into osint_master.db with GLEIF cross-referencing
"""

import sqlite3
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('companies_house_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

SOURCE_DB = Path("F:/OSINT_Data/CompaniesHouse_UK/uk_companies_20251001.db")
TARGET_DB = Path("F:/OSINT_WAREHOUSE/osint_master.db")


def connect_with_wal(db_path, timeout=120):
    """Connect to database with WAL mode"""
    conn = sqlite3.connect(db_path, timeout=timeout)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def create_tables(cursor):
    """Create Companies House tables in master database"""

    logger.info("Creating Companies House tables...")

    # Companies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies_house_uk_companies (
            company_number TEXT PRIMARY KEY,
            company_name TEXT,
            company_status TEXT,
            incorporation_date TEXT,
            registered_address TEXT,
            company_type TEXT,
            sic_codes TEXT,
            accounts_category TEXT,
            provenance_file TEXT,
            provenance_line INTEGER,
            record_hash TEXT,
            processing_timestamp TEXT,
            imported_date TEXT
        )
    """)

    # PSC (People with Significant Control) table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies_house_uk_psc (
            psc_id TEXT PRIMARY KEY,
            company_number TEXT,
            psc_name TEXT,
            nationality TEXT,
            country_of_residence TEXT,
            ownership_percentage REAL,
            control_types TEXT,
            psc_kind TEXT,
            address TEXT,
            natures_of_control TEXT,
            notified_on TEXT,
            ceased_on TEXT,
            provenance_file TEXT,
            record_hash TEXT,
            processing_timestamp TEXT,
            imported_date TEXT,
            FOREIGN KEY (company_number) REFERENCES companies_house_uk_companies(company_number)
        )
    """)

    # China connections table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies_house_uk_china_connections (
            connection_id TEXT PRIMARY KEY,
            company_number TEXT,
            detection_layer TEXT,
            evidence TEXT,
            confidence_score INTEGER,
            timestamp TEXT,
            imported_date TEXT,
            FOREIGN KEY (company_number) REFERENCES companies_house_uk_companies(company_number)
        )
    """)

    # Cross-reference table: Companies House → GLEIF
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies_house_gleif_xref (
            company_number TEXT,
            gleif_lei TEXT,
            match_type TEXT,
            match_confidence INTEGER,
            created_date TEXT,
            PRIMARY KEY (company_number, gleif_lei),
            FOREIGN KEY (company_number) REFERENCES companies_house_uk_companies(company_number),
            FOREIGN KEY (gleif_lei) REFERENCES gleif_entities(lei)
        )
    """)

    logger.info("Tables created successfully")


def copy_companies(source_conn, target_conn):
    """Copy companies from source to target"""

    logger.info("Copying companies...")
    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()

    source_cursor.execute("SELECT COUNT(*) FROM companies")
    total = source_cursor.fetchone()[0]
    logger.info(f"Total companies to copy: {total:,}")

    imported_date = datetime.now(timezone.utc).isoformat()

    source_cursor.execute("SELECT * FROM companies")
    batch = []
    batch_size = 1000
    copied = 0

    for row in source_cursor:
        batch.append(row + (imported_date,))

        if len(batch) >= batch_size:
            target_cursor.executemany("""
                INSERT OR REPLACE INTO companies_house_uk_companies
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batch)
            target_conn.commit()
            copied += len(batch)
            logger.info(f"Copied {copied:,} / {total:,} companies ({copied/total*100:.1f}%)")
            batch = []

    # Final batch
    if batch:
        target_cursor.executemany("""
            INSERT OR REPLACE INTO companies_house_uk_companies
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, batch)
        target_conn.commit()
        copied += len(batch)

    logger.info(f"Companies copied: {copied:,}")
    return copied


def copy_psc(source_conn, target_conn):
    """Copy PSC (People with Significant Control) records"""

    logger.info("Copying PSC records...")
    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()

    source_cursor.execute("SELECT COUNT(*) FROM psc")
    total = source_cursor.fetchone()[0]
    logger.info(f"Total PSC records to copy: {total:,}")

    imported_date = datetime.now(timezone.utc).isoformat()

    source_cursor.execute("SELECT * FROM psc")
    batch = []
    batch_size = 1000
    copied = 0

    for row in source_cursor:
        batch.append(row + (imported_date,))

        if len(batch) >= batch_size:
            target_cursor.executemany("""
                INSERT OR REPLACE INTO companies_house_uk_psc
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batch)
            target_conn.commit()
            copied += len(batch)
            if copied % 10000 == 0:
                logger.info(f"Copied {copied:,} / {total:,} PSC records ({copied/total*100:.1f}%)")
            batch = []

    # Final batch
    if batch:
        target_cursor.executemany("""
            INSERT OR REPLACE INTO companies_house_uk_psc
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, batch)
        target_conn.commit()
        copied += len(batch)

    logger.info(f"PSC records copied: {copied:,}")
    return copied


def copy_china_connections(source_conn, target_conn):
    """Copy China connection detections"""

    logger.info("Copying China connections...")
    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()

    source_cursor.execute("SELECT COUNT(*) FROM china_connections")
    total = source_cursor.fetchone()[0]
    logger.info(f"Total China connections to copy: {total:,}")

    imported_date = datetime.now(timezone.utc).isoformat()

    source_cursor.execute("SELECT * FROM china_connections")
    batch = []
    batch_size = 1000
    copied = 0

    for row in source_cursor:
        batch.append(row + (imported_date,))

        if len(batch) >= batch_size:
            target_cursor.executemany("""
                INSERT OR REPLACE INTO companies_house_uk_china_connections
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, batch)
            target_conn.commit()
            copied += len(batch)
            if copied % 10000 == 0:
                logger.info(f"Copied {copied:,} / {total:,} China connections ({copied/total*100:.1f}%)")
            batch = []

    # Final batch
    if batch:
        target_cursor.executemany("""
            INSERT OR REPLACE INTO companies_house_uk_china_connections
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, batch)
        target_conn.commit()
        copied += len(batch)

    logger.info(f"China connections copied: {copied:,}")
    return copied


def create_gleif_crossref(target_conn):
    """Create cross-reference between Companies House and GLEIF entities"""

    logger.info("Creating GLEIF cross-references...")
    cursor = target_conn.cursor()

    created_date = datetime.now(timezone.utc).isoformat()

    # Match on company name similarity (basic exact match for now)
    # More sophisticated matching can be added later
    logger.info("Matching Companies House → GLEIF by company name...")

    cursor.execute("""
        INSERT OR IGNORE INTO companies_house_gleif_xref
        (company_number, gleif_lei, match_type, match_confidence, created_date)
        SELECT
            ch.company_number,
            g.lei,
            'exact_name' as match_type,
            95 as match_confidence,
            ? as created_date
        FROM companies_house_uk_companies ch
        JOIN gleif_entities g ON LOWER(TRIM(ch.company_name)) = LOWER(TRIM(g.legal_name))
        WHERE ch.company_name IS NOT NULL
          AND g.legal_name IS NOT NULL
          AND LENGTH(ch.company_name) > 0
    """, (created_date,))

    exact_matches = cursor.rowcount
    target_conn.commit()
    logger.info(f"Exact name matches: {exact_matches:,}")

    # Match on OpenCorporates mapping (Companies House uses UK company numbers)
    logger.info("Matching via GLEIF OpenCorporates mapping...")

    cursor.execute("""
        INSERT OR IGNORE INTO companies_house_gleif_xref
        (company_number, gleif_lei, match_type, match_confidence, created_date)
        SELECT
            ch.company_number,
            oc.lei,
            'opencorporates' as match_type,
            100 as match_confidence,
            ? as created_date
        FROM companies_house_uk_companies ch
        JOIN gleif_opencorporates_mapping oc
          ON 'gb/' || ch.company_number = oc.opencorporates_id
          OR 'uk/' || ch.company_number = oc.opencorporates_id
    """, (created_date,))

    oc_matches = cursor.rowcount
    target_conn.commit()
    logger.info(f"OpenCorporates matches: {oc_matches:,}")

    total_matches = exact_matches + oc_matches
    logger.info(f"Total GLEIF cross-references created: {total_matches:,}")

    return total_matches


def create_indexes(cursor):
    """Create indexes for performance"""

    logger.info("Creating indexes...")

    indexes = [
        # Companies table
        ("idx_ch_uk_companies_name", "companies_house_uk_companies(company_name)"),
        ("idx_ch_uk_companies_status", "companies_house_uk_companies(company_status)"),
        ("idx_ch_uk_companies_type", "companies_house_uk_companies(company_type)"),

        # PSC table
        ("idx_ch_uk_psc_company", "companies_house_uk_psc(company_number)"),
        ("idx_ch_uk_psc_name", "companies_house_uk_psc(psc_name)"),
        ("idx_ch_uk_psc_nationality", "companies_house_uk_psc(nationality)"),
        ("idx_ch_uk_psc_residence", "companies_house_uk_psc(country_of_residence)"),

        # China connections table
        ("idx_ch_uk_china_company", "companies_house_uk_china_connections(company_number)"),
        ("idx_ch_uk_china_layer", "companies_house_uk_china_connections(detection_layer)"),
        ("idx_ch_uk_china_confidence", "companies_house_uk_china_connections(confidence_score)"),

        # Cross-reference table
        ("idx_ch_gleif_xref_lei", "companies_house_gleif_xref(gleif_lei)"),
        ("idx_ch_gleif_xref_type", "companies_house_gleif_xref(match_type)"),
    ]

    for idx_name, idx_def in indexes:
        cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {idx_def}")

    logger.info(f"Created {len(indexes)} indexes")


def generate_summary(target_conn):
    """Generate integration summary statistics"""

    logger.info("=" * 80)
    logger.info("INTEGRATION SUMMARY")
    logger.info("=" * 80)

    cursor = target_conn.cursor()

    # Record counts
    companies = cursor.execute("SELECT COUNT(*) FROM companies_house_uk_companies").fetchone()[0]
    psc = cursor.execute("SELECT COUNT(*) FROM companies_house_uk_psc").fetchone()[0]
    china = cursor.execute("SELECT COUNT(*) FROM companies_house_uk_china_connections").fetchone()[0]
    xref = cursor.execute("SELECT COUNT(*) FROM companies_house_gleif_xref").fetchone()[0]

    logger.info(f"Companies:           {companies:,}")
    logger.info(f"PSC Records:         {psc:,}")
    logger.info(f"China Connections:   {china:,}")
    logger.info(f"GLEIF Cross-refs:    {xref:,}")
    logger.info("")

    # Companies with China connections
    china_companies = cursor.execute("""
        SELECT COUNT(DISTINCT company_number)
        FROM companies_house_uk_china_connections
    """).fetchone()[0]
    logger.info(f"Companies with China links: {china_companies:,} ({china_companies/companies*100:.1f}%)")

    # Companies with GLEIF match
    gleif_companies = cursor.execute("""
        SELECT COUNT(DISTINCT company_number)
        FROM companies_house_gleif_xref
    """).fetchone()[0]
    logger.info(f"Companies matched to GLEIF: {gleif_companies:,} ({gleif_companies/companies*100:.1f}%)")

    # Top detection layers
    logger.info("")
    logger.info("Top China Detection Layers:")
    cursor.execute("""
        SELECT detection_layer, COUNT(*) as cnt
        FROM companies_house_uk_china_connections
        GROUP BY detection_layer
        ORDER BY cnt DESC
        LIMIT 10
    """)
    for layer, count in cursor.fetchall():
        logger.info(f"  {layer:30s}: {count:,}")

    # Top PSC nationalities
    logger.info("")
    logger.info("Top PSC Nationalities:")
    cursor.execute("""
        SELECT nationality, COUNT(*) as cnt
        FROM companies_house_uk_psc
        WHERE nationality IS NOT NULL AND nationality != ''
        GROUP BY nationality
        ORDER BY cnt DESC
        LIMIT 10
    """)
    for nat, count in cursor.fetchall():
        logger.info(f"  {nat:30s}: {count:,}")

    # Chinese PSC
    chinese_psc = cursor.execute("""
        SELECT COUNT(*)
        FROM companies_house_uk_psc
        WHERE nationality = 'Chinese'
           OR country_of_residence = 'China'
           OR country_of_residence = 'Hong Kong'
    """).fetchone()[0]
    logger.info("")
    logger.info(f"PSC with Chinese nationality/residence: {chinese_psc:,}")

    logger.info("=" * 80)


def main():
    """Main integration workflow"""

    logger.info("=" * 80)
    logger.info("COMPANIES HOUSE UK INTEGRATION")
    logger.info("=" * 80)
    logger.info(f"Source: {SOURCE_DB}")
    logger.info(f"Target: {TARGET_DB}")
    logger.info("")

    start_time = time.time()

    try:
        # Connect to databases
        logger.info("Connecting to databases...")
        source_conn = connect_with_wal(SOURCE_DB)
        target_conn = connect_with_wal(TARGET_DB)

        target_cursor = target_conn.cursor()

        # Create tables
        create_tables(target_cursor)
        target_conn.commit()

        # Copy data
        companies_copied = copy_companies(source_conn, target_conn)
        psc_copied = copy_psc(source_conn, target_conn)
        china_copied = copy_china_connections(source_conn, target_conn)

        # Create GLEIF cross-references
        xref_created = create_gleif_crossref(target_conn)

        # Create indexes
        create_indexes(target_cursor)
        target_conn.commit()

        # Generate summary
        generate_summary(target_conn)

        # Close connections
        source_conn.close()
        target_conn.close()

        elapsed = time.time() - start_time
        logger.info("")
        logger.info(f"Integration completed in {elapsed/60:.1f} minutes")
        logger.info("")
        logger.info("✓ Companies House UK successfully integrated into osint_master.db")

        return True

    except Exception as e:
        logger.error(f"Integration failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
