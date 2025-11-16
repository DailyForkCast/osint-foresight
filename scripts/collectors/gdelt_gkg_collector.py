#!/usr/bin/env python3
"""
GDELT GKG (Global Knowledge Graph) Collector
Collects thematic, organizational, and sentiment data from GDELT GKG

Purpose:
  Enable keyword/theme searches like "quantum research", "university partnership"
  Cross-reference with existing GDELT events for enriched intelligence

Key Features:
  - Filters for China-related content (themes, organizations)
  - Uses correct timestamp format (YYYYMMDDHHMMSS)
  - Checkpoint/resume support for long collections
  - Cost tracking and reporting
  - Zero Fabrication Protocol compliant

Cost Estimates (validated 2025-11-05):
  - 1.77 TB scanned per day with China filter
  - ~$8.86 per day
  - 30 days: $260.77
  - 365 days: $3,228.48
  - Full backfill (2,115 days): $18,731.48

Output: F:/OSINT_WAREHOUSE/osint_master.db (gdelt_gkg table)
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional, Tuple
import time

from google.cloud import bigquery

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/gkg_collection.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

class GKGCollector:
    """
    Collect GDELT GKG data with China-related themes and organizations
    """

    def __init__(self,
                 master_db="F:/OSINT_WAREHOUSE/osint_master.db",
                 project_id="osint-foresight-2025"):
        """
        Initialize GKG collector

        Args:
            master_db: Path to master database
            project_id: Google Cloud project ID
        """
        self.master_db = Path(master_db)
        self.project_id = project_id
        self.conn = None
        self.bigquery_client = None

        self.stats = {
            "days_processed": 0,
            "records_collected": 0,
            "bytes_scanned": 0,
            "estimated_cost_usd": 0.0,
            "errors": [],
            "date_range": {"start": None, "end": None}
        }

        # Cost tracking ($5/TB after 1 TB free tier)
        self.cost_per_tb = 5.0
        self.free_tier_tb = 1.0

    def connect(self):
        """Connect to master database and BigQuery"""
        logging.info(f"Connecting to master database: {self.master_db}")

        self.master_db.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.master_db)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.execute("PRAGMA cache_size=-64000")

        logging.info("Initializing BigQuery client...")
        self.bigquery_client = bigquery.Client(project=self.project_id)
        logging.info("Connected successfully")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.commit()
            self.conn.close()
            logging.info("Database connection closed")

    def ensure_gkg_table(self):
        """Ensure GKG table exists with proper schema"""
        logging.info("Ensuring GKG table exists...")

        create_sql = """
            CREATE TABLE IF NOT EXISTS gdelt_gkg (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gkg_record_id TEXT UNIQUE,
                publish_date INTEGER,
                source_collection_id INTEGER,
                source_common_name TEXT,
                document_identifier TEXT,

                -- Themes (semicolon-separated)
                themes TEXT,
                v2_themes TEXT,

                -- Entities (semicolon-separated)
                locations TEXT,
                v2_locations TEXT,
                persons TEXT,
                v2_persons TEXT,
                organizations TEXT,
                v2_organizations TEXT,

                -- Counts and tone
                counts TEXT,
                v2_counts TEXT,
                v2_tone TEXT,

                -- Additional fields
                dates TEXT,
                gcam TEXT,
                sharing_image TEXT,

                -- Related events (comma-separated GlobalEventIDs)
                related_event_ids TEXT,

                -- Provenance
                collection_date TEXT,

                -- Metadata
                data_source TEXT DEFAULT 'gdelt_bigquery',
                bigquery_dataset TEXT DEFAULT 'gdelt-bq.gdeltv2.gkg_partitioned',
                selection_criteria TEXT,
                collection_method TEXT DEFAULT 'bigquery_china_filter'
            );

            CREATE INDEX IF NOT EXISTS idx_gdelt_gkg_date ON gdelt_gkg(publish_date);
            CREATE INDEX IF NOT EXISTS idx_gdelt_gkg_source ON gdelt_gkg(source_common_name);
            CREATE INDEX IF NOT EXISTS idx_gdelt_gkg_doc ON gdelt_gkg(document_identifier);
            CREATE INDEX IF NOT EXISTS idx_gdelt_gkg_record_id ON gdelt_gkg(gkg_record_id);
        """

        self.conn.executescript(create_sql)
        self.conn.commit()
        logging.info("GKG table ready")

    def get_date_list_from_events(self, limit_days: Optional[int] = None) -> List[str]:
        """
        Get list of dates (YYYYMMDD) from existing events to collect GKG for

        Args:
            limit_days: Limit to most recent N days (None = all dates)

        Returns:
            List of date strings in YYYYMMDD format, sorted ascending
        """
        logging.info("Getting date list from existing events...")

        cursor = self.conn.cursor()

        if limit_days:
            # Get most recent N days
            cursor.execute("""
                SELECT DISTINCT SUBSTR(event_date, 1, 8) as date
                FROM gdelt_events
                ORDER BY date DESC
                LIMIT ?
            """, (limit_days,))
        else:
            # Get all unique dates
            cursor.execute("""
                SELECT DISTINCT SUBSTR(event_date, 1, 8) as date
                FROM gdelt_events
                ORDER BY date ASC
            """)

        dates = [row[0] for row in cursor.fetchall()]

        # Reverse if we limited (so we process oldest first)
        if limit_days:
            dates.reverse()

        logging.info(f"Found {len(dates)} unique dates to process")
        if dates:
            logging.info(f"  Date range: {dates[0]} to {dates[-1]}")

        return dates

    def get_checkpoint(self) -> Optional[str]:
        """Get last successfully processed date from checkpoint"""
        checkpoint_file = Path("checkpoints/gkg_collection_checkpoint.json")

        if not checkpoint_file.exists():
            return None

        try:
            with open(checkpoint_file, 'r') as f:
                checkpoint = json.load(f)
                last_date = checkpoint.get('last_completed_date')
                logging.info(f"Resuming from checkpoint: {last_date}")
                return last_date
        except Exception as e:
            logging.warning(f"Could not read checkpoint: {e}")
            return None

    def save_checkpoint(self, date: str, stats: Dict):
        """Save checkpoint for resuming"""
        checkpoint_file = Path("checkpoints/gkg_collection_checkpoint.json")
        checkpoint_file.parent.mkdir(parents=True, exist_ok=True)

        checkpoint = {
            'last_completed_date': date,
            'checkpoint_time': datetime.now().isoformat(),
            'cumulative_stats': stats
        }

        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)

    def collect_gkg_for_date(self, date_str: str) -> Tuple[int, int]:
        """
        Collect GKG records for a specific date (YYYYMMDD)

        Args:
            date_str: Date in YYYYMMDD format

        Returns:
            (records_collected, bytes_scanned)
        """
        logging.info(f"Collecting GKG for date: {date_str}")

        # Convert YYYYMMDD to timestamp range
        start_ts = int(f"{date_str}000000")
        end_ts = int(f"{int(date_str) + 1}000000")

        # BigQuery query with China filter
        query = f"""
        SELECT
            GKGRECORDID,
            DATE as publish_date,
            SourceCollectionIdentifier,
            SourceCommonName,
            DocumentIdentifier,

            Themes,
            V2Themes,

            Locations,
            V2Locations,

            Persons,
            V2Persons,

            Organizations,
            V2Organizations,

            Counts,
            V2Counts,
            V2Tone,

            Dates,
            GCAM,
            SharingImage

        FROM `gdelt-bq.gdeltv2.gkg_partitioned`
        WHERE DATE >= {start_ts}
        AND DATE < {end_ts}
        AND (
            -- Themes filter
            LOWER(V2Themes) LIKE '%china%'
            OR LOWER(V2Themes) LIKE '%chinese%'
            OR LOWER(V2Themes) LIKE '%quantum%'
            OR LOWER(V2Themes) LIKE '%semiconductor%'
            OR LOWER(V2Themes) LIKE '%university%'
            OR LOWER(V2Themes) LIKE '%research%'
            OR LOWER(V2Themes) LIKE '%technology%'
            OR LOWER(V2Themes) LIKE '%military%'

            -- Organizations filter
            OR LOWER(V2Organizations) LIKE '%china%'
            OR LOWER(V2Organizations) LIKE '%chinese%'
            OR LOWER(V2Organizations) LIKE '%huawei%'
            OR LOWER(V2Organizations) LIKE '%tencent%'
            OR LOWER(V2Organizations) LIKE '%alibaba%'
            OR LOWER(V2Organizations) LIKE '%university%'
        )
        """

        try:
            query_job = self.bigquery_client.query(query)
            results = query_job.result()

            # Track bytes scanned
            bytes_scanned = query_job.total_bytes_billed
            self.stats['bytes_scanned'] += bytes_scanned

            # Insert records
            records_inserted = 0
            batch = []
            batch_size = 1000

            for row in results:
                record = (
                    row['GKGRECORDID'],
                    row['publish_date'],
                    row['SourceCollectionIdentifier'],
                    row['SourceCommonName'],
                    row['DocumentIdentifier'],
                    row['Themes'],
                    row['V2Themes'],
                    row['Locations'],
                    row['V2Locations'],
                    row['Persons'],
                    row['V2Persons'],
                    row['Organizations'],
                    row['V2Organizations'],
                    row['Counts'],
                    row['V2Counts'],
                    row['V2Tone'],
                    row['Dates'],
                    row['GCAM'],
                    row['SharingImage'],
                    datetime.now().isoformat(),
                    'gdelt_bigquery',
                    'gdelt-bq.gdeltv2.gkg_partitioned',
                    f'china_filter_date_{date_str}',
                    'bigquery_china_filter'
                )
                batch.append(record)

                if len(batch) >= batch_size:
                    self._insert_batch(batch)
                    records_inserted += len(batch)
                    batch = []

            # Insert remaining records
            if batch:
                self._insert_batch(batch)
                records_inserted += len(batch)

            self.conn.commit()

            logging.info(f"  Collected {records_inserted:,} records")
            logging.info(f"  Scanned {bytes_scanned / (1024**4):.3f} TB")

            return records_inserted, bytes_scanned

        except Exception as e:
            logging.error(f"Error collecting GKG for {date_str}: {e}")
            self.stats['errors'].append({'date': date_str, 'error': str(e)})
            return 0, 0

    def _insert_batch(self, batch: List[Tuple]):
        """Insert batch of GKG records"""
        insert_sql = """
            INSERT OR IGNORE INTO gdelt_gkg (
                gkg_record_id, publish_date, source_collection_id,
                source_common_name, document_identifier,
                themes, v2_themes,
                locations, v2_locations,
                persons, v2_persons,
                organizations, v2_organizations,
                counts, v2_counts, v2_tone,
                dates, gcam, sharing_image,
                collection_date, data_source, bigquery_dataset,
                selection_criteria, collection_method
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        self.conn.executemany(insert_sql, batch)

    def collect_range(self,
                     start_date: Optional[str] = None,
                     end_date: Optional[str] = None,
                     limit_days: Optional[int] = None,
                     resume: bool = True):
        """
        Collect GKG data for a date range

        Args:
            start_date: Start date YYYYMMDD (None = earliest in events)
            end_date: End date YYYYMMDD (None = latest in events)
            limit_days: Limit to N most recent days (overrides start/end)
            resume: Resume from checkpoint if available
        """
        logging.info("="*60)
        logging.info("GDELT GKG COLLECTION")
        logging.info("="*60)

        # Get date list from events
        dates = self.get_date_list_from_events(limit_days=limit_days)

        if not dates:
            logging.error("No dates found in events table")
            return

        # Apply date range filter
        if start_date:
            dates = [d for d in dates if d >= start_date]
        if end_date:
            dates = [d for d in dates if d <= end_date]

        if not dates:
            logging.error("No dates in specified range")
            return

        logging.info(f"Will process {len(dates)} dates")
        logging.info(f"Date range: {dates[0]} to {dates[-1]}")

        # Calculate estimated cost
        estimated_tb = len(dates) * 1.77  # 1.77 TB per day from validation
        estimated_cost = max(0, (estimated_tb - self.free_tier_tb) * self.cost_per_tb)

        logging.info(f"Estimated data scan: {estimated_tb:.1f} TB")
        logging.info(f"Estimated cost: ${estimated_cost:.2f}")
        logging.info("="*60)

        # Resume from checkpoint if requested
        checkpoint_date = self.get_checkpoint() if resume else None
        if checkpoint_date:
            # Skip dates up to and including checkpoint
            try:
                checkpoint_idx = dates.index(checkpoint_date)
                dates = dates[checkpoint_idx + 1:]
                logging.info(f"Resuming after {checkpoint_date}")
                logging.info(f"Remaining dates to process: {len(dates)}")
            except ValueError:
                logging.warning(f"Checkpoint date {checkpoint_date} not in date list, starting from beginning")

        self.stats['date_range']['start'] = dates[0] if dates else None
        self.stats['date_range']['end'] = dates[-1] if dates else None

        # Process each date
        for i, date_str in enumerate(dates, 1):
            logging.info(f"\nProcessing date {i}/{len(dates)}: {date_str}")

            records, bytes_scanned = self.collect_gkg_for_date(date_str)

            self.stats['days_processed'] += 1
            self.stats['records_collected'] += records

            # Update cost estimate
            tb_so_far = self.stats['bytes_scanned'] / (1024**4)
            cost_so_far = max(0, (tb_so_far - self.free_tier_tb) * self.cost_per_tb)
            self.stats['estimated_cost_usd'] = cost_so_far

            # Save checkpoint
            self.save_checkpoint(date_str, self.stats)

            # Log progress
            if i % 10 == 0:
                self._print_progress()

            # Rate limiting (avoid overwhelming BigQuery)
            if i < len(dates):  # Don't sleep after last date
                time.sleep(0.5)  # 0.5 second between queries

        # Final report
        self._print_final_report()

    def _print_progress(self):
        """Print progress update"""
        tb_scanned = self.stats['bytes_scanned'] / (1024**4)
        logging.info(f"\nProgress Update:")
        logging.info(f"  Days processed: {self.stats['days_processed']}")
        logging.info(f"  Records collected: {self.stats['records_collected']:,}")
        logging.info(f"  Data scanned: {tb_scanned:.2f} TB")
        logging.info(f"  Estimated cost: ${self.stats['estimated_cost_usd']:.2f}")

    def _print_final_report(self):
        """Print final collection report"""
        tb_scanned = self.stats['bytes_scanned'] / (1024**4)

        logging.info("\n" + "="*60)
        logging.info("COLLECTION COMPLETE")
        logging.info("="*60)
        logging.info(f"Date range: {self.stats['date_range']['start']} to {self.stats['date_range']['end']}")
        logging.info(f"Days processed: {self.stats['days_processed']}")
        logging.info(f"Records collected: {self.stats['records_collected']:,}")
        logging.info(f"Data scanned: {tb_scanned:.2f} TB")
        logging.info(f"Actual cost: ${self.stats['estimated_cost_usd']:.2f}")

        if self.stats['errors']:
            logging.warning(f"Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:5]:  # Show first 5
                logging.warning(f"  {error['date']}: {error['error']}")

        # Save final report
        report_file = Path(f"analysis/gkg_collection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, 'w') as f:
            json.dump(self.stats, f, indent=2)

        logging.info(f"\nReport saved: {report_file}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Collect GDELT GKG data')
    parser.add_argument('--start-date', help='Start date YYYYMMDD')
    parser.add_argument('--end-date', help='End date YYYYMMDD')
    parser.add_argument('--limit-days', type=int, help='Limit to N most recent days')
    parser.add_argument('--no-resume', action='store_true', help='Start from beginning (ignore checkpoint)')
    parser.add_argument('--db', default='F:/OSINT_WAREHOUSE/osint_master.db', help='Database path')

    args = parser.parse_args()

    collector = GKGCollector(master_db=args.db)

    try:
        collector.connect()
        collector.ensure_gkg_table()

        collector.collect_range(
            start_date=args.start_date,
            end_date=args.end_date,
            limit_days=args.limit_days,
            resume=not args.no_resume
        )

    except KeyboardInterrupt:
        logging.info("\nCollection interrupted by user")
        logging.info("Progress saved in checkpoint. Run again to resume.")
    except Exception as e:
        logging.error(f"Collection failed: {e}", exc_info=True)
    finally:
        collector.close()


if __name__ == '__main__':
    main()
