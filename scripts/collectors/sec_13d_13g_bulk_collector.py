#!/usr/bin/env python3
"""
SEC 13D/13G Filings Collector - Bulk Index Method
Downloads quarterly SEC filing indexes and filters for 13D/13G forms
Tracks >5% ownership changes in US-listed companies

Source: SEC EDGAR Bulk Index Files
Date: November 1, 2025
"""

import requests
import sqlite3
from datetime import datetime
from pathlib import Path
import time
import re
from io import StringIO

# Configuration
MASTER_DB = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_DIR = Path("F:/OSINT_Data/SEC_13D_13G")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# SEC EDGAR Bulk Index
# Format: https://www.sec.gov/Archives/edgar/full-index/{year}/QTR{quarter}/master.idx
SEC_INDEX_BASE = "https://www.sec.gov/Archives/edgar/full-index"
USER_AGENT = "OSINT-Foresight-Research mreardon@example.com"  # SEC requires user agent

class SEC13DGBulkCollector:
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
            import json
            prc_file = Path("C:/Projects/OSINT-Foresight/data/prc_identifiers.json")
            if prc_file.exists():
                with open(prc_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Extract company name patterns
                    keywords = set()
                    for entity in data.get('company_names', []):
                        keywords.add(entity.upper())
                    return keywords
        except:
            pass

        # Fallback to basic keywords
        return {
            'CHINA', 'CHINESE', 'SINO', 'HONG KONG',
            'ALIBABA', 'TENCENT', 'BAIDU', 'HUAWEI', 'ZTE',
            'CHINA INVESTMENT CORPORATION', 'CIC',
            'SAFE INVESTMENT', 'STATE ADMINISTRATION OF FOREIGN EXCHANGE',
            'CHINA LIFE', 'PING AN', 'CHINA CONSTRUCTION BANK',
        }

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

                -- Filer (beneficial owner) information
                filer_name TEXT,
                filer_cik TEXT,

                -- Subject company information
                company_name TEXT,
                company_cik TEXT,

                -- URLs
                filing_url TEXT,
                document_url TEXT,

                -- Detection
                is_chinese BOOLEAN DEFAULT 0,
                detection_method TEXT,
                confidence_score REAL,

                -- Metadata
                activist_intent BOOLEAN,  -- True for 13D vs. 13G
                created_at TEXT,
                data_source TEXT DEFAULT 'SEC EDGAR Bulk Index',

                UNIQUE(accession_number)
            )
        ''')
        self.conn.commit()
        print('[OK] Table created or already exists')

    def download_quarter_index(self, year, quarter):
        """Download SEC filing index for a specific quarter"""
        url = f"{SEC_INDEX_BASE}/{year}/QTR{quarter}/master.idx"

        print(f'\n[INFO] Downloading {year} Q{quarter} index...')

        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()

            # Parse index file
            # Format: CIK|Company Name|Form Type|Date Filed|Filename
            lines = response.text.split('\n')

            # Skip header lines (first ~10 lines are metadata)
            data_lines = []
            for i, line in enumerate(lines):
                if i > 10 and '|' in line:  # Data starts after header
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

            # Filter for 13D/13G forms
            # Form types in index: "SCHEDULE 13D", "SCHEDULE 13D/A", "SCHEDULE 13G", "SCHEDULE 13G/A"
            form_type_clean = form_type.strip().upper()
            if not ('13D' in form_type_clean or '13G' in form_type_clean):
                return None

            # Build accession number from filename
            # filename format: edgar/data/CIK/ACCESSION.txt
            acc_match = re.search(r'/(\d{10}-\d{2}-\d{6})\.txt', filename)
            accession = acc_match.group(1) if acc_match else None

            if not accession:
                return None

            return {
                'cik': cik.strip(),
                'company_name': company_name.strip(),
                'form_type': form_type.strip(),
                'filing_date': date_filed.strip(),
                'accession_number': accession,
                'filename': filename.strip(),
                'document_url': f"https://www.sec.gov/Archives/{filename.strip()}"
            }

        except Exception as e:
            return None

    def detect_chinese_filer(self, company_name):
        """Detect if filer is Chinese"""
        if not company_name:
            return False, 0.0, None

        name_upper = company_name.upper()

        # Check against known Chinese keywords
        for keyword in self.chinese_keywords:
            if keyword in name_upper:
                return True, 0.90, f'Keyword match: {keyword}'

        # Additional heuristics
        chinese_indicators = [
            ('BEIJING', 0.85),
            ('SHANGHAI', 0.85),
            ('SHENZHEN', 0.85),
            ('HONG KONG', 0.90),
            ('CAYMAN', 0.60),  # Many Chinese companies incorporate in Cayman
            ('LIMITED HK', 0.80),
        ]

        for indicator, confidence in chinese_indicators:
            if indicator in name_upper:
                return True, confidence, f'Location indicator: {indicator}'

        return False, 0.0, None

    def collect_recent_quarters(self, num_quarters=4):
        """Collect filings from recent quarters"""
        print('=' * 80)
        print(f'COLLECTING SEC 13D/13G FILINGS - Last {num_quarters} Quarters')
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

            # Parse and filter for 13D/13G
            for line in index_lines:
                filing = self.parse_index_line(line)
                if filing:
                    all_filings.append(filing)

            time.sleep(0.2)  # Rate limiting

        print(f'\n[OK] Total 13D/13G filings found: {len(all_filings)}')
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
            # Detect Chinese filer
            is_chinese, confidence, method = self.detect_chinese_filer(
                filing.get('company_name')
            )

            if is_chinese:
                chinese_detected += 1

            try:
                self.cur.execute('''
                    INSERT OR IGNORE INTO sec_13d_13g_filings (
                        accession_number, form_type, filing_date,
                        filer_name, filer_cik,
                        company_name, company_cik,
                        filing_url, html_url,
                        is_chinese, detection_method, confidence_score,
                        activist_intent,
                        created_at, data_source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    filing.get('accession_number'),
                    filing.get('form_type'),
                    filing.get('filing_date'),
                    filing.get('company_name'),  # Note: index shows subject company, not beneficial owner
                    filing.get('cik'),
                    filing.get('company_name'),
                    filing.get('cik'),
                    f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={filing.get('cik')}&type={filing.get('form_type')}",
                    filing.get('document_url'),  # This maps to html_url in table
                    is_chinese,
                    method,
                    confidence,
                    '13D' in filing.get('form_type', ''),  # 13D = activist
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
        print(f'     Chinese filings detected: {chinese_detected}')

        self.chinese_filings = chinese_detected

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
            ('idx_13dg_form', 'form_type'),
        ]

        for idx_name, column in indexes:
            try:
                self.cur.execute(f'''
                    CREATE INDEX IF NOT EXISTS {idx_name}
                    ON sec_13d_13g_filings({column})
                ''')
                print(f'  [OK] {idx_name}')
            except Exception as e:
                print(f'  [SKIP] {idx_name}: {e}')

        self.conn.commit()

    def print_report(self):
        """Print collection report"""
        print('=' * 80)
        print('SEC 13D/13G - COLLECTION REPORT')
        print('=' * 80)

        # Total filings
        self.cur.execute('SELECT COUNT(*) FROM sec_13d_13g_filings')
        total = self.cur.fetchone()[0]
        print(f'\nTotal filings in database: {total}')

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
                SELECT company_name, form_type, filing_date, detection_method
                FROM sec_13d_13g_filings
                WHERE is_chinese = 1
                ORDER BY filing_date DESC
                LIMIT 10
            ''')
            for row in self.cur.fetchall():
                company = row[0][:50] + '...' if len(row[0]) > 50 else row[0]
                print(f'  {company}')
                print(f'    Form: {row[1]}, Date: {row[2]}')
                print(f'    Detection: {row[3]}')
                print()

    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    collector = SEC13DGBulkCollector()

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
        print(f'Chinese filings detected: {collector.chinese_filings}')

        print('\n[NOTE] Collection Strategy:')
        print('  - Downloaded SEC quarterly master index files')
        print('  - Filtered for SC 13D and SC 13G forms')
        print('  - Chinese entity detection based on name patterns')
        print('\n[LIMITATION] SEC index shows subject company, not beneficial owner')
        print('  - Need to parse individual filings to extract actual filer names')
        print('  - For Phase 2: Download and parse filing documents')

    except Exception as e:
        print(f'[ERROR] Collection failed: {e}')
        import traceback
        traceback.print_exc()

    finally:
        collector.close()

if __name__ == '__main__':
    main()
