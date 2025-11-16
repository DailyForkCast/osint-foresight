"""
UN Comtrade Automated Collection System
Implements 3-phase free tier strategy with full automation

Features:
- Automatic rate limiting (100 req/hour, 10K/day)
- Checkpoint/resume functionality
- Error handling and retry logic
- Progress tracking and reporting
- Database storage with deduplication
"""

import sqlite3
import requests
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Configuration
BASE_URL = "https://comtradeapi.un.org/data/v1/get/C/A/HS"
DATABASE_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
CHECKPOINT_PATH = Path("C:/Projects/OSINT-Foresight/data/comtrade_checkpoint.json")
LOG_PATH = Path("C:/Projects/OSINT-Foresight/logs/comtrade_collection.log")

# Rate limits (free tier)
MAX_REQUESTS_PER_HOUR = 100
MAX_REQUESTS_PER_DAY = 10000
REQUESTS_PER_BATCH = 90  # Leave buffer
DELAY_BETWEEN_REQUESTS = 2  # seconds (polite delay)

# Phase definitions
PHASE_1_HS_CODES = [
    # Semiconductors & Electronics
    '854231', '854232', '854233', '854239', '901380',
    # Telecommunications
    '851762', '851770', '852580',
    # Computing & AI Hardware
    '847130', '847150', '847330',
    # Advanced Materials
    '280530', '381800', '854770',
    # Quantum & Emerging Tech
    '903020', '902750', '392690',
    # Dual-Use Components
    '850440', '903290'
]

PHASE_2_HS_CODES = [
    # Aerospace & Defense
    '880240', '880330', '880390', '901420', '880260',
    # Batteries & Energy Storage
    '850760', '854140', '850720',
    # Advanced Manufacturing
    '846221', '846231', '846500', '903180',
    # Biotechnology
    '902780', '902750', '902920'
]

PHASE_3_HS_CODES = [
    # Robotics & Automation
    '847950', '850300', '902830',
    # Chemicals & Materials
    '280461', '281830', '284410',
    # Optics & Sensors
    '900190', '901380', '902610',
    # Other Strategic
    '392010', '902519', '854430', '903289', '903031', '903020'
]

# Country pairs by phase
PHASE_1_PAIRS = [
    ('CN', 'US'), ('US', 'CN'),
    ('CN', 'DE'), ('DE', 'CN'),
    ('CN', 'JP'), ('JP', 'CN'),
    ('CN', 'KR'), ('KR', 'CN'),
    ('CN', 'NL'), ('NL', 'CN')
]

PHASE_2_PAIRS = PHASE_1_PAIRS + [
    ('CN', 'FR'), ('FR', 'CN'),
    ('CN', 'IT'), ('IT', 'CN'),
    ('CN', 'TW'), ('TW', 'CN')
]

PHASE_3_PAIRS = PHASE_2_PAIRS + [
    ('CN', 'GB'), ('GB', 'CN'),
    ('CN', 'ES'), ('ES', 'CN'),
    ('CN', 'PL'), ('PL', 'CN'),
    ('CN', 'CZ'), ('CZ', 'CN'),
    ('CN', 'SG'), ('SG', 'CN'),
    ('CN', 'HK'), ('HK', 'CN')
]

# Years by phase
PHASE_1_YEARS = [2023, 2024, 2025]
PHASE_2_YEARS = [2023, 2024, 2025]
PHASE_3_RECENT_YEARS = [2023, 2024, 2025]
PHASE_3_HISTORICAL_YEARS = [2018, 2020, 2022]


class ComtradeCollector:
    """Automated UN Comtrade data collector with rate limiting and checkpointing"""

    def __init__(self):
        self.db_conn = None
        self.checkpoint = self._load_checkpoint()
        self.session = requests.Session()

        # Rate limiting tracking
        self.requests_this_hour = 0
        self.requests_today = 0
        self.hour_reset_time = datetime.now() + timedelta(hours=1)
        self.day_reset_time = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=1)

        # Statistics
        self.stats = {
            'requests_made': 0,
            'records_collected': 0,
            'errors': 0,
            'skipped_existing': 0,
            'start_time': datetime.now().isoformat()
        }

        # Setup logging
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_PATH),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _load_checkpoint(self) -> Dict:
        """Load checkpoint data to resume collection"""
        if CHECKPOINT_PATH.exists():
            with open(CHECKPOINT_PATH, 'r') as f:
                return json.load(f)
        return {
            'current_phase': 1,
            'completed_requests': [],
            'last_updated': None
        }

    def _save_checkpoint(self):
        """Save checkpoint data"""
        self.checkpoint['last_updated'] = datetime.now().isoformat()
        CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CHECKPOINT_PATH, 'w') as f:
            json.dump(self.checkpoint, f, indent=2)

    def _connect_db(self):
        """Connect to database and create tables if needed"""
        self.db_conn = sqlite3.connect(DATABASE_PATH)
        self.db_conn.execute("PRAGMA journal_mode=WAL")

        # Create comtrade table
        self.db_conn.execute("""
            CREATE TABLE IF NOT EXISTS comtrade_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER NOT NULL,
                reporter_code TEXT NOT NULL,
                reporter_name TEXT,
                partner_code TEXT NOT NULL,
                partner_name TEXT,
                commodity_code TEXT NOT NULL,
                commodity_description TEXT,
                flow_code TEXT,
                flow_description TEXT,
                trade_value_usd REAL,
                quantity REAL,
                quantity_unit TEXT,
                net_weight_kg REAL,
                collected_date TEXT NOT NULL,
                UNIQUE(year, reporter_code, partner_code, commodity_code, flow_code)
            )
        """)

        # Create indexes
        self.db_conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_comtrade_year
            ON comtrade_data(year)
        """)
        self.db_conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_comtrade_reporter
            ON comtrade_data(reporter_code)
        """)
        self.db_conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_comtrade_partner
            ON comtrade_data(partner_code)
        """)
        self.db_conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_comtrade_commodity
            ON comtrade_data(commodity_code)
        """)
        self.db_conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_comtrade_year_commodity
            ON comtrade_data(year, commodity_code)
        """)

        self.db_conn.commit()
        self.logger.info("Database connection established and tables created")

    def _check_rate_limits(self):
        """Check and enforce rate limits"""
        now = datetime.now()

        # Reset hourly counter
        if now >= self.hour_reset_time:
            self.logger.info(f"Hourly rate limit reset. Made {self.requests_this_hour} requests last hour.")
            self.requests_this_hour = 0
            self.hour_reset_time = now + timedelta(hours=1)

        # Reset daily counter
        if now >= self.day_reset_time:
            self.logger.info(f"Daily rate limit reset. Made {self.requests_today} requests yesterday.")
            self.requests_today = 0
            self.day_reset_time = now.replace(hour=0, minute=0, second=0) + timedelta(days=1)

        # Wait if approaching hourly limit
        if self.requests_this_hour >= REQUESTS_PER_BATCH:
            wait_seconds = (self.hour_reset_time - now).total_seconds()
            self.logger.warning(f"Approaching hourly limit ({self.requests_this_hour}/{MAX_REQUESTS_PER_HOUR}). Waiting {wait_seconds:.0f} seconds...")
            time.sleep(wait_seconds + 5)  # Add 5 second buffer
            self.requests_this_hour = 0
            self.hour_reset_time = datetime.now() + timedelta(hours=1)

        # Wait if approaching daily limit
        if self.requests_today >= MAX_REQUESTS_PER_DAY - 100:
            wait_seconds = (self.day_reset_time - now).total_seconds()
            self.logger.warning(f"Approaching daily limit ({self.requests_today}/{MAX_REQUESTS_PER_DAY}). Waiting {wait_seconds:.0f} seconds...")
            time.sleep(wait_seconds + 5)
            self.requests_today = 0
            self.day_reset_time = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=1)

    def _already_collected(self, reporter: str, partner: str, hs_code: str, year: int) -> bool:
        """Check if data already collected"""
        # Check checkpoint
        request_id = f"{reporter}|{partner}|{hs_code}|{year}"
        if request_id in self.checkpoint['completed_requests']:
            return True

        # Check database
        cursor = self.db_conn.execute("""
            SELECT COUNT(*) FROM comtrade_data
            WHERE reporter_code = ? AND partner_code = ?
            AND commodity_code = ? AND year = ?
        """, (reporter, partner, hs_code, year))

        return cursor.fetchone()[0] > 0

    def _make_request(self, reporter: str, partner: str, hs_code: str, year: int) -> Optional[Dict]:
        """Make API request with retry logic"""
        url = f"{BASE_URL}/{year}/{reporter}/{partner}/{hs_code}"

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # Rate limited
                    self.logger.warning(f"Rate limited (429). Waiting 60 seconds...")
                    time.sleep(60)
                    continue
                elif response.status_code == 404:
                    # No data available
                    self.logger.info(f"No data: {reporter} -> {partner}, HS {hs_code}, {year}")
                    return None
                else:
                    self.logger.error(f"HTTP {response.status_code}: {url}")
                    if attempt < max_retries - 1:
                        time.sleep(5 * (attempt + 1))
                        continue
                    return None

            except requests.exceptions.Timeout:
                self.logger.error(f"Timeout (attempt {attempt + 1}/{max_retries}): {url}")
                if attempt < max_retries - 1:
                    time.sleep(10)
                    continue
                return None
            except Exception as e:
                self.logger.error(f"Error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(10)
                    continue
                return None

        return None

    def _store_data(self, data: Dict, reporter: str, partner: str, hs_code: str, year: int):
        """Store data in database"""
        if not data or 'data' not in data:
            return 0

        records = data['data']
        if not records:
            return 0

        collected_date = datetime.now().isoformat()
        stored = 0

        for record in records:
            try:
                self.db_conn.execute("""
                    INSERT OR IGNORE INTO comtrade_data (
                        year, reporter_code, reporter_name, partner_code, partner_name,
                        commodity_code, commodity_description, flow_code, flow_description,
                        trade_value_usd, quantity, quantity_unit, net_weight_kg, collected_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.get('refYear', year),
                    record.get('reporterCode', reporter),
                    record.get('reporterDesc', ''),
                    record.get('partnerCode', partner),
                    record.get('partnerDesc', ''),
                    record.get('cmdCode', hs_code),
                    record.get('cmdDesc', ''),
                    record.get('flowCode', ''),
                    record.get('flowDesc', ''),
                    record.get('primaryValue', 0.0),
                    record.get('qty', 0.0),
                    record.get('qtyUnitCode', ''),
                    record.get('netWgt', 0.0),
                    collected_date
                ))
                stored += 1
            except Exception as e:
                self.logger.error(f"Error storing record: {e}")

        self.db_conn.commit()
        return stored

    def collect_request(self, reporter: str, partner: str, hs_code: str, year: int) -> bool:
        """Collect data for a single request"""
        request_id = f"{reporter}|{partner}|{hs_code}|{year}"

        # Check if already collected
        if self._already_collected(reporter, partner, hs_code, year):
            self.stats['skipped_existing'] += 1
            return True

        # Check rate limits
        self._check_rate_limits()

        # Make request
        self.logger.info(f"Requesting: {reporter} -> {partner}, HS {hs_code}, {year}")
        data = self._make_request(reporter, partner, hs_code, year)

        # Update rate limit counters
        self.requests_this_hour += 1
        self.requests_today += 1
        self.stats['requests_made'] += 1

        # Store data
        if data:
            stored = self._store_data(data, reporter, partner, hs_code, year)
            self.stats['records_collected'] += stored
            self.logger.info(f"  Stored {stored} records")
        else:
            self.stats['errors'] += 1

        # Update checkpoint
        self.checkpoint['completed_requests'].append(request_id)
        if len(self.checkpoint['completed_requests']) % 10 == 0:
            self._save_checkpoint()

        # Polite delay
        time.sleep(DELAY_BETWEEN_REQUESTS)

        return True

    def run_phase_1(self):
        """Execute Phase 1 collection"""
        self.logger.info("="*80)
        self.logger.info("STARTING PHASE 1: Core Technologies")
        self.logger.info(f"HS Codes: {len(PHASE_1_HS_CODES)}, Years: {len(PHASE_1_YEARS)}, Pairs: {len(PHASE_1_PAIRS)}")
        self.logger.info(f"Estimated requests: {len(PHASE_1_HS_CODES) * len(PHASE_1_YEARS) * len(PHASE_1_PAIRS)}")
        self.logger.info("="*80)

        total = len(PHASE_1_HS_CODES) * len(PHASE_1_YEARS) * len(PHASE_1_PAIRS)
        completed = 0

        for hs_code in PHASE_1_HS_CODES:
            for year in PHASE_1_YEARS:
                for reporter, partner in PHASE_1_PAIRS:
                    self.collect_request(reporter, partner, hs_code, year)
                    completed += 1

                    if completed % 50 == 0:
                        progress = (completed / total) * 100
                        self.logger.info(f"Phase 1 Progress: {completed}/{total} ({progress:.1f}%)")
                        self.logger.info(f"  Records collected: {self.stats['records_collected']:,}")
                        self.logger.info(f"  Requests today: {self.requests_today}/{MAX_REQUESTS_PER_DAY}")

        self.checkpoint['current_phase'] = 2
        self._save_checkpoint()
        self.logger.info("PHASE 1 COMPLETE!")

    def run_phase_2(self):
        """Execute Phase 2 collection"""
        self.logger.info("="*80)
        self.logger.info("STARTING PHASE 2: Strategic Expansion")
        self.logger.info(f"HS Codes: {len(PHASE_2_HS_CODES)}, Years: {len(PHASE_2_YEARS)}, Pairs: {len(PHASE_2_PAIRS)}")
        self.logger.info(f"Estimated requests: {len(PHASE_2_HS_CODES) * len(PHASE_2_YEARS) * len(PHASE_2_PAIRS)}")
        self.logger.info("="*80)

        total = len(PHASE_2_HS_CODES) * len(PHASE_2_YEARS) * len(PHASE_2_PAIRS)
        completed = 0

        for hs_code in PHASE_2_HS_CODES:
            for year in PHASE_2_YEARS:
                for reporter, partner in PHASE_2_PAIRS:
                    self.collect_request(reporter, partner, hs_code, year)
                    completed += 1

                    if completed % 50 == 0:
                        progress = (completed / total) * 100
                        self.logger.info(f"Phase 2 Progress: {completed}/{total} ({progress:.1f}%)")
                        self.logger.info(f"  Records collected: {self.stats['records_collected']:,}")
                        self.logger.info(f"  Requests today: {self.requests_today}/{MAX_REQUESTS_PER_DAY}")

        self.checkpoint['current_phase'] = 3
        self._save_checkpoint()
        self.logger.info("PHASE 2 COMPLETE!")

    def run_phase_3_recent(self):
        """Execute Phase 3 collection (recent years)"""
        self.logger.info("="*80)
        self.logger.info("STARTING PHASE 3A: Remaining Codes (Recent Years)")
        self.logger.info(f"HS Codes: {len(PHASE_3_HS_CODES)}, Years: {len(PHASE_3_RECENT_YEARS)}, Pairs: {len(PHASE_3_PAIRS)}")
        self.logger.info(f"Estimated requests: {len(PHASE_3_HS_CODES) * len(PHASE_3_RECENT_YEARS) * len(PHASE_3_PAIRS)}")
        self.logger.info("="*80)

        total = len(PHASE_3_HS_CODES) * len(PHASE_3_RECENT_YEARS) * len(PHASE_3_PAIRS)
        completed = 0

        for hs_code in PHASE_3_HS_CODES:
            for year in PHASE_3_RECENT_YEARS:
                for reporter, partner in PHASE_3_PAIRS:
                    self.collect_request(reporter, partner, hs_code, year)
                    completed += 1

                    if completed % 50 == 0:
                        progress = (completed / total) * 100
                        self.logger.info(f"Phase 3A Progress: {completed}/{total} ({progress:.1f}%)")
                        self.logger.info(f"  Records collected: {self.stats['records_collected']:,}")
                        self.logger.info(f"  Requests today: {self.requests_today}/{MAX_REQUESTS_PER_DAY}")

        self.logger.info("PHASE 3A COMPLETE!")

    def run_phase_3_historical(self):
        """Execute Phase 3 collection (historical years)"""
        self.logger.info("="*80)
        self.logger.info("STARTING PHASE 3B: Historical Data (All Codes)")
        all_codes = PHASE_1_HS_CODES + PHASE_2_HS_CODES + PHASE_3_HS_CODES
        self.logger.info(f"HS Codes: {len(all_codes)}, Years: {len(PHASE_3_HISTORICAL_YEARS)}, Pairs: {len(PHASE_3_PAIRS)}")
        self.logger.info(f"Estimated requests: {len(all_codes) * len(PHASE_3_HISTORICAL_YEARS) * len(PHASE_3_PAIRS)}")
        self.logger.info("="*80)

        total = len(all_codes) * len(PHASE_3_HISTORICAL_YEARS) * len(PHASE_3_PAIRS)
        completed = 0

        for hs_code in all_codes:
            for year in PHASE_3_HISTORICAL_YEARS:
                for reporter, partner in PHASE_3_PAIRS:
                    self.collect_request(reporter, partner, hs_code, year)
                    completed += 1

                    if completed % 100 == 0:
                        progress = (completed / total) * 100
                        self.logger.info(f"Phase 3B Progress: {completed}/{total} ({progress:.1f}%)")
                        self.logger.info(f"  Records collected: {self.stats['records_collected']:,}")
                        self.logger.info(f"  Requests today: {self.requests_today}/{MAX_REQUESTS_PER_DAY}")

        self.checkpoint['current_phase'] = 4  # All complete
        self._save_checkpoint()
        self.logger.info("PHASE 3B COMPLETE!")

    def run_all_phases(self):
        """Run all phases in sequence"""
        try:
            self._connect_db()

            current_phase = self.checkpoint.get('current_phase', 1)

            if current_phase <= 1:
                self.run_phase_1()

            if current_phase <= 2:
                self.run_phase_2()

            if current_phase <= 3:
                self.run_phase_3_recent()
                self.run_phase_3_historical()

            self._print_final_summary()

        except KeyboardInterrupt:
            self.logger.warning("Collection interrupted by user. Progress saved to checkpoint.")
            self._save_checkpoint()
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            self._save_checkpoint()
            raise
        finally:
            if self.db_conn:
                self.db_conn.close()

    def _print_final_summary(self):
        """Print final collection summary"""
        elapsed = (datetime.now() - datetime.fromisoformat(self.stats['start_time'])).total_seconds()

        self.logger.info("="*80)
        self.logger.info("COLLECTION COMPLETE - FINAL SUMMARY")
        self.logger.info("="*80)
        self.logger.info(f"Total requests made: {self.stats['requests_made']:,}")
        self.logger.info(f"Total records collected: {self.stats['records_collected']:,}")
        self.logger.info(f"Skipped (already collected): {self.stats['skipped_existing']:,}")
        self.logger.info(f"Errors: {self.stats['errors']:,}")
        self.logger.info(f"Total time: {elapsed/3600:.1f} hours")
        self.logger.info(f"Average: {self.stats['requests_made']/(elapsed/3600):.1f} requests/hour")
        self.logger.info("="*80)


if __name__ == '__main__':
    collector = ComtradeCollector()
    collector.run_all_phases()
