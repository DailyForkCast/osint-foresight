#!/usr/bin/env python3
"""
SEC 13F Institutional Holdings Collector
Tracks institutional investment managers with $100M+ assets under management

Key targets:
- Chinese sovereign wealth funds (CIC, SAFE Investment)
- State-owned financial institutions (China Life, Ping An, etc.)
- Strategic investment vehicles

Source: SEC EDGAR Bulk Index
Date: November 1, 2025
"""

import requests
import sqlite3
from datetime import datetime
from pathlib import Path
import time
import re
import json

# Configuration
MASTER_DB = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_DIR = Path("F:/OSINT_Data/SEC_13F")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# SEC EDGAR Bulk Index
SEC_INDEX_BASE = "https://www.sec.gov/Archives/edgar/full-index"
USER_AGENT = "OSINT-Foresight-Research mreardon@example.com"

class SEC13FCollector:
    def __init__(self):
        self.conn = sqlite3.connect(MASTER_DB, timeout=300)
        self.conn.execute('PRAGMA journal_mode=WAL')
        self.cur = self.conn.cursor()
        self.total_filings = 0
        self.chinese_filings = 0
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})

        # Load Chinese entity detection data
        self.chinese_keywords = self._load_chinese_keywords()

    def _load_chinese_keywords(self):
        """Load Chinese entity identifiers from project data"""
        try:
            prc_file = Path("C:/Projects/OSINT-Foresight/data/prc_identifiers.json")
            if prc_file.exists():
                with open(prc_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    keywords = set()
                    for entity in data.get('company_names', []):
                        keywords.add(entity.upper())
                    return keywords
        except:
            pass

        # Fallback to known Chinese institutional investors
        return {
            'CHINA', 'CHINESE', 'SINO', 'HONG KONG', 'SHANGHAI', 'BEIJING', 'SHENZHEN',
            'CHINA INVESTMENT CORPORATION', 'CIC',
            'SAFE INVESTMENT', 'STATE ADMINISTRATION OF FOREIGN EXCHANGE',
            'CHINA LIFE', 'PING AN', 'CHINA CONSTRUCTION BANK', 'INDUSTRIAL AND COMMERCIAL BANK OF CHINA', 'ICBC',
            'BANK OF CHINA', 'AGRICULTURAL BANK OF CHINA',
            'CHINA MERCHANTS', 'CITIC', 'CHINA INTERNATIONAL CAPITAL',
            'ALIBABA', 'TENCENT', 'BAIDU', 'HUAWEI', 'ZTE',
            'CHINA NATIONAL PETROLEUM', 'SINOPEC', 'PETROCHINA',
            'CAYMAN',  # Many Chinese companies use Cayman structure
        }

    def create_table(self):
        """Create SEC 13F table"""
        print('=' * 80)
        print('CREATING SEC 13F TABLE')
        print('=' * 80)

        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS sec_13f_filings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- Filing information
                accession_number TEXT UNIQUE NOT NULL,
                form_type TEXT,  -- 13F-HR, 13F-HR/A, 13F-NT (Notice), 13F-NT/A
                filing_date TEXT,
                period_of_report TEXT,

                -- Filer (institutional manager) information
                manager_name TEXT,
                manager_cik TEXT,
                manager_address TEXT,

                -- Holdings summary
                total_value REAL,  -- Total value of holdings (thousands USD)
                number_of_holdings INTEGER,

                -- URLs
                filing_url TEXT,
                html_url TEXT,

                -- Detection
                is_chinese BOOLEAN DEFAULT 0,
                detection_method TEXT,
                confidence_score REAL,

                -- Metadata
                created_at TEXT,
                data_source TEXT DEFAULT 'SEC EDGAR Bulk Index',

                UNIQUE(accession_number)
            )
        ''')

        # Also create holdings detail table (for Phase 2 - parsing individual filings)
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS sec_13f_holdings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                accession_number TEXT NOT NULL,

                -- Security information
                issuer_name TEXT,
                cusip TEXT,
                security_class TEXT,

                -- Holding details
                shares_or_principal_amount INTEGER,
                value REAL,  -- Thousands USD
                investment_discretion TEXT,  -- SOLE, SHARED, OTHER
                voting_authority_sole INTEGER,
                voting_authority_shared INTEGER,
                voting_authority_none INTEGER,

                FOREIGN KEY (accession_number) REFERENCES sec_13f_filings(accession_number)
            )
        ''')

        self.conn.commit()
        print('[OK] Tables created or already exist')

    def download_quarter_index(self, year, quarter):
        """Download SEC filing index for a specific quarter"""
        url = f"{SEC_INDEX_BASE}/{year}/QTR{quarter}/master.idx"

        print(f'\n[INFO] Downloading {year} Q{quarter} index...')

        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()

            lines = response.text.split('\n')
            data_lines = []
            for i, line in enumerate(lines):
                if i > 10 and '|' in line:
                    data_lines.append(line)

            print(f'[OK] Downloaded {len(data_lines)} filings')
            return data_lines

        except Exception as e:
            print(f'[ERROR] Failed to download: {e}')
            return []

    def parse_index_line(self, line):
        """Parse a line from SEC master index"""
        try:
            parts = line.split('|')
            if len(parts) < 5:
                return None

            cik, company_name, form_type, date_filed, filename = parts[:5]

            # Filter for 13F forms
            # Form types: "13F-HR", "13F-HR/A", "13F-NT", "13F-NT/A"
            form_type_clean = form_type.strip().upper()
            if '13F' not in form_type_clean:
                return None

            # Build accession number from filename
            # filename format: edgar/data/CIK/ACCESSION.txt
            acc_match = re.search(r'/(\d{10}-\d{2}-\d{6})\.txt', filename)
            accession = acc_match.group(1) if acc_match else None

            if not accession:
                return None

            return {
                'cik': cik.strip(),
                'manager_name': company_name.strip(),
                'form_type': form_type.strip(),
                'filing_date': date_filed.strip(),
                'accession_number': accession,
                'filename': filename.strip(),
                'document_url': f"https://www.sec.gov/Archives/{filename.strip()}"
            }

        except Exception as e:
            return None

    def detect_chinese_manager(self, manager_name):
        """Detect if institutional manager is Chinese"""
        if not manager_name:
            return False, 0.0, None

        name_upper = manager_name.upper()

        # Check against known Chinese keywords
        for keyword in self.chinese_keywords:
            if keyword in name_upper:
                return True, 0.90, f'Keyword match: {keyword}'

        # Additional heuristics
        chinese_indicators = [
            ('BEIJING', 0.90),
            ('SHANGHAI', 0.90),
            ('SHENZHEN', 0.90),
            ('HONG KONG', 0.85),
            ('CAYMAN', 0.60),  # Many Chinese funds use Cayman structure
            ('LIMITED HK', 0.80),
            ('PRC', 0.95),
        ]

        for indicator, confidence in chinese_indicators:
            if indicator in name_upper:
                return True, confidence, f'Location indicator: {indicator}'

        return False, 0.0, None

    def collect_recent_quarters(self, num_quarters=4):
        """Collect filings from recent quarters"""
        print('=' * 80)
        print(f'COLLECTING SEC 13F FILINGS - Last {num_quarters} Quarters')
        print('=' * 80)

        # Calculate quarters to download
        current_date = datetime.now()
        current_year = current_date.year
        current_quarter = (current_date.month - 1) // 3 + 1

        quarters_to_fetch = []
        year = current_year
        quarter = current_quarter

        for _ in range(num_quarters):
            quarters_to_fetch.append((year, quarter))
            quarter -= 1
            if quarter == 0:
                quarter = 4
                year -= 1

        all_filings = []

        for year, quarter in quarters_to_fetch:
            index_lines = self.download_quarter_index(year, quarter)

            # Parse and filter for 13F
            for line in index_lines:
                filing = self.parse_index_line(line)
                if filing:
                    all_filings.append(filing)

            time.sleep(0.2)  # Rate limiting

        print(f'\n[OK] Total 13F filings found: {len(all_filings)}')
        return all_filings

    def load_to_database(self, filings):
        """Load filings into database"""
        print('=' * 80)
        print('LOADING INTO DATABASE')
        print('=' * 80)

        loaded = 0
        skipped = 0
        chinese_detected = 0

        for filing in filings:
            # Detect Chinese manager
            is_chinese, confidence, method = self.detect_chinese_manager(
                filing.get('manager_name')
            )

            if is_chinese:
                chinese_detected += 1

            try:
                self.cur.execute('''
                    INSERT OR IGNORE INTO sec_13f_filings (
                        accession_number, form_type, filing_date,
                        manager_name, manager_cik,
                        filing_url, html_url,
                        is_chinese, detection_method, confidence_score,
                        created_at, data_source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    filing.get('accession_number'),
                    filing.get('form_type'),
                    filing.get('filing_date'),
                    filing.get('manager_name'),
                    filing.get('cik'),
                    f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={filing.get('cik')}&type=13F",
                    filing.get('document_url'),
                    is_chinese,
                    method,
                    confidence,
                    datetime.now().isoformat(),
                    'SEC EDGAR Bulk Index'
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
        print(f'     Chinese institutional managers detected: {chinese_detected}')

        self.chinese_filings = chinese_detected

    def create_indexes(self):
        """Create database indexes"""
        print('=' * 80)
        print('CREATING INDEXES')
        print('=' * 80)

        indexes = [
            ('idx_13f_accession', 'accession_number'),
            ('idx_13f_manager', 'manager_name'),
            ('idx_13f_date', 'filing_date'),
            ('idx_13f_chinese', 'is_chinese'),
            ('idx_13f_form', 'form_type'),
        ]

        for idx_name, column in indexes:
            try:
                self.cur.execute(f'''
                    CREATE INDEX IF NOT EXISTS {idx_name}
                    ON sec_13f_filings({column})
                ''')
                print(f'  [OK] {idx_name}')
            except Exception as e:
                print(f'  [SKIP] {idx_name}: {e}')

        self.conn.commit()

    def print_report(self):
        """Print collection report"""
        print('=' * 80)
        print('SEC 13F - COLLECTION REPORT')
        print('=' * 80)

        # Total filings
        self.cur.execute('SELECT COUNT(*) FROM sec_13f_filings')
        total = self.cur.fetchone()[0]
        print(f'\nTotal filings in database: {total}')

        # Form type breakdown
        print('\nForm types:')
        self.cur.execute('''
            SELECT form_type, COUNT(*) as count
            FROM sec_13f_filings
            GROUP BY form_type
            ORDER BY count DESC
        ''')
        for row in self.cur.fetchall():
            print(f'  {row[0]}: {row[1]}')

        # Chinese managers
        print('\nChinese institutional managers:')
        self.cur.execute('''
            SELECT COUNT(*) FROM sec_13f_filings
            WHERE is_chinese = 1
        ''')
        chinese_count = self.cur.fetchone()[0]
        print(f'  Total: {chinese_count}')

        # Sample Chinese managers
        if chinese_count > 0:
            print('\nSample Chinese institutional managers:')
            self.cur.execute('''
                SELECT DISTINCT manager_name, detection_method
                FROM sec_13f_filings
                WHERE is_chinese = 1
                ORDER BY manager_name
                LIMIT 20
            ''')
            for row in self.cur.fetchall():
                manager = row[0][:60] + '...' if len(row[0]) > 60 else row[0]
                print(f'  {manager}')
                print(f'    Detection: {row[1]}')

    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    collector = SEC13FCollector()

    try:
        # Create table
        collector.create_table()

        # Collect recent quarters (default: last 4 quarters = 1 year)
        filings = collector.collect_recent_quarters(num_quarters=4)

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
        print(f'Chinese institutional managers detected: {collector.chinese_filings}')

        print('\n[NOTE] Collection Strategy:')
        print('  - Downloaded SEC quarterly master index files')
        print('  - Filtered for 13F-HR and 13F-NT forms')
        print('  - Chinese entity detection based on manager name patterns')
        print('\n[NEXT PHASE] Parse individual 13F-HR filings to extract:')
        print('  - Specific holdings (stocks owned)')
        print('  - Investment amounts and voting rights')
        print('  - Strategic vs. passive positions')

    except Exception as e:
        print(f'[ERROR] Collection failed: {e}')
        import traceback
        traceback.print_exc()

    finally:
        collector.close()

if __name__ == '__main__':
    main()
