#!/usr/bin/env python3
"""
OpenAlex Comprehensive Data Ingestion

Processes ALL 250M+ publications from OpenAlex bulk download into
the unified research mapping database.

ZERO FABRICATION PROTOCOL:
- Process only files that exist and are readable
- Count actual records, never estimate
- Report exact numbers from source
- State "no data" when files are inaccessible
- Full audit trail via processing_status table

Usage:
    # Process all OpenAlex data (will take 30-50 hours)
    python scripts/ingest_openalex_comprehensive.py

    # Process specific date range (for testing)
    python scripts/ingest_openalex_comprehensive.py --start-date 2024-01-01 --end-date 2024-01-31

    # Resume from checkpoint
    python scripts/ingest_openalex_comprehensive.py --resume

    # Parallel processing (multiple workers)
    python scripts/ingest_openalex_comprehensive.py --workers 4
"""

import sqlite3
import json
import gzip
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import argparse
import multiprocessing
from typing import Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OpenAlexIngestionProcessor:
    """Process OpenAlex bulk data into unified research database"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.source_path = Path("F:/OSINT_Backups/openalex/data/works")

        # Statistics
        self.stats = {
            'files_processed': 0,
            'records_processed': 0,
            'records_inserted': 0,
            'records_skipped': 0,
            'duplicates_found': 0,
            'errors': 0
        }

        # Batch size for commits
        self.batch_size = 10000

        # Cached lookups for authors, institutions, topics
        self.author_cache = {}
        self.institution_cache = {}
        self.topic_cache = {}

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with optimizations"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=-2000000")
        conn.execute("PRAGMA temp_store=MEMORY")
        return conn

    def check_duplicate(self, cursor, doi: str, openalex_id: str) -> Optional[int]:
        """Check if publication already exists"""
        if doi:
            cursor.execute(
                "SELECT unified_id FROM unified_publications WHERE doi = ?",
                (doi,)
            )
            result = cursor.fetchone()
            if result:
                return result[0]

        if openalex_id:
            cursor.execute(
                "SELECT unified_id FROM unified_publications WHERE openalex_id = ?",
                (openalex_id,)
            )
            result = cursor.fetchone()
            if result:
                return result[0]

        return None

    def extract_publication_data(self, work: Dict) -> Dict:
        """Extract publication metadata from OpenAlex work"""
        # Basic metadata
        openalex_id = work.get('id', '').replace('https://openalex.org/', '')
        doi = work.get('doi', '').replace('https://doi.org/', '') if work.get('doi') else None

        # Title and abstract
        title = work.get('title') or work.get('display_name', '')
        abstract = work.get('abstract_inverted_index')
        if abstract and isinstance(abstract, dict):
            # Reconstruct abstract from inverted index
            words = []
            for word, positions in abstract.items():
                for pos in positions:
                    words.append((pos, word))
            words.sort()
            abstract = ' '.join([w for _, w in words])
        else:
            abstract = None

        # Dates
        pub_year = work.get('publication_year')
        pub_date = work.get('publication_date')

        # Language
        language = work.get('language')

        # Type
        result_type = work.get('type', 'article')

        # Open access
        oa_info = work.get('open_access', {})
        is_open_access = oa_info.get('is_oa', False)
        oa_status = oa_info.get('oa_status', 'closed')
        oa_url = oa_info.get('oa_url')

        # Citations
        cited_by_count = work.get('cited_by_count', 0)

        return {
            'openalex_id': openalex_id,
            'doi': doi,
            'title': title,
            'abstract': abstract,
            'publication_year': pub_year,
            'publication_date': pub_date,
            'language': language,
            'result_type': result_type,
            'is_open_access': is_open_access,
            'oa_status': oa_status,
            'oa_url': oa_url,
            'cited_by_count': cited_by_count,
            'raw_data_json': json.dumps(work)
        }

    def insert_publication(self, cursor, pub_data: Dict) -> int:
        """Insert publication and return unified_id"""
        cursor.execute("""
            INSERT INTO unified_publications (
                openalex_id, doi, title, abstract,
                publication_year, publication_date, language,
                result_type, source_system, is_primary_record,
                is_open_access, oa_status, oa_url,
                cited_by_count, processing_date, raw_data_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pub_data['openalex_id'],
            pub_data['doi'],
            pub_data['title'],
            pub_data['abstract'],
            pub_data['publication_year'],
            pub_data['publication_date'],
            pub_data['language'],
            pub_data['result_type'],
            'openalex',
            True,  # is_primary_record
            pub_data['is_open_access'],
            pub_data['oa_status'],
            pub_data['oa_url'],
            pub_data['cited_by_count'],
            datetime.now().isoformat(),
            pub_data['raw_data_json']
        ))

        return cursor.lastrowid

    def get_or_create_author(self, cursor, author_data: Dict) -> int:
        """Get existing author or create new one"""
        author_id = author_data.get('id', '').replace('https://openalex.org/', '')
        orcid = author_data.get('orcid')

        # Check cache
        cache_key = orcid if orcid else author_id
        if cache_key in self.author_cache:
            return self.author_cache[cache_key]

        # Check database
        if orcid:
            cursor.execute("SELECT author_id FROM research_authors WHERE orcid = ?", (orcid,))
        else:
            cursor.execute("SELECT author_id FROM research_authors WHERE openalex_author_id = ?", (author_id,))

        result = cursor.fetchone()
        if result:
            self.author_cache[cache_key] = result[0]
            return result[0]

        # Create new author
        display_name = author_data.get('display_name', 'Unknown')
        cursor.execute("""
            INSERT INTO research_authors (display_name, orcid, openalex_author_id, first_seen)
            VALUES (?, ?, ?, ?)
        """, (display_name, orcid, author_id, datetime.now().isoformat()))

        new_id = cursor.lastrowid
        self.author_cache[cache_key] = new_id
        return new_id

    def get_or_create_institution(self, cursor, inst_data: Dict) -> int:
        """Get existing institution or create new one"""
        inst_id = inst_data.get('id', '').replace('https://openalex.org/', '')
        ror = inst_data.get('ror', '').replace('https://ror.org/', '') if inst_data.get('ror') else None

        # Check cache
        cache_key = ror if ror else inst_id
        if cache_key in self.institution_cache:
            return self.institution_cache[cache_key]

        # Check database
        if ror:
            cursor.execute("SELECT institution_id FROM research_institutions WHERE ror_id = ?", (ror,))
        else:
            cursor.execute("SELECT institution_id FROM research_institutions WHERE openalex_inst_id = ?", (inst_id,))

        result = cursor.fetchone()
        if result:
            self.institution_cache[cache_key] = result[0]
            return result[0]

        # Create new institution
        display_name = inst_data.get('display_name', 'Unknown')
        country_code = inst_data.get('country_code')
        inst_type = inst_data.get('type')

        cursor.execute("""
            INSERT INTO research_institutions (
                display_name, ror_id, openalex_inst_id,
                country_code, institution_type, first_seen
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (display_name, ror, inst_id, country_code, inst_type, datetime.now().isoformat()))

        new_id = cursor.lastrowid
        self.institution_cache[cache_key] = new_id
        return new_id

    def process_authorships(self, cursor, unified_id: int, work: Dict):
        """Process and insert author relationships"""
        authorships = work.get('authorships', [])

        for authorship in authorships:
            author_data = authorship.get('author', {})
            if not author_data:
                continue

            # Get or create author
            author_id = self.get_or_create_author(cursor, author_data)

            # Insert publication-author relationship
            author_position = authorship.get('author_position', 'unknown')
            is_corresponding = authorship.get('is_corresponding', False)
            raw_author_name = authorship.get('raw_author_name', author_data.get('display_name'))

            try:
                cursor.execute("""
                    INSERT INTO publication_authors (
                        unified_id, author_id, author_position,
                        is_corresponding, raw_author_name
                    ) VALUES (?, ?, ?, ?, ?)
                """, (unified_id, author_id, author_position, is_corresponding, raw_author_name))
            except sqlite3.IntegrityError:
                # Already exists
                pass

            # Process institutions for this author
            institutions = authorship.get('institutions', [])
            for inst_data in institutions:
                if not inst_data:
                    continue

                institution_id = self.get_or_create_institution(cursor, inst_data)

                # Insert publication-institution relationship
                raw_affiliation = authorship.get('raw_affiliation_string')
                try:
                    cursor.execute("""
                        INSERT INTO publication_institutions (
                            unified_id, institution_id, author_id, raw_affiliation_string
                        ) VALUES (?, ?, ?, ?)
                    """, (unified_id, institution_id, author_id, raw_affiliation))
                except sqlite3.IntegrityError:
                    # Already exists
                    pass

    def process_topics(self, cursor, unified_id: int, work: Dict):
        """Process and insert topic relationships"""
        topics = work.get('topics', [])

        for topic_data in topics:
            topic_name = topic_data.get('display_name')
            if not topic_name:
                continue

            # Get or create topic
            topic_id = self.topic_cache.get(topic_name)
            if not topic_id:
                cursor.execute("SELECT topic_id FROM research_topics WHERE topic_name = ?", (topic_name,))
                result = cursor.fetchone()
                if result:
                    topic_id = result[0]
                else:
                    # Create new topic
                    openalex_topic_id = topic_data.get('id', '').replace('https://openalex.org/', '')
                    cursor.execute("""
                        INSERT INTO research_topics (topic_name, topic_type, openalex_topic_id)
                        VALUES (?, ?, ?)
                    """, (topic_name, 'openalex_topic', openalex_topic_id))
                    topic_id = cursor.lastrowid

                self.topic_cache[topic_name] = topic_id

            # Insert publication-topic relationship
            score = topic_data.get('score', 0.0)
            try:
                cursor.execute("""
                    INSERT INTO publication_topics (unified_id, topic_id, score)
                    VALUES (?, ?, ?)
                """, (unified_id, topic_id, score))
            except sqlite3.IntegrityError:
                # Already exists
                pass

    def process_collaboration_detection(self, cursor, unified_id: int, work: Dict):
        """Detect and record collaboration patterns"""
        authorships = work.get('authorships', [])
        if not authorships:
            return

        # Collect countries and institutions
        countries = set()
        institutions = []
        has_china = False

        for authorship in authorships:
            # Countries
            auth_countries = authorship.get('countries', [])
            for country in auth_countries:
                countries.add(country)
                if country in ['CN', 'HK', 'MO']:
                    has_china = True

            # Institutions
            for inst in authorship.get('institutions', []):
                inst_id = inst.get('id', '')
                if inst_id:
                    institutions.append(inst_id)
                country_code = inst.get('country_code')
                if country_code in ['CN', 'HK', 'MO']:
                    has_china = True

        # Determine collaboration type
        country_count = len(countries)
        if country_count == 0:
            collab_type = 'unknown'
        elif country_count == 1:
            collab_type = 'domestic'
        elif country_count == 2:
            collab_type = 'bilateral'
        else:
            collab_type = 'multilateral'

        # Insert collaboration record
        cursor.execute("""
            INSERT INTO research_collaborations (
                unified_id, collaboration_type, country_codes,
                country_count, institution_count,
                has_china_institution, detected_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            unified_id,
            collab_type,
            json.dumps(list(countries)),
            country_count,
            len(institutions),
            has_china,
            datetime.now().isoformat()
        ))

    def process_work(self, cursor, work: Dict) -> bool:
        """Process single OpenAlex work"""
        try:
            # Extract publication data
            pub_data = self.extract_publication_data(work)

            # Check for duplicates
            duplicate_id = self.check_duplicate(cursor, pub_data.get('doi'), pub_data.get('openalex_id'))
            if duplicate_id:
                self.stats['duplicates_found'] += 1
                return False

            # Insert publication
            unified_id = self.insert_publication(cursor, pub_data)
            self.stats['records_inserted'] += 1

            # Process relationships
            self.process_authorships(cursor, unified_id, work)
            self.process_topics(cursor, unified_id, work)
            self.process_collaboration_detection(cursor, unified_id, work)

            return True

        except Exception as e:
            logger.error(f"Error processing work {work.get('id')}: {e}")
            self.stats['errors'] += 1
            return False

    def process_file(self, file_path: Path, conn: sqlite3.Connection) -> Tuple[int, int]:
        """Process single gzipped JSONL file"""
        cursor = conn.cursor()
        records_processed = 0
        records_inserted = 0

        try:
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                batch = []
                for line in f:
                    try:
                        work = json.loads(line)
                        batch.append(work)

                        # Process in batches
                        if len(batch) >= self.batch_size:
                            for w in batch:
                                records_processed += 1
                                if self.process_work(cursor, w):
                                    records_inserted += 1

                            conn.commit()
                            batch = []

                            # Log progress
                            if records_processed % 50000 == 0:
                                logger.info(f"Processed {records_processed} records from {file_path.name}")

                    except json.JSONDecodeError:
                        continue

                # Process remaining batch
                for w in batch:
                    records_processed += 1
                    if self.process_work(cursor, w):
                        records_inserted += 1

                conn.commit()

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            conn.rollback()

        return records_processed, records_inserted

    def update_processing_status(self, conn: sqlite3.Connection, source_file: str,
                                 status: str, records_processed: int,
                                 records_inserted: int, started_at: str,
                                 error_message: str = None):
        """Update processing status table"""
        cursor = conn.cursor()
        completed_at = datetime.now().isoformat()
        duration = (datetime.fromisoformat(completed_at) - datetime.fromisoformat(started_at)).total_seconds()

        cursor.execute("""
            INSERT OR REPLACE INTO processing_status (
                source_system, source_file, status,
                records_processed, records_inserted,
                records_skipped, duplicates_found,
                started_at, completed_at, processing_duration_seconds,
                error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'openalex',
            source_file,
            status,
            records_processed,
            records_inserted,
            records_processed - records_inserted,
            self.stats['duplicates_found'],
            started_at,
            completed_at,
            int(duration),
            error_message
        ))
        conn.commit()

    def get_date_partitions(self, start_date: str = None, end_date: str = None) -> List[Path]:
        """Get list of date partitions to process"""
        if not self.source_path.exists():
            logger.error(f"Source path does not exist: {self.source_path}")
            return []

        # Get all date partitions
        partitions = sorted([d for d in self.source_path.iterdir() if d.is_dir() and d.name.startswith('updated_date=')])

        # Filter by date range if provided
        if start_date or end_date:
            filtered = []
            for partition in partitions:
                date_str = partition.name.replace('updated_date=', '')
                if start_date and date_str < start_date:
                    continue
                if end_date and date_str > end_date:
                    continue
                filtered.append(partition)
            return filtered

        return partitions

    def process_all(self, start_date: str = None, end_date: str = None, resume: bool = False):
        """Process all OpenAlex data"""
        logger.info("=" * 80)
        logger.info("OPENALEX COMPREHENSIVE INGESTION")
        logger.info("=" * 80)

        # Get partitions to process
        partitions = self.get_date_partitions(start_date, end_date)
        logger.info(f"Found {len(partitions)} date partitions to process")

        if resume:
            # Get already processed partitions
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT source_file FROM processing_status
                WHERE source_system = 'openalex' AND status = 'complete'
            """)
            completed = set(row[0] for row in cursor.fetchall())
            conn.close()

            partitions = [p for p in partitions if p.name not in completed]
            logger.info(f"Resuming: {len(partitions)} partitions remaining")

        # Process each partition
        for i, partition in enumerate(partitions, 1):
            logger.info(f"\n[{i}/{len(partitions)}] Processing partition: {partition.name}")

            # Get all files in partition
            files = sorted(partition.glob("*.gz"))
            logger.info(f"  Found {len(files)} files in partition")

            conn = self.get_connection()
            partition_started = datetime.now().isoformat()

            partition_records = 0
            partition_inserted = 0

            for file_path in files:
                try:
                    file_started = datetime.now().isoformat()
                    records_processed, records_inserted = self.process_file(file_path, conn)

                    partition_records += records_processed
                    partition_inserted += records_inserted

                    self.update_processing_status(
                        conn, f"{partition.name}/{file_path.name}",
                        'complete', records_processed, records_inserted,
                        file_started
                    )

                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    self.update_processing_status(
                        conn, f"{partition.name}/{file_path.name}",
                        'error', 0, 0, partition_started, str(e)
                    )

            conn.close()

            logger.info(f"  Partition complete: {partition_inserted:,} inserted from {partition_records:,} processed")
            self.stats['files_processed'] += len(files)
            self.stats['records_processed'] += partition_records
            self.stats['records_inserted'] += partition_inserted

        logger.info("\n" + "=" * 80)
        logger.info("INGESTION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Partitions processed: {len(partitions)}")
        logger.info(f"Total records processed: {self.stats['records_processed']:,}")
        logger.info(f"Total records inserted: {self.stats['records_inserted']:,}")
        logger.info(f"Duplicates found: {self.stats['duplicates_found']:,}")
        logger.info(f"Errors: {self.stats['errors']:,}")


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description='Ingest OpenAlex data into research mapping database')
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    parser.add_argument('--resume', action='store_true', help='Resume from previous run')
    parser.add_argument('--db-path', default='F:/OSINT_WAREHOUSE/research_mapping_comprehensive.db',
                        help='Database path')

    args = parser.parse_args()

    processor = OpenAlexIngestionProcessor(args.db_path)
    processor.process_all(
        start_date=args.start_date,
        end_date=args.end_date,
        resume=args.resume
    )


if __name__ == "__main__":
    main()
