#!/usr/bin/env python3
"""
Create SOE Tracking Database Schema

Creates entity_mergers and entity_aliases tables for tracking Chinese SOE lifecycle.

Author: OSINT Foresight Team
Date: 2025-10-21
"""

import sqlite3
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
WAREHOUSE_DB_PATH = PROJECT_ROOT / "data" / "osint_warehouse.db"


def create_schema():
    """Create SOE tracking schema"""
    logger.info("="*80)
    logger.info("CREATING SOE TRACKING DATABASE SCHEMA")
    logger.info("="*80 + "\n")

    logger.info(f"Database: {WAREHOUSE_DB_PATH}")

    conn = sqlite3.connect(WAREHOUSE_DB_PATH)
    cursor = conn.cursor()

    # Create entity_mergers table
    logger.info("Creating entity_mergers table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entity_mergers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- Core entity information
            legacy_entity_name TEXT NOT NULL,
            current_parent TEXT,
            merged_into TEXT,
            merger_date_iso TEXT,
            merger_type TEXT,
            strategic_sector TEXT,

            -- Source tracking
            source_url TEXT,
            source_publisher TEXT,
            source_date_iso TEXT,
            detection_method TEXT,

            -- Historical tracking (from historical database)
            historical_entity_id TEXT,
            creation_date_iso TEXT,
            predecessor_entities TEXT,  -- JSON array
            successor_entity_id TEXT,
            lifecycle_status TEXT,  -- existing, merged, dissolved, privatized

            -- Detection metadata
            keywords_matched TEXT,  -- JSON array
            detection_confidence REAL,

            -- Intelligence classification
            importance_tier TEXT,

            -- US contracting history
            us_contracting_history INTEGER DEFAULT 0,
            us_contracting_count INTEGER DEFAULT 0,
            us_contracting_value_usd REAL DEFAULT 0.0,
            us_contracting_last_date_iso TEXT,

            -- European contracting history
            eu_contracting_history INTEGER DEFAULT 0,
            eu_contracting_count INTEGER DEFAULT 0,
            eu_contracting_countries TEXT,  -- JSON array
            eu_contracting_last_date_iso TEXT,

            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    logger.info("  [OK] entity_mergers table created")

    # Create indexes for entity_mergers
    logger.info("Creating indexes for entity_mergers...")
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_mergers_legacy_name ON entity_mergers(legacy_entity_name)",
        "CREATE INDEX IF NOT EXISTS idx_mergers_current_parent ON entity_mergers(current_parent)",
        "CREATE INDEX IF NOT EXISTS idx_mergers_merger_date ON entity_mergers(merger_date_iso)",
        "CREATE INDEX IF NOT EXISTS idx_mergers_importance_tier ON entity_mergers(importance_tier)",
        "CREATE INDEX IF NOT EXISTS idx_mergers_strategic_sector ON entity_mergers(strategic_sector)",
        "CREATE INDEX IF NOT EXISTS idx_mergers_historical_id ON entity_mergers(historical_entity_id)",
        "CREATE INDEX IF NOT EXISTS idx_mergers_lifecycle_status ON entity_mergers(lifecycle_status)",
    ]

    for idx_sql in indexes:
        cursor.execute(idx_sql)
        logger.info(f"  [OK] {idx_sql.split('ON')[0].split('INDEX')[1].strip()}")

    # Create entity_aliases table
    logger.info("\nCreating entity_aliases table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entity_aliases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- Entity information
            canonical_name TEXT NOT NULL,
            alias TEXT NOT NULL,
            alias_type TEXT,  -- common_name, abbreviation, translation, historical_name

            -- Source tracking
            source TEXT,
            confidence REAL DEFAULT 1.0,

            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            -- Uniqueness constraint
            UNIQUE(canonical_name, alias)
        )
    """)
    logger.info("  [OK] entity_aliases table created")

    # Create indexes for entity_aliases
    logger.info("Creating indexes for entity_aliases...")
    alias_indexes = [
        "CREATE INDEX IF NOT EXISTS idx_aliases_canonical ON entity_aliases(canonical_name)",
        "CREATE INDEX IF NOT EXISTS idx_aliases_alias ON entity_aliases(alias)",
        "CREATE INDEX IF NOT EXISTS idx_aliases_type ON entity_aliases(alias_type)",
    ]

    for idx_sql in alias_indexes:
        cursor.execute(idx_sql)
        logger.info(f"  [OK] {idx_sql.split('ON')[0].split('INDEX')[1].strip()}")

    # Commit changes
    conn.commit()

    # Verify tables created
    logger.info("\nVerifying tables...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    logger.info(f"Tables in database: {', '.join(tables)}")

    conn.close()

    logger.info("\n" + "="*80)
    logger.info("[SUCCESS] SOE tracking schema created successfully!")
    logger.info("="*80 + "\n")


if __name__ == "__main__":
    create_schema()
