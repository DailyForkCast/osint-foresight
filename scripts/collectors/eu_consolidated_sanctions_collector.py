#!/usr/bin/env python3
"""
EU Consolidated Financial Sanctions List Collector
Collects EU financial sanctions from official XML export
~4,000 sanctioned entities (Russian, Chinese, Iranian, North Korean, etc.)

Source: https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/content
Date: November 1, 2025
"""

import requests
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
import json

# Configuration
MASTER_DB = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_DIR = Path("F:/OSINT_Data/EU_Sanctions")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# EU Consolidated Sanctions List XML URL
EU_SANCTIONS_URL = "https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/content"

class EUSanctionsCollector:
    def __init__(self):
        self.conn = sqlite3.connect(MASTER_DB, timeout=300)
        self.conn.execute('PRAGMA journal_mode=WAL')
        self.cur = self.conn.cursor()
        self.total_entities = 0
        self.chinese_entities = 0

    def create_table(self):
        """Create EU sanctions table"""
        print('=' * 80)
        print('CREATING EU CONSOLIDATED SANCTIONS TABLE')
        print('=' * 80)

        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS eu_consolidated_sanctions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- Entity information
                entity_name TEXT NOT NULL,
                entity_type TEXT,  -- person, organization
                aliases TEXT,

                -- Birth/incorporation
                birth_date TEXT,
                birth_place TEXT,
                incorporation_date TEXT,

                -- Address
                addresses TEXT,
                country TEXT,

                -- Identification
                passport_number TEXT,
                national_id TEXT,

                -- Sanctions details
                reason_for_sanctions TEXT,
                legal_basis TEXT,  -- EU regulation number
                sanctions_program TEXT,  -- Russia, China, Iran, etc.
                date_added TEXT,

                -- Metadata
                created_at TEXT,
                data_source TEXT DEFAULT 'EU Consolidated Financial Sanctions List',

                UNIQUE(entity_name, birth_date)
            )
        ''')
        self.conn.commit()
        print('[OK] Table created or already exists')

    def download_xml(self):
        """Download EU sanctions XML file"""
        print('=' * 80)
        print('DOWNLOADING EU CONSOLIDATED SANCTIONS LIST')
        print('=' * 80)
        print(f'URL: {EU_SANCTIONS_URL}')

        xml_path = OUTPUT_DIR / 'eu_consolidated_sanctions.xml'

        try:
            print('[INFO] Downloading XML file...')
            response = requests.get(EU_SANCTIONS_URL, timeout=60, verify=False)
            response.raise_for_status()

            with open(xml_path, 'wb') as f:
                f.write(response.content)

            print(f'[OK] Downloaded: {xml_path}')
            print(f'     Size: {len(response.content) / (1024*1024):.2f} MB')

            return xml_path

        except Exception as e:
            print(f'[ERROR] Download failed: {e}')
            return None

    def parse_xml(self, xml_path):
        """Parse EU sanctions XML"""
        print('=' * 80)
        print('PARSING XML')
        print('=' * 80)

        entities = []

        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # EU XML uses namespaces
            ns = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}

            # Find all sanctioned entities
            for entity_elem in root.findall('.//sanctionEntity', ns):
                entity = self._extract_entity(entity_elem, ns)
                if entity:
                    entities.append(entity)
                    self.total_entities += 1

            print(f'[OK] Parsed {len(entities)} entities')

        except Exception as e:
            print(f'[ERROR] XML parsing failed: {e}')
            import traceback
            traceback.print_exc()

        return entities

    def _extract_entity(self, elem, ns):
        """Extract entity information from XML element"""
        entity = {}

        # Helper function to get text
        def get_text(path, default=None):
            found = elem.find(path, ns)
            return found.text if found is not None and found.text else default

        # Helper function to get all text for multiple elements
        def get_all_text(path):
            elements = elem.findall(path, ns)
            return [e.text for e in elements if e.text] if elements else []

        # Basic info
        entity['entity_name'] = get_text('.//nameAlias/wholeName') or get_text('.//nameAlias/firstName')
        if not entity['entity_name']:
            return None  # Skip if no name

        entity['entity_type'] = get_text('.//subjectType')  # person/enterprise/entity
        entity['aliases'] = '; '.join(get_all_text('.//nameAlias/wholeName'))

        # Birth/incorporation
        entity['birth_date'] = get_text('.//birthdate/birthdate')
        entity['birth_place'] = get_text('.//birthdate/city')
        entity['incorporation_date'] = get_text('.//incorporationDate')

        # Address
        addresses = []
        for addr in elem.findall('.//address', ns):
            addr_parts = []
            if addr.find('.//street', ns) is not None:
                addr_parts.append(addr.find('.//street', ns).text)
            if addr.find('.//city', ns) is not None:
                addr_parts.append(addr.find('.//city', ns).text)
            if addr.find('.//zipCode', ns) is not None:
                addr_parts.append(addr.find('.//zipCode', ns).text)
            if addr.find('.//country', ns) is not None:
                addr_parts.append(addr.find('.//country', ns).text)
                entity['country'] = addr.find('.//country', ns).text
            if addr_parts:
                addresses.append(', '.join(filter(None, addr_parts)))

        entity['addresses'] = '; '.join(addresses) if addresses else None

        # Identification
        entity['passport_number'] = get_text('.//identification/number')
        entity['national_id'] = get_text('.//identification/number')

        # Sanctions details
        entity['reason_for_sanctions'] = get_text('.//remark')
        entity['legal_basis'] = get_text('.//regulation')
        entity['sanctions_program'] = get_text('.//program')
        entity['date_added'] = get_text('.//publicationDate')

        # Detect Chinese entities
        if entity.get('country'):
            if any(c in entity['country'].upper() for c in ['CHINA', 'CHN', 'PRC', 'HONG KONG']):
                self.chinese_entities += 1

        return entity

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
                    INSERT OR IGNORE INTO eu_consolidated_sanctions (
                        entity_name, entity_type, aliases,
                        birth_date, birth_place, incorporation_date,
                        addresses, country,
                        passport_number, national_id,
                        reason_for_sanctions, legal_basis,
                        sanctions_program, date_added,
                        created_at, data_source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entity.get('entity_name'),
                    entity.get('entity_type'),
                    entity.get('aliases'),
                    entity.get('birth_date'),
                    entity.get('birth_place'),
                    entity.get('incorporation_date'),
                    entity.get('addresses'),
                    entity.get('country'),
                    entity.get('passport_number'),
                    entity.get('national_id'),
                    entity.get('reason_for_sanctions'),
                    entity.get('legal_basis'),
                    entity.get('sanctions_program'),
                    entity.get('date_added'),
                    datetime.now().isoformat(),
                    'EU Consolidated Financial Sanctions List'
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
            ('idx_eu_sanctions_name', 'entity_name'),
            ('idx_eu_sanctions_country', 'country'),
            ('idx_eu_sanctions_program', 'sanctions_program'),
            ('idx_eu_sanctions_date', 'date_added'),
        ]

        for idx_name, column in indexes:
            print(f'Creating {idx_name}...')
            self.cur.execute(f'''
                CREATE INDEX IF NOT EXISTS {idx_name}
                ON eu_consolidated_sanctions({column})
            ''')
            print(f'  [OK] Created')

        self.conn.commit()

    def print_report(self):
        """Print collection report"""
        print('=' * 80)
        print('EU CONSOLIDATED SANCTIONS - COLLECTION REPORT')
        print('=' * 80)

        # Total entities
        self.cur.execute('SELECT COUNT(*) FROM eu_consolidated_sanctions')
        total = self.cur.fetchone()[0]
        print(f'Total entities in database: {total}')

        # Top countries
        print('\nTop countries:')
        self.cur.execute('''
            SELECT country, COUNT(*) as count
            FROM eu_consolidated_sanctions
            WHERE country IS NOT NULL
            GROUP BY country
            ORDER BY count DESC
            LIMIT 10
        ''')
        for row in self.cur.fetchall():
            print(f'  {row[0]}: {row[1]}')

        # Sanctions programs
        print('\nTop sanctions programs:')
        self.cur.execute('''
            SELECT sanctions_program, COUNT(*) as count
            FROM eu_consolidated_sanctions
            WHERE sanctions_program IS NOT NULL
            GROUP BY sanctions_program
            ORDER BY count DESC
            LIMIT 10
        ''')
        for row in self.cur.fetchall():
            print(f'  {row[0]}: {row[1]}')

        # Sample Chinese entities
        print('\nSample Chinese entities:')
        self.cur.execute('''
            SELECT entity_name, country
            FROM eu_consolidated_sanctions
            WHERE country LIKE '%China%' OR country LIKE '%Hong Kong%'
            LIMIT 10
        ''')
        for row in self.cur.fetchall():
            name = row[0][:50] + '...' if len(row[0]) > 50 else row[0]
            print(f'  {name} ({row[1]})')

    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    collector = EUSanctionsCollector()

    try:
        # Create table
        collector.create_table()

        # Download XML
        xml_path = collector.download_xml()
        if not xml_path:
            print('[ERROR] Cannot proceed without XML file')
            return

        # Parse XML
        entities = collector.parse_xml(xml_path)

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
