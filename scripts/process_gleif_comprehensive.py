#!/usr/bin/env python3
"""
Comprehensive GLEIF Data Processor
Processes all GLEIF Golden Copy files: entities, relationships, cross-references
"""

import sqlite3
import json
import zipfile
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Iterator
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
GLEIF_DATA_DIR = Path("F:/GLEIF")

class GLEIFProcessor:
    def __init__(self):
        self.db_path = DB_PATH
        self.data_dir = GLEIF_DATA_DIR
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def setup_schema(self):
        """Create GLEIF tables with indexes"""
        logger.info("Creating GLEIF database schema...")

        cursor = self.conn.cursor()

        # Main entities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gleif_entities (
                lei TEXT PRIMARY KEY,
                legal_name TEXT,
                legal_name_lang TEXT,
                legal_address_line1 TEXT,
                legal_address_city TEXT,
                legal_address_region TEXT,
                legal_address_country TEXT,
                legal_address_postal TEXT,
                hq_address_line1 TEXT,
                hq_address_city TEXT,
                hq_address_region TEXT,
                hq_address_country TEXT,
                hq_address_postal TEXT,
                entity_category TEXT,
                legal_form_code TEXT,
                entity_status TEXT,
                entity_creation_date TEXT,
                legal_jurisdiction TEXT,
                registration_status TEXT,
                registration_initial_date TEXT,
                registration_last_update TEXT,
                registration_next_renewal TEXT,
                managing_lou TEXT,
                validation_sources TEXT,
                processed_date TEXT
            )
        """)

        # Relationships table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gleif_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_lei TEXT,
                parent_lei TEXT,
                relationship_type TEXT,
                relationship_status TEXT,
                start_date TEXT,
                last_update_date TEXT,
                validation_documents TEXT,
                validation_reference TEXT,
                processed_date TEXT,
                UNIQUE(child_lei, parent_lei, relationship_type)
            )
        """)

        # QCC-LEI mapping (Chinese company codes)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gleif_qcc_mapping (
                qcc_code TEXT,
                lei TEXT,
                legal_name TEXT,
                country TEXT,
                processed_date TEXT,
                PRIMARY KEY (qcc_code, lei)
            )
        """)

        # ISIN-LEI mapping
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gleif_isin_mapping (
                isin TEXT,
                lei TEXT,
                legal_name TEXT,
                processed_date TEXT,
                PRIMARY KEY (isin, lei)
            )
        """)

        # BIC-LEI mapping
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gleif_bic_mapping (
                bic TEXT,
                lei TEXT,
                legal_name TEXT,
                processed_date TEXT,
                PRIMARY KEY (bic, lei)
            )
        """)

        # OpenCorporates-LEI mapping
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gleif_opencorporates_mapping (
                oc_id TEXT,
                lei TEXT,
                legal_name TEXT,
                jurisdiction TEXT,
                processed_date TEXT,
                PRIMARY KEY (oc_id, lei)
            )
        """)

        # REPEX table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gleif_repex (
                lei TEXT PRIMARY KEY,
                exception_category TEXT,
                exception_reason TEXT,
                exception_reference TEXT,
                processed_date TEXT
            )
        """)

        # Create indexes
        logger.info("Creating indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_gleif_entities_country ON gleif_entities(legal_address_country)",
            "CREATE INDEX IF NOT EXISTS idx_gleif_entities_category ON gleif_entities(entity_category)",
            "CREATE INDEX IF NOT EXISTS idx_gleif_entities_status ON gleif_entities(entity_status)",
            "CREATE INDEX IF NOT EXISTS idx_gleif_entities_name ON gleif_entities(legal_name)",
            "CREATE INDEX IF NOT EXISTS idx_gleif_relationships_child ON gleif_relationships(child_lei)",
            "CREATE INDEX IF NOT EXISTS idx_gleif_relationships_parent ON gleif_relationships(parent_lei)",
            "CREATE INDEX IF NOT EXISTS idx_gleif_relationships_type ON gleif_relationships(relationship_type)",
            "CREATE INDEX IF NOT EXISTS idx_gleif_qcc_lei ON gleif_qcc_mapping(lei)",
            "CREATE INDEX IF NOT EXISTS idx_gleif_isin_lei ON gleif_isin_mapping(lei)",
            "CREATE INDEX IF NOT EXISTS idx_gleif_bic_lei ON gleif_bic_mapping(lei)",
            "CREATE INDEX IF NOT EXISTS idx_gleif_oc_lei ON gleif_opencorporates_mapping(lei)"
        ]

        for idx_sql in indexes:
            cursor.execute(idx_sql)

        self.conn.commit()
        logger.info("Schema created successfully")

    def extract_nested_value(self, obj, default=''):
        """Extract value from nested GLEIF JSON structure"""
        if isinstance(obj, dict):
            return obj.get('$', default)
        return obj if obj is not None else default

    def process_lei_entities(self):
        """Process LEI Level 2 entity records"""
        logger.info("Processing LEI entities...")

        zip_file = self.data_dir / "20251011-0800-gleif-goldencopy-lei2-golden-copy.json.zip"
        if not zip_file.exists():
            logger.error(f"Entity file not found: {zip_file}")
            return

        cursor = self.conn.cursor()
        batch = []
        batch_size = 1000
        processed = 0
        start_time = time.time()

        with zipfile.ZipFile(zip_file) as zf:
            json_filename = zf.namelist()[0]
            logger.info(f"Reading {json_filename}...")

            with zf.open(json_filename) as f:
                data = json.load(f)
                records = data.get('records', [])
                total_records = len(records)
                logger.info(f"Found {total_records:,} entity records")

                for record in records:
                    try:
                        lei_data = record.get('LEI', {})
                        lei = self.extract_nested_value(lei_data)

                        entity = record.get('Entity', {})
                        legal_name_obj = entity.get('LegalName', {})
                        legal_address = entity.get('LegalAddress', {})
                        hq_address = entity.get('HeadquartersAddress', {})

                        registration = record.get('Registration', {})

                        entity_record = (
                            lei,
                            self.extract_nested_value(legal_name_obj),
                            legal_name_obj.get('@xml:lang') if isinstance(legal_name_obj, dict) else 'en',
                            self.extract_nested_value(legal_address.get('FirstAddressLine', {})),
                            self.extract_nested_value(legal_address.get('City', {})),
                            self.extract_nested_value(legal_address.get('Region', {})),
                            self.extract_nested_value(legal_address.get('Country', {})),
                            self.extract_nested_value(legal_address.get('PostalCode', {})),
                            self.extract_nested_value(hq_address.get('FirstAddressLine', {})),
                            self.extract_nested_value(hq_address.get('City', {})),
                            self.extract_nested_value(hq_address.get('Region', {})),
                            self.extract_nested_value(hq_address.get('Country', {})),
                            self.extract_nested_value(hq_address.get('PostalCode', {})),
                            self.extract_nested_value(entity.get('EntityCategory', {})),
                            self.extract_nested_value(entity.get('LegalForm', {}).get('EntityLegalFormCode', {})),
                            self.extract_nested_value(entity.get('EntityStatus', {})),
                            self.extract_nested_value(entity.get('EntityCreationDate', {})),
                            self.extract_nested_value(entity.get('LegalJurisdiction', {})),
                            self.extract_nested_value(registration.get('RegistrationStatus', {})),
                            self.extract_nested_value(registration.get('InitialRegistrationDate', {})),
                            self.extract_nested_value(registration.get('LastUpdateDate', {})),
                            self.extract_nested_value(registration.get('NextRenewalDate', {})),
                            self.extract_nested_value(registration.get('ManagingLOU', {})),
                            self.extract_nested_value(registration.get('ValidationSources', {})),
                            datetime.now(timezone.utc).isoformat()
                        )

                        batch.append(entity_record)

                        if len(batch) >= batch_size:
                            cursor.executemany("""
                                INSERT OR REPLACE INTO gleif_entities VALUES
                                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, batch)
                            self.conn.commit()
                            processed += len(batch)
                            elapsed = time.time() - start_time
                            rate = processed / elapsed if elapsed > 0 else 0
                            eta = (total_records - processed) / rate if rate > 0 else 0
                            logger.info(f"Processed {processed:,}/{total_records:,} entities ({rate:.0f}/sec, ETA: {eta/60:.1f}min)")
                            batch = []

                    except Exception as e:
                        logger.warning(f"Error processing entity record: {e}")
                        continue

                # Final batch
                if batch:
                    cursor.executemany("""
                        INSERT OR REPLACE INTO gleif_entities VALUES
                        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, batch)
                    self.conn.commit()
                    processed += len(batch)

        elapsed = time.time() - start_time
        logger.info(f"Completed: {processed:,} entities processed in {elapsed/60:.1f} minutes")

    def process_relationships(self):
        """Process RR relationship records"""
        logger.info("Processing relationship records...")

        zip_file = self.data_dir / "20251011-0800-gleif-goldencopy-rr-golden-copy.json.zip"
        if not zip_file.exists():
            logger.error(f"Relationship file not found: {zip_file}")
            return

        cursor = self.conn.cursor()
        batch = []
        batch_size = 1000
        processed = 0
        start_time = time.time()

        with zipfile.ZipFile(zip_file) as zf:
            json_filename = zf.namelist()[0]
            logger.info(f"Reading {json_filename}...")

            with zf.open(json_filename) as f:
                data = json.load(f)
                relations = data.get('relations', [])
                total_relations = len(relations)
                logger.info(f"Found {total_relations:,} relationship records")

                for relation in relations:
                    try:
                        relationship_data = relation.get('Relationship', {})

                        child_lei = self.extract_nested_value(relationship_data.get('StartNode', {}).get('NodeID', {}))
                        parent_lei = self.extract_nested_value(relationship_data.get('EndNode', {}).get('NodeID', {}))
                        rel_type = self.extract_nested_value(relationship_data.get('RelationshipType', {}))
                        rel_status = self.extract_nested_value(relationship_data.get('RelationshipStatus', {}))

                        periods = relationship_data.get('RelationshipPeriods', [])
                        start_date = ''
                        last_update = ''
                        if periods and len(periods) > 0:
                            period = periods[0] if isinstance(periods, list) else periods
                            if isinstance(period, dict):
                                start_date = self.extract_nested_value(period.get('StartDate', {}))
                                last_update = self.extract_nested_value(period.get('PeriodLastUpdateDate', {}))

                        validation_docs = self.extract_nested_value(
                            relationship_data.get('RelationshipQualifier', {}).get('QualifierDimension', {}).get('ValidationDocuments', {})
                        )

                        validation_ref = ''

                        rel_record = (
                            child_lei,
                            parent_lei,
                            rel_type,
                            rel_status,
                            start_date,
                            last_update,
                            validation_docs,
                            validation_ref,
                            datetime.now(timezone.utc).isoformat()
                        )

                        batch.append(rel_record)

                        if len(batch) >= batch_size:
                            cursor.executemany("""
                                INSERT OR IGNORE INTO gleif_relationships
                                (child_lei, parent_lei, relationship_type, relationship_status,
                                 start_date, last_update_date, validation_documents, validation_reference, processed_date)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, batch)
                            self.conn.commit()
                            processed += len(batch)
                            elapsed = time.time() - start_time
                            rate = processed / elapsed if elapsed > 0 else 0
                            logger.info(f"Processed {processed:,}/{total_relations:,} relationships ({rate:.0f}/sec)")
                            batch = []

                    except Exception as e:
                        logger.warning(f"Error processing relationship: {e}")
                        continue

                # Final batch
                if batch:
                    cursor.executemany("""
                        INSERT OR IGNORE INTO gleif_relationships
                        (child_lei, parent_lei, relationship_type, relationship_status,
                         start_date, last_update_date, validation_documents, validation_reference, processed_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, batch)
                    self.conn.commit()
                    processed += len(batch)

        elapsed = time.time() - start_time
        logger.info(f"Completed: {processed:,} relationships processed in {elapsed/60:.1f} minutes")

    def generate_summary(self):
        """Generate processing summary"""
        cursor = self.conn.cursor()

        # Entity counts
        total_entities = cursor.execute("SELECT COUNT(*) FROM gleif_entities").fetchone()[0]
        by_country = cursor.execute("""
            SELECT legal_address_country, COUNT(*) as cnt
            FROM gleif_entities
            WHERE legal_address_country IS NOT NULL AND legal_address_country != ''
            GROUP BY legal_address_country
            ORDER BY cnt DESC
            LIMIT 20
        """).fetchall()

        by_category = cursor.execute("""
            SELECT entity_category, COUNT(*) as cnt
            FROM gleif_entities
            WHERE entity_category IS NOT NULL AND entity_category != ''
            GROUP BY entity_category
            ORDER BY cnt DESC
        """).fetchall()

        # Relationship counts
        total_relationships = cursor.execute("SELECT COUNT(*) FROM gleif_relationships").fetchone()[0]
        by_rel_type = cursor.execute("""
            SELECT relationship_type, COUNT(*) as cnt
            FROM gleif_relationships
            WHERE relationship_type IS NOT NULL
            GROUP BY relationship_type
            ORDER BY cnt DESC
        """).fetchall()

        # China-specific analysis (CN entities)
        cn_entities = cursor.execute("""
            SELECT COUNT(*) FROM gleif_entities
            WHERE legal_address_country = 'CN'
        """).fetchone()[0]

        # Hong Kong entities
        hk_entities = cursor.execute("""
            SELECT COUNT(*) FROM gleif_entities
            WHERE legal_address_country = 'HK'
        """).fetchone()[0]

        summary = {
            'processing_timestamp': datetime.now(timezone.utc).isoformat(),
            'entities': {
                'total': total_entities,
                'mainland_china': cn_entities,
                'hong_kong': hk_entities,
                'top_countries': [{'country': r[0], 'count': r[1]} for r in by_country],
                'by_category': [{'category': r[0], 'count': r[1]} for r in by_category]
            },
            'relationships': {
                'total': total_relationships,
                'by_type': [{'type': r[0], 'count': r[1]} for r in by_rel_type]
            }
        }

        logger.info(f"\nPROCESSING SUMMARY:")
        logger.info(f"Total Entities: {total_entities:,}")
        logger.info(f"  - Mainland China: {cn_entities:,}")
        logger.info(f"  - Hong Kong: {hk_entities:,}")
        logger.info(f"Total Relationships: {total_relationships:,}")
        logger.info(f"\nTop 10 Countries:")
        for country_data in by_country[:10]:
            logger.info(f"  {country_data[0]}: {country_data[1]:,}")

        # Save summary
        summary_file = Path("analysis/GLEIF_PROCESSING_SUMMARY.json")
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"\nSummary saved to: {summary_file}")

        return summary

    def run(self):
        """Execute full GLEIF processing pipeline"""
        try:
            logger.info("Starting GLEIF comprehensive processing...")
            start_time = time.time()

            self.setup_schema()
            self.process_lei_entities()
            self.process_relationships()
            summary = self.generate_summary()

            elapsed = time.time() - start_time
            logger.info(f"\n{'='*60}")
            logger.info(f"GLEIF PROCESSING COMPLETE")
            logger.info(f"Total time: {elapsed/60:.1f} minutes")
            logger.info(f"{'='*60}")

        except Exception as e:
            logger.error(f"Processing failed: {e}", exc_info=True)
        finally:
            self.conn.close()

if __name__ == "__main__":
    processor = GLEIFProcessor()
    processor.run()
