#!/usr/bin/env python3
"""
SEC 13D/13G Filings Collector
Tracks >5% ownership changes in US-listed companies
Identifies Chinese strategic stakes, takeover attempts, activist positions

Forms:
- 13D: Must file within 10 days of crossing 5% (activist intent)
- 13G: Passive investors (institutional, less than 20%)

Source: SEC EDGAR
Date: November 1, 2025
"""

import requests
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import json
import time
import re

# Configuration
MASTER_DB = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_DIR = Path("F:/OSINT_Data/SEC_13D_13G")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# SEC EDGAR API
SEC_EDGAR_BASE = "https://www.sec.gov/cgi-bin/browse-edgar"
USER_AGENT = "OSINT-Foresight-Research contact@example.com"  # SEC requires user agent

class SEC13DGCollector:
    def __init__(self):
        self.conn = sqlite3.connect(MASTER_DB, timeout=300)
        self.conn.execute('PRAGMA journal_mode=WAL')
        self.cur = self.conn.cursor()
        self.total_filings = 0
        self.chinese_filings = 0
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})

    def create_table(self):
        """Create SEC 13D/13G table"""
        print('=' * 80)
        print('CREATING SEC 13D/13G TABLE')
        print('=' * 80)

        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS sec_13d_13g_filings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- Filing information
                accession_number TEXT UNIQUE NOT NULL,
                form_type TEXT,  -- SC 13D, SC 13D/A, SC 13G, SC 13G/A
                filing_date TEXT,
                acceptance_date TEXT,

                -- Filer (beneficial owner) information
                filer_name TEXT,
                filer_cik TEXT,
                filer_address TEXT,
                filer_country TEXT,

                -- Subject company information
                company_name TEXT,
                company_cik TEXT,
                company_ticker TEXT,

                -- Ownership details
                shares_owned INTEGER,
                percent_owned REAL,

                -- Investment purpose
                purpose TEXT,  -- From Item 4 of 13D
                activist_intent BOOLEAN,  -- True for 13D vs. 13G

                -- URLs
                filing_url TEXT,
                html_url TEXT,

                -- Detection
                is_chinese BOOLEAN DEFAULT 0,
                detection_method TEXT,
                confidence_score REAL,

                -- Metadata
                created_at TEXT,
                data_source TEXT DEFAULT 'SEC EDGAR',

                UNIQUE(accession_number)
            )
        ''')
        self.conn.commit()
        print('[OK] Table created or already exists')

    def search_recent_filings(self, days_back=90):
        """Search for recent 13D/13G filings"""
        print('=' * 80)
        print(f'SEARCHING RECENT 13D/13G FILINGS (Last {days_back} days)')
        print('=' * 80)

        form_types = ['SC 13D', 'SC 13G']
        all_filings = []

        for form_type in form_types:
            print(f'\n[INFO] Searching {form_type} filings...')

            # SEC EDGAR search
            params = {
                'action': 'getcompany',
                'type': form_type,
                'dateb': '',  # End date (empty = today)
                'owner': 'include',
                'count': '100',  # Max per page
                'output': 'atom'  # XML format
            }

            try:
                response = self.session.get(SEC_EDGAR_BASE, params=params)
                response.raise_for_status()

                # Parse ATOM feed (simplified - full XML parsing would be better)
                filings = self._parse_atom_feed(response.text, form_type)

                print(f'[OK] Found {len(filings)} {form_type} filings')
                all_filings.extend(filings)

                time.sleep(0.1)  # Rate limiting

            except Exception as e:
                print(f'[ERROR] Search failed for {form_type}: {e}')

        return all_filings

    def _parse_atom_feed(self, atom_xml, form_type):
        """Parse ATOM XML feed (simplified)"""
        filings = []

        # Regex to extract key info (quick and dirty)
        entries = re.findall(r'<entry>.*?</entry>', atom_xml, re.DOTALL)

        for entry in entries:
            try:
                filing = {
                    'form_type': form_type,
                    'accession_number': self._extract_tag(entry, 'accession-number'),
                    'filing_date': self._extract_tag(entry, 'filing-date'),
                    'company_name': self._extract_tag(entry, 'company-name'),
                    'company_cik': self._extract_tag(entry, 'cik'),
                    'filer_name': self._extract_tag(entry, 'company-name'),  # Will update with actual filer
                }

                # Build filing URL
                acc_num = filing['accession_number'].replace('-', '')
                filing['filing_url'] = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={filing['company_cik']}&type={form_type}&dateb=&owner=include&count=100"

                filings.append(filing)

            except Exception as e:
                continue

        return filings

    def _extract_tag(self, xml, tag):
        """Extract tag content from XML"""
        match = re.search(f'<{tag}>(.*?)</{tag}>', xml)
        return match.group(1) if match else None

    def detect_chinese_filer(self, filer_name, filer_address=None):
        """Detect if filer is Chinese"""
        if not filer_name:
            return False, 0.0

        filer_upper = filer_name.upper()

        # High confidence indicators
        chinese_companies = [
            'CHINA', 'CHINESE', 'SINO', 'HONG KONG',
            'ALIBABA', 'TENCENT', 'BAIDU', 'HUAWEI',
            'CHINA INVESTMENT CORPORATION', 'CIC',
            'SAFE INVESTMENT', 'STATE ADMINISTRATION OF FOREIGN EXCHANGE',
        ]

        for keyword in chinese_companies:
            if keyword in filer_upper:
                return True, 0.90

        # Address-based detection
        if filer_address:
            addr_upper = filer_address.upper()
            if any(city in addr_upper for city in ['BEIJING', 'SHANGHAI', 'SHENZHEN', 'HONG KONG']):
                return True, 0.85

        return False, 0.0

    def load_to_database(self, filings):
        """Load filings into database"""
        print('=' * 80)
        print('LOADING INTO DATABASE')
        print('=' * 80)

        loaded = 0
        skipped = 0

        for filing in filings:
            # Detect Chinese filer
            is_chinese, confidence = self.detect_chinese_filer(
                filing.get('filer_name'),
                filing.get('filer_address')
            )

            if is_chinese:
                self.chinese_filings += 1

            try:
                self.cur.execute('''
                    INSERT OR IGNORE INTO sec_13d_13g_filings (
                        accession_number, form_type, filing_date,
                        filer_name, filer_cik, filer_address, filer_country,
                        company_name, company_cik, company_ticker,
                        filing_url, html_url,
                        is_chinese, detection_method, confidence_score,
                        activist_intent,
                        created_at, data_source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    filing.get('accession_number'),
                    filing.get('form_type'),
                    filing.get('filing_date'),
                    filing.get('filer_name'),
                    filing.get('filer_cik'),
                    filing.get('filer_address'),
                    filing.get('filer_country'),
                    filing.get('company_name'),
                    filing.get('company_cik'),
                    filing.get('company_ticker'),
                    filing.get('filing_url'),
                    filing.get('html_url'),
                    is_chinese,
                    'Name and address pattern matching',
                    confidence,
                    filing.get('form_type') == 'SC 13D',  # 13D = activist
                    datetime.now().isoformat(),
                    'SEC EDGAR'
                ))

                if self.cur.rowcount > 0:
                    loaded += 1
                else:
                    skipped += 1

            except Exception as e:
                print(f'[ERROR] Failed to insert filing: {e}')
                skipped += 1

        self.conn.commit()

        print(f'[OK] Loaded {loaded} filings')
        print(f'     Skipped {skipped} duplicates')
        print(f'     Chinese filings: {self.chinese_filings}')

    def create_indexes(self):
        """Create database indexes"""
        print('=' * 80)
        print('CREATING INDEXES')
        print('=' * 80)

        indexes = [
            ('idx_13dg_accession', 'accession_number'),
            ('idx_13dg_filer', 'filer_name'),
            ('idx_13dg_company', 'company_name'),
            ('idx_13dg_date', 'filing_date'),
            ('idx_13dg_chinese', 'is_chinese'),
        ]

        for idx_name, column in indexes:
            print(f'Creating {idx_name}...')
            self.cur.execute(f'''
                CREATE INDEX IF NOT EXISTS {idx_name}
                ON sec_13d_13g_filings({column})
            ''')
            print(f'  [OK] Created')

        self.conn.commit()

    def print_report(self):
        """Print collection report"""
        print('=' * 80)
        print('SEC 13D/13G - COLLECTION REPORT')
        print('=' * 80)

        # Total filings
        self.cur.execute('SELECT COUNT(*) FROM sec_13d_13g_filings')
        total = self.cur.fetchone()[0]
        print(f'Total filings in database: {total}')

        # Form type breakdown
        print('\nForm types:')
        self.cur.execute('''
            SELECT form_type, COUNT(*) as count
            FROM sec_13d_13g_filings
            GROUP BY form_type
            ORDER BY count DESC
        ''')
        for row in self.cur.fetchall():
            print(f'  {row[0]}: {row[1]}')

        # Chinese filings
        print('\nChinese filings:')
        self.cur.execute('''
            SELECT COUNT(*) FROM sec_13d_13g_filings
            WHERE is_chinese = 1
        ''')
        chinese_count = self.cur.fetchone()[0]
        print(f'  Total: {chinese_count}')

        # Sample Chinese filings
        if chinese_count > 0:
            print('\nSample Chinese filings:')
            self.cur.execute('''
                SELECT filer_name, company_name, form_type, filing_date
                FROM sec_13d_13g_filings
                WHERE is_chinese = 1
                ORDER BY filing_date DESC
                LIMIT 10
            ''')
            for row in self.cur.fetchall():
                filer = row[0][:40] + '...' if len(row[0]) > 40 else row[0]
                company = row[1][:30] + '...' if len(row[1]) > 30 else row[1]
                print(f'  {filer} → {company} ({row[2]}, {row[3]})')

    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    collector = SEC13DGCollector()

    try:
        # Create table
        collector.create_table()

        # Search recent filings (last 90 days)
        filings = collector.search_recent_filings(days_back=90)

        if filings:
            # Load to database
            collector.load_to_database(filings)

            # Create indexes
            collector.create_indexes()

            # Print report
            collector.print_report()

        print('=' * 80)
        print('COLLECTION COMPLETE')
        print('=' * 80)
        print(f'Total filings collected: {len(filings)}')
        print(f'Chinese filings detected: {collector.chinese_filings}')
        print('\n[NOTE] This is a starter collection of recent filings')
        print('[TODO] For full historical data, need to:')
        print('       1. Download full 13D/13G filing index from SEC')
        print('       2. Parse individual filing documents for ownership %')
        print('       3. Extract Item 4 (Purpose) from 13D filings')

    except Exception as e:
        print(f'[ERROR] Collection failed: {e}')
        import traceback
        traceback.print_exc()

    finally:
        collector.close()

if __name__ == '__main__':
    main()
