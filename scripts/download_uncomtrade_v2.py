#!/usr/bin/env python3
"""
UN Comtrade API v2 Data Collector
Downloads bilateral trade flow data using the new API system
"""

import os
import sys
import requests
import pandas as pd
import sqlite3
from pathlib import Path
import json
import logging
from datetime import datetime
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

class UNComtradeV2Collector:
    def __init__(self):
        self.base_path = Path("F:/OSINT_Data/Trade_Facilities/uncomtrade")
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Get API keys from environment
        self.primary_key = os.getenv('UNCOMTRADE_PRIMARY_KEY')
        self.secondary_key = os.getenv('UNCOMTRADE_SECONDARY_KEY')

        if not self.primary_key:
            raise ValueError("UN Comtrade primary key not found in .env.local")

        # New API v2 endpoints
        self.base_url = "https://comtradeapi.un.org"

        # Headers with subscription key
        self.headers = {
            'Ocp-Apim-Subscription-Key': self.primary_key,
            'Accept': 'application/json'
        }

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def test_connection(self):
        """Test API v2 connection"""
        print("\n" + "="*80)
        print("Testing UN Comtrade API v2 Connection")
        print("="*80)

        # Try a simple data availability check - correct endpoint
        test_url = f"{self.base_url}/data/v1/get/C/A/HS"

        params = {
            'reporterCode': '156',  # China
            'period': '2023',
            'partnerCode': '0',     # World
            'cmdCode': 'TOTAL',
            'flowCode': 'X',        # Exports
            'maxRecords': 1
        }

        try:
            response = requests.get(test_url, headers=self.headers, params=params)

            if response.status_code == 200:
                print("[OK] API v2 connection successful!")
                data = response.json()
                if 'data' in data:
                    print(f"Response contains {len(data['data'])} records")
                return True
            elif response.status_code == 401:
                print("[ERROR] Authentication failed - check your API key")
                print(f"Response: {response.text}")
                return False
            else:
                print(f"[ERROR] API returned status {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return False

        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    def get_china_bilateral_trade(self, year=2023, flow='X'):
        """Get China's bilateral trade with major partners"""
        print(f"\n" + "="*80)
        print(f"Fetching China's {'Exports' if flow == 'X' else 'Imports'} for {year}")
        print("="*80)

        # Major trade partners
        partners = {
            '842': 'United States',
            '276': 'Germany',
            '392': 'Japan',
            '410': 'South Korea',
            '826': 'United Kingdom',
            '036': 'Australia',
            '124': 'Canada',
            '643': 'Russia',
            '356': 'India',
            '076': 'Brazil',
            '702': 'Singapore',
            '458': 'Malaysia',
            '704': 'Vietnam',
            '764': 'Thailand',
            '360': 'Indonesia'
        }

        all_data = []

        for partner_code, partner_name in partners.items():
            print(f"\nFetching trade with {partner_name}...")

            # Use the correct data endpoint
            url = f"{self.base_url}/data/v1/get/C/A/HS"

            params = {
                'reporterCode': '156',  # China
                'period': str(year),
                'partnerCode': partner_code,
                'flowCode': flow,
                'cmdCode': 'AG2',  # 2-digit aggregation
                'maxRecords': 500
            }

            try:
                time.sleep(1)  # Rate limiting
                response = requests.get(url, headers=self.headers, params=params)

                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and data['data']:
                        df = pd.DataFrame(data['data'])
                        df['partnerDesc'] = partner_name
                        print(f"  Found {len(df)} commodity categories")
                        all_data.append(df)
                    else:
                        print(f"  No data available")
                elif response.status_code == 403:
                    print(f"  Access denied - may require premium subscription")
                else:
                    print(f"  Error {response.status_code}: {response.text[:100]}")

            except Exception as e:
                self.logger.error(f"Error fetching {partner_name}: {e}")

        # Combine and save
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)

            # Save to CSV
            flow_name = 'exports' if flow == 'X' else 'imports'
            output_file = self.base_path / f'china_{flow_name}_{year}.csv'
            combined_df.to_csv(output_file, index=False)

            print(f"\n[OK] Saved {len(combined_df)} records to {output_file}")

            # Analyze top commodities
            self.analyze_trade_patterns(combined_df, flow)

            return combined_df

        return pd.DataFrame()

    def get_strategic_commodities(self, year=2023):
        """Get trade data for strategic/dual-use commodities"""
        print(f"\n" + "="*80)
        print(f"Fetching Strategic Commodities Trade for {year}")
        print("="*80)

        # Strategic HS codes
        strategic_codes = {
            '84': 'Nuclear reactors, machinery',
            '85': 'Electrical machinery',
            '88': 'Aircraft and spacecraft',
            '90': 'Optical and precision instruments',
            '28': 'Inorganic chemicals',
            '29': 'Organic chemicals',
            '30': 'Pharmaceutical products',
            '93': 'Arms and ammunition',
            '81': 'Other base metals (tungsten, etc)'
        }

        strategic_data = []

        for hs_code, description in strategic_codes.items():
            print(f"\nFetching HS Chapter {hs_code}: {description}")

            url = f"{self.base_url}/data/v1/get/C/A/HS"

            params = {
                'reporterCode': '156',  # China
                'period': str(year),
                'partnerCode': '0',     # World
                'flowCode': 'M,X',      # Imports and Exports
                'cmdCode': hs_code,
                'maxRecords': 1000
            }

            try:
                time.sleep(1)
                response = requests.get(url, headers=self.headers, params=params)

                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and data['data']:
                        df = pd.DataFrame(data['data'])
                        df['cmdCategory'] = description
                        print(f"  Found {len(df)} trade flows")
                        strategic_data.append(df)
                    else:
                        print(f"  No data available")

            except Exception as e:
                self.logger.error(f"Error fetching {description}: {e}")

        # Save strategic commodities data
        if strategic_data:
            strategic_df = pd.concat(strategic_data, ignore_index=True)

            output_file = self.base_path / f'strategic_commodities_{year}.csv'
            strategic_df.to_csv(output_file, index=False)

            print(f"\n[OK] Saved {len(strategic_df)} strategic commodity records")

            return strategic_df

        return pd.DataFrame()

    def analyze_trade_patterns(self, df, flow_type):
        """Analyze trade patterns from data"""
        if df.empty:
            return

        print("\n" + "-"*60)
        print("Trade Pattern Analysis")
        print("-"*60)

        # Top partners by total value
        if 'primaryValue' in df.columns and 'partnerDesc' in df.columns:
            partner_totals = df.groupby('partnerDesc')['primaryValue'].sum().sort_values(ascending=False)

            print(f"\nTop {'Export' if flow_type == 'X' else 'Import'} Partners by Value:")
            for partner, value in partner_totals.head(10).items():
                print(f"  {partner}: ${value/1e9:.2f} billion")

        # Top commodity categories
        if 'cmdCode' in df.columns and 'primaryValue' in df.columns:
            commodity_totals = df.groupby('cmdCode')['primaryValue'].sum().sort_values(ascending=False)

            print(f"\nTop Commodity Categories (HS 2-digit):")
            for code, value in commodity_totals.head(10).items():
                print(f"  HS {code}: ${value/1e9:.2f} billion")

    def create_database(self):
        """Create SQLite database for trade data"""
        db_path = self.base_path / 'uncomtrade_v2.db'

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Bilateral trade table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bilateral_trade (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER,
                reporter_code TEXT,
                reporter_desc TEXT,
                partner_code TEXT,
                partner_desc TEXT,
                flow_code TEXT,
                flow_desc TEXT,
                cmd_code TEXT,
                cmd_desc TEXT,
                primary_value REAL,
                net_weight REAL,
                gross_weight REAL,
                qty_unit_code TEXT,
                qty REAL,
                is_reported_by_partner INTEGER
            )
        ''')

        # Strategic commodities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategic_commodities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER,
                hs_chapter TEXT,
                category TEXT,
                partner_code TEXT,
                partner_desc TEXT,
                flow_code TEXT,
                flow_desc TEXT,
                trade_value REAL,
                quantity REAL,
                risk_level TEXT
            )
        ''')

        conn.commit()
        conn.close()

        print(f"Database created: {db_path}")
        return db_path

    def run_collection(self):
        """Run complete data collection"""
        # Test connection
        if not self.test_connection():
            print("\n[ERROR] Failed to connect to UN Comtrade API v2")
            print("Please check:")
            print("1. Your API keys are correct in .env.local")
            print("2. You've registered at https://comtradedeveloper.un.org")
            print("3. Your subscription is active")
            return

        # Create database
        self.create_database()

        # Get China's exports
        exports_df = self.get_china_bilateral_trade(year=2023, flow='X')

        # Get China's imports
        imports_df = self.get_china_bilateral_trade(year=2023, flow='M')

        # Get strategic commodities
        strategic_df = self.get_strategic_commodities(year=2023)

        # Summary
        print("\n" + "="*80)
        print("UN Comtrade v2 Collection Complete!")
        print("="*80)
        print(f"Data location: {self.base_path}")
        print(f"Export records: {len(exports_df) if not exports_df.empty else 0}")
        print(f"Import records: {len(imports_df) if not imports_df.empty else 0}")
        print(f"Strategic commodity records: {len(strategic_df) if not strategic_df.empty else 0}")

        return {
            'exports': exports_df,
            'imports': imports_df,
            'strategic': strategic_df
        }

if __name__ == "__main__":
    collector = UNComtradeV2Collector()
    results = collector.run_collection()
