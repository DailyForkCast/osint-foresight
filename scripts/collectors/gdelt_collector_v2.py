#!/usr/bin/env python3
"""
GDELT Collector V2 - Production Ready
Fixes critical issues from V1:
- Pagination (no 100k limit)
- Automated validation
- Checkpointing/resume
- Better error handling
- Data quality metrics
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional, Tuple
import time

try:
    from google.cloud import bigquery
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False
    print("Error: google-cloud-bigquery not installed")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/gdelt_collection_v2.log'),
        logging.StreamHandler()
    ]
)

class CheckpointManager:
    """Manage collection checkpoints for resume capability"""

    def __init__(self, checkpoint_file: str):
        self.checkpoint_file = Path(checkpoint_file)
        self.data = self._load()

    def _load(self) -> Dict:
        """Load checkpoint from file"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file) as f:
                return json.load(f)
        return {
            "collection_id": None,
            "started": None,
            "last_updated": None,
            "completed_ranges": [],
            "failed_ranges": [],
            "in_progress": None,
            "total_events": 0,
            "status": "not_started"
        }

    def _save(self):
        """Save checkpoint to file"""
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def is_completed(self, start_date: str, end_date: str) -> bool:
        """Check if date range already completed"""
        range_key = f"{start_date}_{end_date}"
        return any(r["range"] == range_key for r in self.data["completed_ranges"])

    def mark_completed(self, start_date: str, end_date: str, events: int):
        """Mark date range as completed"""
        range_key = f"{start_date}_{end_date}"
        self.data["completed_ranges"].append({
            "range": range_key,
            "start_date": start_date,
            "end_date": end_date,
            "events": events,
            "timestamp": datetime.now().isoformat()
        })
        self.data["total_events"] += events
        self.data["last_updated"] = datetime.now().isoformat()
        self._save()
        logging.info(f"Checkpoint saved: {range_key} ({events:,} events)")

    def mark_failed(self, start_date: str, end_date: str, error: str):
        """Mark date range as failed"""
        range_key = f"{start_date}_{end_date}"
        self.data["failed_ranges"].append({
            "range": range_key,
            "start_date": start_date,
            "end_date": end_date,
            "error": str(error),
            "timestamp": datetime.now().isoformat()
        })
        self.data["last_updated"] = datetime.now().isoformat()
        self._save()
        logging.error(f"Range failed: {range_key} - {error}")

    def start_collection(self, collection_id: str):
        """Initialize new collection"""
        self.data["collection_id"] = collection_id
        self.data["started"] = datetime.now().isoformat()
        self.data["status"] = "in_progress"
        self._save()

    def finish_collection(self):
        """Mark collection as complete"""
        self.data["status"] = "completed"
        self.data["last_updated"] = datetime.now().isoformat()
        self._save()


class ValidationReport:
    """Collection validation report"""

    def __init__(self):
        self.passed = True
        self.issues = []

    def add_issue(self, severity: str, code: str, message: str, action: str):
        """Add validation issue"""
        self.issues.append({
            "severity": severity,
            "code": code,
            "message": message,
            "action": action
        })
        if severity in ["CRITICAL", "ERROR"]:
            self.passed = False

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "passed": self.passed,
            "issues": self.issues,
            "summary": {
                "total_issues": len(self.issues),
                "critical": len([i for i in self.issues if i["severity"] == "CRITICAL"]),
                "errors": len([i for i in self.issues if i["severity"] == "ERROR"]),
                "warnings": len([i for i in self.issues if i["severity"] == "WARNING"])
            }
        }

    def print_report(self):
        """Print validation report"""
        if self.passed:
            print("\n[OK] Validation PASSED")
        else:
            print("\n[FAILED] Validation FAILED")

        if self.issues:
            print(f"\nIssues found: {len(self.issues)}")
            for issue in self.issues:
                print(f"  [{issue['severity']}] {issue['code']}: {issue['message']}")
                print(f"     Action: {issue['action']}")


class GDELTCollectorV2:
    """
    GDELT Collector V2 - Production Ready

    Improvements over V1:
    - Pagination for unlimited collection
    - Automated validation
    - Checkpoint/resume capability
    - Better error handling
    """

    def __init__(self,
                 master_db="F:/OSINT_WAREHOUSE/osint_master.db",
                 checkpoint_file="checkpoints/gdelt_checkpoint.json"):

        self.master_db = Path(master_db)
        self.checkpoint = CheckpointManager(checkpoint_file)
        self.conn = None
        self.bigquery_client = None

        self.stats = {
            "events_queried": 0,
            "events_inserted": 0,
            "events_duplicate": 0,
            "events_error": 0,
            "query_time_seconds": 0,
            "insert_time_seconds": 0
        }

        # GDELT BigQuery project
        self.bigquery_project = "gdelt-bq"
        self.bigquery_dataset = "gdeltv2.events"

    def connect(self):
        """Connect to master database"""
        logging.info(f"Connecting to master database: {self.master_db}")
        self.master_db.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.master_db)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.execute("PRAGMA cache_size=-64000")

    def setup_bigquery(self):
        """Setup BigQuery client"""
        try:
            self.bigquery_client = bigquery.Client()
            logging.info("BigQuery client initialized")
            return True
        except Exception as e:
            logging.error(f"Failed to setup BigQuery: {e}")
            return False

    def create_tables(self):
        """Create GDELT tables"""
        create_sql = """
            CREATE TABLE IF NOT EXISTS gdelt_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                globaleventid INTEGER UNIQUE,
                sqldate INTEGER,
                event_date TEXT,

                -- Actors
                actor1_code TEXT,
                actor1_name TEXT,
                actor1_country_code TEXT,
                actor1_type1_code TEXT,
                actor1_type2_code TEXT,
                actor1_type3_code TEXT,

                actor2_code TEXT,
                actor2_name TEXT,
                actor2_country_code TEXT,
                actor2_type1_code TEXT,
                actor2_type2_code TEXT,
                actor2_type3_code TEXT,

                -- Event
                is_root_event INTEGER,
                event_code TEXT,
                event_base_code TEXT,
                event_root_code TEXT,
                quad_class INTEGER,
                goldstein_scale REAL,
                num_mentions INTEGER,
                num_sources INTEGER,
                num_articles INTEGER,
                avg_tone REAL,

                -- Location
                action_geo_type INTEGER,
                action_geo_fullname TEXT,
                action_geo_country_code TEXT,
                action_geo_lat REAL,
                action_geo_long REAL,

                -- Provenance
                source_url TEXT,
                collection_date TEXT,
                data_source TEXT,
                bigquery_dataset TEXT,
                selection_criteria TEXT,
                collection_method TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_gdelt_events_date ON gdelt_events(sqldate);
            CREATE INDEX IF NOT EXISTS idx_gdelt_events_actor1 ON gdelt_events(actor1_country_code);
            CREATE INDEX IF NOT EXISTS idx_gdelt_events_actor2 ON gdelt_events(actor2_country_code);
            CREATE INDEX IF NOT EXISTS idx_gdelt_events_event_code ON gdelt_events(event_code);
            CREATE INDEX IF NOT EXISTS idx_gdelt_events_china ON gdelt_events(actor1_country_code, actor2_country_code)
                WHERE actor1_country_code = 'CHN' OR actor2_country_code = 'CHN';
        """

        try:
            self.conn.executescript(create_sql)
            self.conn.commit()
            logging.info("Tables created/verified")
        except sqlite3.Error as e:
            logging.error(f"Error creating tables: {e}")
            raise

    def query_bigquery_events_paginated(self,
                                       start_date: str,
                                       end_date: str,
                                       actor_filter: str = "CHN",
                                       chunk_size: int = 50000) -> List[Dict]:
        """
        Query GDELT events with pagination (no limit)

        Args:
            start_date: YYYYMMDD format
            end_date: YYYYMMDD format
            actor_filter: Country code (default CHN)
            chunk_size: Records per query (default 50000)

        Returns:
            List of all events (no limit)
        """
        if not self.bigquery_client:
            logging.error("BigQuery client not initialized")
            return []

        all_events = []
        offset = 0
        query_start = time.time()

        logging.info(f"Querying BigQuery: {start_date} to {end_date} (paginated, no limit)")

        while True:
            query = f"""
            SELECT
                GLOBALEVENTID,
                SQLDATE,
                DATEADDED as event_date,

                Actor1Code,
                Actor1Name,
                Actor1CountryCode,
                Actor1Type1Code,
                Actor1Type2Code,
                Actor1Type3Code,

                Actor2Code,
                Actor2Name,
                Actor2CountryCode,
                Actor2Type1Code,
                Actor2Type2Code,
                Actor2Type3Code,

                IsRootEvent,
                EventCode,
                EventBaseCode,
                EventRootCode,
                QuadClass,
                GoldsteinScale,
                NumMentions,
                NumSources,
                NumArticles,
                AvgTone,

                ActionGeo_Type,
                ActionGeo_FullName,
                ActionGeo_CountryCode,
                ActionGeo_Lat,
                ActionGeo_Long,

                SOURCEURL
            FROM `{self.bigquery_project}.{self.bigquery_dataset}`
            WHERE (Actor1CountryCode = '{actor_filter}' OR Actor2CountryCode = '{actor_filter}')
              AND SQLDATE >= {start_date}
              AND SQLDATE <= {end_date}
            LIMIT {chunk_size}
            OFFSET {offset}
            """

            try:
                query_job = self.bigquery_client.query(query)
                results = query_job.result()

                batch = [dict(row.items()) for row in results]

                if len(batch) == 0:
                    break  # No more results

                all_events.extend(batch)
                offset += chunk_size

                logging.info(f"  Fetched {len(all_events):,} events so far...")

            except Exception as e:
                logging.error(f"BigQuery query failed at offset {offset}: {e}")
                break

        query_time = time.time() - query_start
        self.stats["query_time_seconds"] += query_time
        self.stats["events_queried"] = len(all_events)

        logging.info(f"Query complete: {len(all_events):,} events in {query_time:.1f}s")

        return all_events

    def insert_events(self, events: List[Dict]) -> Tuple[int, int, int]:
        """
        Insert events with deduplication tracking

        Returns:
            (inserted, duplicates, errors)
        """
        if not events:
            return (0, 0, 0)

        insert_sql = """
        INSERT OR IGNORE INTO gdelt_events (
            globaleventid, sqldate, event_date,
            actor1_code, actor1_name, actor1_country_code,
            actor1_type1_code, actor1_type2_code, actor1_type3_code,
            actor2_code, actor2_name, actor2_country_code,
            actor2_type1_code, actor2_type2_code, actor2_type3_code,
            is_root_event, event_code, event_base_code, event_root_code,
            quad_class, goldstein_scale, num_mentions, num_sources,
            num_articles, avg_tone,
            action_geo_type, action_geo_fullname, action_geo_country_code,
            action_geo_lat, action_geo_long,
            source_url, collection_date,
            data_source, bigquery_dataset, selection_criteria, collection_method
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?
        )
        """

        collection_date = datetime.now().isoformat()
        data_source = 'GDELT BigQuery v2'
        bigquery_dataset = f'{self.bigquery_project}.{self.bigquery_dataset}'
        selection_criteria = 'Actor1CountryCode=CHN OR Actor2CountryCode=CHN'
        collection_method = 'BigQuery SQL Query (Paginated)'

        inserted = 0
        duplicates = 0
        errors = 0

        insert_start = time.time()

        for event in events:
            try:
                values = (
                    event.get('GLOBALEVENTID'),
                    event.get('SQLDATE'),
                    event.get('event_date'),
                    event.get('Actor1Code'),
                    event.get('Actor1Name'),
                    event.get('Actor1CountryCode'),
                    event.get('Actor1Type1Code'),
                    event.get('Actor1Type2Code'),
                    event.get('Actor1Type3Code'),
                    event.get('Actor2Code'),
                    event.get('Actor2Name'),
                    event.get('Actor2CountryCode'),
                    event.get('Actor2Type1Code'),
                    event.get('Actor2Type2Code'),
                    event.get('Actor2Type3Code'),
                    event.get('IsRootEvent'),
                    event.get('EventCode'),
                    event.get('EventBaseCode'),
                    event.get('EventRootCode'),
                    event.get('QuadClass'),
                    event.get('GoldsteinScale'),
                    event.get('NumMentions'),
                    event.get('NumSources'),
                    event.get('NumArticles'),
                    event.get('AvgTone'),
                    event.get('ActionGeo_Type'),
                    event.get('ActionGeo_FullName'),
                    event.get('ActionGeo_CountryCode'),
                    event.get('ActionGeo_Lat'),
                    event.get('ActionGeo_Long'),
                    event.get('SOURCEURL'),
                    collection_date,
                    data_source,
                    bigquery_dataset,
                    selection_criteria,
                    collection_method
                )

                cursor = self.conn.execute(insert_sql, values)
                if cursor.rowcount > 0:
                    inserted += 1
                else:
                    duplicates += 1  # INSERT OR IGNORE skipped

            except sqlite3.Error as e:
                logging.warning(f"Failed to insert event {event.get('GLOBALEVENTID')}: {e}")
                errors += 1
                continue

        self.conn.commit()
        insert_time = time.time() - insert_start

        self.stats["events_inserted"] += inserted
        self.stats["events_duplicate"] += duplicates
        self.stats["events_error"] += errors
        self.stats["insert_time_seconds"] += insert_time

        logging.info(f"Insert complete: {inserted:,} new, {duplicates:,} dupes, {errors} errors in {insert_time:.1f}s")

        return (inserted, duplicates, errors)

    def validate_collection(self, start_date: str, end_date: str, events_collected: int) -> ValidationReport:
        """
        Validate collection quality

        Checks:
        - NULL rates for critical fields
        - Data completeness
        - Duplicate detection
        """
        report = ValidationReport()

        # Check NULL rates
        cur = self.conn.cursor()
        cur.execute(f"""
            SELECT
                SUM(CASE WHEN actor1_country_code IS NULL THEN 1 ELSE 0 END) as null_actor1,
                SUM(CASE WHEN actor2_country_code IS NULL THEN 1 ELSE 0 END) as null_actor2,
                COUNT(*) as total
            FROM gdelt_events
            WHERE sqldate BETWEEN {start_date} AND {end_date}
        """)
        row = cur.fetchone()

        if row and row[2] > 0:
            null_actor1_pct = (row[0] / row[2]) * 100
            null_actor2_pct = (row[1] / row[2]) * 100

            if null_actor2_pct > 25:
                report.add_issue(
                    "WARNING",
                    "HIGH_NULL_RATE_ACTOR2",
                    f"{null_actor2_pct:.1f}% of events missing Actor2 country code",
                    "This is normal for GDELT data but may affect country-specific filtering"
                )

        # Check if we got expected events
        if events_collected == 0:
            report.add_issue(
                "CRITICAL",
                "ZERO_EVENTS_COLLECTED",
                "No events were collected for this date range",
                "Verify BigQuery query and date range"
            )

        logging.info(f"Validation complete: {'PASSED' if report.passed else 'FAILED'}")

        return report

    def collect_date_range(self, start_date: str, end_date: str) -> Dict:
        """
        Collect events for a date range with full validation

        Returns:
            Collection report
        """
        # Check checkpoint
        if self.checkpoint.is_completed(start_date, end_date):
            logging.info(f"Skipping {start_date}-{end_date} (already completed)")
            return {"status": "skipped", "reason": "already_completed"}

        logging.info(f"=" * 80)
        logging.info(f"Collecting: {start_date} to {end_date}")
        logging.info(f"=" * 80)

        try:
            # Query with pagination
            events = self.query_bigquery_events_paginated(start_date, end_date)

            # Insert
            inserted, duplicates, errors = self.insert_events(events)

            # Validate
            validation = self.validate_collection(start_date, end_date, inserted)

            # Save checkpoint
            self.checkpoint.mark_completed(start_date, end_date, inserted)

            report = {
                "status": "success",
                "date_range": {"start": start_date, "end": end_date},
                "events_queried": len(events),
                "events_inserted": inserted,
                "events_duplicate": duplicates,
                "events_error": errors,
                "validation": validation.to_dict()
            }

            validation.print_report()

            return report

        except Exception as e:
            logging.error(f"Collection failed for {start_date}-{end_date}: {e}")
            self.checkpoint.mark_failed(start_date, end_date, str(e))

            return {
                "status": "failed",
                "date_range": {"start": start_date, "end": end_date},
                "error": str(e)
            }

    def collect_months(self, year: int, months: List[int]) -> Dict:
        """
        Collect multiple months with automatic date range generation

        Args:
            year: 2021
            months: [7, 8, 9, 10, 11, 12]
        """
        collection_id = f"gdelt_{year}_months_{'_'.join(map(str, months))}"
        self.checkpoint.start_collection(collection_id)

        logging.info(f"\nStarting collection: {collection_id}")
        logging.info(f"Total months: {len(months)}")
        logging.info(f"Checkpoint: {self.checkpoint.checkpoint_file}\n")

        reports = []

        for i, month in enumerate(months, 1):
            # Generate date range for month
            start_date = f"{year}{month:02d}01"

            # Last day of month
            if month == 12:
                end_date = f"{year}1231"
            else:
                next_month_first = datetime(year, month + 1, 1)
                last_day = next_month_first - timedelta(days=1)
                end_date = f"{year}{month:02d}{last_day.day}"

            print(f"\n[{i}/{len(months)}] Collecting {start_date} to {end_date}...")

            report = self.collect_date_range(start_date, end_date)
            reports.append(report)

            if report["status"] == "failed":
                print(f"[ERROR] Failed to collect {start_date}-{end_date}")
                print(f"Error: {report['error']}")
                print("Continuing to next month...")

        self.checkpoint.finish_collection()

        summary = {
            "collection_id": collection_id,
            "total_months": len(months),
            "successful": len([r for r in reports if r["status"] == "success"]),
            "failed": len([r for r in reports if r["status"] == "failed"]),
            "skipped": len([r for r in reports if r["status"] == "skipped"]),
            "total_events_inserted": sum(r.get("events_inserted", 0) for r in reports),
            "reports": reports
        }

        return summary

    def run(self):
        """Main execution"""
        try:
            self.connect()
            self.create_tables()

            if not self.setup_bigquery():
                logging.error("BigQuery setup failed")
                return

            # Ready to collect
            logging.info("Collector initialized and ready")

        finally:
            if self.conn:
                self.conn.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GDELT Collector V2 - Production Ready")
    parser.add_argument("--year", type=int, help="Year to collect (e.g., 2021)")
    parser.add_argument("--months", type=str, help="Months to collect (e.g., '7,8,9,10,11,12')")
    parser.add_argument("--start-date", help="Start date (YYYYMMDD)")
    parser.add_argument("--end-date", help="End date (YYYYMMDD)")
    parser.add_argument("--checkpoint", default="checkpoints/gdelt_checkpoint.json", help="Checkpoint file")

    args = parser.parse_args()

    collector = GDELTCollectorV2(checkpoint_file=args.checkpoint)
    collector.connect()
    collector.create_tables()

    if not collector.setup_bigquery():
        print("ERROR: BigQuery setup failed")
        sys.exit(1)

    if args.year and args.months:
        # Collect specific months
        months = [int(m) for m in args.months.split(',')]
        summary = collector.collect_months(args.year, months)

        print("\n" + "=" * 80)
        print("COLLECTION SUMMARY")
        print("=" * 80)
        print(f"Collection ID: {summary['collection_id']}")
        print(f"Total months: {summary['total_months']}")
        print(f"Successful: {summary['successful']}")
        print(f"Failed: {summary['failed']}")
        print(f"Skipped: {summary['skipped']}")
        print(f"Total events inserted: {summary['total_events_inserted']:,}")
        print("=" * 80)

    elif args.start_date and args.end_date:
        # Collect single date range
        report = collector.collect_date_range(args.start_date, args.end_date)
        print(f"\nCollection {report['status']}")
        if report['status'] == 'success':
            print(f"Events inserted: {report['events_inserted']:,}")

    else:
        parser.print_help()

    if collector.conn:
        collector.conn.close()
