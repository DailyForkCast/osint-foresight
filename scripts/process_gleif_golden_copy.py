#!/usr/bin/env python3
"""
GLEIF Golden Copy Data Processor
Imports GLEIF entity, relationship, and mapping data into OSINT master database
"""

import sqlite3
import zipfile
import json
import csv
from pathlib import Path
from datetime import datetime
import logging
import io

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GLEIFProcessor:
    def __init__(self):
        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        self.data_dir = Path("F:/GLEIF")
        self.batch_size = 1000

        # File mappings
        self.files = {
            'lei2': '20251011-0800-gleif-goldencopy-lei2-golden-copy.json.zip',
            'rr': '20251011-0800-gleif-goldencopy-rr-golden-copy.json.zip',
            'repex': '20251011-0800-gleif-goldencopy-repex-golden-copy.json.zip',
            'isin': 'isin-lei-20251011T070301.zip',
            'bic': 'LEI-BIC-20250926.zip',
            'qcc': 'LEI-QCC-20250901.zip',
            'opencorporates': 'oc-lei-20251001T131236.zip'
        }

    def setup_database(self):
        """Create GLEIF tables if they don't exist"""
        logger.info("Setting up database schema...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create gleif_entities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gleif_entities (
                lei TEXT PRIMARY KEY,
                legal_name TEXT,
                legal_name_language TEXT,
                legal_address_line1 TEXT,
                legal_address_city TEXT,
                legal_address_region TEXT,
                legal_address_country TEXT,
                legal_address_postal TEXT,
                hq_address_line1 TEXT,
                hq_address_city TEXT,
                hq_address_region TEXT,
                hq_address_country TEXT,
                legal_jurisdiction TEXT,
                entity_category TEXT,
                entity_status TEXT,
                legal_form_code TEXT,
                entity_creation_date TEXT,
                registration_status TEXT,
                initial_registration_date TEXT,
                last_update_date TEXT,
                managing_lou TEXT,
                validation_sources TEXT,
                conformity_flag TEXT,
                data_source TEXT DEFAULT 'GLEIF_LEI2',
                imported_date TEXT
            )
        """)

        # Create gleif_relationships table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gleif_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_lei TEXT,
                end_lei TEXT,
                relationship_type TEXT,
                relationship_status TEXT,
                relationship_start_date TEXT,
                relationship_end_date TEXT,
                registration_status TEXT,
                last_update_date TEXT,
                validation_sources TEXT,
                validation_reference TEXT,
                data_source TEXT DEFAULT 'GLEIF_RR',
                imported_date TEXT
            )
        """)

        # Create mapping tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gleif_isin_mapping (
                lei TEXT,
                isin TEXT,
                imported_date TEXT,
                PRIMARY KEY (lei, isin)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gleif_bic_mapping (
                lei TEXT,
                bic TEXT,
                imported_date TEXT,
                PRIMARY KEY (lei, bic)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gleif_qcc_mapping (
                lei TEXT,
                qcc TEXT,
                imported_date TEXT,
                PRIMARY KEY (lei, qcc)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gleif_opencorporates_mapping (
                lei TEXT PRIMARY KEY,
                opencorporates_id TEXT,
                jurisdiction_code TEXT,
                company_number TEXT,
                imported_date TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gleif_repex (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lei TEXT,
                exception_category TEXT,
                exception_reason TEXT,
                exception_reference TEXT,
                registration_status TEXT,
                last_update_date TEXT,
                imported_date TEXT
            )
        """)

        conn.commit()
        conn.close()

        # Create indexes in separate connection to ensure tables exist
        logger.info("Creating indexes...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_gleif_entities_country ON gleif_entities(legal_address_country)",
            "CREATE INDEX IF NOT EXISTS idx_gleif_entities_jurisdiction ON gleif_entities(legal_jurisdiction)",
            "CREATE INDEX IF NOT EXISTS idx_gleif_entities_status ON gleif_entities(entity_status)",
            "CREATE INDEX IF NOT EXISTS idx_gleif_entities_reg_status ON gleif_entities(registration_status)",
            "CREATE INDEX IF NOT EXISTS idx_gleif_relationships_start ON gleif_relationships(start_lei)",
            "CREATE INDEX IF NOT EXISTS idx_gleif_relationships_end ON gleif_relationships(end_lei)",
            "CREATE INDEX IF NOT EXISTS idx_gleif_relationships_type ON gleif_relationships(relationship_type)",
            "CREATE INDEX IF NOT EXISTS idx_gleif_relationships_status ON gleif_relationships(relationship_status)",
            "CREATE INDEX IF NOT EXISTS idx_gleif_isin_lei ON gleif_isin_mapping(lei)",
            "CREATE INDEX IF NOT EXISTS idx_gleif_isin_isin ON gleif_isin_mapping(isin)",
            "CREATE INDEX IF NOT EXISTS idx_gleif_bic_lei ON gleif_bic_mapping(lei)",
            "CREATE INDEX IF NOT EXISTS idx_gleif_opencorp_oc ON gleif_opencorporates_mapping(opencorporates_id)"
        ]

        for idx_sql in indexes:
            try:
                cursor.execute(idx_sql)
            except Exception as e:
                logger.warning(f"Index creation warning: {e}")

        conn.commit()
        conn.close()

        logger.info("Database schema ready")

    def extract_json_value(self, obj, path):
        """Safely extract nested JSON values"""
        if not obj:
            return None

        parts = path.split('.')
        current = obj

        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None

            if current is None:
                return None

        # Handle GLEIF's {"$": "value"} format
        if isinstance(current, dict) and '$' in current:
            return current['$']

        return current

    def process_lei2_entities(self):
        """Process LEI2 entity data"""
        logger.info("Processing LEI2 entities...")

        file_path = self.data_dir / self.files['lei2']
        if not file_path.exists():
            logger.error(f"LEI2 file not found: {file_path}")
            return 0

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Clear existing data
        cursor.execute('DELETE FROM gleif_entities')
        conn.commit()
        logger.info("Cleared existing entities")

        imported = 0
        batch = []
        imported_date = datetime.now().isoformat()

        try:
            with zipfile.ZipFile(file_path, 'r') as z:
                json_filename = z.namelist()[0]

                with z.open(json_filename) as f:
                    # Read file line by line (NDJSON-like, but wrapped in {"records": [...]})
                    content = f.read().decode('utf-8')

                    # Parse as single JSON (contains {"records": [...]})
                    data = json.loads(content)
                    records = data.get('records', [])

                    logger.info(f"Found {len(records)} entity records")

                    for record in records:
                        try:
                            lei = self.extract_json_value(record, 'LEI')

                            entity = {
                                'lei': lei,
                                'legal_name': self.extract_json_value(record, 'Entity.LegalName'),
                                'legal_name_language': record.get('Entity', {}).get('LegalName', {}).get('@xml:lang'),
                                'legal_address_line1': self.extract_json_value(record, 'Entity.LegalAddress.FirstAddressLine'),
                                'legal_address_city': self.extract_json_value(record, 'Entity.LegalAddress.City'),
                                'legal_address_region': self.extract_json_value(record, 'Entity.LegalAddress.Region'),
                                'legal_address_country': self.extract_json_value(record, 'Entity.LegalAddress.Country'),
                                'legal_address_postal': self.extract_json_value(record, 'Entity.LegalAddress.PostalCode'),
                                'hq_address_line1': self.extract_json_value(record, 'Entity.HeadquartersAddress.FirstAddressLine'),
                                'hq_address_city': self.extract_json_value(record, 'Entity.HeadquartersAddress.City'),
                                'hq_address_region': self.extract_json_value(record, 'Entity.HeadquartersAddress.Region'),
                                'hq_address_country': self.extract_json_value(record, 'Entity.HeadquartersAddress.Country'),
                                'legal_jurisdiction': self.extract_json_value(record, 'Entity.LegalJurisdiction'),
                                'entity_category': self.extract_json_value(record, 'Entity.EntityCategory'),
                                'entity_status': self.extract_json_value(record, 'Entity.EntityStatus'),
                                'legal_form_code': self.extract_json_value(record, 'Entity.LegalForm.EntityLegalFormCode'),
                                'entity_creation_date': self.extract_json_value(record, 'Entity.EntityCreationDate'),
                                'registration_status': self.extract_json_value(record, 'Registration.RegistrationStatus'),
                                'initial_registration_date': self.extract_json_value(record, 'Registration.InitialRegistrationDate'),
                                'last_update_date': self.extract_json_value(record, 'Registration.LastUpdateDate'),
                                'managing_lou': self.extract_json_value(record, 'Registration.ManagingLOU'),
                                'validation_sources': self.extract_json_value(record, 'Registration.ValidationSources'),
                                'conformity_flag': self.extract_json_value(record, 'Extension.gleif:conformity.gleif:conformityflag'),
                                'imported_date': imported_date
                            }

                            batch.append(entity)

                            # Batch insert
                            if len(batch) >= self.batch_size:
                                cursor.executemany("""
                                    INSERT OR REPLACE INTO gleif_entities (
                                        lei, legal_name, legal_name_language,
                                        legal_address_line1, legal_address_city, legal_address_region,
                                        legal_address_country, legal_address_postal,
                                        hq_address_line1, hq_address_city, hq_address_region, hq_address_country,
                                        legal_jurisdiction, entity_category, entity_status,
                                        legal_form_code, entity_creation_date,
                                        registration_status, initial_registration_date, last_update_date,
                                        managing_lou, validation_sources, conformity_flag, imported_date
                                    ) VALUES (
                                        :lei, :legal_name, :legal_name_language,
                                        :legal_address_line1, :legal_address_city, :legal_address_region,
                                        :legal_address_country, :legal_address_postal,
                                        :hq_address_line1, :hq_address_city, :hq_address_region, :hq_address_country,
                                        :legal_jurisdiction, :entity_category, :entity_status,
                                        :legal_form_code, :entity_creation_date,
                                        :registration_status, :initial_registration_date, :last_update_date,
                                        :managing_lou, :validation_sources, :conformity_flag, :imported_date
                                    )
                                """, batch)
                                conn.commit()
                                imported += len(batch)
                                logger.info(f"Imported {imported:,} entities...")
                                batch = []

                        except Exception as e:
                            logger.warning(f"Error processing entity {lei}: {e}")
                            continue

                    # Insert remaining batch
                    if batch:
                        cursor.executemany("""
                            INSERT OR REPLACE INTO gleif_entities (
                                lei, legal_name, legal_name_language,
                                legal_address_line1, legal_address_city, legal_address_region,
                                legal_address_country, legal_address_postal,
                                hq_address_line1, hq_address_city, hq_address_region, hq_address_country,
                                legal_jurisdiction, entity_category, entity_status,
                                legal_form_code, entity_creation_date,
                                registration_status, initial_registration_date, last_update_date,
                                managing_lou, validation_sources, conformity_flag, imported_date
                            ) VALUES (
                                :lei, :legal_name, :legal_name_language,
                                :legal_address_line1, :legal_address_city, :legal_address_region,
                                :legal_address_country, :legal_address_postal,
                                :hq_address_line1, :hq_address_city, :hq_address_region, :hq_address_country,
                                :legal_jurisdiction, :entity_category, :entity_status,
                                :legal_form_code, :entity_creation_date,
                                :registration_status, :initial_registration_date, :last_update_date,
                                :managing_lou, :validation_sources, :conformity_flag, :imported_date
                            )
                        """, batch)
                        conn.commit()
                        imported += len(batch)

        except Exception as e:
            logger.error(f"Error processing LEI2 file: {e}")
            import traceback
            traceback.print_exc()

        finally:
            conn.close()

        logger.info(f"Imported {imported:,} entities")
        return imported

    def process_rr_relationships(self):
        """Process RR relationship data"""
        logger.info("Processing RR relationships...")

        file_path = self.data_dir / self.files['rr']
        if not file_path.exists():
            logger.error(f"RR file not found: {file_path}")
            return 0

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Clear existing data
        cursor.execute('DELETE FROM gleif_relationships')
        conn.commit()
        logger.info("Cleared existing relationships")

        imported = 0
        batch = []
        imported_date = datetime.now().isoformat()

        try:
            with zipfile.ZipFile(file_path, 'r') as z:
                json_filename = z.namelist()[0]

                with z.open(json_filename) as f:
                    content = f.read().decode('utf-8')
                    data = json.loads(content)
                    records = data.get('relations', [])

                    logger.info(f"Found {len(records)} relationship records")

                    for record in records:
                        try:
                            rel_record = record.get('RelationshipRecord', {})
                            relationship = rel_record.get('Relationship', {})
                            registration = rel_record.get('Registration', {})

                            # Extract relationship period dates
                            periods = relationship.get('RelationshipPeriods', {})
                            period = periods.get('RelationshipPeriod', {}) if periods else {}

                            start_date = self.extract_json_value(period, 'StartDate')
                            end_date = self.extract_json_value(period, 'EndDate')

                            rel = {
                                'start_lei': self.extract_json_value(relationship, 'StartNode.NodeID'),
                                'end_lei': self.extract_json_value(relationship, 'EndNode.NodeID'),
                                'relationship_type': self.extract_json_value(relationship, 'RelationshipType'),
                                'relationship_status': self.extract_json_value(relationship, 'RelationshipStatus'),
                                'relationship_start_date': start_date,
                                'relationship_end_date': end_date,
                                'registration_status': self.extract_json_value(registration, 'RegistrationStatus'),
                                'last_update_date': self.extract_json_value(registration, 'LastUpdateDate'),
                                'validation_sources': self.extract_json_value(registration, 'ValidationSources'),
                                'validation_reference': self.extract_json_value(registration, 'ValidationReference'),
                                'imported_date': imported_date
                            }

                            batch.append(rel)

                            # Batch insert
                            if len(batch) >= self.batch_size:
                                cursor.executemany("""
                                    INSERT INTO gleif_relationships (
                                        start_lei, end_lei, relationship_type, relationship_status,
                                        relationship_start_date, relationship_end_date,
                                        registration_status, last_update_date,
                                        validation_sources, validation_reference, imported_date
                                    ) VALUES (
                                        :start_lei, :end_lei, :relationship_type, :relationship_status,
                                        :relationship_start_date, :relationship_end_date,
                                        :registration_status, :last_update_date,
                                        :validation_sources, :validation_reference, :imported_date
                                    )
                                """, batch)
                                conn.commit()
                                imported += len(batch)
                                logger.info(f"Imported {imported:,} relationships...")
                                batch = []

                        except Exception as e:
                            logger.warning(f"Error processing relationship: {e}")
                            continue

                    # Insert remaining batch
                    if batch:
                        cursor.executemany("""
                            INSERT INTO gleif_relationships (
                                start_lei, end_lei, relationship_type, relationship_status,
                                relationship_start_date, relationship_end_date,
                                registration_status, last_update_date,
                                validation_sources, validation_reference, imported_date
                            ) VALUES (
                                :start_lei, :end_lei, :relationship_type, :relationship_status,
                                :relationship_start_date, :relationship_end_date,
                                :registration_status, :last_update_date,
                                :validation_sources, :validation_reference, :imported_date
                            )
                        """, batch)
                        conn.commit()
                        imported += len(batch)

        except Exception as e:
            logger.error(f"Error processing RR file: {e}")
            import traceback
            traceback.print_exc()

        finally:
            conn.close()

        logger.info(f"Imported {imported:,} relationships")
        return imported

    def process_csv_mapping(self, file_key, table_name, columns):
        """Generic CSV mapping processor"""
        logger.info(f"Processing {file_key} mapping...")

        file_path = self.data_dir / self.files[file_key]
        if not file_path.exists():
            logger.error(f"{file_key} file not found: {file_path}")
            return 0

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Clear existing data
        cursor.execute(f'DELETE FROM {table_name}')
        conn.commit()

        imported = 0
        batch = []
        imported_date = datetime.now().isoformat()

        try:
            with zipfile.ZipFile(file_path, 'r') as z:
                csv_filename = z.namelist()[0]

                with z.open(csv_filename) as f:
                    # Decode bytes to text
                    text_file = io.TextIOWrapper(f, encoding='utf-8')
                    reader = csv.DictReader(text_file)

                    for row in reader:
                        # Add imported_date
                        row['imported_date'] = imported_date

                        # Special handling for OpenCorporates
                        if file_key == 'opencorporates' and 'OpenCorporatesID' in row:
                            oc_id = row['OpenCorporatesID']
                            if '/' in oc_id:
                                jurisdiction, company_num = oc_id.split('/', 1)
                                row['jurisdiction_code'] = jurisdiction
                                row['company_number'] = company_num
                            row['opencorporates_id'] = oc_id

                        batch.append(row)

                        # Batch insert
                        if len(batch) >= self.batch_size:
                            placeholders = ', '.join([f':{col}' for col in columns])
                            cols_str = ', '.join(columns)
                            cursor.executemany(f"""
                                INSERT OR REPLACE INTO {table_name} ({cols_str})
                                VALUES ({placeholders})
                            """, batch)
                            conn.commit()
                            imported += len(batch)
                            logger.info(f"Imported {imported:,} {file_key} mappings...")
                            batch = []

                    # Insert remaining batch
                    if batch:
                        placeholders = ', '.join([f':{col}' for col in columns])
                        cols_str = ', '.join(columns)
                        cursor.executemany(f"""
                            INSERT OR REPLACE INTO {table_name} ({cols_str})
                            VALUES ({placeholders})
                        """, batch)
                        conn.commit()
                        imported += len(batch)

        except Exception as e:
            logger.error(f"Error processing {file_key} file: {e}")
            import traceback
            traceback.print_exc()

        finally:
            conn.close()

        logger.info(f"Imported {imported:,} {file_key} mappings")
        return imported

    def generate_summary(self):
        """Generate summary statistics"""
        logger.info("\n" + "="*80)
        logger.info("GLEIF Data Import Summary")
        logger.info("="*80)

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        # Entities summary
        total_entities = conn.execute('SELECT COUNT(*) FROM gleif_entities').fetchone()[0]
        active_entities = conn.execute('SELECT COUNT(*) FROM gleif_entities WHERE entity_status = "ACTIVE"').fetchone()[0]

        entities_by_country = conn.execute("""
            SELECT legal_address_country, COUNT(*) as cnt
            FROM gleif_entities
            WHERE legal_address_country IS NOT NULL
            GROUP BY legal_address_country
            ORDER BY cnt DESC
            LIMIT 10
        """).fetchall()

        # Relationships summary
        total_relationships = conn.execute('SELECT COUNT(*) FROM gleif_relationships').fetchone()[0]
        active_relationships = conn.execute('SELECT COUNT(*) FROM gleif_relationships WHERE relationship_status = "ACTIVE"').fetchone()[0]

        rel_by_type = conn.execute("""
            SELECT relationship_type, COUNT(*) as cnt
            FROM gleif_relationships
            GROUP BY relationship_type
            ORDER BY cnt DESC
            LIMIT 10
        """).fetchall()

        # Mappings summary
        isin_count = conn.execute('SELECT COUNT(*) FROM gleif_isin_mapping').fetchone()[0]
        bic_count = conn.execute('SELECT COUNT(*) FROM gleif_bic_mapping').fetchone()[0]
        qcc_count = conn.execute('SELECT COUNT(*) FROM gleif_qcc_mapping').fetchone()[0]
        oc_count = conn.execute('SELECT COUNT(*) FROM gleif_opencorporates_mapping').fetchone()[0]

        conn.close()

        logger.info(f"\nEntities: {total_entities:,} total, {active_entities:,} active")
        logger.info(f"\nTop 10 Countries:")
        for row in entities_by_country:
            logger.info(f"  {row['legal_address_country']}: {row['cnt']:,}")

        logger.info(f"\nRelationships: {total_relationships:,} total, {active_relationships:,} active")
        logger.info(f"\nTop 10 Relationship Types:")
        for row in rel_by_type:
            logger.info(f"  {row['relationship_type']}: {row['cnt']:,}")

        logger.info(f"\nCross-Reference Mappings:")
        logger.info(f"  ISIN: {isin_count:,}")
        logger.info(f"  BIC: {bic_count:,}")
        logger.info(f"  QCC: {qcc_count:,}")
        logger.info(f"  OpenCorporates: {oc_count:,}")

        logger.info("="*80 + "\n")

    def run(self):
        """Execute full processing pipeline"""
        logger.info("Starting GLEIF Golden Copy processing...")
        start_time = datetime.now()

        # Setup database
        self.setup_database()

        # Process entities (Priority 1)
        entities_imported = self.process_lei2_entities()

        # Process relationships (Priority 1)
        relationships_imported = self.process_rr_relationships()

        # Process mappings (Priority 2)
        isin_imported = self.process_csv_mapping(
            'isin',
            'gleif_isin_mapping',
            ['lei', 'isin', 'imported_date']
        )

        bic_imported = self.process_csv_mapping(
            'bic',
            'gleif_bic_mapping',
            ['lei', 'bic', 'imported_date']
        )

        qcc_imported = self.process_csv_mapping(
            'qcc',
            'gleif_qcc_mapping',
            ['lei', 'qcc', 'imported_date']
        )

        oc_imported = self.process_csv_mapping(
            'opencorporates',
            'gleif_opencorporates_mapping',
            ['lei', 'opencorporates_id', 'jurisdiction_code', 'company_number', 'imported_date']
        )

        # Generate summary
        self.generate_summary()

        elapsed = datetime.now() - start_time
        logger.info(f"Processing completed in {elapsed}")

        return {
            'entities': entities_imported,
            'relationships': relationships_imported,
            'isin': isin_imported,
            'bic': bic_imported,
            'qcc': qcc_imported,
            'opencorporates': oc_imported,
            'elapsed': str(elapsed)
        }


if __name__ == "__main__":
    processor = GLEIFProcessor()
    result = processor.run()
    logger.info(f"Import complete: {result}")
