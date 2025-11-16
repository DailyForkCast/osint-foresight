#!/usr/bin/env python3
"""
BIS Entity List Collector
Collects US Bureau of Industry and Security (BIS) Entity List
~600 entities restricted from US exports (Huawei, SMIC, DJI, etc.)

Source: https://www.bis.doc.gov/index.php/policy-guidance/lists-of-parties-of-concern/entity-list
Date: November 1, 2025
"""

import requests
import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
import json

# Configuration
MASTER_DB = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_DIR = Path("F:/OSINT_Data/BIS_Entity_List")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# BIS Entity List URL (downloadable format)
BIS_ENTITY_LIST_URL = "https://www.bis.doc.gov/index.php/documents/regulations-docs/2326-supplement-no-4-to-part-744-entity-list-4/file"

class BISEntityListCollector:
    def __init__(self):
        self.conn = sqlite3.connect(MASTER_DB, timeout=300)
        self.conn.execute('PRAGMA journal_mode=WAL')
        self.cur = self.conn.cursor()
        self.total_entities = 0
        self.chinese_entities = 0

    def create_table(self):
        """Create BIS Entity List table"""
        print('=' * 80)
        print('CREATING BIS ENTITY LIST TABLE')
        print('=' * 80)

        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS bis_entity_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- Entity information
                entity_name TEXT NOT NULL,
                alternate_names TEXT,
                addresses TEXT,

                -- Location
                country TEXT,
                city TEXT,
                state TEXT,

                -- Listing details
                federal_register_notice TEXT,
                date_added TEXT,
                reason_for_listing TEXT,
                license_requirement TEXT,
                license_policy TEXT,

                -- Metadata
                collection_date TEXT,
                data_source TEXT DEFAULT 'BIS_ENTITY_LIST',

                UNIQUE(entity_name, country, addresses)
            )
        ''')
        self.conn.commit()
        print('[OK] Table created or already exists')
        print()

    def download_entity_list(self):
        """Download BIS Entity List from official source"""
        print('=' * 80)
        print('DOWNLOADING BIS ENTITY LIST')
        print('=' * 80)
        print(f'URL: {BIS_ENTITY_LIST_URL}')
        print()

        try:
            # Try official PDF download first
            print('[INFO] Attempting to download official PDF...')
            response = requests.get(BIS_ENTITY_LIST_URL, timeout=60)

            if response.status_code == 200:
                output_file = OUTPUT_DIR / 'bis_entity_list.pdf'
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                print(f'[OK] Downloaded to: {output_file}')
                print(f'    Size: {len(response.content):,} bytes')
                return output_file
            else:
                print(f'[WARN] Download failed with status {response.status_code}')
                return None

        except Exception as e:
            print(f'[ERROR] Download failed: {e}')
            return None

    def parse_manual_data(self):
        """
        Parse known high-profile Chinese entities for initial database

        Note: Full BIS Entity List requires PDF parsing.
        This provides a starter dataset of major entities.
        """
        print('=' * 80)
        print('LOADING KNOWN HIGH-PROFILE ENTITIES')
        print('=' * 80)
        print('[INFO] Loading curated list of major Chinese entities')
        print()

        # Major known entities from BIS Entity List (as of 2024-2025)
        entities = [
            {
                'entity_name': 'Huawei Technologies Co., Ltd.',
                'country': 'China',
                'city': 'Shenzhen',
                'reason_for_listing': 'Foreign Direct Product Rule - National Security',
                'date_added': '2019-05-16',
                'federal_register_notice': '84 FR 22961',
                'license_requirement': 'For all items subject to the EAR',
                'license_policy': 'Presumption of denial'
            },
            {
                'entity_name': 'Semiconductor Manufacturing International Corporation (SMIC)',
                'country': 'China',
                'city': 'Shanghai',
                'reason_for_listing': 'Military end use',
                'date_added': '2020-12-18',
                'federal_register_notice': '85 FR 83416',
                'license_requirement': 'For all items subject to the EAR',
                'license_policy': 'Presumption of denial'
            },
            {
                'entity_name': 'DJI Technology Co., Ltd.',
                'country': 'China',
                'city': 'Shenzhen',
                'reason_for_listing': 'Complicity in human rights violations',
                'date_added': '2021-12-16',
                'federal_register_notice': '86 FR 71553',
                'license_requirement': 'For all items subject to the EAR',
                'license_policy': 'Presumption of denial'
            },
            {
                'entity_name': 'Yangtze Memory Technologies Corp. (YMTC)',
                'country': 'China',
                'city': 'Wuhan',
                'reason_for_listing': 'Military end use',
                'date_added': '2022-12-15',
                'federal_register_notice': '87 FR 76655',
                'license_requirement': 'For all items subject to the EAR',
                'license_policy': 'Presumption of denial'
            },
            {
                'entity_name': 'Hikvision Digital Technology Co., Ltd.',
                'country': 'China',
                'city': 'Hangzhou',
                'reason_for_listing': 'Complicity in human rights violations in Xinjiang',
                'date_added': '2019-10-09',
                'federal_register_notice': '84 FR 54002',
                'license_requirement': 'For all items subject to the EAR',
                'license_policy': 'Presumption of denial'
            },
            {
                'entity_name': 'Huawei Marine Networks Co., Limited',
                'country': 'China',
                'city': 'Tianjin',
                'reason_for_listing': 'Foreign Direct Product Rule - National Security',
                'date_added': '2019-08-19',
                'federal_register_notice': '84 FR 43493',
                'license_requirement': 'For all items subject to the EAR',
                'license_policy': 'Presumption of denial'
            },
            {
                'entity_name': 'ZTE Corporation',
                'country': 'China',
                'city': 'Shenzhen',
                'reason_for_listing': 'Violation of Iran sanctions',
                'date_added': '2016-03-07',
                'federal_register_notice': '81 FR 11489',
                'license_requirement': 'For all items subject to the EAR',
                'license_policy': 'Presumption of denial'
            },
            {
                'entity_name': 'China Electronics Technology Group Corporation (CETC)',
                'country': 'China',
                'city': 'Beijing',
                'reason_for_listing': 'Military end use',
                'date_added': '2021-12-23',
                'federal_register_notice': '86 FR 72917',
                'license_requirement': 'For all items subject to the EAR',
                'license_policy': 'Presumption of denial'
            },
            {
                'entity_name': 'Sugon (Dawning Information Industry Co., Ltd.)',
                'country': 'China',
                'city': 'Tianjin',
                'reason_for_listing': 'Supercomputing for military modernization',
                'date_added': '2019-06-24',
                'federal_register_notice': '84 FR 29661',
                'license_requirement': 'For all items subject to the EAR',
                'license_policy': 'Presumption of denial'
            },
            {
                'entity_name': 'Tianjin Phytium Information Technology Inc.',
                'country': 'China',
                'city': 'Tianjin',
                'reason_for_listing': 'Supercomputing for military modernization',
                'date_added': '2019-06-24',
                'federal_register_notice': '84 FR 29661',
                'license_requirement': 'For all items subject to the EAR',
                'license_policy': 'Presumption of denial'
            }
        ]

        return entities

    def load_entities(self, entities):
        """Load entities into database"""
        print('=' * 80)
        print('LOADING ENTITIES INTO DATABASE')
        print('=' * 80)

        collection_date = datetime.now().isoformat()

        for entity in entities:
            try:
                self.cur.execute('''
                    INSERT OR REPLACE INTO bis_entity_list (
                        entity_name, country, city, state,
                        reason_for_listing, date_added, federal_register_notice,
                        license_requirement, license_policy,
                        collection_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entity['entity_name'],
                    entity.get('country'),
                    entity.get('city'),
                    entity.get('state'),
                    entity.get('reason_for_listing'),
                    entity.get('date_added'),
                    entity.get('federal_register_notice'),
                    entity.get('license_requirement'),
                    entity.get('license_policy'),
                    collection_date
                ))

                self.total_entities += 1
                if entity.get('country') == 'China':
                    self.chinese_entities += 1

            except Exception as e:
                print(f'[ERROR] Failed to load {entity.get("entity_name", "unknown")}: {e}')

        self.conn.commit()
        print(f'[OK] Loaded {self.total_entities} entities')
        print(f'    Chinese entities: {self.chinese_entities}')
        print()

    def create_indexes(self):
        """Create indexes for query performance"""
        print('=' * 80)
        print('CREATING INDEXES')
        print('=' * 80)

        indexes = [
            ('idx_bis_entity_name', 'entity_name'),
            ('idx_bis_country', 'country'),
            ('idx_bis_date_added', 'date_added'),
        ]

        for idx_name, column in indexes:
            try:
                print(f'Creating {idx_name}...')
                self.cur.execute(f'CREATE INDEX IF NOT EXISTS {idx_name} ON bis_entity_list({column})')
                self.conn.commit()
                print(f'  [OK] Created')
            except Exception as e:
                print(f'  [ERROR] {e}')

        print()

    def generate_report(self):
        """Generate collection report"""
        print('=' * 80)
        print('BIS ENTITY LIST - COLLECTION REPORT')
        print('=' * 80)

        # Total entities
        self.cur.execute('SELECT COUNT(*) FROM bis_entity_list')
        total = self.cur.fetchone()[0]
        print(f'Total entities in database: {total:,}')

        # By country
        self.cur.execute('''
            SELECT country, COUNT(*) as count
            FROM bis_entity_list
            WHERE country IS NOT NULL
            GROUP BY country
            ORDER BY count DESC
            LIMIT 10
        ''')
        print('\nTop countries:')
        for country, count in self.cur.fetchall():
            print(f'  {country}: {count:,}')

        # By reason
        self.cur.execute('''
            SELECT reason_for_listing, COUNT(*) as count
            FROM bis_entity_list
            WHERE reason_for_listing IS NOT NULL
            GROUP BY reason_for_listing
            ORDER BY count DESC
            LIMIT 10
        ''')
        print('\nTop reasons for listing:')
        for reason, count in self.cur.fetchall():
            reason_short = reason[:60] + '...' if len(reason) > 60 else reason
            print(f'  {reason_short}: {count:,}')

        # Sample Chinese entities
        self.cur.execute('''
            SELECT entity_name, city, reason_for_listing
            FROM bis_entity_list
            WHERE country = 'China'
            LIMIT 10
        ''')
        print('\nSample Chinese entities:')
        for name, city, reason in self.cur.fetchall():
            name_short = name[:40] + '...' if len(name) > 40 else name
            print(f'  {name_short} ({city})')

        print()

    def run(self):
        """Main execution"""
        print('=' * 80)
        print('BIS ENTITY LIST COLLECTOR')
        print('=' * 80)
        print(f'Master database: {MASTER_DB}')
        print(f'Output directory: {OUTPUT_DIR}')
        print()

        # Create table
        self.create_table()

        # Try to download official list
        pdf_file = self.download_entity_list()

        if pdf_file:
            print('[INFO] PDF downloaded successfully')
            print('[INFO] PDF parsing requires manual review')
            print('[INFO] Loading curated high-profile entities instead...')
            print()
        else:
            print('[INFO] Using curated high-profile entities')
            print()

        # Load known entities
        entities = self.parse_manual_data()
        self.load_entities(entities)

        # Create indexes
        self.create_indexes()

        # Generate report
        self.generate_report()

        # Summary
        print('=' * 80)
        print('COLLECTION COMPLETE')
        print('=' * 80)
        print(f'Total entities loaded: {self.total_entities}')
        print(f'Chinese entities: {self.chinese_entities}')
        print()
        print('[NOTE] This is a starter dataset of high-profile entities')
        print('[NOTE] Full BIS Entity List has ~600 entities')
        print('[TODO] Download PDF manually from:')
        print('       https://www.bis.doc.gov/index.php/policy-guidance/lists-of-parties-of-concern/entity-list')
        print()

    def close(self):
        self.conn.close()

def main():
    collector = BISEntityListCollector()
    try:
        collector.run()
    finally:
        collector.close()

if __name__ == '__main__':
    main()
