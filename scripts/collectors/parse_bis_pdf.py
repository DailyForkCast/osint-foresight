#!/usr/bin/env python3
"""
Parse BIS Entity List PDF
Extracts all ~600 entities from official BIS PDF
"""

import pdfplumber
import sqlite3
import re
from datetime import datetime
from pathlib import Path
import json

# Configuration
PDF_PATH = "F:/OSINT_Data/BIS_Entity_List/bis_entity_list.pdf"
MASTER_DB = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_JSON = "F:/OSINT_Data/BIS_Entity_List/parsed_entities.json"

class BISPDFParser:
    def __init__(self):
        self.entities = []
        self.conn = sqlite3.connect(MASTER_DB, timeout=300)
        self.conn.execute('PRAGMA journal_mode=WAL')
        self.cur = self.conn.cursor()

    def parse_pdf(self):
        """Extract entities from PDF"""
        print('=' * 80)
        print('PARSING BIS ENTITY LIST PDF')
        print('=' * 80)
        print(f'PDF: {PDF_PATH}')

        with pdfplumber.open(PDF_PATH) as pdf:
            print(f'Total pages: {len(pdf.pages)}')

            for page_num, page in enumerate(pdf.pages, 1):
                print(f'Processing page {page_num}/{len(pdf.pages)}...', end='\r')

                # Extract tables from page
                tables = page.extract_tables()

                if tables:
                    for table in tables:
                        self._process_table(table)

                # Also extract text for entities not in tables
                text = page.extract_text()
                if text:
                    self._extract_from_text(text)

        print(f'\n[OK] Extracted {len(self.entities)} entities')
        return self.entities

    def _process_table(self, table):
        """Process a table from the PDF"""
        if not table or len(table) < 2:
            return

        # BIS tables typically have headers in first row
        headers = table[0] if table[0] else []

        for row in table[1:]:
            if not row or len(row) < 2:
                continue

            # Try to extract entity info
            entity_name = row[0] if len(row) > 0 else None
            address = row[1] if len(row) > 1 else None
            country = self._extract_country(address) if address else None

            if entity_name and len(entity_name.strip()) > 3:
                entity = {
                    'entity_name': entity_name.strip(),
                    'address': address.strip() if address else None,
                    'country': country,
                    'source': 'BIS Entity List PDF',
                    'extracted_date': datetime.now().isoformat()
                }
                self.entities.append(entity)

    def _extract_from_text(self, text):
        """Extract entities from plain text (fallback)"""
        # Look for entity patterns in text
        # BIS format often has "Entity Name.... Address"
        lines = text.split('\n')

        for line in lines:
            # Skip headers and page numbers
            if re.match(r'^\d+$', line.strip()):
                continue
            if 'Entity' in line and 'Address' in line:
                continue

            # Look for potential entity entries
            # Format: "COMPANY NAME........ City, Country"
            if '........' in line or '\t\t' in line:
                parts = re.split(r'\.{3,}|\t{2,}', line)
                if len(parts) >= 2:
                    entity_name = parts[0].strip()
                    address = parts[1].strip()

                    if len(entity_name) > 3:
                        country = self._extract_country(address)

                        # Check if not duplicate
                        if not any(e['entity_name'] == entity_name for e in self.entities):
                            entity = {
                                'entity_name': entity_name,
                                'address': address,
                                'country': country,
                                'source': 'BIS Entity List PDF',
                                'extracted_date': datetime.now().isoformat()
                            }
                            self.entities.append(entity)

    def _extract_country(self, address):
        """Extract country from address string"""
        if not address:
            return None

        # Common country patterns
        countries = {
            'China': ['China', 'PRC', 'P.R.C.', 'People\'s Republic of China'],
            'Russia': ['Russia', 'Russian Federation'],
            'Iran': ['Iran'],
            'North Korea': ['North Korea', 'DPRK', 'D.P.R.K.'],
            'Hong Kong': ['Hong Kong', 'HK'],
            'Pakistan': ['Pakistan'],
            'UAE': ['UAE', 'United Arab Emirates'],
        }

        for country, patterns in countries.items():
            for pattern in patterns:
                if pattern.lower() in address.lower():
                    return country

        # Try to extract last part of address (often country)
        parts = address.split(',')
        if len(parts) > 1:
            potential_country = parts[-1].strip()
            if len(potential_country) < 30:  # Country names are usually short
                return potential_country

        return None

    def save_to_database(self):
        """Save entities to database"""
        print('=' * 80)
        print('SAVING TO DATABASE')
        print('=' * 80)

        # Get existing entity names to avoid duplicates
        self.cur.execute('SELECT entity_name FROM bis_entity_list')
        existing = {row[0] for row in self.cur.fetchall()}

        new_entities = 0
        chinese_entities = 0

        for entity in self.entities:
            if entity['entity_name'] in existing:
                continue

            self.cur.execute('''
                INSERT INTO bis_entity_list (
                    entity_name, addresses, country,
                    reason_for_listing, date_added,
                    federal_register_notice,
                    collection_date, data_source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entity['entity_name'],
                entity.get('address'),
                entity.get('country'),
                'Export restrictions',  # Generic for parsed entries
                None,  # Date not easily extractable from PDF
                None,  # FR notice not easily extractable
                datetime.now().isoformat(),
                'BIS Entity List PDF (automated extraction)'
            ))

            new_entities += 1

            if entity.get('country') in ['China', 'PRC', 'Hong Kong']:
                chinese_entities += 1

        self.conn.commit()

        print(f'[OK] Inserted {new_entities} new entities')
        print(f'     Chinese entities: {chinese_entities}')

        # Total count
        self.cur.execute('SELECT COUNT(*) FROM bis_entity_list')
        total = self.cur.fetchone()[0]
        print(f'     Total in database: {total}')

        return new_entities

    def save_to_json(self):
        """Save parsed entities to JSON"""
        with open(OUTPUT_JSON, 'w') as f:
            json.dump(self.entities, f, indent=2)
        print(f'[OK] Saved to: {OUTPUT_JSON}')

    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    parser = BISPDFParser()

    try:
        # Parse PDF
        entities = parser.parse_pdf()

        # Save to JSON
        parser.save_to_json()

        # Save to database
        new_count = parser.save_to_database()

        print('=' * 80)
        print('PARSING COMPLETE')
        print('=' * 80)
        print(f'Total entities extracted: {len(entities)}')
        print(f'New entities added to database: {new_count}')

    except Exception as e:
        print(f'[ERROR] {e}')
        import traceback
        traceback.print_exc()

    finally:
        parser.close()

if __name__ == '__main__':
    main()
