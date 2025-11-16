#!/usr/bin/env python3
"""
Integrate Historical SOE Database with Entity Mergers Table

This script:
1. Reads the comprehensive historical SOE database
2. Cross-references with existing entity_mergers table
3. Enriches merger records with historical lineage data
4. Populates missing historical mergers into entity_mergers
5. Creates comprehensive SOE lineage tracking

Author: OSINT Foresight Team
Date: 2025-10-21
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
HISTORICAL_DB_PATH = PROJECT_ROOT / "data" / "prc_soe_historical_database.json"
WAREHOUSE_DB_PATH = PROJECT_ROOT / "data" / "osint_warehouse.db"
ANALYSIS_DIR = PROJECT_ROOT / "analysis"
ANALYSIS_DIR.mkdir(exist_ok=True)


class HistoricalSOEIntegrator:
    """Integrate historical SOE database with entity_mergers table"""

    def __init__(self, historical_db_path: Path, warehouse_db_path: Path):
        """Initialize integrator with database paths"""
        self.historical_db_path = historical_db_path
        self.warehouse_db_path = warehouse_db_path
        self.conn = None
        self.historical_data = None

        # Statistics
        self.stats = {
            'historical_entities_loaded': 0,
            'existing_mergers': 0,
            'new_mergers_added': 0,
            'mergers_enriched': 0,
            'aliases_added': 0,
            'errors': 0
        }

    def connect_database(self):
        """Connect to warehouse database"""
        logger.info(f"Connecting to warehouse: {self.warehouse_db_path}")
        self.conn = sqlite3.connect(self.warehouse_db_path)
        self.conn.row_factory = sqlite3.Row
        logger.info("  [OK] Connected to warehouse database")

    def load_historical_database(self):
        """Load historical SOE database"""
        logger.info(f"Loading historical database: {self.historical_db_path}")

        with open(self.historical_db_path, 'r', encoding='utf-8') as f:
            self.historical_data = json.load(f)

        self.stats['historical_entities_loaded'] = len(self.historical_data['entities'])
        logger.info(f"  [OK] Loaded {self.stats['historical_entities_loaded']} historical entities")

    def get_existing_mergers(self) -> List[Dict]:
        """Get existing mergers from entity_mergers table"""
        logger.info("Querying existing mergers from entity_mergers table")

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                legacy_entity_name,
                current_parent,
                merged_into,
                merger_date_iso,
                merger_type,
                strategic_sector
            FROM entity_mergers
        """)

        mergers = []
        for row in cursor.fetchall():
            mergers.append(dict(row))

        self.stats['existing_mergers'] = len(mergers)
        logger.info(f"  [OK] Found {len(mergers)} existing merger records")

        return mergers

    def enrich_merger_record(self, entity_id: str, historical_entity: Dict):
        """
        Enrich existing merger record with historical data

        Args:
            entity_id: Historical entity ID
            historical_entity: Historical entity data from JSON
        """
        cursor = self.conn.cursor()

        # Get legacy entity name
        legacy_name = historical_entity.get('official_name_en', '')
        aliases = historical_entity.get('aliases', [])

        # Check if merger exists (check both canonical name and aliases)
        placeholders = ','.join(['?'] * (len(aliases) + 1))
        query = f"SELECT id FROM entity_mergers WHERE legacy_entity_name IN ({placeholders})"
        cursor.execute(query, [legacy_name] + aliases)

        existing = cursor.fetchone()

        if existing:
            # Update with historical context
            cursor.execute("""
                UPDATE entity_mergers
                SET
                    historical_entity_id = ?,
                    creation_date_iso = ?,
                    predecessor_entities = ?,
                    successor_entity_id = ?,
                    lifecycle_status = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                entity_id,
                historical_entity['lifecycle'].get('creation_date'),
                json.dumps(historical_entity.get('historical_timeline', [])),
                historical_entity.get('merger_details', {}).get('combined_entity_id'),
                historical_entity['lifecycle']['status'],
                existing['id']
            ))

            self.stats['mergers_enriched'] += 1
            logger.info(f"    [ENRICHED] {legacy_name} with historical context")

    def add_new_merger_from_historical(self, historical_entity: Dict):
        """
        Add new merger record from historical database

        Args:
            historical_entity: Historical entity data from JSON
        """
        if historical_entity['lifecycle']['status'] != 'merged':
            return  # Only add merged entities

        if 'merger_details' not in historical_entity:
            return  # No merger details

        cursor = self.conn.cursor()
        merger_details = historical_entity['merger_details']

        # Check if already exists
        cursor.execute("""
            SELECT id FROM entity_mergers
            WHERE legacy_entity_name = ?
        """, (historical_entity['official_name_en'],))

        if cursor.fetchone():
            return  # Already exists

        # Insert new merger record
        try:
            cursor.execute("""
                INSERT INTO entity_mergers (
                    legacy_entity_name,
                    current_parent,
                    merged_into,
                    merger_date_iso,
                    merger_type,
                    strategic_sector,
                    source_url,
                    source_publisher,
                    detection_method,
                    historical_entity_id,
                    creation_date_iso,
                    predecessor_entities,
                    successor_entity_id,
                    lifecycle_status,
                    keywords_matched,
                    detection_confidence,
                    importance_tier,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                historical_entity['official_name_en'],
                historical_entity['lifecycle'].get('current_parent', ''),
                merger_details.get('merged_into', ''),
                merger_details.get('merger_date', ''),
                merger_details.get('formation_type', 'merger'),
                historical_entity.get('sector', ''),
                'Historical SOE Database',
                'OSINT Foresight Historical Research',
                'historical_database_integration',
                historical_entity['entity_id'],
                historical_entity['lifecycle'].get('creation_date'),
                json.dumps(historical_entity.get('historical_timeline', [])),
                merger_details.get('combined_entity_id'),
                'merged',
                json.dumps(['merger', 'consolidation', 'SOE']),
                1.0,  # High confidence - from historical research
                historical_entity.get('strategic_classification', 'TIER_2')
            ))

            self.stats['new_mergers_added'] += 1
            logger.info(f"    [NEW MERGER] Added {historical_entity['official_name_en']}")

        except Exception as e:
            logger.error(f"    [ERROR] Failed to add merger for {historical_entity['official_name_en']}: {e}")
            self.stats['errors'] += 1

    def add_aliases_to_table(self, historical_entity: Dict):
        """
        Add entity aliases to entity_aliases table

        Args:
            historical_entity: Historical entity data from JSON
        """
        cursor = self.conn.cursor()

        entity_name = historical_entity['official_name_en']
        aliases = historical_entity.get('aliases', [])

        for alias in aliases:
            # Check if alias already exists
            cursor.execute("""
                SELECT id FROM entity_aliases
                WHERE canonical_name = ? AND alias = ?
            """, (entity_name, alias))

            if not cursor.fetchone():
                try:
                    cursor.execute("""
                        INSERT INTO entity_aliases (
                            canonical_name,
                            alias,
                            alias_type,
                            source,
                            created_at
                        ) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (
                        entity_name,
                        alias,
                        'common_name',
                        'Historical SOE Database'
                    ))

                    self.stats['aliases_added'] += 1

                except Exception as e:
                    logger.warning(f"      Failed to add alias '{alias}': {e}")

    def create_historical_schema_if_needed(self):
        """Create historical tracking columns in entity_mergers if they don't exist"""
        cursor = self.conn.cursor()

        # Check if columns exist
        cursor.execute("PRAGMA table_info(entity_mergers)")
        columns = {row['name'] for row in cursor.fetchall()}

        new_columns = []
        if 'historical_entity_id' not in columns:
            new_columns.append("ALTER TABLE entity_mergers ADD COLUMN historical_entity_id TEXT")
        if 'creation_date_iso' not in columns:
            new_columns.append("ALTER TABLE entity_mergers ADD COLUMN creation_date_iso TEXT")
        if 'predecessor_entities' not in columns:
            new_columns.append("ALTER TABLE entity_mergers ADD COLUMN predecessor_entities TEXT")
        if 'successor_entity_id' not in columns:
            new_columns.append("ALTER TABLE entity_mergers ADD COLUMN successor_entity_id TEXT")
        if 'lifecycle_status' not in columns:
            new_columns.append("ALTER TABLE entity_mergers ADD COLUMN lifecycle_status TEXT")

        if new_columns:
            logger.info("Adding historical tracking columns to entity_mergers table")
            for sql in new_columns:
                cursor.execute(sql)
                logger.info(f"  [OK] {sql}")
            self.conn.commit()
        else:
            logger.info("  [OK] Historical tracking columns already exist")

    def process_all_entities(self):
        """Process all historical entities"""
        logger.info("\n" + "="*80)
        logger.info("PROCESSING HISTORICAL ENTITIES")
        logger.info("="*80 + "\n")

        for entity in self.historical_data['entities']:
            entity_id = entity['entity_id']
            entity_name = entity['official_name_en']

            logger.info(f"Processing: {entity_name} ({entity_id})")
            logger.info(f"  Status: {entity['lifecycle']['status']}")
            logger.info(f"  Sector: {entity.get('sector', 'Unknown')}")

            # Enrich existing merger if present
            self.enrich_merger_record(entity_id, entity)

            # Add new merger if merged entity
            if entity['lifecycle']['status'] == 'merged':
                self.add_new_merger_from_historical(entity)

            # Add aliases
            self.add_aliases_to_table(entity)

        self.conn.commit()
        logger.info("\n  [OK] All entities processed")

    def generate_integration_report(self):
        """Generate comprehensive integration report"""
        report_path = ANALYSIS_DIR / f"HISTORICAL_SOE_INTEGRATION_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Get updated merger counts
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM entity_mergers")
        total_mergers = cursor.fetchone()['total']

        cursor.execute("""
            SELECT COUNT(*) as enriched
            FROM entity_mergers
            WHERE historical_entity_id IS NOT NULL
        """)
        enriched_mergers = cursor.fetchone()['enriched']

        cursor.execute("SELECT COUNT(*) as total FROM entity_aliases")
        total_aliases = cursor.fetchone()['total']

        # Get lifecycle breakdown
        cursor.execute("""
            SELECT lifecycle_status, COUNT(*) as count
            FROM entity_mergers
            WHERE lifecycle_status IS NOT NULL
            GROUP BY lifecycle_status
        """)
        lifecycle_breakdown = {row['lifecycle_status']: row['count'] for row in cursor.fetchall()}

        # Get sector breakdown
        cursor.execute("""
            SELECT strategic_sector, COUNT(*) as count
            FROM entity_mergers
            GROUP BY strategic_sector
            ORDER BY count DESC
            LIMIT 10
        """)
        sector_breakdown = {row['strategic_sector']: row['count'] for row in cursor.fetchall() if row['strategic_sector']}

        report = {
            'integration_timestamp': datetime.now().isoformat(),
            'integration_stats': self.stats,
            'database_status': {
                'total_mergers_in_database': total_mergers,
                'mergers_with_historical_data': enriched_mergers,
                'total_aliases_in_database': total_aliases,
                'historical_enrichment_rate': f"{(enriched_mergers/total_mergers*100):.1f}%" if total_mergers > 0 else "0%"
            },
            'lifecycle_breakdown': lifecycle_breakdown,
            'top_sectors': sector_breakdown,
            'historical_database_metadata': self.historical_data['metadata']
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"\n[OK] Integration report saved: {report_path}")

        return report

    def print_summary(self, report: Dict):
        """Print integration summary"""
        logger.info("\n" + "="*80)
        logger.info("HISTORICAL SOE DATABASE INTEGRATION - SUMMARY")
        logger.info("="*80)
        logger.info(f"\nHistorical Entities Processed: {self.stats['historical_entities_loaded']}")
        logger.info(f"Existing Mergers in Database: {self.stats['existing_mergers']}")
        logger.info(f"New Mergers Added: {self.stats['new_mergers_added']}")
        logger.info(f"Mergers Enriched with Historical Data: {self.stats['mergers_enriched']}")
        logger.info(f"Aliases Added: {self.stats['aliases_added']}")
        logger.info(f"Errors: {self.stats['errors']}")

        logger.info(f"\nDatabase Status:")
        logger.info(f"  Total Mergers: {report['database_status']['total_mergers_in_database']}")
        logger.info(f"  Mergers with Historical Data: {report['database_status']['mergers_with_historical_data']}")
        logger.info(f"  Historical Enrichment Rate: {report['database_status']['historical_enrichment_rate']}")
        logger.info(f"  Total Aliases: {report['database_status']['total_aliases_in_database']}")

        logger.info(f"\nLifecycle Status Breakdown:")
        for status, count in report['lifecycle_breakdown'].items():
            logger.info(f"  {status}: {count}")

        logger.info(f"\nTop Sectors:")
        for sector, count in list(report['top_sectors'].items())[:5]:
            logger.info(f"  {sector}: {count}")

        logger.info("\n" + "="*80)
        logger.info("[SUCCESS] Historical SOE database integration complete!")
        logger.info("="*80 + "\n")

    def run(self):
        """Run full integration process"""
        try:
            # Load data
            self.load_historical_database()
            self.connect_database()

            # Create schema if needed
            self.create_historical_schema_if_needed()

            # Get existing mergers
            self.get_existing_mergers()

            # Process all entities
            self.process_all_entities()

            # Generate report
            report = self.generate_integration_report()

            # Print summary
            self.print_summary(report)

        except Exception as e:
            logger.error(f"\n[ERROR] Integration failed: {e}")
            import traceback
            traceback.print_exc()

        finally:
            if self.conn:
                self.conn.close()
                logger.info("[OK] Database connection closed")


def main():
    """Main entry point"""
    logger.info("="*80)
    logger.info("HISTORICAL SOE DATABASE INTEGRATION")
    logger.info("="*80 + "\n")

    integrator = HistoricalSOEIntegrator(
        historical_db_path=HISTORICAL_DB_PATH,
        warehouse_db_path=WAREHOUSE_DB_PATH
    )

    integrator.run()


if __name__ == "__main__":
    main()
