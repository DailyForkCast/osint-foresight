#!/usr/bin/env python3
"""
ETL Pipeline - Extract, Transform, Load
Phase 3 Week 2 - Database Integration

Orchestrates the complete data flow:
1. Extract: Load data from source files
2. Transform: Convert to UnifiedDocument using converters
3. Load: Insert into PostgreSQL database

Supports:
- Multiple data sources (OpenAlex, USASpending, TED)
- Batch processing with checkpoints
- Error handling and recovery
- Progress tracking and statistics
- Deduplication
"""

import json
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator
from datetime import datetime
from collections import defaultdict

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from schemas.converters import ConverterFactory, convert_batch
from schemas.unified_schema import UnifiedDocument

# Import db_helper from parent directory
sys.path.insert(0, str(Path(__file__).parent))
from db_helper import DatabaseHelper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataSource:
    """Base class for data sources"""

    def __init__(self, name: str, source_format: str):
        self.name = name
        self.source_format = source_format
        self.stats = {
            'files_processed': 0,
            'records_read': 0,
            'records_converted': 0,
            'records_inserted': 0,
            'records_skipped': 0,
            'errors': 0
        }

    def load_records(self) -> Iterator[Dict[str, Any]]:
        """Load records from source - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement load_records()")

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for this data source"""
        return {
            'source': self.name,
            'format': self.source_format,
            **self.stats
        }


class OpenAlexSource(DataSource):
    """OpenAlex data source"""

    def __init__(self, data_dir: str = "data/processed/openalex_production"):
        super().__init__("OpenAlex", "openalex")
        self.data_dir = Path(data_dir)

    def load_records(self) -> Iterator[Dict[str, Any]]:
        """Load OpenAlex collaboration records"""
        logger.info(f"Loading OpenAlex data from {self.data_dir}")

        json_files = sorted(self.data_dir.glob("*.json"))
        logger.info(f"Found {len(json_files)} JSON files")

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # OpenAlex files have 'collaborations' array
                collaborations = data.get('collaborations', [])

                for collab in collaborations:
                    self.stats['records_read'] += 1
                    yield collab

                self.stats['files_processed'] += 1

            except Exception as e:
                logger.error(f"Error loading {json_file}: {e}")
                self.stats['errors'] += 1


class USASpendingSource(DataSource):
    """USASpending data source"""

    def __init__(self, data_dir: str = "data/processed/usaspending_production"):
        super().__init__("USASpending", "usaspending")
        self.data_dir = Path(data_dir)

    def load_records(self) -> Iterator[Dict[str, Any]]:
        """Load USASpending detection records"""
        logger.info(f"Loading USASpending data from {self.data_dir}")

        json_files = sorted(self.data_dir.glob("*.json"))
        logger.info(f"Found {len(json_files)} JSON files")

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # USASpending files have 'detections' array
                detections = data.get('detections', [])

                for detection in detections:
                    self.stats['records_read'] += 1
                    yield detection

                self.stats['files_processed'] += 1

            except Exception as e:
                logger.error(f"Error loading {json_file}: {e}")
                self.stats['errors'] += 1


class TEDSource(DataSource):
    """TED (European procurement) data source"""

    def __init__(self, data_file: str = "analysis/TED_CHINESE_CONTRACTORS_FINAL_REPORT.json"):
        super().__init__("TED", "ted")
        self.data_file = Path(data_file)

    def load_records(self) -> Iterator[Dict[str, Any]]:
        """Load TED contractor records"""
        logger.info(f"Loading TED data from {self.data_file}")

        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # TED file has 'high_confidence_contractors' and 'medium_confidence_contractors'
            high_conf = data.get('high_confidence_contractors', [])
            medium_conf = data.get('medium_confidence_contractors', [])

            for contractor in high_conf + medium_conf:
                self.stats['records_read'] += 1
                yield contractor

            self.stats['files_processed'] = 1

        except Exception as e:
            logger.error(f"Error loading {self.data_file}: {e}")
            self.stats['errors'] += 1


class ETLPipeline:
    """
    Main ETL Pipeline orchestrator

    Coordinates the complete Extract-Transform-Load process
    """

    def __init__(self, db_config: Optional[Dict[str, str]] = None,
                 batch_size: int = 1000,
                 checkpoint_interval: int = 5000):
        """
        Initialize ETL pipeline

        Args:
            db_config: Database configuration (host, port, database, user, password)
            batch_size: Number of records to process in each batch
            checkpoint_interval: Save checkpoint every N records
        """
        self.batch_size = batch_size
        self.checkpoint_interval = checkpoint_interval
        self.db_config = db_config or {}

        self.stats = {
            'start_time': None,
            'end_time': None,
            'duration_seconds': 0,
            'total_records': 0,
            'total_converted': 0,
            'total_inserted': 0,
            'total_skipped': 0,
            'total_errors': 0,
            'sources': {}
        }

        self.factory = ConverterFactory()

    def run(self, sources: List[DataSource],
            skip_duplicates: bool = True,
            dry_run: bool = False) -> Dict[str, Any]:
        """
        Run the ETL pipeline

        Args:
            sources: List of data sources to process
            skip_duplicates: Skip duplicate documents based on hash
            dry_run: If True, don't insert into database

        Returns:
            Statistics dictionary
        """
        logger.info("=" * 70)
        logger.info("ETL PIPELINE STARTED")
        logger.info("=" * 70)

        self.stats['start_time'] = datetime.now()
        db = None

        try:
            # Initialize database connection (unless dry run)
            if not dry_run:
                logger.info("Connecting to database...")
                db = DatabaseHelper(**self.db_config)
                logger.info(f"Database connected: {db.database}")
            else:
                logger.info("DRY RUN MODE - No database operations")

            # Process each source
            for source in sources:
                logger.info("\n" + "=" * 70)
                logger.info(f"Processing source: {source.name}")
                logger.info("=" * 70)

                self._process_source(source, db, skip_duplicates, dry_run)

                # Track source stats
                self.stats['sources'][source.name] = source.get_stats()

            # Final statistics
            self.stats['end_time'] = datetime.now()
            self.stats['duration_seconds'] = (
                self.stats['end_time'] - self.stats['start_time']
            ).total_seconds()

            # Aggregate stats
            self.stats['total_records'] = sum(
                s['records_read'] for s in self.stats['sources'].values()
            )
            self.stats['total_converted'] = sum(
                s['records_converted'] for s in self.stats['sources'].values()
            )
            self.stats['total_inserted'] = sum(
                s['records_inserted'] for s in self.stats['sources'].values()
            )
            self.stats['total_skipped'] = sum(
                s['records_skipped'] for s in self.stats['sources'].values()
            )
            self.stats['total_errors'] = sum(
                s['errors'] for s in self.stats['sources'].values()
            )

            # Print summary
            self._print_summary()

            return self.stats

        except Exception as e:
            logger.error(f"ETL pipeline failed: {e}", exc_info=True)
            raise

        finally:
            # Cleanup
            if db:
                db.close()
                logger.info("Database connection closed")

    def _process_source(self, source: DataSource, db: Optional[DatabaseHelper],
                       skip_duplicates: bool, dry_run: bool):
        """Process a single data source"""

        batch = []
        batch_num = 0
        checkpoint_counter = 0

        for record in source.load_records():
            batch.append(record)

            # Process batch when full
            if len(batch) >= self.batch_size:
                batch_num += 1
                checkpoint_counter += len(batch)

                self._process_batch(
                    batch, source, db, skip_duplicates, dry_run, batch_num
                )

                batch = []

                # Checkpoint
                if checkpoint_counter >= self.checkpoint_interval:
                    logger.info(f"Checkpoint: {checkpoint_counter} records processed")
                    checkpoint_counter = 0

        # Process remaining records
        if batch:
            batch_num += 1
            self._process_batch(
                batch, source, db, skip_duplicates, dry_run, batch_num
            )

        logger.info(f"Completed {source.name}: {source.stats['records_read']} records")

    def _process_batch(self, batch: List[Dict[str, Any]], source: DataSource,
                      db: Optional[DatabaseHelper], skip_duplicates: bool,
                      dry_run: bool, batch_num: int):
        """Process a batch of records"""

        try:
            # Convert batch to UnifiedDocuments
            logger.info(f"Batch {batch_num}: Converting {len(batch)} records...")
            unified_docs = convert_batch(batch, source_format=source.source_format)

            source.stats['records_converted'] += len(unified_docs)

            if dry_run:
                logger.info(f"Batch {batch_num}: [DRY RUN] Would insert {len(unified_docs)} docs")
                source.stats['records_inserted'] += len(unified_docs)
                return

            # Insert into database
            if db and unified_docs:
                logger.info(f"Batch {batch_num}: Inserting {len(unified_docs)} documents...")

                result = db.batch_insert_documents(
                    unified_docs,
                    skip_duplicates=skip_duplicates,
                    batch_size=self.batch_size
                )

                source.stats['records_inserted'] += result['inserted']
                source.stats['records_skipped'] += result['skipped']
                source.stats['errors'] += result['errors']

                logger.info(
                    f"Batch {batch_num}: Inserted {result['inserted']}, "
                    f"Skipped {result['skipped']}, Errors {result['errors']}"
                )

        except Exception as e:
            logger.error(f"Error processing batch {batch_num}: {e}")
            source.stats['errors'] += len(batch)

    def _print_summary(self):
        """Print pipeline execution summary"""

        logger.info("\n" + "=" * 70)
        logger.info("ETL PIPELINE COMPLETED")
        logger.info("=" * 70)

        logger.info(f"\nExecution Time: {self.stats['duration_seconds']:.2f} seconds")

        logger.info(f"\nOverall Statistics:")
        logger.info(f"  Total Records:     {self.stats['total_records']:,}")
        logger.info(f"  Converted:         {self.stats['total_converted']:,}")
        logger.info(f"  Inserted:          {self.stats['total_inserted']:,}")
        logger.info(f"  Skipped (Dups):    {self.stats['total_skipped']:,}")
        logger.info(f"  Errors:            {self.stats['total_errors']:,}")

        if self.stats['duration_seconds'] > 0:
            throughput = self.stats['total_converted'] / self.stats['duration_seconds']
            logger.info(f"  Throughput:        {throughput:.1f} docs/sec")

        logger.info(f"\nBy Source:")
        for source_name, source_stats in self.stats['sources'].items():
            logger.info(f"\n  {source_name}:")
            logger.info(f"    Files Processed:   {source_stats['files_processed']}")
            logger.info(f"    Records Read:      {source_stats['records_read']:,}")
            logger.info(f"    Converted:         {source_stats['records_converted']:,}")
            logger.info(f"    Inserted:          {source_stats['records_inserted']:,}")
            logger.info(f"    Skipped:           {source_stats['records_skipped']:,}")
            logger.info(f"    Errors:            {source_stats['errors']:,}")

        logger.info("\n" + "=" * 70)


def main():
    """Main entry point for ETL pipeline"""
    import argparse

    parser = argparse.ArgumentParser(description='ETL Pipeline for OSINT Database')
    parser.add_argument('--sources', nargs='+',
                       choices=['openalex', 'usaspending', 'ted', 'all'],
                       default=['all'],
                       help='Data sources to process')
    parser.add_argument('--batch-size', type=int, default=1000,
                       help='Batch size for processing (default: 1000)')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of records per source (for testing)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Dry run mode - no database operations')
    parser.add_argument('--skip-duplicates', action='store_true', default=True,
                       help='Skip duplicate documents (default: True)')

    # Database config
    parser.add_argument('--db-host', default='localhost')
    parser.add_argument('--db-port', type=int, default=5432)
    parser.add_argument('--db-name', default='osint_foresight')
    parser.add_argument('--db-user', default='postgres')
    parser.add_argument('--db-password', default='')

    args = parser.parse_args()

    # Database configuration
    db_config = {
        'host': args.db_host,
        'port': args.db_port,
        'database': args.db_name,
        'user': args.db_user,
        'password': args.db_password
    }

    # Initialize pipeline
    pipeline = ETLPipeline(
        db_config=db_config,
        batch_size=args.batch_size
    )

    # Setup data sources
    sources = []
    source_list = args.sources if 'all' not in args.sources else ['openalex', 'usaspending']

    if 'openalex' in source_list:
        sources.append(OpenAlexSource())

    if 'usaspending' in source_list:
        sources.append(USASpendingSource())

    if 'ted' in source_list:
        sources.append(TEDSource())

    # Run pipeline
    try:
        stats = pipeline.run(
            sources=sources,
            skip_duplicates=args.skip_duplicates,
            dry_run=args.dry_run
        )

        # Save stats
        stats_file = f"etl_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(stats_file, 'w') as f:
            # Convert datetime to string for JSON
            stats_copy = stats.copy()
            stats_copy['start_time'] = str(stats['start_time'])
            stats_copy['end_time'] = str(stats['end_time'])
            json.dump(stats_copy, f, indent=2)

        logger.info(f"\nStatistics saved to: {stats_file}")

        return 0

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
