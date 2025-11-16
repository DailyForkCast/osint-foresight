#!/usr/bin/env python3
"""
Complete Companies House UK Integration
Finish the integration by creating indexes and generating summary
"""

import sqlite3
import logging
import re
from datetime import datetime
from pathlib import Path

# ============================================================================
# SECURITY: SQL injection prevention through identifier validation
# ============================================================================

def validate_sql_identifier(identifier):
    """
    SECURITY: Validate SQL identifier (table or column name).
    Only allows alphanumeric characters and underscores.
    Prevents SQL injection from dynamic SQL construction.
    """
    if not identifier:
        raise ValueError("Identifier cannot be empty")

    # Check for valid characters only (alphanumeric + underscore)
    if not re.match(r'^[a-zA-Z0-9_]+$', identifier):
        raise ValueError(f"Invalid identifier: {identifier}. Contains illegal characters.")

    # Check length (SQLite limit is 1024, we use 100 for safety)
    if len(identifier) > 100:
        raise ValueError(f"Identifier too long: {identifier}")

    # Blacklist dangerous SQL keywords
    dangerous_keywords = {'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
                         'EXEC', 'EXECUTE', 'UNION', 'SELECT', '--', ';', '/*', '*/'}
    if identifier.upper() in dangerous_keywords:
        raise ValueError(f"Identifier contains SQL keyword: {identifier}")

    return identifier

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('companies_house_completion.log'),
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
        try:
            # SECURITY: Validate index name before use in SQL
            safe_idx_name = validate_sql_identifier(idx_name)

            # Parse and validate index definition (format: "table(column)")
            match = re.match(r'^([a-zA-Z0-9_]+)\(([a-zA-Z0-9_]+)\)$', idx_def)
            if match:
                table_name, column_name = match.groups()
                safe_table = validate_sql_identifier(table_name)
                safe_column = validate_sql_identifier(column_name)
                safe_idx_def = f"{safe_table}({safe_column})"
            else:
                raise ValueError(f"Invalid index definition format: {idx_def}")

            cursor.execute(f"CREATE INDEX IF NOT EXISTS {safe_idx_name} ON {safe_idx_def}")
            logger.info(f"  Created index: {idx_name}")
        except Exception as e:
            logger.warning(f"  Failed to create {idx_name}: {e}")

    logger.info(f"Index creation complete")


def generate_summary(conn):
    """Generate integration summary statistics"""

    logger.info("=" * 80)
    logger.info("COMPANIES HOUSE UK INTEGRATION SUMMARY")
    logger.info("=" * 80)

    cursor = conn.cursor()

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
    if xref > 0:
        gleif_companies = cursor.execute("""
            SELECT COUNT(DISTINCT company_number)
            FROM companies_house_gleif_xref
        """).fetchone()[0]
        logger.info(f"Companies matched to GLEIF: {gleif_companies:,} ({gleif_companies/companies*100:.1f}%)")
    else:
        logger.info("Companies matched to GLEIF: 0 (GLEIF matching was skipped)")

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
        logger.info(f"  {layer:40s}: {count:,}")

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
        logger.info(f"  {nat:40s}: {count:,}")

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

    # Company status breakdown
    logger.info("")
    logger.info("Company Status Breakdown:")
    cursor.execute("""
        SELECT company_status, COUNT(*) as cnt
        FROM companies_house_uk_companies
        WHERE company_status IS NOT NULL
        GROUP BY company_status
        ORDER BY cnt DESC
        LIMIT 10
    """)
    for status, count in cursor.fetchall():
        logger.info(f"  {status:40s}: {count:,}")

    logger.info("=" * 80)


def main():
    """Main completion workflow"""

    logger.info("=" * 80)
    logger.info("COMPLETING COMPANIES HOUSE UK INTEGRATION")
    logger.info("=" * 80)
    logger.info(f"Database: {TARGET_DB}")
    logger.info("")

    try:
        # Connect to database
        logger.info("Connecting to database...")
        conn = connect_db(TARGET_DB)
        cursor = conn.cursor()

        # Create indexes
        create_indexes(cursor)
        conn.commit()

        # Generate summary
        generate_summary(conn)

        # Close connection
        conn.close()

        logger.info("")
        logger.info("Integration completion successful")
        logger.info("")

        return True

    except Exception as e:
        logger.error(f"Completion failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
