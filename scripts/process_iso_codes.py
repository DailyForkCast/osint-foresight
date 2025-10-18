#!/usr/bin/env python3
"""
Process ISO Country and Currency Code Files
Extracts and standardizes ISO codes from various formats
"""

import pandas as pd
import sqlite3
from pathlib import Path
import json
import logging
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class ISOCodeProcessor:
    def __init__(self, base_path: str = "F:/OSINT_Data/Trade_Facilities"):
        self.base_path = Path(base_path)
        self.iso_path = self.base_path / 'iso_codes'
        self.iso_path.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def process_currency_codes(self, file_path: str):
        """Process ISO 4217 currency codes from Excel"""
        print("\n" + "="*80)
        print("Processing ISO 4217 Currency Codes")
        print("="*80)

        try:
            # Read Excel file - try different sheets
            xl_file = pd.ExcelFile(file_path)
            print(f"Found sheets: {xl_file.sheet_names}")

            # Process each sheet
            all_currencies = []
            for sheet_name in xl_file.sheet_names:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    print(f"\nSheet '{sheet_name}': {len(df)} rows, {len(df.columns)} columns")

                    # Print first few rows to understand structure
                    if not df.empty:
                        print(f"Columns: {df.columns.tolist()}")
                        print(f"First row sample: {df.iloc[0].tolist() if len(df) > 0 else 'Empty'}")

                        # Try to identify currency code columns
                        currency_cols = []
                        for col in df.columns:
                            col_str = str(col).lower()
                            if any(term in col_str for term in ['currency', 'code', 'alpha', 'iso', 'numeric']):
                                currency_cols.append(col)

                        if currency_cols:
                            print(f"Potential currency columns: {currency_cols}")
                            all_currencies.append(df)

                except Exception as e:
                    print(f"Error reading sheet {sheet_name}: {e}")

            # Combine and save
            if all_currencies:
                combined_df = pd.concat(all_currencies, ignore_index=True)

                # Save to CSV
                output_file = self.iso_path / 'iso_4217_currencies.csv'
                combined_df.to_csv(output_file, index=False)
                print(f"\nSaved {len(combined_df)} currency records to {output_file}")

                return combined_df

        except Exception as e:
            self.logger.error(f"Error processing currency codes: {e}")
            return None

    def process_country_codes(self, file_path: str):
        """Process ISO 3166 country codes"""
        print("\n" + "="*80)
        print("Processing ISO 3166 Country Codes")
        print("="*80)

        try:
            # Check file extension
            file_ext = Path(file_path).suffix.lower()

            if file_ext in ['.xls', '.xlsx']:
                # Read Excel file
                xl_file = pd.ExcelFile(file_path)
                print(f"Found sheets: {xl_file.sheet_names}")

                all_countries = []
                for sheet_name in xl_file.sheet_names:
                    try:
                        df = pd.read_excel(file_path, sheet_name=sheet_name)
                        print(f"\nSheet '{sheet_name}': {len(df)} rows")

                        if not df.empty:
                            print(f"Columns: {df.columns.tolist()[:10]}...")  # First 10 columns

                            # Look for country-related columns
                            country_cols = []
                            for col in df.columns:
                                col_str = str(col).lower()
                                if any(term in col_str for term in ['country', 'name', 'alpha', 'iso', 'code', 'numeric']):
                                    country_cols.append(col)

                            if country_cols:
                                print(f"Country-related columns: {country_cols[:10]}")
                                all_countries.append(df)

                    except Exception as e:
                        print(f"Error reading sheet {sheet_name}: {e}")

                # Save combined data
                if all_countries:
                    combined_df = pd.concat(all_countries, ignore_index=True)
                    output_file = self.iso_path / 'iso_3166_countries.csv'
                    combined_df.to_csv(output_file, index=False)
                    print(f"\nSaved {len(combined_df)} country records to {output_file}")
                    return combined_df

            elif file_ext == '.doc':
                # For DOC files, we'll need python-docx or similar
                print("DOC format detected - would need python-docx library")
                print("Recommend converting to Excel or CSV for processing")
                return None

            elif file_ext == '.xml':
                # Try to parse XML
                try:
                    df = pd.read_xml(file_path)
                    print(f"Read XML: {len(df)} records")
                    output_file = self.iso_path / 'iso_data_from_xml.csv'
                    df.to_csv(output_file, index=False)
                    return df
                except Exception as e:
                    print(f"Error reading XML: {e}")
                    return None

        except Exception as e:
            self.logger.error(f"Error processing country codes: {e}")
            return None

    def create_iso_database(self, currencies_df=None, countries_df=None):
        """Create database with ISO codes"""
        print("\n" + "="*80)
        print("Creating ISO Codes Database")
        print("="*80)

        db_path = self.base_path / 'databases' / 'iso_codes.db'
        db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS iso_currencies (
                currency_code TEXT PRIMARY KEY,
                numeric_code TEXT,
                currency_name TEXT,
                country_name TEXT,
                minor_units INTEGER,
                withdrawal_date TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS iso_countries (
                alpha_2 TEXT PRIMARY KEY,
                alpha_3 TEXT,
                numeric_code TEXT,
                country_name TEXT,
                official_name TEXT,
                capital TEXT,
                continent TEXT,
                subregion TEXT,
                languages TEXT,
                currency_codes TEXT
            )
        ''')

        # Create China-specific view
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS china_related_codes (
                entity_type TEXT,
                code TEXT,
                name TEXT,
                description TEXT,
                notes TEXT
            )
        ''')

        # Insert China-related codes
        china_codes = [
            ('country', 'CN', 'China', 'People\'s Republic of China', 'Mainland China'),
            ('country', 'HK', 'Hong Kong', 'Hong Kong SAR', 'Special Administrative Region'),
            ('country', 'MO', 'Macao', 'Macao SAR', 'Special Administrative Region'),
            ('country', 'TW', 'Taiwan', 'Taiwan, Province of China', 'Separate customs territory'),
            ('currency', 'CNY', 'Yuan Renminbi', 'Chinese Yuan', 'Mainland currency'),
            ('currency', 'CNH', 'Yuan (offshore)', 'Offshore RMB', 'Hong Kong traded'),
            ('currency', 'HKD', 'Hong Kong Dollar', 'Hong Kong currency', 'Pegged to USD'),
            ('currency', 'MOP', 'Pataca', 'Macao currency', 'Pegged to HKD'),
            ('currency', 'TWD', 'New Taiwan Dollar', 'Taiwan currency', 'Taiwan currency')
        ]

        cursor.executemany(
            'INSERT OR REPLACE INTO china_related_codes VALUES (?, ?, ?, ?, ?)',
            china_codes
        )

        conn.commit()

        # Save dataframes if provided
        if currencies_df is not None and not currencies_df.empty:
            currencies_df.to_sql('raw_currencies', conn, if_exists='replace', index=False)
            print(f"Added {len(currencies_df)} currency records")

        if countries_df is not None and not countries_df.empty:
            countries_df.to_sql('raw_countries', conn, if_exists='replace', index=False)
            print(f"Added {len(countries_df)} country records")

        conn.close()
        print(f"Created ISO database: {db_path}")
        return db_path

    def analyze_china_trade_partners(self):
        """Analyze major trading partners and their codes"""
        print("\n" + "="*80)
        print("China Trade Partner Analysis")
        print("="*80)

        # Major trade partners and their codes
        trade_partners = {
            'United States': {'alpha_2': 'US', 'alpha_3': 'USA', 'currency': 'USD'},
            'European Union': {'alpha_2': 'EU', 'alpha_3': 'EUR', 'currency': 'EUR'},
            'Japan': {'alpha_2': 'JP', 'alpha_3': 'JPN', 'currency': 'JPY'},
            'South Korea': {'alpha_2': 'KR', 'alpha_3': 'KOR', 'currency': 'KRW'},
            'Germany': {'alpha_2': 'DE', 'alpha_3': 'DEU', 'currency': 'EUR'},
            'United Kingdom': {'alpha_2': 'GB', 'alpha_3': 'GBR', 'currency': 'GBP'},
            'Australia': {'alpha_2': 'AU', 'alpha_3': 'AUS', 'currency': 'AUD'},
            'Canada': {'alpha_2': 'CA', 'alpha_3': 'CAN', 'currency': 'CAD'},
            'Russia': {'alpha_2': 'RU', 'alpha_3': 'RUS', 'currency': 'RUB'},
            'India': {'alpha_2': 'IN', 'alpha_3': 'IND', 'currency': 'INR'},
            'Brazil': {'alpha_2': 'BR', 'alpha_3': 'BRA', 'currency': 'BRL'},
            'Singapore': {'alpha_2': 'SG', 'alpha_3': 'SGP', 'currency': 'SGD'},
            'Malaysia': {'alpha_2': 'MY', 'alpha_3': 'MYS', 'currency': 'MYR'},
            'Vietnam': {'alpha_2': 'VN', 'alpha_3': 'VNM', 'currency': 'VND'},
            'Thailand': {'alpha_2': 'TH', 'alpha_3': 'THA', 'currency': 'THB'}
        }

        # Belt and Road countries
        bri_partners = {
            'Pakistan': {'alpha_2': 'PK', 'alpha_3': 'PAK', 'currency': 'PKR'},
            'Kazakhstan': {'alpha_2': 'KZ', 'alpha_3': 'KAZ', 'currency': 'KZT'},
            'Iran': {'alpha_2': 'IR', 'alpha_3': 'IRN', 'currency': 'IRR'},
            'Turkey': {'alpha_2': 'TR', 'alpha_3': 'TUR', 'currency': 'TRY'},
            'Indonesia': {'alpha_2': 'ID', 'alpha_3': 'IDN', 'currency': 'IDR'}
        }

        # Save analysis
        analysis_file = self.iso_path / 'china_trade_partner_codes.json'
        analysis_data = {
            'china_codes': {
                'CN': {'name': 'China', 'currency': 'CNY'},
                'HK': {'name': 'Hong Kong', 'currency': 'HKD'},
                'MO': {'name': 'Macao', 'currency': 'MOP'},
                'TW': {'name': 'Taiwan', 'currency': 'TWD'}
            },
            'major_trade_partners': trade_partners,
            'belt_road_partners': bri_partners
        }

        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)

        print(f"Saved trade partner analysis to {analysis_file}")
        print(f"- China entities: 4")
        print(f"- Major trade partners: {len(trade_partners)}")
        print(f"- Belt & Road partners: {len(bri_partners)}")

        return analysis_data

    def run_processing(self):
        """Process all ISO code files"""
        results = {
            'currencies_processed': 0,
            'countries_processed': 0,
            'databases_created': []
        }

        # Process files
        files = {
            'currencies': 'F:/list-one.xls',
            'countries': 'F:/list-three.xls',
            'additional': 'F:/list-two.doc'
        }

        currencies_df = None
        countries_df = None

        # Process currency codes (list-one.xls)
        if Path(files['currencies']).exists():
            currencies_df = self.process_currency_codes(files['currencies'])
            if currencies_df is not None:
                results['currencies_processed'] = len(currencies_df)

        # Process country codes (list-three.xls)
        if Path(files['countries']).exists():
            countries_df = self.process_country_codes(files['countries'])
            if countries_df is not None:
                results['countries_processed'] = len(countries_df)

        # Note about DOC file
        if Path(files['additional']).exists():
            print(f"\nNote: {files['additional']} requires manual processing or conversion")

        # Create database
        db_path = self.create_iso_database(currencies_df, countries_df)
        results['databases_created'].append(str(db_path))

        # Analyze trade partners
        self.analyze_china_trade_partners()

        # Summary
        print("\n" + "="*80)
        print("ISO Code Processing Complete!")
        print("="*80)
        print(f"Currency records processed: {results['currencies_processed']}")
        print(f"Country records processed: {results['countries_processed']}")
        print(f"Databases created: {len(results['databases_created'])}")
        print("\nKey China-related codes documented:")
        print("- CN/CNY (Mainland), HK/HKD (Hong Kong)")
        print("- MO/MOP (Macao), TW/TWD (Taiwan)")

        return results

if __name__ == "__main__":
    processor = ISOCodeProcessor()
    results = processor.run_processing()

    print("\n" + "="*80)
    print("INTEGRATION READY:")
    print("="*80)
    print("1. ISO codes database created for trade analysis")
    print("2. China and trade partner codes mapped")
    print("3. Ready to cross-reference with UN/LOCODE facilities")
    print("4. Currency codes available for value conversions")
