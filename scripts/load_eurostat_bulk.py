#!/usr/bin/env python3
"""
Load Eurostat COMEXT Bulk China Data into Master Database
Loads 6.3M filtered China/HK/Macau trade records from 23 annual files
Date: November 1, 2025
"""

import sqlite3
import csv
import time
from pathlib import Path
from datetime import datetime

# Paths
FILTERED_DIR = Path("F:/OSINT_Data/Trade_Facilities/eurostat_comext_v3")
MASTER_DB = "F:/OSINT_WAREHOUSE/osint_master.db"
BATCH_SIZE = 5000

class EurostatBulkLoader:
    def __init__(self):
        self.conn = sqlite3.connect(MASTER_DB, timeout=300)
        self.conn.execute('PRAGMA journal_mode=WAL')
        self.conn.execute('PRAGMA synchronous=NORMAL')
        self.conn.execute('PRAGMA cache_size=100000')
        self.cur = self.conn.cursor()
        self.total_loaded = 0
        self.total_skipped = 0
        self.errors = 0

    def create_table(self):
        """Create Eurostat COMEXT table"""
        print('=' * 80)
        print('CREATING EUROSTAT COMEXT TABLE')
        print('=' * 80)

        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS eurostat_comext (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- Geography
                reporter TEXT,
                partner TEXT,

                -- Trade flow
                trade_type TEXT,
                flow TEXT,

                -- Products (multiple classification systems)
                product_nc TEXT,
                product_sitc TEXT,
                product_cpa21 TEXT,
                product_bec TEXT,
                product_bec5 TEXT,
                product_section TEXT,

                -- Procedure
                stat_procedure TEXT,
                suppl_unit TEXT,

                -- Time
                period TEXT,
                year INTEGER,

                -- Values
                value_eur REAL,
                value_nac REAL,
                quantity_kg REAL,
                quantity_suppl_unit REAL,

                -- Metadata
                data_source TEXT DEFAULT 'EUROSTAT_COMEXT_BULK',
                collection_date TEXT,

                UNIQUE(reporter, partner, trade_type, product_nc, period)
            )
        ''')
        self.conn.commit()
        print('[OK] Table created or already exists')
        print()

    def load_csv_file(self, csv_path):
        """Load a single CSV file"""
        print(f'Loading: {csv_path.name}')

        batch = []
        file_loaded = 0
        file_skipped = 0
        file_errors = 0

        collection_date = datetime.now().isoformat()

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    try:
                        # Extract year from period (format: YYYYMM or YYYY)
                        period = row.get('PERIOD', '')
                        year = int(period[:4]) if period and len(period) >= 4 else None

                        # Convert numeric fields
                        value_eur = float(row.get('VALUE_EUR', 0) or 0)
                        value_nac = float(row.get('VALUE_NAC', 0) or 0)
                        quantity_kg = float(row.get('QUANTITY_KG', 0) or 0) if row.get('QUANTITY_KG') else None
                        quantity_suppl_unit = float(row.get('QUANTITY_SUPPL_UNIT', 0) or 0) if row.get('QUANTITY_SUPPL_UNIT') else None

                        batch.append((
                            row.get('REPORTER'),
                            row.get('PARTNER'),
                            row.get('TRADE_TYPE'),
                            row.get('FLOW'),
                            row.get('PRODUCT_NC'),
                            row.get('PRODUCT_SITC'),
                            row.get('PRODUCT_CPA21'),
                            row.get('PRODUCT_BEC'),
                            row.get('PRODUCT_BEC5'),
                            row.get('PRODUCT_SECTION'),
                            row.get('STAT_PROCEDURE'),
                            row.get('SUPPL_UNIT'),
                            period,
                            year,
                            value_eur,
                            value_nac,
                            quantity_kg,
                            quantity_suppl_unit,
                            collection_date
                        ))

                        # Batch insert
                        if len(batch) >= BATCH_SIZE:
                            inserted = self._insert_batch(batch)
                            file_loaded += inserted
                            file_skipped += (len(batch) - inserted)
                            batch = []

                    except Exception as e:
                        file_errors += 1
                        if file_errors < 5:
                            print(f'  [WARN] Row error: {str(e)[:60]}')

                # Insert remaining batch
                if batch:
                    inserted = self._insert_batch(batch)
                    file_loaded += inserted
                    file_skipped += (len(batch) - inserted)

            print(f'  Loaded: {file_loaded:,} | Skipped: {file_skipped:,} | Errors: {file_errors:,}')
            print()

            self.total_loaded += file_loaded
            self.total_skipped += file_skipped
            self.errors += file_errors

        except Exception as e:
            print(f'  [ERROR] Failed to load file: {e}')
            print()

    def _insert_batch(self, batch):
        """Insert a batch of records"""
        inserted = 0
        try:
            self.cur.executemany('''
                INSERT OR IGNORE INTO eurostat_comext (
                    reporter, partner, trade_type, flow,
                    product_nc, product_sitc, product_cpa21, product_bec, product_bec5, product_section,
                    stat_procedure, suppl_unit, period, year,
                    value_eur, value_nac, quantity_kg, quantity_suppl_unit,
                    collection_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', batch)
            inserted = self.cur.rowcount
            self.conn.commit()
        except Exception as e:
            print(f'  [ERROR] Batch insert failed: {e}')
            self.conn.rollback()
        return inserted

    def create_indexes(self):
        """Create indexes for query performance"""
        print('=' * 80)
        print('CREATING INDEXES')
        print('=' * 80)

        indexes = [
            ('idx_eurostat_reporter', 'reporter'),
            ('idx_eurostat_partner', 'partner'),
            ('idx_eurostat_product_nc', 'product_nc'),
            ('idx_eurostat_period', 'period'),
            ('idx_eurostat_year', 'year'),
            ('idx_eurostat_flow', 'flow'),
            ('idx_eurostat_trade_type', 'trade_type'),
            ('idx_eurostat_reporter_partner', 'reporter, partner'),
            ('idx_eurostat_partner_product', 'partner, product_nc')
        ]

        for idx_name, column in indexes:
            try:
                print(f'Creating {idx_name}...')
                start = time.time()
                self.cur.execute(f'CREATE INDEX IF NOT EXISTS {idx_name} ON eurostat_comext({column})')
                self.conn.commit()
                print(f'  [OK] Created in {time.time() - start:.1f}s')
            except Exception as e:
                print(f'  [ERROR] {e}')

        print()

    def verify_data(self):
        """Verify loaded data"""
        print('=' * 80)
        print('DATA VERIFICATION')
        print('=' * 80)

        # Total records
        self.cur.execute('SELECT COUNT(*) FROM eurostat_comext')
        total = self.cur.fetchone()[0]
        print(f'Total records in database: {total:,}')

        # By partner
        self.cur.execute('''
            SELECT partner, COUNT(*) as count
            FROM eurostat_comext
            WHERE partner IN ('CN', 'HK', 'MO')
            GROUP BY partner
            ORDER BY count DESC
        ''')
        print('\nRecords by China partner:')
        for partner, count in self.cur.fetchall():
            print(f'  {partner}: {count:,}')

        # By year
        self.cur.execute('''
            SELECT year, COUNT(*) as count
            FROM eurostat_comext
            WHERE year IS NOT NULL
            GROUP BY year
            ORDER BY year DESC
            LIMIT 10
        ''')
        print('\nRecords by year (top 10):')
        for year, count in self.cur.fetchall():
            print(f'  {year}: {count:,}')

        # Sample record
        self.cur.execute('SELECT * FROM eurostat_comext LIMIT 1')
        sample = self.cur.fetchone()
        if sample:
            print('\nSample record:')
            print(f'  Reporter: {sample[1]}')
            print(f'  Partner: {sample[2]}')
            print(f'  Product: {sample[5]}')
            print(f'  Period: {sample[13]}')
            print(f'  Value EUR: {sample[15]:,.2f}')

        print()

    def load_all_files(self):
        """Load all filtered China CSV files"""
        print('=' * 80)
        print('EUROSTAT COMEXT BULK DATA LOADER')
        print('=' * 80)
        print(f'Master database: {MASTER_DB}')
        print(f'Filtered data directory: {FILTERED_DIR}')
        print()

        # Create table
        self.create_table()

        # Find all China CSV files
        csv_files = sorted(FILTERED_DIR.glob('full_*_china_all_products.csv'))

        if not csv_files:
            print('[ERROR] No filtered CSV files found!')
            print(f'Expected pattern: full_*_china_all_products.csv')
            print(f'In directory: {FILTERED_DIR}')
            return

        print(f'Found {len(csv_files)} files to load')
        print()

        start_time = time.time()

        # Load each file
        for i, csv_file in enumerate(csv_files, 1):
            print(f'[{i}/{len(csv_files)}] Processing {csv_file.name}')
            self.load_csv_file(csv_file)

        elapsed = time.time() - start_time

        # Create indexes
        self.create_indexes()

        # Verify data
        self.verify_data()

        # Summary
        print('=' * 80)
        print('LOADING COMPLETE')
        print('=' * 80)
        print(f'Files processed: {len(csv_files)}')
        print(f'Records loaded: {self.total_loaded:,}')
        print(f'Records skipped (duplicates): {self.total_skipped:,}')
        print(f'Errors: {self.errors:,}')
        print(f'Time elapsed: {elapsed/60:.1f} minutes')
        print()

    def close(self):
        self.conn.close()

def main():
    loader = EurostatBulkLoader()
    try:
        loader.load_all_files()
    finally:
        loader.close()

if __name__ == '__main__':
    main()
