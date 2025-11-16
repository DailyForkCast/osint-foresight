#!/usr/bin/env python3
"""
Filter Eurostat COMEXT Bulk Download for China-Relevant Records
Extracts China, Hong Kong, Macau trade data from massive bulk files
Date: October 30, 2025
"""

import pandas as pd
import gzip
import csv
from pathlib import Path
from datetime import datetime

# Paths
BULK_DIR = Path("F:/OSINT_Data/Trade_Facilities/eurostat_comext_bulk")
OUTPUT_DIR = Path("F:/OSINT_Data/Trade_Facilities/eurostat_comext_v3")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# China-related partner codes (ISO2)
CHINA_PARTNERS = ['CN', 'HK', 'MO']  # China, Hong Kong, Macau

# Strategic product CN8 prefixes (first 4 digits)
STRATEGIC_PRODUCTS = [
    '8542',  # Electronic integrated circuits
    '8541',  # Semiconductor devices, LEDs
    '8517',  # Telephone/telecom equipment
    '8471',  # Computers/data processing machines
    '9027',  # Scientific/precision instruments
    '8525',  # Transmission apparatus
    '2846',  # Rare earth compounds
    '2805',  # Rare earth metals
    '7601',  # Aluminum (unwrought)
    '7219',  # Stainless steel (flat-rolled)
    '8112',  # Beryllium, chromium, germanium, vanadium
    '3004',  # Medicaments
    '3002',  # Vaccines, blood products
    '9031',  # Measuring/checking instruments
    '9013',  # Liquid crystal devices, lasers
    '8543',  # Electrical machines/apparatus
]

class EurostatBulkFilter:
    def __init__(self):
        self.total_rows = 0
        self.china_rows = 0
        self.strategic_rows = 0
        self.output_files = []

    def open_bulk_file(self, filepath):
        """Open bulk file (handles .gz compression)"""
        if filepath.suffix == '.gz':
            return gzip.open(filepath, 'rt', encoding='utf-8')
        else:
            return open(filepath, 'r', encoding='utf-8')

    def is_strategic_product(self, product_code):
        """Check if product code matches strategic prefixes"""
        if not product_code or len(product_code) < 4:
            return False

        prefix = product_code[:4]
        return prefix in STRATEGIC_PRODUCTS

    def filter_china_records(self, input_file, output_prefix):
        """Filter bulk file for China-related records"""
        print(f"\n{'='*80}")
        print(f"Filtering: {input_file.name}")
        print(f"{'='*80}")

        if not input_file.exists():
            print(f"[ERROR] File not found: {input_file}")
            return

        # Output files
        china_all_file = OUTPUT_DIR / f"{output_prefix}_china_all_products.csv"
        china_strategic_file = OUTPUT_DIR / f"{output_prefix}_china_strategic.csv"

        china_all_rows = []
        china_strategic_rows = []

        try:
            with self.open_bulk_file(input_file) as f:
                # Determine delimiter (TSV or CSV)
                first_line = f.readline()
                f.seek(0)

                delimiter = '\t' if '\t' in first_line else ','

                reader = csv.DictReader(f, delimiter=delimiter)
                headers = reader.fieldnames

                delim_name = 'TAB' if delimiter == '\t' else 'COMMA'
                print(f"Delimiter: {delim_name}")
                print(f"Columns: {len(headers) if headers else 0}")
                if headers:
                    print(f"Sample columns: {', '.join(headers[:5])}...")

                # Identify partner column (varies by dataset)
                partner_col = None
                for col in ['partner', 'PARTNER', 'partner_code', 'DECLARANT_ISO']:
                    if col in headers:
                        partner_col = col
                        break

                if not partner_col:
                    print("[ERROR] Cannot identify partner/country column")
                    return

                # Identify product column
                product_col = None
                for col in ['product', 'PRODUCT', 'product_code', 'cn8', 'CN8']:
                    if col in headers:
                        product_col = col
                        break

                print(f"Partner column: {partner_col}")
                print(f"Product column: {product_col}")
                print(f"\nProcessing rows...")

                for row in reader:
                    self.total_rows += 1

                    if self.total_rows % 100000 == 0:
                        print(f"  Processed: {self.total_rows:,} | China: {self.china_rows:,} | Strategic: {self.strategic_rows:,}", end='\r')

                    # Check if China-related
                    partner = row.get(partner_col, '')
                    if partner in CHINA_PARTNERS:
                        self.china_rows += 1
                        china_all_rows.append(row)

                        # Check if strategic product
                        if product_col:
                            product_code = row.get(product_col, '')
                            if self.is_strategic_product(product_code):
                                self.strategic_rows += 1
                                china_strategic_rows.append(row)

                print(f"\n  Processed: {self.total_rows:,} | China: {self.china_rows:,} | Strategic: {self.strategic_rows:,}")

                # Write output files
                if china_all_rows:
                    df_all = pd.DataFrame(china_all_rows)
                    df_all.to_csv(china_all_file, index=False, encoding='utf-8')
                    print(f"\n[OK] Wrote {len(china_all_rows):,} China records to:")
                    print(f"     {china_all_file}")
                    self.output_files.append(china_all_file)

                if china_strategic_rows:
                    df_strategic = pd.DataFrame(china_strategic_rows)
                    df_strategic.to_csv(china_strategic_file, index=False, encoding='utf-8')
                    print(f"[OK] Wrote {len(china_strategic_rows):,} strategic records to:")
                    print(f"     {china_strategic_file}")
                    self.output_files.append(china_strategic_file)

        except Exception as e:
            print(f"[ERROR] Failed to process file: {e}")

    def process_all_bulk_files(self):
        """Process all bulk files in the directory"""
        print("="*80)
        print("EUROSTAT BULK FILE CHINA FILTER")
        print("="*80)
        print(f"Bulk directory: {BULK_DIR}")
        print(f"Output directory: {OUTPUT_DIR}")
        print(f"\nChina partners: {', '.join(CHINA_PARTNERS)}")
        print(f"Strategic products: {len(STRATEGIC_PRODUCTS)} CN8 prefixes")

        # Find bulk files
        bulk_files = list(BULK_DIR.glob("*.csv.gz")) + list(BULK_DIR.glob("*.csv")) + \
                     list(BULK_DIR.glob("*.tsv.gz")) + list(BULK_DIR.glob("*.tsv")) + \
                     list(BULK_DIR.glob("*.dat"))

        if not bulk_files:
            print(f"\n[WARN] No bulk files found in {BULK_DIR}")
            print("\nExpected files:")
            print("  - ds-056120.csv.gz (or .csv, .tsv.gz, .tsv)")
            print("\nAfter downloading from Eurostat, place files in:")
            print(f"  {BULK_DIR}")
            return

        print(f"\nFound {len(bulk_files)} bulk file(s)")

        for bulk_file in bulk_files:
            # Generate output prefix from filename
            output_prefix = bulk_file.stem.replace('.csv', '').replace('.tsv', '')
            self.filter_china_records(bulk_file, output_prefix)

        # Summary
        print("\n" + "="*80)
        print("FILTERING COMPLETE")
        print("="*80)
        print(f"Total rows processed: {self.total_rows:,}")
        print(f"China-related records: {self.china_rows:,} ({self.china_rows/self.total_rows*100:.1f}%)" if self.total_rows > 0 else "")
        print(f"Strategic products: {self.strategic_rows:,} ({self.strategic_rows/self.china_rows*100:.1f}%)" if self.china_rows > 0 else "")
        print(f"\nOutput files created: {len(self.output_files)}")
        for f in self.output_files:
            print(f"  - {f.name}")

        print("\n" + "="*80)
        print("NEXT STEPS")
        print("="*80)
        print("1. Review filtered CSV files in:")
        print(f"   {OUTPUT_DIR}")
        print("\n2. Load into master database:")
        print("   python scripts/load_eurostat_into_master.py")
        print("\n3. Wait for database locks to clear if needed")

def main():
    filter = EurostatBulkFilter()
    filter.process_all_bulk_files()

if __name__ == '__main__':
    main()
