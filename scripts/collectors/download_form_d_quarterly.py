#!/usr/bin/env python3
"""
download_form_d_quarterly.py - Download & Parse SEC Form D Quarterly Datasets

Purpose:
    Download SEC's quarterly Form D datasets (complete VC/PE deal data)
    Extract and parse the structured data files
    Load into database for analysis

These datasets contain ALL Form D filings for each quarter in structured format.
This is much more efficient than scraping individual filings.

Usage:
    # Download Q2 2025 (most recent)
    python download_form_d_quarterly.py --quarter 2025q2

    # Download multiple quarters
    python download_form_d_quarterly.py --quarter 2025q2 2025q1 2024q4

    # Download and analyze only (don't load to database)
    python download_form_d_quarterly.py --quarter 2025q2 --analyze-only

Output:
    - Downloads to: data/raw/sec_form_d/quarterly/
    - Extracts to: data/processed/sec_form_d/quarterly/
    - Database: osint_master.db (table: sec_form_d_filings)

Last Updated: 2025-10-22
"""

import requests
import zipfile
import os
import csv
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import time
import argparse

class FormDQuarterlyDownloader:
    """Download and process SEC Form D quarterly datasets"""

    def __init__(self, output_dir='data/raw/sec_form_d/quarterly'):
        self.base_url = 'https://www.sec.gov'
        self.headers = {
            'User-Agent': 'OSINT-Foresight Research project@example.com',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }

        self.raw_dir = Path(output_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)

        self.processed_dir = Path('data/processed/sec_form_d/quarterly')
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        self.stats = {
            'downloaded': 0,
            'extracted': 0,
            'parsed': 0,
            'errors': 0
        }

    def download_quarterly_dataset(self, quarter, use_existing=False):
        """
        Download a quarterly Form D dataset

        Args:
            quarter: Format like '2025q2', '2025q1', '2024q4', etc.
            use_existing: If True, skip re-download prompt for existing files

        Returns:
            Path to downloaded ZIP file
        """
        print("="*70)
        print(f"DOWNLOADING FORM D DATASET: {quarter.upper()}")
        print("="*70)

        # Construct URL
        zip_filename = f"{quarter}_d.zip"
        download_url = f"{self.base_url}/files/structureddata/data/form-d-data-sets/{zip_filename}"

        local_path = self.raw_dir / zip_filename

        # Check if already downloaded
        if local_path.exists():
            print(f"\n[OK] File already exists: {local_path}")
            print(f"     Size: {local_path.stat().st_size:,} bytes")
            if use_existing:
                print(f"     Using existing file (--use-existing flag)")
                return local_path
            response = input("     Re-download? (y/n): ")
            if response.lower() != 'y':
                return local_path

        print(f"\n-> Downloading from: {download_url}")
        print(f"-> Saving to: {local_path}")

        try:
            time.sleep(0.5)  # Rate limiting
            response = requests.get(download_url, headers=self.headers, stream=True, timeout=300)

            if response.status_code == 200:
                # Get file size
                total_size = int(response.headers.get('content-length', 0))
                print(f"-> File size: {total_size:,} bytes ({total_size / 1024 / 1024:.1f} MB)")

                # Download with progress
                downloaded = 0
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)

                            # Show progress
                            if total_size > 0:
                                progress = (downloaded / total_size) * 100
                                print(f"\r   Progress: {progress:.1f}% ({downloaded:,} / {total_size:,} bytes)", end='')

                print(f"\n[OK] Downloaded successfully")
                self.stats['downloaded'] += 1
                return local_path

            else:
                print(f"[FAIL] HTTP {response.status_code}")
                self.stats['errors'] += 1
                return None

        except Exception as e:
            print(f"[FAIL] Error downloading: {e}")
            self.stats['errors'] += 1
            return None

    def extract_dataset(self, zip_path):
        """Extract ZIP file and identify contents"""
        print(f"\n-> Extracting: {zip_path.name}")

        extract_dir = self.processed_dir / zip_path.stem
        extract_dir.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # List contents
                file_list = zip_ref.namelist()
                print(f"[OK] ZIP contains {len(file_list)} files:")

                for filename in file_list:
                    print(f"     - {filename}")

                # Extract all
                zip_ref.extractall(extract_dir)
                print(f"[OK] Extracted to: {extract_dir}")

                self.stats['extracted'] += 1
                return extract_dir, file_list

        except Exception as e:
            print(f"[FAIL] Error extracting: {e}")
            self.stats['errors'] += 1
            return None, []

    def parse_tsv_file(self, file_path, max_rows=10):
        """Parse TSV file and show structure"""
        print(f"\n-> Parsing: {file_path.name}")

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Use csv.DictReader with tab delimiter
                reader = csv.DictReader(f, delimiter='\t')

                # Get column names
                columns = reader.fieldnames
                print(f"[OK] Found {len(columns)} columns:")

                # Show columns in groups
                for i in range(0, len(columns), 5):
                    cols = columns[i:i+5]
                    print(f"     {', '.join(cols)}")

                # Read sample rows
                rows = []
                for i, row in enumerate(reader):
                    if i >= max_rows:
                        break
                    rows.append(row)

                print(f"\n[OK] Sample data (first {len(rows)} rows):")
                print("-" * 70)

                # Show first row as example
                if rows:
                    sample_row = rows[0]
                    print("\nSAMPLE RECORD:")
                    for key, value in sample_row.items():
                        if value and len(str(value)) > 0:
                            display_value = str(value)[:100]
                            print(f"  {key:30s}: {display_value}")

                self.stats['parsed'] += 1
                return {
                    'columns': columns,
                    'sample_rows': rows,
                    'row_count': i + 1
                }

        except Exception as e:
            print(f"[FAIL] Error parsing: {e}")
            self.stats['errors'] += 1
            return None

    def analyze_dataset(self, extract_dir):
        """Analyze extracted dataset files"""
        print("\n" + "="*70)
        print("DATASET ANALYSIS")
        print("="*70)

        analysis = {
            'files': {},
            'total_records': 0,
            'key_fields': []
        }

        # Find all TSV/TXT files (search recursively for nested directories)
        data_files = list(extract_dir.glob('**/*.txt')) + list(extract_dir.glob('**/*.tsv'))

        print(f"\n-> Found {len(data_files)} data files")

        for data_file in data_files:
            print(f"\n" + "-"*70)
            print(f"FILE: {data_file.name}")
            print("-"*70)

            file_info = self.parse_tsv_file(data_file, max_rows=3)

            if file_info:
                analysis['files'][data_file.name] = file_info

                # Count total records (approximately)
                with open(data_file, 'r', encoding='utf-8', errors='ignore') as f:
                    line_count = sum(1 for _ in f) - 1  # Subtract header

                print(f"\n[OK] Total records in file: ~{line_count:,}")
                analysis['total_records'] += line_count

        return analysis

    def identify_key_tables(self, analysis):
        """Identify the key tables in the dataset"""
        print("\n" + "="*70)
        print("KEY TABLES IDENTIFICATION")
        print("="*70)

        key_tables = {}

        for filename, file_info in analysis['files'].items():
            filename_upper = filename.upper()

            # Identify by filename pattern (more reliable than column matching)
            if 'OFFERING' in filename_upper and 'OFFERING' == filename_upper.replace('.TSV', '').replace('.TXT', ''):
                key_tables['offerings'] = filename
                print(f"\n[OK] OFFERINGS TABLE: {filename}")
                print(f"     - Main Form D filings")
                print(f"     - Contains: company info, offering amounts, dates")

            elif 'RELATEDPERSON' in filename_upper:
                key_tables['persons'] = filename
                print(f"\n[OK] PERSONS TABLE: {filename}")
                print(f"     - Executives, directors, promoters")
                print(f"     - May include investor names!")

            elif 'ISSUER' in filename_upper and 'ISSUERS' == filename_upper.replace('.TSV', '').replace('.TXT', ''):
                key_tables['issuers'] = filename
                print(f"\n[OK] ISSUERS TABLE: {filename}")
                print(f"     - Company information")

            elif 'FORMDSUBMISSION' in filename_upper:
                key_tables['submissions'] = filename
                print(f"\n[OK] SUBMISSIONS TABLE: {filename}")
                print(f"     - Filing metadata")

        return key_tables

    def load_to_database(self, extract_dir, key_tables, quarter=None, db_path='F:/OSINT_WAREHOUSE/osint_master.db'):
        """Load Form D data into database"""
        print("\n" + "="*70)
        print("DATABASE LOADING")
        print("="*70)

        print(f"\n-> Database: {db_path}")

        # First, load all data into memory to join tables
        # Load issuers (company info)
        issuers = {}
        if 'issuers' in key_tables:
            # Find the file (may be in subdirectory)
            issuers_file = list(extract_dir.glob(f"**/{key_tables['issuers']}"))[0]
            print(f"-> Reading issuers data from: {issuers_file.name}...")
            with open(issuers_file, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f, delimiter='\t')
                for row in reader:
                    acc = row.get('ACCESSIONNUMBER')
                    if acc:
                        issuers[acc] = row

        # Load filing dates
        filings = {}
        if 'submissions' in key_tables:
            # Find the file (may be in subdirectory)
            filings_file = list(extract_dir.glob(f"**/{key_tables['submissions']}"))[0]
            print(f"-> Reading filing dates from: {filings_file.name}...")
            with open(filings_file, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f, delimiter='\t')
                for row in reader:
                    acc = row.get('ACCESSIONNUMBER')
                    if acc:
                        filings[acc] = row

        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sec_form_d_offerings (
                accession_number TEXT PRIMARY KEY,
                filing_date DATE,
                issuer_name TEXT,
                issuer_cik TEXT,
                issuer_address_city TEXT,
                issuer_address_state TEXT,
                issuer_address_zip TEXT,
                industry_group_type TEXT,
                revenue_range TEXT,
                total_offering_amount REAL,
                total_amount_sold REAL,
                total_remaining REAL,
                is_equity_type INTEGER,
                is_debt_type INTEGER,
                more_than_one_year INTEGER,
                collected_quarter TEXT,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sec_form_d_persons (
                person_id INTEGER PRIMARY KEY AUTOINCREMENT,
                accession_number TEXT,
                person_name TEXT,
                person_address_city TEXT,
                person_address_state TEXT,
                relationship TEXT,
                is_executive INTEGER,
                is_director INTEGER,
                is_promoter INTEGER,
                clarification_text TEXT,
                FOREIGN KEY (accession_number) REFERENCES sec_form_d_offerings(accession_number)
            )
        """)

        print("[OK] Tables created/verified")

        # Load offerings with joined data
        if 'offerings' in key_tables:
            # Find the file (may be in subdirectory)
            offerings_file = list(extract_dir.glob(f"**/{key_tables['offerings']}"))[0]
            print(f"\n-> Loading offerings from: {offerings_file.name}")

            loaded = 0
            errors = 0
            with open(offerings_file, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f, delimiter='\t')

                for row in reader:
                    try:
                        acc_num = row.get('ACCESSIONNUMBER')
                        if not acc_num:
                            continue

                        # Get issuer data
                        issuer_data = issuers.get(acc_num, {})
                        filing_data = filings.get(acc_num, {})

                        cursor.execute("""
                            INSERT OR REPLACE INTO sec_form_d_offerings (
                                accession_number, filing_date,
                                issuer_name, issuer_cik,
                                issuer_address_city, issuer_address_state, issuer_address_zip,
                                industry_group_type, revenue_range,
                                total_offering_amount, total_amount_sold, total_remaining,
                                is_equity_type, is_debt_type, more_than_one_year,
                                collected_quarter
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            acc_num,
                            filing_data.get('FILING_DATE'),
                            issuer_data.get('ENTITYNAME'),
                            issuer_data.get('CIK'),
                            issuer_data.get('CITY'),
                            issuer_data.get('STATEORCOUNTRY'),
                            issuer_data.get('ZIPCODE'),
                            row.get('INDUSTRYGROUPTYPE'),
                            row.get('REVENUERANGE'),
                            self.safe_float(row.get('TOTALOFFERINGAMOUNT')),
                            self.safe_float(row.get('TOTALAMOUNTSOLD')),
                            self.safe_float(row.get('TOTALREMAINING')),
                            1 if row.get('ISEQUITYTYPE', '').lower() == 'true' else 0,
                            1 if row.get('ISDEBTTYPE', '').lower() == 'true' else 0,
                            1 if row.get('MORETHANONEYEAR', '').lower() == 'true' else 0,
                            quarter or '2025q2'
                        ))

                        loaded += 1
                        if loaded % 1000 == 0:
                            print(f"\r   Loaded: {loaded:,} records", end='', flush=True)

                    except Exception as e:
                        errors += 1
                        if errors <= 3:
                            print(f"\n[WARN] Error loading record: {e}")

            print(f"\n[OK] Loaded {loaded:,} offerings")

        # Load persons data
        if 'persons' in key_tables:
            # Find the file (may be in subdirectory)
            persons_file = list(extract_dir.glob(f"**/{key_tables['persons']}"))[0]
            print(f"\n-> Loading persons from: {persons_file.name}")

            loaded = 0
            with open(persons_file, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f, delimiter='\t')

                for row in reader:
                    try:
                        acc_num = row.get('ACCESSIONNUMBER')
                        if not acc_num:
                            continue

                        # Build person name
                        firstname = row.get('FIRSTNAME', '')
                        middlename = row.get('MIDDLENAME', '')
                        lastname = row.get('LASTNAME', '')
                        full_name = ' '.join([firstname, middlename, lastname]).strip()

                        if not full_name:
                            continue

                        relationship = row.get('RELATIONSHIP_1', '')

                        cursor.execute("""
                            INSERT INTO sec_form_d_persons (
                                accession_number, person_name,
                                person_address_city, person_address_state,
                                relationship,
                                is_executive, is_director, is_promoter,
                                clarification_text
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            acc_num,
                            full_name,
                            row.get('CITY'),
                            row.get('STATEORCOUNTRY'),
                            relationship,
                            1 if 'Executive' in relationship else 0,
                            1 if 'Director' in relationship else 0,
                            1 if 'Promoter' in relationship else 0,
                            row.get('RELATIONSHIPCLARIFICATION')
                        ))

                        loaded += 1
                        if loaded % 1000 == 0:
                            print(f"\r   Loaded: {loaded:,} records", end='', flush=True)

                    except:
                        continue

            print(f"\n[OK] Loaded {loaded:,} persons")

        conn.commit()
        conn.close()

        print("\n[OK] Database loading complete")

    def safe_float(self, value):
        """Safely convert to float"""
        try:
            return float(value) if value else None
        except:
            return None

    def safe_int(self, value):
        """Safely convert to int"""
        try:
            return int(value) if value else 0
        except:
            return 0

    def process_quarter(self, quarter, analyze_only=False, use_existing=False):
        """Complete processing workflow for a quarter"""
        print("\n" + "="*70)
        print(f"PROCESSING QUARTER: {quarter.upper()}")
        print("="*70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)

        # Step 1: Download
        zip_path = self.download_quarterly_dataset(quarter, use_existing=use_existing)
        if not zip_path:
            return False

        # Step 2: Extract
        extract_dir, file_list = self.extract_dataset(zip_path)
        if not extract_dir:
            return False

        # Step 3: Analyze
        analysis = self.analyze_dataset(extract_dir)

        # Step 4: Identify key tables
        key_tables = self.identify_key_tables(analysis)

        # Step 5: Load to database (unless analyze-only)
        if not analyze_only:
            self.load_to_database(extract_dir, key_tables, quarter=quarter)
        else:
            print("\n[SKIP] Database loading (--analyze-only mode)")

        # Summary
        print("\n" + "="*70)
        print("PROCESSING COMPLETE")
        print("="*70)
        print(f"Quarter:          {quarter}")
        print(f"Total Records:    ~{analysis['total_records']:,}")
        print(f"Files Processed:  {len(analysis['files'])}")
        print(f"Database Loaded:  {'NO (analyze-only)' if analyze_only else 'YES'}")
        print("="*70)

        return True


def main():
    parser = argparse.ArgumentParser(
        description='Download and process SEC Form D quarterly datasets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download Q2 2025 (most recent)
  python download_form_d_quarterly.py --quarter 2025q2

  # Download multiple quarters
  python download_form_d_quarterly.py --quarter 2025q2 2025q1 2024q4

  # Analyze only (don't load to database)
  python download_form_d_quarterly.py --quarter 2025q2 --analyze-only
        """
    )

    parser.add_argument('--quarter', nargs='+', required=True,
                       help='Quarter(s) to download (e.g., 2025q2 2025q1)')
    parser.add_argument('--analyze-only', action='store_true',
                       help='Analyze data but do not load to database')
    parser.add_argument('--use-existing', action='store_true',
                       help='Use existing downloaded files without prompting')

    args = parser.parse_args()

    downloader = FormDQuarterlyDownloader()

    success_count = 0
    for quarter in args.quarter:
        if downloader.process_quarter(quarter, analyze_only=args.analyze_only, use_existing=args.use_existing):
            success_count += 1

    # Final summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print(f"Quarters Processed: {success_count} / {len(args.quarter)}")
    print(f"Downloaded:         {downloader.stats['downloaded']}")
    print(f"Extracted:          {downloader.stats['extracted']}")
    print(f"Parsed:             {downloader.stats['parsed']}")
    print(f"Errors:             {downloader.stats['errors']}")
    print("="*70)


if __name__ == '__main__':
    main()
