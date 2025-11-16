#!/usr/bin/env python3
"""
GDELT EU-China Bilateral Events Collector
Collects bilateral events between specific EU countries and China (2020-2025)

Query Logic:
    WHERE ((Actor1CountryCode = 'EUR_COUNTRY' OR Actor2CountryCode = 'EUR_COUNTRY')
           AND (Actor1CountryCode = 'CHN' OR Actor2CountryCode = 'CHN'))

This ensures we only get events where BOTH the EU country AND China are involved.
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import logging
import argparse

# BigQuery imports
try:
    from google.cloud import bigquery
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False
    print("ERROR: google-cloud-bigquery not installed")
    print("Install with: pip install google-cloud-bigquery")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class EUChinaBilateralCollector:
    """Collect bilateral GDELT events between EU country and China"""

    def __init__(self, db_path="F:/OSINT_WAREHOUSE/osint_master.db"):
        self.db_path = Path(db_path)
        self.conn = None
        self.bigquery_client = None
        self.bigquery_project = "gdelt-bq"
        self.bigquery_dataset = "gdeltv2.events"

    def init_bigquery(self):
        """Initialize BigQuery client"""
        try:
            # Use application default credentials
            self.bigquery_client = bigquery.Client(project="osint-foresight-2025")
            logging.info("✅ BigQuery client initialized")
            return True
        except Exception as e:
            logging.error(f"❌ BigQuery initialization failed: {e}")
            return False

    def init_database(self):
        """Connect to database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            logging.info(f"✅ Connected to database: {self.db_path}")
            return True
        except Exception as e:
            logging.error(f"❌ Database connection failed: {e}")
            return False

    def query_bilateral_events(self, country_code, start_date, end_date, limit=1000000):
        """
        Query bilateral events between EU country and China

        Args:
            country_code: EU country code (e.g., 'GRC', 'SVK', 'FIN')
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            limit: Maximum records

        Returns:
            List of event dictionaries
        """
        if not self.bigquery_client:
            logging.error("BigQuery client not initialized")
            return []

        # Bilateral query - both country AND China must be present
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
        WHERE ((Actor1CountryCode = '{country_code}' OR Actor2CountryCode = '{country_code}')
               AND (Actor1CountryCode = 'CHN' OR Actor2CountryCode = 'CHN'))
          AND SQLDATE >= {start_date}
          AND SQLDATE <= {end_date}
        ORDER BY SQLDATE DESC
        LIMIT {limit}
        """

        try:
            logging.info(f"🔍 Querying {country_code}-China bilateral events: {start_date} to {end_date}")
            logging.info(f"Query: ((Actor1='{country_code}' OR Actor2='{country_code}') AND (Actor1='CHN' OR Actor2='CHN'))")

            query_job = self.bigquery_client.query(query)
            results = query_job.result()

            events = []
            for row in results:
                event = dict(row.items())
                events.append(event)

            # Calculate data scanned (for cost estimation)
            bytes_scanned = query_job.total_bytes_processed
            gb_scanned = bytes_scanned / (1024 ** 3)
            cost_estimate = max(0, (gb_scanned - 1000) * 5 / 1024)  # $5 per TB after first 1TB free

            logging.info(f"✅ Retrieved {len(events):,} bilateral events")
            logging.info(f"📊 Data scanned: {gb_scanned:.2f} GB")
            logging.info(f"💰 Estimated cost: ${cost_estimate:.4f}")

            return events, gb_scanned

        except Exception as e:
            logging.error(f"❌ BigQuery query failed: {e}")
            return [], 0

    def insert_events(self, events, country_code):
        """Insert events into database"""
        if not events:
            logging.info("No events to insert")
            return 0

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
        bigquery_dataset = 'gdelt-bq.gdeltv2.events'
        selection_criteria = f'(Actor1={country_code} OR Actor2={country_code}) AND (Actor1=CHN OR Actor2=CHN)'
        collection_method = 'BigQuery Bilateral Query'
        inserted = 0

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
                self.conn.execute(insert_sql, values)
                inserted += 1
            except Exception as e:
                logging.warning(f"Failed to insert event {event.get('GLOBALEVENTID')}: {e}")

        self.conn.commit()
        logging.info(f"✅ Inserted {inserted:,} events into database")
        return inserted

    def collect(self, country_code, start_date, end_date):
        """Main collection workflow"""
        logging.info(f"\n{'='*100}")
        logging.info(f"COLLECTING: {country_code}-China bilateral events")
        logging.info(f"Period: {start_date} to {end_date}")
        logging.info(f"{'='*100}\n")

        # Initialize
        if not self.init_bigquery():
            return False
        if not self.init_database():
            return False

        # Query
        events, gb_scanned = self.query_bilateral_events(country_code, start_date, end_date)

        if not events:
            logging.info("⚠️  No events found for this period")
            return True  # Not an error, just no data

        # Insert
        inserted = self.insert_events(events, country_code)

        logging.info(f"\n{'='*100}")
        logging.info(f"✅ COLLECTION COMPLETE")
        logging.info(f"Events collected: {len(events):,}")
        logging.info(f"Events inserted: {inserted:,}")
        logging.info(f"Data scanned: {gb_scanned:.2f} GB")
        logging.info(f"{'='*100}\n")

        return True

    def close(self):
        """Close connections"""
        if self.conn:
            self.conn.close()

def main():
    parser = argparse.ArgumentParser(description='GDELT EU-China Bilateral Collector')
    parser.add_argument('--country', required=True, help='EU country code (e.g., GRC, SVK, FIN)')
    parser.add_argument('--start-date', required=True, help='Start date (YYYYMMDD)')
    parser.add_argument('--end-date', required=True, help='End date (YYYYMMDD)')
    parser.add_argument('--db', default='F:/OSINT_WAREHOUSE/osint_master.db', help='Database path')

    args = parser.parse_args()

    collector = EUChinaBilateralCollector(db_path=args.db)
    try:
        success = collector.collect(args.country, args.start_date, args.end_date)
        sys.exit(0 if success else 1)
    finally:
        collector.close()

if __name__ == '__main__':
    main()
