#!/usr/bin/env python3
"""
arXiv Comprehensive Data Ingestion

Processes ALL 2.85M arXiv preprints into the unified research mapping database.
Matches against existing OpenAlex records to avoid duplicates.

ZERO FABRICATION PROTOCOL:
- Process exact file that exists
- Count actual records from arXiv JSON
- Report duplicates found via DOI/arXiv ID matching
- Full audit trail

Usage:
    python scripts/ingest_arxiv_comprehensive.py
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


class ArXivIngestionProcessor:
    """Process arXiv data into unified research database"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.arxiv_json_path = Path("F:/Kaggle_arXiv_extracted/arxiv-metadata-oai-snapshot.json")

        # Statistics
        self.stats = {
            'records_processed': 0,
            'records_inserted': 0,
            'duplicates_found': 0,
            'errors': 0
        }

        self.batch_size = 10000

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def check_duplicate(self, cursor, doi: str, arxiv_id: str) -> Optional[int]:
        """Check if publication already exists"""
        # Check by DOI first (most reliable)
        if doi:
            cursor.execute(
                "SELECT unified_id FROM unified_publications WHERE doi = ?",
                (doi,)
            )
            result = cursor.fetchone()
            if result:
                return result[0]

        # Check by arXiv ID
        if arxiv_id:
            cursor.execute(
                "SELECT unified_id FROM unified_publications WHERE arxiv_id = ?",
                (arxiv_id,)
            )
            result = cursor.fetchone()
            if result:
                return result[0]

        return None

    def extract_arxiv_data(self, record: Dict) -> Dict:
        """Extract publication data from arXiv record"""
        arxiv_id = record.get('id', '')
        title = record.get('title', '').replace('\n', ' ').strip()
        abstract = record.get('abstract', '').replace('\n', ' ').strip()

        # DOI
        doi = record.get('doi')
        if doi:
            doi = doi.strip()

        # Authors
        authors_str = record.get('authors', '')
        authors = [a.strip() for a in authors_str.split(',') if a.strip()]

        # Categories
        categories = record.get('categories', '').split()
        primary_category = categories[0] if categories else None

        # Dates
        versions = record.get('versions', [])
        if versions:
            first_version = versions[0]
            first_date = first_version.get('created', '')
        else:
            first_date = ''

        update_date = record.get('update_date', '')

        # Extract year
        pub_year = None
        if first_date:
            try:
                pub_year = int(first_date[:4])
            except:
                pass

        return {
            'arxiv_id': arxiv_id,
            'doi': doi,
            'title': title,
            'abstract': abstract,
            'authors': authors,
            'categories': categories,
            'primary_category': primary_category,
            'publication_year': pub_year,
            'publication_date': first_date[:10] if first_date else None,
            'update_date': update_date,
            'raw_data_json': json.dumps(record)
        }

    def insert_publication(self, cursor, data: Dict) -> int:
        """Insert arXiv publication"""
        cursor.execute("""
            INSERT INTO unified_publications (
                arxiv_id, doi, title, abstract,
                publication_year, publication_date,
                result_type, source_system, is_primary_record,
                is_open_access, oa_status,
                processing_date, raw_data_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['arxiv_id'],
            data['doi'],
            data['title'],
            data['abstract'],
            data['publication_year'],
            data['publication_date'],
            'preprint',
            'arxiv',
            True,  # is_primary (unless found duplicate)
            True,  # arXiv is open access
            'green',  # arXiv OA status
            datetime.now().isoformat(),
            data['raw_data_json']
        ))

        return cursor.lastrowid

    def insert_authors(self, cursor, unified_id: int, authors: list):
        """Insert simple author records for arXiv (no ORCID/institution data)"""
        for i, author_name in enumerate(authors):
            # Check if author exists
            cursor.execute(
                "SELECT author_id FROM research_authors WHERE display_name = ?",
                (author_name,)
            )
            result = cursor.fetchone()

            if result:
                author_id = result[0]
            else:
                # Create new author
                cursor.execute("""
                    INSERT INTO research_authors (display_name, first_seen)
                    VALUES (?, ?)
                """, (author_name, datetime.now().isoformat()))
                author_id = cursor.lastrowid

            # Link to publication
            position = 'first' if i == 0 else ('last' if i == len(authors)-1 else 'middle')
            try:
                cursor.execute("""
                    INSERT INTO publication_authors (
                        unified_id, author_id, author_position, raw_author_name
                    ) VALUES (?, ?, ?, ?)
                """, (unified_id, author_id, position, author_name))
            except sqlite3.IntegrityError:
                # Already exists
                pass

    def insert_categories(self, cursor, unified_id: int, categories: list):
        """Insert arXiv categories as topics"""
        for category in categories:
            # Get or create topic
            cursor.execute(
                "SELECT topic_id FROM research_topics WHERE arxiv_category = ?",
                (category,)
            )
            result = cursor.fetchone()

            if result:
                topic_id = result[0]
            else:
                # Create new topic
                cursor.execute("""
                    INSERT INTO research_topics (topic_name, topic_type, arxiv_category)
                    VALUES (?, ?, ?)
                """, (category, 'arxiv_category', category))
                topic_id = cursor.lastrowid

            # Link to publication
            try:
                cursor.execute("""
                    INSERT INTO publication_topics (unified_id, topic_id, score, is_primary)
                    VALUES (?, ?, ?, ?)
                """, (unified_id, topic_id, 1.0, category == categories[0]))
            except sqlite3.IntegrityError:
                # Already exists
                pass

    def link_duplicate(self, cursor, primary_id: int, arxiv_id: str, doi: str, match_method: str):
        """Link arXiv record to existing OpenAlex record"""
        cursor.execute("""
            INSERT INTO cross_reference_map (
                primary_unified_id, arxiv_id, doi,
                match_confidence, match_method, match_date
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            primary_id,
            arxiv_id,
            doi,
            1.0 if match_method == 'doi' else 0.98,
            match_method,
            datetime.now().isoformat()
        ))

    def process_record(self, cursor, record: Dict) -> bool:
        """Process single arXiv record"""
        try:
            # Extract data
            data = self.extract_arxiv_data(record)

            # Check for duplicates (likely in OpenAlex already)
            duplicate_id = self.check_duplicate(cursor, data.get('doi'), data.get('arxiv_id'))
            if duplicate_id:
                # Link to existing record
                match_method = 'doi' if data.get('doi') else 'arxiv_id'
                self.link_duplicate(
                    cursor, duplicate_id, data['arxiv_id'], data.get('doi'), match_method
                )
                self.stats['duplicates_found'] += 1
                return False

            # Insert as new record
            unified_id = self.insert_publication(cursor, data)
            self.insert_authors(cursor, unified_id, data['authors'])
            self.insert_categories(cursor, unified_id, data['categories'])

            self.stats['records_inserted'] += 1
            return True

        except Exception as e:
            logger.error(f"Error processing arXiv record {record.get('id')}: {e}")
            self.stats['errors'] += 1
            return False

    def process_all(self):
        """Process all arXiv data"""
        logger.info("=" * 80)
        logger.info("ARXIV COMPREHENSIVE INGESTION")
        logger.info("=" * 80)

        if not self.arxiv_json_path.exists():
            logger.error(f"arXiv data file not found: {self.arxiv_json_path}")
            return

        logger.info(f"Reading from: {self.arxiv_json_path}")
        logger.info(f"File size: {self.arxiv_json_path.stat().st_size / (1024**3):.2f} GB")

        conn = self.get_connection()
        cursor = conn.cursor()

        started_at = datetime.now().isoformat()
        batch = []

        try:
            with open(self.arxiv_json_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        record = json.loads(line)
                        batch.append(record)

                        # Process in batches
                        if len(batch) >= self.batch_size:
                            for r in batch:
                                self.process_record(cursor, r)
                                self.stats['records_processed'] += 1

                            conn.commit()
                            batch = []

                            # Log progress
                            if self.stats['records_processed'] % 100000 == 0:
                                logger.info(f"Processed: {self.stats['records_processed']:,} records")
                                logger.info(f"  Inserted: {self.stats['records_inserted']:,}")
                                logger.info(f"  Duplicates: {self.stats['duplicates_found']:,}")

                    except json.JSONDecodeError:
                        continue

                # Process remaining batch
                for r in batch:
                    self.process_record(cursor, r)
                    self.stats['records_processed'] += 1

                conn.commit()

            # Update processing status
            completed_at = datetime.now().isoformat()
            duration = (datetime.fromisoformat(completed_at) - datetime.fromisoformat(started_at)).total_seconds()

            cursor.execute("""
                INSERT INTO processing_status (
                    source_system, source_file, status,
                    records_processed, records_inserted,
                    records_skipped, duplicates_found,
                    started_at, completed_at, processing_duration_seconds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                'arxiv',
                str(self.arxiv_json_path),
                'complete',
                self.stats['records_processed'],
                self.stats['records_inserted'],
                self.stats['records_processed'] - self.stats['records_inserted'],
                self.stats['duplicates_found'],
                started_at,
                completed_at,
                int(duration)
            ))
            conn.commit()

        except Exception as e:
            logger.error(f"Fatal error: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()

        finally:
            conn.close()

        logger.info("\n" + "=" * 80)
        logger.info("INGESTION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Total records processed: {self.stats['records_processed']:,}")
        logger.info(f"Total records inserted: {self.stats['records_inserted']:,}")
        logger.info(f"Duplicates found: {self.stats['duplicates_found']:,}")
        logger.info(f"Errors: {self.stats['errors']:,}")
        logger.info(f"Duplicate rate: {self.stats['duplicates_found']/self.stats['records_processed']*100:.1f}%")


def main():
    """Main execution"""
    db_path = "F:/OSINT_WAREHOUSE/research_mapping_comprehensive.db"
    processor = ArXivIngestionProcessor(db_path)
    processor.process_all()


if __name__ == "__main__":
    main()
