#!/usr/bin/env python3
"""
Initialize U.S. Government Documents Database
Creates tables, indexes, and views for Tech Sweep and China Sweep collections
"""

import sqlite3
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
SCHEMA_PATH = Path("schema/usgov_documents_schema.sql")

def init_database():
    """Initialize US Gov documents tables in the database"""
    logger.info(f"Initializing US Gov documents schema in {DB_PATH}")

    if not DB_PATH.exists():
        logger.error(f"Database file not found: {DB_PATH}")
        return False

    if not SCHEMA_PATH.exists():
        logger.error(f"Schema file not found: {SCHEMA_PATH}")
        return False

    try:
        conn = sqlite3.connect(DB_PATH, timeout=60)
        cursor = conn.cursor()

        # Read schema SQL
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # Execute schema (split by semicolons for multiple statements)
        statements = [s.strip() for s in schema_sql.split(';') if s.strip()]

        for i, statement in enumerate(statements, 1):
            try:
                cursor.execute(statement)
                logger.debug(f"Executed statement {i}/{len(statements)}")
            except sqlite3.OperationalError as e:
                if "already exists" in str(e).lower():
                    logger.debug(f"Statement {i} - object already exists (OK)")
                else:
                    logger.warning(f"Statement {i} error: {e}")
                    continue

        conn.commit()

        # Verify tables created
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name LIKE 'usgov_%'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]

        logger.info(f"Created/verified {len(tables)} US Gov tables:")
        for table in tables:
            count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            logger.info(f"  - {table}: {count:,} records")

        # Insert controlled vocabularies
        logger.info("Populating controlled vocabularies...")

        # Tech topics
        tech_topics = [
            ('artificial_intelligence', 'technology', 'AI and machine learning systems'),
            ('quantum_computing', 'technology', 'Quantum information science'),
            ('semiconductors', 'technology', 'Microelectronics and chip technology'),
            ('biotechnology', 'technology', 'Biological sciences and biotech'),
            ('advanced_materials', 'technology', 'Novel materials and metamaterials'),
            ('cybersecurity', 'technology', 'Cyber defense and security'),
            ('space_technology', 'technology', 'Space systems and satellites'),
            ('export_controls', 'policy', 'Export control regulations'),
            ('supply_chain', 'policy', 'Supply chain security and resilience'),
            ('standards', 'policy', 'Technical standards and standardization'),
            ('critical_minerals', 'resources', 'Rare earth elements and strategic materials')
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO usgov_controlled_topics (topic, category, description)
            VALUES (?, ?, ?)
        """, tech_topics)

        # Agency codes
        agencies = [
            ('DOC/BIS', 'Bureau of Industry and Security', 'Commerce', 'DOC'),
            ('DOC/NIST', 'National Institute of Standards and Technology', 'Commerce', 'DOC'),
            ('DOC/NTIA', 'National Telecommunications and Information Administration', 'Commerce', 'DOC'),
            ('DOD/OSD', 'Office of the Secretary of Defense', 'Defense', 'DOD'),
            ('DOD/DARPA', 'Defense Advanced Research Projects Agency', 'Defense', 'DOD'),
            ('DOD/DIU', 'Defense Innovation Unit', 'Defense', 'DOD'),
            ('DHS/CISA', 'Cybersecurity and Infrastructure Security Agency', 'Homeland Security', 'DHS'),
            ('Whitehouse/OSTP', 'Office of Science and Technology Policy', 'Executive Office', 'Whitehouse'),
            ('Whitehouse/NSC', 'National Security Council', 'Executive Office', 'Whitehouse'),
            ('State', 'Department of State', 'State', None),
            ('Treasury/OFAC', 'Office of Foreign Assets Control', 'Treasury', 'Treasury'),
            ('DOE/ARPA-E', 'Advanced Research Projects Agency-Energy', 'Energy', 'DOE'),
            ('GAO', 'Government Accountability Office', 'Legislative Branch', None),
            ('CRS', 'Congressional Research Service', 'Legislative Branch', None)
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO usgov_controlled_agencies (agency_code, full_name, agency_type, parent_agency)
            VALUES (?, ?, ?, ?)
        """, agencies)

        conn.commit()

        logger.info("✅ US Gov documents database initialized successfully")
        logger.info(f"   Tables: {len(tables)}")
        logger.info(f"   Topics: {len(tech_topics)}")
        logger.info(f"   Agencies: {len(agencies)}")

        conn.close()
        return True

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = init_database()
    exit(0 if success else 1)
