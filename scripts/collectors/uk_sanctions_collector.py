#!/usr/bin/env python3
"""
UK Financial Sanctions List Collector
Collects UK Office of Financial Sanctions Implementation (OFSI) sanctions
~2,000 sanctioned entities (post-Brexit independent regime)

Source: https://www.gov.uk/government/publications/financial-sanctions-consolidated-list-of-targets
Date: November 1, 2025
"""

import requests
import sqlite3
import csv
from datetime import datetime
from pathlib import Path
import json
import io

# Configuration
MASTER_DB = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_DIR = Path("F:/OSINT_Data/UK_Sanctions")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# UK OFSI Consolidated List (CSV format)
UK_SANCTIONS_CSV_URL = "https://assets.publishing.service.gov.uk/media/672390cf0a5ec6e62fbe8dac/ConList.csv"

class UKSanctionsCollector:
    def __init__(self):
        self.conn = sqlite3.connect(MASTER_DB, timeout=300)
        self.conn.execute('PRAGMA journal_mode=WAL')
        self.cur = self.conn.cursor()
        self.total_entities = 0
        self.chinese_entities = 0

    def create_table(self):
        """Create UK sanctions table"""
        print('=' * 80)
        print('CREATING UK SANCTIONS TABLE')
        print('=' * 80)

        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS uk_sanctions_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- Entity information
                name TEXT NOT NULL,
                name_6 TEXT,  -- Additional name field
                entity_type TEXT,  -- Individual/Entity
                aliases TEXT,

                -- Birth/incorporation
                date_of_birth TEXT,
                town_of_birth TEXT,
                country_of_birth TEXT,

                -- Address
                address_1 TEXT,
                address_2 TEXT,
                address_3 TEXT,
                address_4 TEXT,
                address_5 TEXT,
                address_6 TEXT,
                post_zip_code TEXT,
                country TEXT,

                -- Identification
                passport_details TEXT,
                national_id_number TEXT,
                position TEXT,
                other_information TEXT,

                -- Sanctions details
                group_id TEXT,
                regime TEXT,  -- Russia, China, Iran, etc.
                sanctions_type TEXT,  -- Asset freeze, travel ban, etc.
                date_designated TEXT,

                -- UK specific
                uk_sanctions_list_date_designated TEXT,
                last_updated TEXT,

                -- Metadata
                created_at TEXT,
                data_source TEXT DEFAULT 'UK OFSI Consolidated List',

                UNIQUE(name, date_of_birth)
            )
        ''')
        self.conn.commit()
        print('[OK] Table created or already exists')

    def download_csv(self):
        """Download UK sanctions CSV file"""
        print('=' * 80)
        print('DOWNLOADING UK SANCTIONS LIST')
        print('=' * 80)
        print(f'URL: {UK_SANCTIONS_CSV_URL}')

        csv_path = OUTPUT_DIR / 'uk_consolidated_list.csv'

        try:
            print('[INFO] Downloading CSV file...')
            response = requests.get(UK_SANCTIONS_CSV_URL, timeout=60)
            response.raise_for_status()

            with open(csv_path, 'wb') as f:
                f.write(response.content)

            print(f'[OK] Downloaded: {csv_path}')
            print(f'     Size: {len(response.content) / (1024*1024):.2f} MB')

            return csv_path

        except Exception as e:
            print(f'[ERROR] Download failed: {e}')
            return None

    def parse_csv(self, csv_path):
        """Parse UK sanctions CSV"""
        print('=' * 80)
        print('PARSING CSV')
        print('=' * 80)

        entities = []

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                # UK CSV uses ';' as delimiter
                reader = csv.DictReader(f, delimiter=',')

                for row in reader:
                    entity = {
                        'name': row.get('Name 6', '').strip() or row.get('Name 1', '').strip(),
                        'name_6': row.get('Name 6', '').strip(),
                        'entity_type': row.get('Group Type', '').strip(),

                        # Aliases - combine multiple name fields
                        'aliases': '; '.join(filter(None, [
                            row.get('Name 1', '').strip(),
                            row.get('Name 2', '').strip(),
                            row.get('Name 3', '').strip(),
                            row.get('Name 4', '').strip(),
                            row.get('Name 5', '').strip(),
                        ])),

                        # Birth info
                        'date_of_birth': row.get('DOB', '').strip(),
                        'town_of_birth': row.get('Town of Birth', '').strip(),
                        'country_of_birth': row.get('Country of Birth', '').strip(),

                        # Address
                        'address_1': row.get('Address 1', '').strip(),
                        'address_2': row.get('Address 2', '').strip(),
                        'address_3': row.get('Address 3', '').strip(),
                        'address_4': row.get('Address 4', '').strip(),
                        'address_5': row.get('Address 5', '').strip(),
                        'address_6': row.get('Address 6', '').strip(),
                        'post_zip_code': row.get('Post/Zip Code', '').strip(),
                        'country': row.get('Country', '').strip(),

                        # Identification
                        'passport_details': row.get('Passport Details', '').strip(),
                        'national_id_number': row.get('National Identification Number', '').strip(),
                        'position': row.get('Position', '').strip(),
                        'other_information': row.get('Other Information', '').strip(),

                        # Sanctions details
                        'group_id': row.get('Group ID', '').strip(),
                        'regime': row.get('Regime', '').strip(),
                        'date_designated': row.get('Date Designated', '').strip(),
                        'uk_sanctions_list_date_designated': row.get('UK_Sanctions List Date Designated', '').strip(),
                        'last_updated': row.get('Last Updated', '').strip(),
                    }

                    # Detect Chinese entities
                    if entity.get('country'):
                        if any(c in entity['country'].upper() for c in ['CHINA', 'CHN', 'PRC', 'HONG KONG', 'CHINESE']):
                            self.chinese_entities += 1

                    entities.append(entity)
                    self.total_entities += 1

            print(f'[OK] Parsed {len(entities)} entities')

        except Exception as e:
            print(f'[ERROR] CSV parsing failed: {e}')
            import traceback
            traceback.print_exc()

        return entities

    def load_to_database(self, entities):
        """Load entities into database"""
        print('=' * 80)
        print('LOADING INTO DATABASE')
        print('=' * 80)

        loaded = 0
        skipped = 0

        for entity in entities:
            try:
                self.cur.execute('''
                    INSERT OR IGNORE INTO uk_sanctions_list (
                        name, name_6, entity_type, aliases,
                        date_of_birth, town_of_birth, country_of_birth,
                        address_1, address_2, address_3, address_4, address_5, address_6,
                        post_zip_code, country,
                        passport_details, national_id_number, position, other_information,
                        group_id, regime, date_designated,
                        uk_sanctions_list_date_designated, last_updated,
                        created_at, data_source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entity.get('name'),
                    entity.get('name_6'),
                    entity.get('entity_type'),
                    entity.get('aliases'),
                    entity.get('date_of_birth'),
                    entity.get('town_of_birth'),
                    entity.get('country_of_birth'),
                    entity.get('address_1'),
                    entity.get('address_2'),
                    entity.get('address_3'),
                    entity.get('address_4'),
                    entity.get('address_5'),
                    entity.get('address_6'),
                    entity.get('post_zip_code'),
                    entity.get('country'),
                    entity.get('passport_details'),
                    entity.get('national_id_number'),
                    entity.get('position'),
                    entity.get('other_information'),
                    entity.get('group_id'),
                    entity.get('regime'),
                    entity.get('date_designated'),
                    entity.get('uk_sanctions_list_date_designated'),
                    entity.get('last_updated'),
                    datetime.now().isoformat(),
                    'UK OFSI Consolidated List'
                ))

                if self.cur.rowcount > 0:
                    loaded += 1
                else:
                    skipped += 1

            except Exception as e:
                print(f'[ERROR] Failed to insert entity: {e}')
                skipped += 1

        self.conn.commit()

        print(f'[OK] Loaded {loaded} entities')
        print(f'     Skipped {skipped} duplicates')
        print(f'     Chinese entities: {self.chinese_entities}')

    def create_indexes(self):
        """Create database indexes"""
        print('=' * 80)
        print('CREATING INDEXES')
        print('=' * 80)

        indexes = [
            ('idx_uk_sanctions_name', 'name'),
            ('idx_uk_sanctions_country', 'country'),
            ('idx_uk_sanctions_regime', 'regime'),
            ('idx_uk_sanctions_date', 'date_designated'),
        ]

        for idx_name, column in indexes:
            print(f'Creating {idx_name}...')
            self.cur.execute(f'''
                CREATE INDEX IF NOT EXISTS {idx_name}
                ON uk_sanctions_list({column})
            ''')
            print(f'  [OK] Created')

        self.conn.commit()

    def print_report(self):
        """Print collection report"""
        print('=' * 80)
        print('UK SANCTIONS LIST - COLLECTION REPORT')
        print('=' * 80)

        # Total entities
        self.cur.execute('SELECT COUNT(*) FROM uk_sanctions_list')
        total = self.cur.fetchone()[0]
        print(f'Total entities in database: {total}')

        # Top countries
        print('\nTop countries:')
        self.cur.execute('''
            SELECT country, COUNT(*) as count
            FROM uk_sanctions_list
            WHERE country IS NOT NULL AND country != ''
            GROUP BY country
            ORDER BY count DESC
            LIMIT 10
        ''')
        for row in self.cur.fetchall():
            print(f'  {row[0]}: {row[1]}')

        # Sanctions regimes
        print('\nTop sanctions regimes:')
        self.cur.execute('''
            SELECT regime, COUNT(*) as count
            FROM uk_sanctions_list
            WHERE regime IS NOT NULL AND regime != ''
            GROUP BY regime
            ORDER BY count DESC
            LIMIT 10
        ''')
        for row in self.cur.fetchall():
            print(f'  {row[0]}: {row[1]}')

        # Entity types
        print('\nEntity types:')
        self.cur.execute('''
            SELECT entity_type, COUNT(*) as count
            FROM uk_sanctions_list
            WHERE entity_type IS NOT NULL AND entity_type != ''
            GROUP BY entity_type
            ORDER BY count DESC
        ''')
        for row in self.cur.fetchall():
            print(f'  {row[0]}: {row[1]}')

        # Sample Chinese entities
        print('\nSample Chinese entities:')
        self.cur.execute('''
            SELECT name, country, regime
            FROM uk_sanctions_list
            WHERE country LIKE '%China%' OR country LIKE '%Hong Kong%' OR country LIKE '%Chinese%'
            LIMIT 10
        ''')
        for row in self.cur.fetchall():
            name = row[0][:50] + '...' if len(row[0]) > 50 else row[0]
            print(f'  {name} ({row[1]}) - {row[2]}')

    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    collector = UKSanctionsCollector()

    try:
        # Create table
        collector.create_table()

        # Download CSV
        csv_path = collector.download_csv()
        if not csv_path:
            print('[ERROR] Cannot proceed without CSV file')
            return

        # Parse CSV
        entities = collector.parse_csv(csv_path)

        # Load to database
        collector.load_to_database(entities)

        # Create indexes
        collector.create_indexes()

        # Print report
        collector.print_report()

        print('=' * 80)
        print('COLLECTION COMPLETE')
        print('=' * 80)
        print(f'Total entities collected: {collector.total_entities}')
        print(f'Chinese entities: {collector.chinese_entities}')

    except Exception as e:
        print(f'[ERROR] Collection failed: {e}')
        import traceback
        traceback.print_exc()

    finally:
        collector.close()

if __name__ == '__main__':
    main()
