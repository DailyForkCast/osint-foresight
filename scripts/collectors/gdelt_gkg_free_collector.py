#!/usr/bin/env python3
"""
GDELT GKG Free Collector
Downloads and processes GDELT GKG files directly from public repository (ZERO COST)

Data Source: http://data.gdeltproject.org/gdeltv2/
File Format: Tab-delimited CSV, updated every 15 minutes
Cost: $0 (vs $8.86/day on BigQuery)

GKG 2.0 Column Structure (27 columns, tab-delimited):
0. GKGRECORDID
1. DATE (V2.1: YYYYMMDDHHMMSS)
2. SourceCollectionIdentifier
3. SourceCommonName
4. DocumentIdentifier
5. Counts
6. V2Counts
7. Themes
8. V2Themes
9. Locations
10. V2Locations
11. Persons
12. V2Persons
13. Organizations
14. V2Organizations
15. V2Tone
16. Dates
17. GCAM
18. SharingImage
19. RelatedImages
20. SocialImageEmbeds
21. SocialVideoEmbeds
22. Quotations
23. AllNames
24. Amounts
25. TranslationInfo
26. Extras

Reference: http://data.gdeltproject.org/documentation/GDELT-Global_Knowledge_Graph_Codebook-V2.1.pdf
"""

import sys
import requests
import zipfile
import io
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional
import time
import csv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/gkg_free_collection.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

class GKGFreeCollector:
    """
    Download and parse GDELT GKG files directly (zero cost)
    """

    def __init__(self, master_db="F:/OSINT_WAREHOUSE/osint_master.db"):
        self.master_db = Path(master_db)
        self.conn = None

        # GDELT GKG 2.0 file URL pattern
        self.gkg_url_pattern = "http://data.gdeltproject.org/gdeltv2/{timestamp}.gkg.csv.zip"

        # China-related keywords for filtering
        self.china_keywords = [
            'china', 'chinese', 'beijing', 'prc', 'peoples republic',
            'huawei', 'tencent', 'alibaba', 'xiaomi', 'baidu',
            'quantum', 'semiconductor', 'technology', 'university',
            'research', 'military', 'pla', 'belt and road'
        ]

        self.stats = {
            'files_downloaded': 0,
            'files_processed': 0,
            'total_records': 0,
            'china_records': 0,
            'bytes_downloaded': 0,
            'errors': []
        }

    def connect(self):
        """Connect to database"""
        logging.info(f"Connecting to: {self.master_db}")
        self.master_db.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.master_db)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.execute("PRAGMA cache_size=-64000")

    def close(self):
        """Close database"""
        if self.conn:
            self.conn.commit()
            self.conn.close()

    def ensure_gkg_table(self):
        """Ensure GKG table exists (matches existing schema)"""
        # Table already exists from gdelt_bigquery_collector.py
        # Just verify it's there
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='gdelt_gkg'")
        if cursor.fetchone():
            logging.info("Using existing gdelt_gkg table")
        else:
            logging.warning("gdelt_gkg table does not exist - creating it")
            create_sql = """
                CREATE TABLE IF NOT EXISTS gdelt_gkg (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gkg_record_id TEXT UNIQUE,
                    publish_date INTEGER,
                    source_collection_id INTEGER,
                    source_common_name TEXT,
                    document_identifier TEXT,
                    themes TEXT,
                    locations TEXT,
                    persons TEXT,
                    organizations TEXT,
                    tone REAL,
                    positive_score REAL,
                    negative_score REAL,
                    polarity REAL,
                    activity_reference_density REAL,
                    self_reference_density REAL,
                    word_count INTEGER,
                    related_event_ids TEXT,
                    collection_date TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_gdelt_gkg_date ON gdelt_gkg(publish_date);
                CREATE INDEX IF NOT EXISTS idx_gdelt_gkg_source ON gdelt_gkg(source_common_name);
            """
            self.conn.executescript(create_sql)
            self.conn.commit()

    def get_timestamps_for_date(self, date_str: str) -> List[str]:
        """
        Generate all 15-minute timestamps for a given date
        GDELT publishes new files every 15 minutes

        Args:
            date_str: Date in YYYYMMDD format

        Returns:
            List of timestamps in YYYYMMDDHHMMSS format
        """
        timestamps = []

        # Generate timestamps for all 15-minute intervals in a day
        for hour in range(24):
            for minute in [0, 15, 30, 45]:
                timestamp = f"{date_str}{hour:02d}{minute:02d}00"
                timestamps.append(timestamp)

        return timestamps

    def is_china_related(self, record: List[str]) -> bool:
        """
        Check if GKG record is China-related

        Args:
            record: List of field values from GKG file

        Returns:
            True if China-related, False otherwise
        """
        # Check key text fields (themes, orgs, persons, document ID)
        check_fields = [
            record[7] if len(record) > 7 else '',   # Themes
            record[8] if len(record) > 8 else '',   # V2Themes
            record[13] if len(record) > 13 else '', # Organizations
            record[14] if len(record) > 14 else '', # V2Organizations
            record[11] if len(record) > 11 else '', # Persons
            record[12] if len(record) > 12 else '', # V2Persons
            record[4] if len(record) > 4 else '',   # DocumentIdentifier
            record[3] if len(record) > 3 else ''    # SourceCommonName
        ]

        combined_text = ' '.join(check_fields).lower()

        # Check for any China keyword
        for keyword in self.china_keywords:
            if keyword in combined_text:
                return True

        return False

    def download_and_process_file(self, timestamp: str) -> int:
        """
        Download and process a single GKG file

        Args:
            timestamp: Timestamp in YYYYMMDDHHMMSS format

        Returns:
            Number of China-related records inserted
        """
        url = self.gkg_url_pattern.format(timestamp=timestamp)

        try:
            # Download file
            response = requests.get(url, timeout=30)

            if response.status_code == 404:
                # File doesn't exist (no data for this timestamp)
                return 0

            response.raise_for_status()

            self.stats['bytes_downloaded'] += len(response.content)
            self.stats['files_downloaded'] += 1

            # Unzip in memory
            with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                # Get the CSV filename (should be only file in zip)
                csv_filename = zf.namelist()[0]

                # Read CSV content
                with zf.open(csv_filename) as csv_file:
                    # Decode and parse tab-delimited
                    content = csv_file.read().decode('utf-8', errors='ignore')
                    reader = csv.reader(io.StringIO(content), delimiter='\t')

                    china_records = []
                    total_records = 0

                    for row in reader:
                        total_records += 1

                        # Check if China-related
                        if self.is_china_related(row):
                            # Pad row to 27 columns if needed
                            while len(row) < 27:
                                row.append('')

                            china_records.append(row)

                    # Insert China-related records
                    if china_records:
                        self._insert_batch(china_records)

                    self.stats['total_records'] += total_records
                    self.stats['china_records'] += len(china_records)
                    self.stats['files_processed'] += 1

                    if len(china_records) > 0:
                        logging.info(f"  {timestamp}: {len(china_records):,} China records (of {total_records:,} total)")

                    return len(china_records)

        except requests.exceptions.RequestException as e:
            if '404' not in str(e):
                logging.debug(f"  {timestamp}: No file (404)")
            return 0
        except Exception as e:
            error_msg = f"Error processing {timestamp}: {e}"
            logging.error(error_msg)
            self.stats['errors'].append(error_msg)
            return 0

    def _insert_batch(self, records: List[List[str]]):
        """Insert batch of GKG records (matching existing simple schema)"""
        collection_date = datetime.now().isoformat()

        insert_sql = """
            INSERT OR IGNORE INTO gdelt_gkg (
                gkg_record_id, publish_date, source_collection_id,
                source_common_name, document_identifier,
                themes, locations, persons, organizations,
                tone, positive_score, negative_score, polarity,
                activity_reference_density, self_reference_density, word_count,
                related_event_ids, collection_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        batch = []
        for row in records:
            # Ensure we have all 27 columns
            while len(row) < 27:
                row.append('')

            # Parse V2Tone (column 15): tone,positive,negative,polarity,activity_density,self_density,word_count
            tone_str = row[15] if len(row) > 15 else ''
            tone_parts = tone_str.split(',') if tone_str else []

            # Extract tone metrics (pad with None if missing)
            try:
                tone = float(tone_parts[0]) if len(tone_parts) > 0 and tone_parts[0] else None
                positive = float(tone_parts[1]) if len(tone_parts) > 1 and tone_parts[1] else None
                negative = float(tone_parts[2]) if len(tone_parts) > 2 and tone_parts[2] else None
                polarity = float(tone_parts[3]) if len(tone_parts) > 3 and tone_parts[3] else None
                activity = float(tone_parts[4]) if len(tone_parts) > 4 and tone_parts[4] else None
                self_ref = float(tone_parts[5]) if len(tone_parts) > 5 and tone_parts[5] else None
                word_count = int(tone_parts[6]) if len(tone_parts) > 6 and tone_parts[6] else None
            except ValueError:
                tone = positive = negative = polarity = activity = self_ref = word_count = None

            # Map GKG columns to existing schema
            record = (
                row[0],   # gkg_record_id
                int(row[1]) if row[1] else None,  # publish_date
                int(row[2]) if row[2] else None,  # source_collection_id
                row[3],   # source_common_name
                row[4],   # document_identifier
                row[8],   # themes (V2Themes)
                row[10],  # locations (V2Locations)
                row[12],  # persons (V2Persons)
                row[14],  # organizations (V2Organizations)
                tone,     # tone
                positive, # positive_score
                negative, # negative_score
                polarity, # polarity
                activity, # activity_reference_density
                self_ref, # self_reference_density
                word_count, # word_count
                None,     # related_event_ids (not in GKG files)
                collection_date
            )
            batch.append(record)

        self.conn.executemany(insert_sql, batch)
        self.conn.commit()

    def collect_date(self, date_str: str):
        """
        Collect GKG data for a full date

        Args:
            date_str: Date in YYYYMMDD format
        """
        logging.info(f"\nCollecting GKG for {date_str}...")

        timestamps = self.get_timestamps_for_date(date_str)

        total_china = 0
        files_found = 0

        for i, timestamp in enumerate(timestamps, 1):
            china_count = self.download_and_process_file(timestamp)
            total_china += china_count

            if china_count > 0:
                files_found += 1

            # Progress indicator every 24 files (6 hours)
            if i % 24 == 0:
                logging.info(f"  Progress: {i}/{len(timestamps)} files, {total_china:,} China records so far")

            # Rate limiting - be nice to GDELT servers
            time.sleep(0.1)  # 100ms between requests

        logging.info(f"Completed {date_str}: {total_china:,} China records from {files_found} files")

        return total_china

    def is_date_already_collected(self, date_str: str) -> bool:
        """
        Check if a date is already in the database

        Args:
            date_str: Date in YYYYMMDD format

        Returns:
            True if date already has records in database
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM gdelt_gkg
            WHERE SUBSTR(CAST(publish_date AS TEXT), 1, 8) = ?
        """, (date_str,))
        count = cursor.fetchone()[0]
        return count > 0

    def collect_dates(self, date_list: List[str]):
        """
        Collect GKG for multiple dates

        Args:
            date_list: List of dates in YYYYMMDD format
        """
        logging.info("="*60)
        logging.info("GDELT GKG FREE COLLECTION")
        logging.info("="*60)
        logging.info(f"Dates to collect: {len(date_list)}")
        logging.info(f"Cost: $0.00 (FREE)")
        logging.info("="*60)

        # Check which dates are already collected
        already_collected = []
        for date_str in date_list:
            if self.is_date_already_collected(date_str):
                already_collected.append(date_str)

        if already_collected:
            logging.info(f"\nSkipping {len(already_collected)} already-collected dates:")
            for date_str in already_collected[:10]:
                logging.info(f"  [SKIP] {date_str}")
            if len(already_collected) > 10:
                logging.info(f"  ... and {len(already_collected) - 10} more")

        # Filter to only uncollected dates
        dates_to_collect = [d for d in date_list if d not in already_collected]
        logging.info(f"\nRemaining to collect: {len(dates_to_collect)} dates")
        logging.info("="*60)

        for i, date_str in enumerate(dates_to_collect, 1):
            logging.info(f"\n[{i}/{len(dates_to_collect)}] Processing {date_str}...")

            self.collect_date(date_str)

        # Final report
        self._print_report()

    def _print_report(self):
        """Print final collection report"""
        mb_downloaded = self.stats['bytes_downloaded'] / (1024**2)

        logging.info("\n" + "="*60)
        logging.info("COLLECTION COMPLETE")
        logging.info("="*60)
        logging.info(f"Files downloaded: {self.stats['files_downloaded']:,}")
        logging.info(f"Files processed: {self.stats['files_processed']:,}")
        logging.info(f"Data downloaded: {mb_downloaded:.1f} MB")
        logging.info(f"Total GKG records: {self.stats['total_records']:,}")
        logging.info(f"China-related records: {self.stats['china_records']:,}")
        logging.info(f"Filter efficiency: {self.stats['china_records']/max(1, self.stats['total_records'])*100:.1f}%")
        logging.info(f"Cost: $0.00")

        if self.stats['errors']:
            logging.warning(f"\nErrors: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:5]:
                logging.warning(f"  {error}")

        # Save report
        report_file = Path(f"analysis/gkg_free_collection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, 'w') as f:
            json.dump(self.stats, f, indent=2)

        logging.info(f"\nReport saved: {report_file}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Collect GDELT GKG data (FREE)')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--dates', help='Comma-separated dates (YYYYMMDD)')
    group.add_argument('--date-file', help='File containing dates (one per line)')
    parser.add_argument('--db', default='F:/OSINT_WAREHOUSE/osint_master.db', help='Database path')

    args = parser.parse_args()

    # Parse dates from command line or file
    if args.dates:
        date_list = [d.strip() for d in args.dates.split(',')]
    else:
        # Read from file
        with open(args.date_file, 'r') as f:
            date_list = [line.strip() for line in f if line.strip()]

    logging.info(f"Will collect {len(date_list)} dates: {', '.join(date_list)}")

    collector = GKGFreeCollector(master_db=args.db)

    try:
        collector.connect()
        collector.ensure_gkg_table()
        collector.collect_dates(date_list)
    except KeyboardInterrupt:
        logging.info("\nCollection interrupted by user")
    except Exception as e:
        logging.error(f"Collection failed: {e}", exc_info=True)
    finally:
        collector.close()


if __name__ == '__main__':
    main()
