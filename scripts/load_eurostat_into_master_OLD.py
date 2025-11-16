#!/usr/bin/env python3
"""
Load Eurostat COMEXT Data into Master Database
Integrates collected EU trade data into osint_master.db
Date: October 30, 2025
"""

import sqlite3
import csv
import os
from datetime import datetime
from pathlib import Path

# Paths
EUROSTAT_DATA_DIR = Path("F:/OSINT_Data/Trade_Facilities/eurostat_comext_v3")
MASTER_DB = "F:/OSINT_WAREHOUSE/osint_master.db"

# Country code mapping (ISO2 to ISO3)
COUNTRY_MAP = {
    'AT': 'AUT', 'BE': 'BEL', 'BG': 'BGR', 'HR': 'HRV', 'CY': 'CYP',
    'CZ': 'CZE', 'DK': 'DNK', 'EE': 'EST', 'FI': 'FIN', 'FR': 'FRA',
    'DE': 'DEU', 'GR': 'GRC', 'HU': 'HUN', 'IE': 'IRL', 'IT': 'ITA',
    'LV': 'LVA', 'LT': 'LTU', 'LU': 'LUX', 'MT': 'MLT', 'NL': 'NLD',
    'PL': 'POL', 'PT': 'PRT', 'RO': 'ROU', 'SK': 'SVK', 'SI': 'SVN',
    'ES': 'ESP', 'SE': 'SWE', 'CN': 'CHN', 'US': 'USA', 'GB': 'GBR',
    'JP': 'JPN', 'KR': 'KOR', 'RU': 'RUS', 'CH': 'CHE', 'TR': 'TUR'
}

class EurostatLoader:
    def __init__(self):
        self.conn = sqlite3.connect(MASTER_DB, timeout=120)
        self.cur = self.conn.cursor()
        self.records_loaded = 0
        self.records_skipped = 0
        self.errors = 0

    def create_eurostat_table(self):
        """Create Eurostat trade table in master database"""
        print("\n" + "="*80)
        print("Creating Eurostat COMEXT Table")
        print("="*80)

        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS eurostat_comext_trade (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- Geographic
                reporter_iso2 TEXT,
                reporter_iso3 TEXT,
                reporter_name TEXT,
                partner_code TEXT,
                partner_name TEXT,

                -- Product
                product_code TEXT,
                product_name TEXT,
                cn8_code TEXT,

                -- Trade flow
                flow_code TEXT,
                flow_name TEXT,

                -- Temporal
                frequency TEXT,
                time_period TEXT,
                year INTEGER,
                month INTEGER,

                -- Value
                value_euros REAL,

                -- Metadata
                dataset_id TEXT,
                data_source TEXT DEFAULT 'EUROSTAT_COMEXT',
                collection_date TEXT,

                UNIQUE(reporter_iso2, partner_code, product_code, flow_code, time_period)
            )
        ''')

        # Create indexes
        self.cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_eurostat_reporter
            ON eurostat_comext_trade(reporter_iso2)
        ''')

        self.cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_eurostat_partner
            ON eurostat_comext_trade(partner_code)
        ''')

        self.cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_eurostat_product
            ON eurostat_comext_trade(product_code)
        ''')

        self.cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_eurostat_year
            ON eurostat_comext_trade(year)
        ''')

        self.conn.commit()
        print("[OK] Table created with indexes")

    def parse_time_period(self, time_period):
        """Parse time period into year and month"""
        if not time_period or time_period == '':
            return None, None

        try:
            if '-' in time_period:  # Format: 2024-01
                year, month = time_period.split('-')
                return int(year), int(month)
            elif len(time_period) == 4:  # Annual: 2024
                return int(time_period), None
            else:
                return None, None
        except:
            return None, None

    def load_csv_file(self, csv_file, dataset_id):
        """Load a single Eurostat CSV file"""
        print(f"\nLoading: {csv_file.name}")
        print(f"Dataset: {dataset_id}")

        if not csv_file.exists():
            print(f"[ERROR] File not found: {csv_file}")
            return

        loaded = 0
        skipped = 0

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    try:
                        # Parse time period
                        year, month = self.parse_time_period(row['TIME_PERIOD'])

                        if not year:  # Skip rows without valid date
                            skipped += 1
                            continue

                        # Parse value
                        try:
                            value_euros = float(row['OBS_VALUE']) if row['OBS_VALUE'] else None
                        except:
                            value_euros = None

                        # Map reporter country
                        reporter_iso2 = row['reporter']
                        reporter_iso3 = COUNTRY_MAP.get(reporter_iso2, reporter_iso2)

                        # Insert record
                        self.cur.execute('''
                            INSERT OR IGNORE INTO eurostat_comext_trade (
                                reporter_iso2, reporter_iso3, reporter_name,
                                partner_code, partner_name,
                                product_code, product_name,
                                flow_code, flow_name,
                                frequency, time_period,
                                year, month,
                                value_euros,
                                dataset_id, collection_date
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            reporter_iso2,
                            reporter_iso3,
                            row['REPORTER'],
                            row['partner'],
                            row['PARTNER'],
                            row['product'],
                            row['PRODUCT'],
                            row['flow'],
                            row['FLOW'],
                            row['freq'],
                            row['TIME_PERIOD'],
                            year,
                            month,
                            value_euros,
                            dataset_id,
                            datetime.now().isoformat()
                        ))

                        loaded += 1

                        if loaded % 500 == 0:
                            self.conn.commit()
                            print(f"  Loaded: {loaded} records...", end='\r')

                    except Exception as e:
                        self.errors += 1
                        if self.errors <= 5:  # Show first 5 errors
                            print(f"\n  [ERROR] Row error: {str(e)[:80]}")

                self.conn.commit()
                print(f"\n  [OK] Loaded {loaded} records, skipped {skipped}")

        except Exception as e:
            print(f"[ERROR] Failed to load file: {e}")
            self.errors += 1

        self.records_loaded += loaded
        self.records_skipped += skipped

    def load_all_eurostat_files(self):
        """Load all Eurostat CSV files from collection directory"""
        print("\n" + "="*80)
        print("Loading Eurostat COMEXT Data Files")
        print("="*80)

        # Files to load
        files_to_load = [
            ('DS-045409_china_trade_20251030.csv', 'DS-045409'),
            ('DS-059329_china_trade_20251030.csv', 'DS-059329')
        ]

        for filename, dataset_id in files_to_load:
            csv_file = EUROSTAT_DATA_DIR / filename
            if csv_file.exists():
                self.load_csv_file(csv_file, dataset_id)
            else:
                print(f"\n[WARN] File not found: {filename}")

    def generate_summary(self):
        """Generate summary statistics"""
        print("\n" + "="*80)
        print("EUROSTAT INTEGRATION SUMMARY")
        print("="*80)

        # Total records in table
        self.cur.execute('SELECT COUNT(*) FROM eurostat_comext_trade')
        total_records = self.cur.fetchone()[0]

        # Records by year
        self.cur.execute('''
            SELECT year, COUNT(*) as count
            FROM eurostat_comext_trade
            WHERE year IS NOT NULL
            GROUP BY year
            ORDER BY year DESC
            LIMIT 10
        ''')

        print(f"\nTotal records in database: {total_records:,}")
        print(f"Records loaded this session: {self.records_loaded:,}")
        print(f"Records skipped: {self.records_skipped:,}")
        print(f"Errors: {self.errors}")

        print("\nRecords by year:")
        for year, count in self.cur.fetchall():
            print(f"  {year}: {count:,}")

        # Records by reporter country
        self.cur.execute('''
            SELECT reporter_name, COUNT(*) as count
            FROM eurostat_comext_trade
            GROUP BY reporter_name
            ORDER BY count DESC
            LIMIT 10
        ''')

        print("\nTop reporting countries:")
        for country, count in self.cur.fetchall():
            print(f"  {country}: {count:,}")

        # Records by dataset
        self.cur.execute('''
            SELECT dataset_id, COUNT(*) as count
            FROM eurostat_comext_trade
            GROUP BY dataset_id
            ORDER BY count DESC
        ''')

        print("\nRecords by dataset:")
        for dataset, count in self.cur.fetchall():
            print(f"  {dataset}: {count:,}")

    def close(self):
        self.conn.close()

def main():
    print("="*80)
    print("EUROSTAT COMEXT DATA LOADER")
    print("="*80)
    print(f"Master Database: {MASTER_DB}")
    print(f"Data Directory: {EUROSTAT_DATA_DIR}")
    print()

    loader = EurostatLoader()

    try:
        # Step 1: Create table
        loader.create_eurostat_table()

        # Step 2: Load all CSV files
        loader.load_all_eurostat_files()

        # Step 3: Generate summary
        loader.generate_summary()

        print("\n" + "="*80)
        print("EUROSTAT INTEGRATION COMPLETE")
        print("="*80)
        print("\nNEXT STEPS:")
        print("1. Review analysis/EUROSTAT_COMEXT_VS_UNCOMTRADE_20251030.md")
        print("2. For comprehensive Eurostat data, use manual bulk downloads:")
        print("   https://ec.europa.eu/eurostat/web/international-trade-in-goods/data/database")
        print("3. Subscribe to UN Comtrade Standard ($500/year) for:")
        print("   - China-Taiwan semiconductor flows (CRITICAL)")
        print("   - BRI countries bilateral trade")
        print("   - Global sanctions monitoring")

    finally:
        loader.close()

if __name__ == '__main__':
    main()
