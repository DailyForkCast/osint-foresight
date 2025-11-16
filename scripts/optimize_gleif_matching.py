#!/usr/bin/env python3
"""
Optimized GLEIF Matching for Companies House UK
Uses pre-computed normalized names with indexes for fast matching
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
        logging.FileHandler('gleif_matching_optimized.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

TARGET_DB = Path("F:/OSINT_WAREHOUSE/osint_master.db")


def connect_db(db_path, timeout=120):
    """Connect to database with WAL mode"""
    conn = sqlite3.connect(db_path, timeout=timeout)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def add_normalized_columns(cursor):
    """Add normalized name columns for fast matching"""

    logger.info("Adding normalized name columns...")

    # Add to Companies House table
    try:
        cursor.execute("""
            ALTER TABLE companies_house_uk_companies
            ADD COLUMN company_name_normalized TEXT
        """)
        logger.info("  Added company_name_normalized column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            logger.info("  company_name_normalized column already exists")
        else:
            raise

    # Add to GLEIF table
    try:
        cursor.execute("""
            ALTER TABLE gleif_entities
            ADD COLUMN legal_name_normalized TEXT
        """)
        logger.info("  Added legal_name_normalized column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            logger.info("  legal_name_normalized column already exists")
        else:
            raise


def populate_normalized_names(conn):
    """Populate normalized name columns"""

    cursor = conn.cursor()

    # Companies House
    logger.info("Normalizing Companies House company names...")
    cursor.execute("""
        UPDATE companies_house_uk_companies
        SET company_name_normalized = LOWER(TRIM(company_name))
        WHERE company_name IS NOT NULL
    """)
    ch_updated = cursor.rowcount
    conn.commit()
    logger.info(f"  Normalized {ch_updated:,} company names")

    # GLEIF (this will take a while - 3M+ records)
    logger.info("Normalizing GLEIF legal names (3M+ records, may take 2-3 minutes)...")
    start = time.time()
    cursor.execute("""
        UPDATE gleif_entities
        SET legal_name_normalized = LOWER(TRIM(legal_name))
        WHERE legal_name IS NOT NULL
    """)
    gleif_updated = cursor.rowcount
    conn.commit()
    elapsed = time.time() - start
    logger.info(f"  Normalized {gleif_updated:,} GLEIF names in {elapsed:.1f} seconds")


def create_normalized_indexes(cursor):
    """Create indexes on normalized columns"""

    logger.info("Creating indexes on normalized columns...")

    start = time.time()
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ch_name_normalized
        ON companies_house_uk_companies(company_name_normalized)
    """)
    logger.info(f"  Created index on Companies House normalized names ({time.time()-start:.1f}s)")

    start = time.time()
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_gleif_name_normalized
        ON gleif_entities(legal_name_normalized)
    """)
    logger.info(f"  Created index on GLEIF normalized names ({time.time()-start:.1f}s)")


def match_by_normalized_name(conn):
    """Match using normalized names (FAST with indexes)"""

    cursor = conn.cursor()
    created_date = datetime.now(timezone.utc).isoformat()

    logger.info("Matching Companies House → GLEIF by normalized name...")
    logger.info("  (This should be VERY fast now - using indexes!)")

    start = time.time()
    cursor.execute("""
        INSERT OR IGNORE INTO companies_house_gleif_xref
        (company_number, gleif_lei, match_type, match_confidence, created_date)
        SELECT
            ch.company_number,
            g.lei,
            'exact_name_normalized' as match_type,
            95 as match_confidence,
            ? as created_date
        FROM companies_house_uk_companies ch
        JOIN gleif_entities g ON ch.company_name_normalized = g.legal_name_normalized
        WHERE ch.company_name_normalized IS NOT NULL
          AND g.legal_name_normalized IS NOT NULL
          AND LENGTH(ch.company_name_normalized) > 0
    """, (created_date,))

    matches = cursor.rowcount
    elapsed = time.time() - start
    conn.commit()

    logger.info(f"  Exact name matches: {matches:,} in {elapsed:.1f} seconds")
    logger.info(f"  Performance: {matches/elapsed if elapsed > 0 else 0:.0f} matches/second")

    return matches


def match_by_opencorporates(conn):
    """Match using OpenCorporates mapping"""

    cursor = conn.cursor()
    created_date = datetime.now(timezone.utc).isoformat()

    logger.info("Matching via GLEIF OpenCorporates mapping...")

    start = time.time()
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

    matches = cursor.rowcount
    elapsed = time.time() - start
    conn.commit()

    logger.info(f"  OpenCorporates matches: {matches:,} in {elapsed:.1f} seconds")

    return matches


def generate_summary(conn):
    """Generate matching summary"""

    cursor = conn.cursor()

    logger.info("")
    logger.info("=" * 80)
    logger.info("GLEIF MATCHING SUMMARY")
    logger.info("=" * 80)

    # Total matches
    total = cursor.execute("SELECT COUNT(*) FROM companies_house_gleif_xref").fetchone()[0]
    logger.info(f"Total GLEIF cross-references: {total:,}")

    # Unique companies matched
    unique = cursor.execute("""
        SELECT COUNT(DISTINCT company_number) FROM companies_house_gleif_xref
    """).fetchone()[0]

    total_companies = cursor.execute("""
        SELECT COUNT(*) FROM companies_house_uk_companies
    """).fetchone()[0]

    logger.info(f"Unique companies matched: {unique:,} / {total_companies:,} ({unique/total_companies*100:.1f}%)")

    # By match type
    logger.info("")
    logger.info("Matches by type:")
    cursor.execute("""
        SELECT match_type, COUNT(*) as cnt
        FROM companies_house_gleif_xref
        GROUP BY match_type
        ORDER BY cnt DESC
    """)
    for match_type, count in cursor.fetchall():
        logger.info(f"  {match_type:30s}: {count:,}")

    # Sample matches
    logger.info("")
    logger.info("Sample matches:")
    cursor.execute("""
        SELECT
            ch.company_number,
            ch.company_name,
            g.lei,
            g.legal_name,
            xref.match_type,
            xref.match_confidence
        FROM companies_house_gleif_xref xref
        JOIN companies_house_uk_companies ch ON xref.company_number = ch.company_number
        JOIN gleif_entities g ON xref.gleif_lei = g.lei
        LIMIT 10
    """)
    for row in cursor.fetchall():
        logger.info(f"  {row[0]}: {row[1]} → {row[2]} ({row[5]}% confidence)")

    logger.info("=" * 80)


def main():
    """Main optimization workflow"""

    logger.info("=" * 80)
    logger.info("OPTIMIZED GLEIF MATCHING FOR COMPANIES HOUSE UK")
    logger.info("=" * 80)
    logger.info(f"Database: {TARGET_DB}")
    logger.info("")

    overall_start = time.time()

    try:
        # Connect to database
        logger.info("Connecting to database...")
        conn = connect_db(TARGET_DB)
        cursor = conn.cursor()

        # Step 1: Add normalized columns
        add_normalized_columns(cursor)
        conn.commit()

        # Step 2: Populate normalized names
        populate_normalized_names(conn)

        # Step 3: Create indexes
        create_normalized_indexes(cursor)
        conn.commit()

        # Step 4: Match by normalized name (FAST!)
        name_matches = match_by_normalized_name(conn)

        # Step 5: Match by OpenCorporates (also fast)
        oc_matches = match_by_opencorporates(conn)

        # Step 6: Generate summary
        generate_summary(conn)

        # Close connection
        conn.close()

        total_time = time.time() - overall_start
        logger.info("")
        logger.info(f"Total optimization time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
        logger.info("")
        logger.info("✓ GLEIF matching optimization complete!")

        return True

    except Exception as e:
        logger.error(f"Optimization failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
