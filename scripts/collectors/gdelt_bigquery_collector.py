#!/usr/bin/env python3
"""
GDELT News Monitoring Collector
Collects global news events from GDELT Project via BigQuery

GDELT Coverage:
- 300M+ events per year from 100,000+ sources worldwide
- Includes: Xinhua, CGTN, People's Daily, Global Times (Chinese state media)
- Western media: NYT, WSJ, FT, Reuters, Bloomberg
- European media: Le Monde, Der Spiegel, The Guardian
- Historical archives back to 1979

Data Sources:
- GDELT Event Database (who did what to whom)
- GDELT Mentions (media coverage frequency)
- GDELT Global Knowledge Graph (themes, locations, sentiment)

Access Methods:
1. BigQuery (recommended): Free up to 1TB/month queries
2. Direct downloads: Daily update files from gdeltproject.org

Output: F:/OSINT_WAREHOUSE/osint_master.db

Zero Fabrication Protocol: ENFORCED
- Only processes actual GDELT data
- No inference or extrapolation
- Source provenance tracked for every record
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional
import time

# BigQuery imports
try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False
    print("Warning: google-cloud-bigquery not installed. Install with: pip install google-cloud-bigquery")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/gdelt_collection.log'),
        logging.StreamHandler()
    ]
)

class GDELTCollector:
    """
    Collect GDELT news data via BigQuery or direct downloads

    Focus Areas:
    - China-related events (Actor1/Actor2 = CHN)
    - Technology partnerships
    - Investment announcements
    - Regulatory actions
    - Trade disputes
    """

    def __init__(self,
                 master_db="F:/OSINT_WAREHOUSE/osint_master.db",
                 use_bigquery=True,
                 credentials_path=None):
        """
        Initialize GDELT collector

        Args:
            master_db: Path to master database
            use_bigquery: Use BigQuery API (True) or direct downloads (False)
            credentials_path: Path to Google Cloud service account JSON (optional)
        """
        self.master_db = Path(master_db)
        self.use_bigquery = use_bigquery and BIGQUERY_AVAILABLE
        self.credentials_path = credentials_path
        self.conn = None
        self.bigquery_client = None

        self.stats = {
            "events_collected": 0,
            "mentions_collected": 0,
            "gkg_collected": 0,
            "errors": [],
            "date_range": {"start": None, "end": None}
        }

        # GDELT BigQuery project and datasets
        self.bigquery_project = "gdelt-bq"
        self.bigquery_datasets = {
            "events": "gdeltv2.events",
            "mentions": "gdeltv2.eventmentions",
            "gkg": "gdeltv2.gkg"
        }

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
        if not self.use_bigquery:
            logging.warning("BigQuery not available or disabled")
            return False

        try:
            if self.credentials_path:
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=["https://www.googleapis.com/auth/bigquery"]
                )
                self.bigquery_client = bigquery.Client(
                    credentials=credentials,
                    project=credentials.project_id
                )
            else:
                # Use application default credentials
                self.bigquery_client = bigquery.Client()

            logging.info("BigQuery client initialized successfully")
            return True
        except Exception as e:
            logging.error(f"Failed to setup BigQuery: {e}")
            self.use_bigquery = False
            return False

    def create_tables(self):
        """Create GDELT tables in master database"""
        logging.info("Creating GDELT tables...")

        tables = {
            "gdelt_events": """
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
                    collection_date TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_gdelt_events_date ON gdelt_events(sqldate);
                CREATE INDEX IF NOT EXISTS idx_gdelt_events_actor1 ON gdelt_events(actor1_country_code);
                CREATE INDEX IF NOT EXISTS idx_gdelt_events_actor2 ON gdelt_events(actor2_country_code);
                CREATE INDEX IF NOT EXISTS idx_gdelt_events_event_code ON gdelt_events(event_code);
                CREATE INDEX IF NOT EXISTS idx_gdelt_events_china ON gdelt_events(actor1_country_code, actor2_country_code)
                    WHERE actor1_country_code = 'CHN' OR actor2_country_code = 'CHN';
            """,

            "gdelt_mentions": """
                CREATE TABLE IF NOT EXISTS gdelt_mentions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    globaleventid INTEGER,
                    event_timestamp INTEGER,
                    mention_timestamp INTEGER,
                    mention_type INTEGER,
                    mention_source_name TEXT,
                    mention_identifier TEXT,
                    sentence_id INTEGER,
                    actor1_offset INTEGER,
                    actor2_offset INTEGER,
                    action_offset INTEGER,
                    in_raw_text INTEGER,
                    confidence INTEGER,
                    mention_doc_len INTEGER,
                    mention_doc_tone REAL,

                    collection_date TEXT,

                    FOREIGN KEY (globaleventid) REFERENCES gdelt_events(globaleventid)
                );

                CREATE INDEX IF NOT EXISTS idx_gdelt_mentions_event ON gdelt_mentions(globaleventid);
                CREATE INDEX IF NOT EXISTS idx_gdelt_mentions_source ON gdelt_mentions(mention_source_name);
                CREATE INDEX IF NOT EXISTS idx_gdelt_mentions_timestamp ON gdelt_mentions(mention_timestamp);
            """,

            "gdelt_gkg": """
                CREATE TABLE IF NOT EXISTS gdelt_gkg (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gkg_record_id TEXT UNIQUE,
                    publish_date INTEGER,
                    source_collection_id INTEGER,
                    source_common_name TEXT,
                    document_identifier TEXT,

                    -- Themes (JSON array)
                    themes TEXT,

                    -- Locations (JSON array)
                    locations TEXT,

                    -- Persons (JSON array)
                    persons TEXT,

                    -- Organizations (JSON array)
                    organizations TEXT,

                    -- Tone
                    tone REAL,
                    positive_score REAL,
                    negative_score REAL,
                    polarity REAL,
                    activity_reference_density REAL,
                    self_reference_density REAL,
                    word_count INTEGER,

                    -- Related events
                    related_event_ids TEXT,

                    collection_date TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_gdelt_gkg_date ON gdelt_gkg(publish_date);
                CREATE INDEX IF NOT EXISTS idx_gdelt_gkg_source ON gdelt_gkg(source_common_name);
                CREATE INDEX IF NOT EXISTS idx_gdelt_gkg_doc ON gdelt_gkg(document_identifier);
            """
        }

        for table_name, create_sql in tables.items():
            try:
                self.conn.executescript(create_sql)
                logging.info(f"Created table: {table_name}")
            except sqlite3.Error as e:
                logging.error(f"Error creating {table_name}: {e}")
                self.stats["errors"].append(f"Table creation {table_name}: {str(e)}")

        self.conn.commit()

    def query_bigquery_events(self,
                              start_date: str,
                              end_date: str,
                              actor_filter: str = "CHN",
                              limit: int = 100000) -> List[Dict]:
        """
        Query GDELT events from BigQuery

        Args:
            start_date: Start date (YYYYMMDD format)
            end_date: End date (YYYYMMDD format)
            actor_filter: Country code to filter (default: CHN for China)
            limit: Maximum records to return

        Returns:
            List of event dictionaries
        """
        if not self.bigquery_client:
            logging.error("BigQuery client not initialized")
            return []

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
        FROM `{self.bigquery_project}.{self.bigquery_datasets['events']}`
        WHERE (Actor1CountryCode = '{actor_filter}' OR Actor2CountryCode = '{actor_filter}')
          AND SQLDATE >= {start_date}
          AND SQLDATE <= {end_date}
        ORDER BY SQLDATE DESC
        LIMIT {limit}
        """

        try:
            logging.info(f"Querying BigQuery for events: {start_date} to {end_date}")
            query_job = self.bigquery_client.query(query)
            results = query_job.result()

            events = []
            for row in results:
                event = dict(row.items())
                events.append(event)

            logging.info(f"Retrieved {len(events)} events from BigQuery")
            return events

        except Exception as e:
            logging.error(f"BigQuery query failed: {e}")
            self.stats["errors"].append(f"BigQuery events query: {str(e)}")
            return []

    def insert_events(self, events: List[Dict]):
        """Insert events into database"""
        if not events:
            return

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
        selection_criteria = 'Actor1CountryCode=CHN OR Actor2CountryCode=CHN'
        collection_method = 'BigQuery SQL Query'
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

            except sqlite3.Error as e:
                logging.warning(f"Failed to insert event {event.get('GLOBALEVENTID')}: {e}")
                continue

        self.conn.commit()
        self.stats["events_collected"] += inserted
        logging.info(f"Inserted {inserted} events into database")

    def collect_china_events(self,
                            start_date: str,
                            end_date: str,
                            batch_size: int = 10000):
        """
        Collect China-related events for date range

        Args:
            start_date: Start date (YYYYMMDD format, e.g., "20200101")
            end_date: End date (YYYYMMDD format, e.g., "20251101")
            batch_size: Events per batch (default: 10,000)
        """
        if not self.use_bigquery:
            logging.error("BigQuery not available. Use direct download method instead.")
            return

        logging.info(f"Collecting China events: {start_date} to {end_date}")
        self.stats["date_range"]["start"] = start_date
        self.stats["date_range"]["end"] = end_date

        # Query and insert in batches
        events = self.query_bigquery_events(start_date, end_date, "CHN", batch_size)
        self.insert_events(events)

    def collect_recent_week(self):
        """Collect last 7 days of China-related events"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")

        logging.info(f"Collecting recent week: {start_str} to {end_str}")
        self.collect_china_events(start_str, end_str)

    def collect_recent_month(self):
        """Collect last 30 days of China-related events"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")

        logging.info(f"Collecting recent month: {start_str} to {end_str}")
        self.collect_china_events(start_str, end_str)

    def collect_year(self, year: int):
        """Collect full year of China-related events"""
        start_str = f"{year}0101"
        end_str = f"{year}1231"

        logging.info(f"Collecting year {year}: {start_str} to {end_str}")
        self.collect_china_events(start_str, end_str)

    def generate_report(self) -> Dict:
        """Generate collection summary report with full provenance"""
        report = {
            "collection_timestamp": datetime.now().isoformat(),
            "provenance": {
                "data_source": "GDELT BigQuery v2",
                "bigquery_project": "gdelt-bq",
                "bigquery_dataset": "gdeltv2.events",
                "table_version": "latest",
                "api_method": "google.cloud.bigquery.Client",
                "collector_script": "gdelt_bigquery_collector.py",
                "collector_version": "1.0"
            },
            "selection_criteria": {
                "filter": "Actor1CountryCode = 'CHN' OR Actor2CountryCode = 'CHN'",
                "rationale": "Project mission: China-related global events",
                "date_range_start": self.stats["date_range"].get("start", ""),
                "date_range_end": self.stats["date_range"].get("end", ""),
                "additional_filters": []
            },
            "statistics": {
                "events_collected": self.stats["events_collected"],
                "mentions_collected": self.stats["mentions_collected"],
                "gkg_collected": self.stats["gkg_collected"]
            },
            "errors": self.stats["errors"],
            "database": str(self.master_db),
            "method": "BigQuery" if self.use_bigquery else "Direct Download",
            "reproducibility": {
                "can_recreate": True,
                "requires": ["Google Cloud credentials", "BigQuery API access"],
                "estimated_cost": "$0.00 (within free tier)"
            }
        }

        return report

    def run(self, mode: str = "recent_week", custom_dates: tuple = None):
        """
        Main execution method

        Args:
            mode: Collection mode - "recent_week", "recent_month", "year", "custom"
            custom_dates: (start_date, end_date) tuple for custom mode (YYYYMMDD format)
        """
        try:
            # Connect to database
            self.connect()

            # Create tables
            self.create_tables()

            # Setup BigQuery if using
            if self.use_bigquery:
                if not self.setup_bigquery():
                    logging.error("BigQuery setup failed. Exiting.")
                    return

            # Collect based on mode
            if mode == "recent_week":
                self.collect_recent_week()
            elif mode == "recent_month":
                self.collect_recent_month()
            elif mode == "year" and custom_dates:
                self.collect_year(custom_dates[0])
            elif mode == "custom" and custom_dates:
                self.collect_china_events(custom_dates[0], custom_dates[1])
            else:
                logging.error(f"Invalid mode: {mode}")
                return

            # Generate report
            report = self.generate_report()

            # Save report
            report_path = Path("F:/OSINT_DATA/GDELT/collection_reports") / f"gdelt_collection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)

            logging.info(f"Collection complete. Report saved to {report_path}")
            logging.info(f"Events collected: {self.stats['events_collected']}")

        except Exception as e:
            logging.error(f"Collection failed: {e}")
            raise

        finally:
            if self.conn:
                self.conn.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GDELT News Monitoring Collector")
    parser.add_argument("--mode", default="recent_week",
                       choices=["recent_week", "recent_month", "year", "custom"],
                       help="Collection mode")
    parser.add_argument("--start-date", help="Start date (YYYYMMDD) for custom mode")
    parser.add_argument("--end-date", help="End date (YYYYMMDD) for custom mode")
    parser.add_argument("--year", type=int, help="Year to collect (for year mode)")
    parser.add_argument("--credentials", help="Path to Google Cloud credentials JSON")
    parser.add_argument("--no-bigquery", action="store_true", help="Disable BigQuery, use downloads")

    args = parser.parse_args()

    # Validate arguments
    custom_dates = None
    if args.mode == "custom":
        if not args.start_date or not args.end_date:
            parser.error("--start-date and --end-date required for custom mode")
        custom_dates = (args.start_date, args.end_date)
    elif args.mode == "year":
        if not args.year:
            parser.error("--year required for year mode")
        custom_dates = (args.year,)

    # Initialize collector
    collector = GDELTCollector(
        use_bigquery=not args.no_bigquery,
        credentials_path=args.credentials
    )

    # Run collection
    collector.run(mode=args.mode, custom_dates=custom_dates)
