#!/usr/bin/env python3
"""
OpenAIRE Comprehensive Data Ingestion

Processes OpenAIRE research outputs from existing database into
the unified research mapping database.

Matches against OpenAlex and arXiv to avoid duplicates, linking
EU-specific metadata to existing records.

ZERO FABRICATION PROTOCOL:
- Process exact records from OpenAIRE database
- Count actual records
- Match via DOI before inserting
- Full audit trail

Usage:
    python scripts/ingest_openaire_comprehensive.py
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OpenAIREIngestionProcessor:
    """Process OpenAIRE data into unified research database"""

    def __init__(self, db_path: str, openaire_db_path: str):
        self.db_path = db_path
        self.openaire_db_path = openaire_db_path

        # Statistics
        self.stats = {
            'records_processed': 0,
            'records_inserted': 0,
            'duplicates_found': 0,
            'linked_to_openalex': 0,
            'linked_to_arxiv': 0,
            'errors': 0
        }

        self.batch_size = 10000

    def get_connection(self) -> sqlite3.Connection:
        """Get unified database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def get_openaire_connection(self) -> sqlite3.Connection:
        """Get OpenAIRE source database connection"""
        return sqlite3.connect(self.openaire_db_path)

    def check_duplicate(self, cursor, doi: str, openaire_id: str) -> Optional[tuple]:
        """Check if publication already exists, return (unified_id, source_system)"""
        # Check by DOI first (most reliable)
        if doi:
            cursor.execute("""
                SELECT unified_id, source_system
                FROM unified_publications
                WHERE doi = ?
            """, (doi,))
            result = cursor.fetchone()
            if result:
                return result

        # Check by OpenAIRE ID
        if openaire_id:
            cursor.execute("""
                SELECT unified_id, source_system
                FROM unified_publications
                WHERE openaire_id = ?
            """, (openaire_id,))
            result = cursor.fetchone()
            if result:
                return result

        return None

    def extract_openaire_data(self, record: Dict) -> Dict:
        """Extract publication data from OpenAIRE record"""
        # Parse raw_data if stored as JSON
        if isinstance(record.get('raw_data'), str):
            try:
                raw_data = json.loads(record['raw_data'])
            except:
                raw_data = {}
        else:
            raw_data = record.get('raw_data', {})

        openaire_id = str(record.get('id', ''))
        title = record.get('title', '')
        doi = record.get('doi')

        # Extract year from date_accepted
        date_accepted = record.get('date_accepted')
        pub_year = None
        if date_accepted:
            try:
                pub_year = int(date_accepted[:4])
            except:
                pass

        result_type = record.get('result_type', 'article')
        country_code = record.get('country_code')

        return {
            'openaire_id': openaire_id,
            'doi': doi,
            'title': title,
            'publication_year': pub_year,
            'publication_date': date_accepted,
            'result_type': result_type,
            'country_code': country_code,
            'has_collaboration': record.get('has_collaboration', False),
            'raw_data_json': json.dumps(raw_data)
        }

    def insert_publication(self, cursor, data: Dict) -> int:
        """Insert OpenAIRE publication as new record"""
        cursor.execute("""
            INSERT INTO unified_publications (
                openaire_id, doi, title,
                publication_year, publication_date,
                result_type, source_system, is_primary_record,
                processing_date, raw_data_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['openaire_id'],
            data['doi'],
            data['title'],
            data['publication_year'],
            data['publication_date'],
            data['result_type'],
            'openaire',
            True,  # is_primary unless found duplicate
            datetime.now().isoformat(),
            data['raw_data_json']
        ))

        return cursor.lastrowid

    def link_duplicate(self, cursor, primary_id: int, openaire_id: str,
                      doi: str, source_system: str):
        """Link OpenAIRE record to existing record"""
        match_method = 'doi' if doi else 'openaire_id'
        match_confidence = 1.0 if match_method == 'doi' else 0.85

        cursor.execute("""
            INSERT OR IGNORE INTO cross_reference_map (
                primary_unified_id, openaire_id, doi,
                match_confidence, match_method, match_date
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            primary_id,
            openaire_id,
            doi,
            match_confidence,
            match_method,
            datetime.now().isoformat()
        ))

        if source_system == 'openalex':
            self.stats['linked_to_openalex'] += 1
        elif source_system == 'arxiv':
            self.stats['linked_to_arxiv'] += 1

    def process_record(self, cursor, record: Dict) -> bool:
        """Process single OpenAIRE record"""
        try:
            # Extract data
            data = self.extract_openaire_data(record)

            # Check for duplicates
            duplicate = self.check_duplicate(cursor, data.get('doi'), data.get('openaire_id'))
            if duplicate:
                unified_id, source_system = duplicate
                # Link to existing record
                self.link_duplicate(
                    cursor, unified_id, data['openaire_id'],
                    data.get('doi'), source_system
                )
                self.stats['duplicates_found'] += 1
                return False

            # Insert as new record
            unified_id = self.insert_publication(cursor, data)

            # Note: OpenAIRE has limited author/institution data in our current extract
            # Could enhance this by re-querying OpenAIRE API for full metadata

            self.stats['records_inserted'] += 1
            return True

        except Exception as e:
            logger.error(f"Error processing OpenAIRE record {record.get('id')}: {e}")
            self.stats['errors'] += 1
            return False

    def process_all(self):
        """Process all OpenAIRE data"""
        logger.info("=" * 80)
        logger.info("OPENAIRE COMPREHENSIVE INGESTION")
        logger.info("=" * 80)

        if not Path(self.openaire_db_path).exists():
            logger.error(f"OpenAIRE database not found: {self.openaire_db_path}")
            return

        logger.info(f"Reading from: {self.openaire_db_path}")

        # Connect to both databases
        unified_conn = self.get_connection()
        unified_cursor = unified_conn.cursor()

        openaire_conn = self.get_openaire_connection()
        openaire_cursor = openaire_conn.cursor()

        started_at = datetime.now().isoformat()

        try:
            # Count total records
            openaire_cursor.execute("SELECT COUNT(*) FROM research_products")
            total_records = openaire_cursor.fetchone()[0]
            logger.info(f"Total OpenAIRE records to process: {total_records:,}")

            # Process in batches
            batch_size = self.batch_size
            offset = 0

            while offset < total_records:
                # Fetch batch
                openaire_cursor.execute("""
                    SELECT * FROM research_products
                    LIMIT ? OFFSET ?
                """, (batch_size, offset))

                columns = [desc[0] for desc in openaire_cursor.description]
                records = [dict(zip(columns, row)) for row in openaire_cursor.fetchall()]

                if not records:
                    break

                # Process batch
                for record in records:
                    self.process_record(unified_cursor, record)
                    self.stats['records_processed'] += 1

                unified_conn.commit()
                offset += batch_size

                # Log progress
                if self.stats['records_processed'] % 100000 == 0:
                    logger.info(f"Progress: {self.stats['records_processed']:,} / {total_records:,}")
                    logger.info(f"  Inserted: {self.stats['records_inserted']:,}")
                    logger.info(f"  Duplicates: {self.stats['duplicates_found']:,}")
                    logger.info(f"  Linked to OpenAlex: {self.stats['linked_to_openalex']:,}")

            # Update processing status
            completed_at = datetime.now().isoformat()
            duration = (datetime.fromisoformat(completed_at) - datetime.fromisoformat(started_at)).total_seconds()

            unified_cursor.execute("""
                INSERT INTO processing_status (
                    source_system, source_file, status,
                    records_processed, records_inserted,
                    records_skipped, duplicates_found,
                    started_at, completed_at, processing_duration_seconds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                'openaire',
                self.openaire_db_path,
                'complete',
                self.stats['records_processed'],
                self.stats['records_inserted'],
                self.stats['records_processed'] - self.stats['records_inserted'],
                self.stats['duplicates_found'],
                started_at,
                completed_at,
                int(duration)
            ))
            unified_conn.commit()

        except Exception as e:
            logger.error(f"Fatal error: {e}")
            import traceback
            traceback.print_exc()
            unified_conn.rollback()

        finally:
            openaire_conn.close()
            unified_conn.close()

        logger.info("\n" + "=" * 80)
        logger.info("INGESTION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Total records processed: {self.stats['records_processed']:,}")
        logger.info(f"Total records inserted: {self.stats['records_inserted']:,}")
        logger.info(f"Duplicates found: {self.stats['duplicates_found']:,}")
        logger.info(f"  Linked to OpenAlex: {self.stats['linked_to_openalex']:,}")
        logger.info(f"  Linked to arXiv: {self.stats['linked_to_arxiv']:,}")
        logger.info(f"Errors: {self.stats['errors']:,}")
        logger.info(f"Duplicate rate: {self.stats['duplicates_found']/self.stats['records_processed']*100:.1f}%")


def main():
    """Main execution"""
    unified_db = "F:/OSINT_WAREHOUSE/research_mapping_comprehensive.db"
    openaire_db = "F:/OSINT_Data/openaire_production_comprehensive/openaire_production.db"

    processor = OpenAIREIngestionProcessor(unified_db, openaire_db)
    processor.process_all()


if __name__ == "__main__":
    main()
