#!/usr/bin/env python3
"""
UN Comtrade API Data Collector
Downloads bilateral trade flow data for China analysis
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

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))
from scripts.utils.config_loader import config

class UNComtradeCollector:
    def __init__(self):
        self.base_path = Path("F:/OSINT_Data/Trade_Facilities/uncomtrade")
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self.config = config.get_uncomtrade_config()

        # Check if keys are configured
        if not self.config['primary_key']:
            raise ValueError("UN Comtrade primary key not configured in .env.local")
        if not self.config['secondary_key']:
            raise ValueError("UN Comtrade secondary key not configured in .env.local")

        # API configuration - UN Comtrade v2 API
        self.base_url = "https://comtradeapi.un.org"  # New v2 API endpoint
        self.headers = {
            'Ocp-Apim-Subscription-Key': self.config['primary_key']
        }

        # Rate limiting (1 request per second as per config)
        self.rate_limit = self.config['rate_limit']

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def test_connection(self):
        """Test API connection and authentication"""
        print("\n" + "="*80)
        print("Testing UN Comtrade API Connection")
        print("="*80)

        # Test endpoint - v2 API preview endpoint
        test_url = f"{self.base_url}/data/v1/preview/C/A/HS"

        try:
            response = requests.get(
                test_url,
                headers=self.headers,
                params={'reporterCode': '156', 'period': '2023', 'partnerCode': '0', 'cmdCode': 'TOTAL', 'maxRecords': '10'}
            )

            if response.status_code == 200:
                print("[OK] API connection successful!")
                data = response.json()
                print(f"Available datasets: {len(data) if isinstance(data, list) else 'Unknown'}")
                return True
            else:
                print(f"[ERROR] API error: {response.status_code}")
                print(f"Response: {response.text}")

                # Try secondary key if primary fails
                if response.status_code == 401:
                    print("\nTrying secondary key...")
                    self.headers['Ocp-Apim-Subscription-Key'] = self.config['secondary_key']
                    response = requests.get(test_url, headers=self.headers)
                    if response.status_code == 200:
                        print("[OK] Secondary key works!")
                        return True

                return False

        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    def get_china_trade_flows(self, year=2023, partner_codes=None):
        """Get China's bilateral trade flows"""
        print(f"\n" + "="*80)
        print(f"Fetching China Trade Flows for {year}")
        print("="*80)

        # Default to major trade partners if none specified
        if partner_codes is None:
            partner_codes = [
                842,  # USA
                276,  # Germany
                392,  # Japan
                410,  # South Korea
                36,   # Australia
                124,  # Canada
                826,  # UK
                643,  # Russia
                356,  # India
                76,   # Brazil
                702,  # Singapore
                458,  # Malaysia
                704,  # Vietnam
                764,  # Thailand
                360   # Indonesia
            ]

        all_data = []

        for partner in partner_codes:
            print(f"\nFetching trade with partner {partner}...")

            # Build API request
            params = {
                'typeCode': 'C',  # Commodities
                'freqCode': 'A',  # Annual
                'clCode': 'HS',  # Harmonized System
                'period': year,
                'reporterCode': 156,  # China
                'partnerCode': partner,
                'flowCode': 'M,X',  # Imports and Exports
                'partner2Code': None,
                'customsCode': 'C00',
                'motCode': '0'
            }

            try:
                # API v2 endpoint for trade data
                url = f"{self.base_url}/data/v1/get/C/A/HS"

                # Rate limiting
                time.sleep(self.rate_limit)

                response = requests.get(url, headers=self.headers, params=params)

                if response.status_code == 200:
                    data = response.json()

                    if 'dataset' in data and data['dataset']:
                        df = pd.DataFrame(data['dataset'])
                        print(f"  Found {len(df)} trade records")
                        all_data.append(df)
                    else:
                        print(f"  No data available")

                else:
                    print(f"  Error: {response.status_code}")

            except Exception as e:
                self.logger.error(f"Error fetching partner {partner}: {e}")

        # Combine all data
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)

            # Save to CSV
            output_file = self.base_path / f'china_trade_{year}.csv'
            combined_df.to_csv(output_file, index=False)
            print(f"\nSaved {len(combined_df)} records to {output_file}")

            return combined_df

        return pd.DataFrame()

    def get_strategic_goods_trade(self, commodity_codes=None, year=2023):
        """Get trade data for strategic/dual-use goods"""
        print(f"\n" + "="*80)
        print(f"Fetching Strategic Goods Trade for {year}")
        print("="*80)

        # Strategic HS codes (computers, semiconductors, etc.)
        if commodity_codes is None:
            commodity_codes = [
                '8471',  # Automatic data processing machines
                '8517',  # Telephones and telecommunications
                '8541',  # Semiconductor devices
                '8542',  # Electronic integrated circuits
                '9013',  # Liquid crystal devices, lasers
                '9027',  # Instruments for physical/chemical analysis
                '8525',  # Transmission apparatus
                '8804',  # Aircraft parts
                '8803',  # Parts of aircraft/spacecraft
                '8802',  # Aircraft, spacecraft
                '8906',  # Warships
                '9301',  # Military weapons
                '3002',  # Human blood, vaccines
                '2844',  # Radioactive elements
                '8101',  # Tungsten
                '8112'   # Beryllium, chromium, germanium
            ]

        strategic_data = []

        for commodity in commodity_codes:
            print(f"\nFetching HS {commodity}...")

            params = {
                'typeCode': 'C',
                'freqCode': 'A',
                'clCode': 'HS',
                'period': year,
                'reporterCode': 156,  # China
                'cmdCode': commodity,
                'flowCode': 'M,X',
                'partnerCode': 'all',
                'customsCode': 'C00',
                'motCode': '0'
            }

            try:
                url = f"{self.base_url}/data/v1/get/C/A/HS"
                time.sleep(self.rate_limit)

                response = requests.get(url, headers=self.headers, params=params)

                if response.status_code == 200:
                    data = response.json()

                    if 'dataset' in data and data['dataset']:
                        df = pd.DataFrame(data['dataset'])
                        df['commodity_code'] = commodity
                        print(f"  Found {len(df)} records")
                        strategic_data.append(df)
                    else:
                        print(f"  No data available")

                else:
                    print(f"  Error: {response.status_code}")

            except Exception as e:
                self.logger.error(f"Error fetching commodity {commodity}: {e}")

        # Combine and save
        if strategic_data:
            strategic_df = pd.concat(strategic_data, ignore_index=True)

            output_file = self.base_path / f'strategic_goods_{year}.csv'
            strategic_df.to_csv(output_file, index=False)
            print(f"\nSaved {len(strategic_df)} strategic goods records")

            return strategic_df

        return pd.DataFrame()

    def analyze_trade_patterns(self, df):
        """Analyze trade patterns and trends"""
        if df.empty:
            return

        print("\n" + "="*80)
        print("Trade Pattern Analysis")
        print("="*80)

        # Group by flow (import/export)
        if 'rgDesc' in df.columns and 'TradeValue' in df.columns:
            flow_summary = df.groupby('rgDesc')['TradeValue'].sum()
            print("\nTrade by Flow:")
            for flow, value in flow_summary.items():
                print(f"  {flow}: ${value:,.0f}")

        # Top partners
        if 'ptTitle' in df.columns and 'TradeValue' in df.columns:
            top_partners = df.groupby('ptTitle')['TradeValue'].sum().sort_values(ascending=False).head(10)
            print("\nTop 10 Trade Partners:")
            for partner, value in top_partners.items():
                print(f"  {partner}: ${value:,.0f}")

        # Top commodities
        if 'cmdDescE' in df.columns and 'TradeValue' in df.columns:
            top_commodities = df.groupby('cmdDescE')['TradeValue'].sum().sort_values(ascending=False).head(10)
            print("\nTop 10 Commodities:")
            for commodity, value in top_commodities.items():
                print(f"  {commodity[:50]}: ${value:,.0f}")

    def create_trade_database(self):
        """Create SQLite database with trade data"""
        db_path = self.base_path / 'uncomtrade.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bilateral_trade (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER,
                reporter_code INTEGER,
                reporter_name TEXT,
                partner_code INTEGER,
                partner_name TEXT,
                commodity_code TEXT,
                commodity_desc TEXT,
                flow_code TEXT,
                flow_desc TEXT,
                trade_value REAL,
                trade_quantity REAL,
                quantity_unit TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategic_goods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER,
                commodity_code TEXT,
                commodity_category TEXT,
                partner_code INTEGER,
                partner_name TEXT,
                export_value REAL,
                import_value REAL,
                risk_level TEXT
            )
        ''')

        conn.commit()
        conn.close()

        print(f"Created trade database: {db_path}")
        return db_path

    def run_collection(self):
        """Run complete data collection"""
        # Test connection first
        if not self.test_connection():
            print("\n[ERROR] Failed to connect to UN Comtrade API")
            print("Please check your API keys in .env.local")
            return

        # Create database
        self.create_trade_database()

        # Get China's bilateral trade
        trade_df = self.get_china_trade_flows(year=2023)
        if not trade_df.empty:
            self.analyze_trade_patterns(trade_df)

        # Get strategic goods trade
        strategic_df = self.get_strategic_goods_trade(year=2023)

        # Summary
        print("\n" + "="*80)
        print("UN Comtrade Collection Complete!")
        print("="*80)
        print(f"Data location: {self.base_path}")
        print(f"Trade records: {len(trade_df) if not trade_df.empty else 0}")
        print(f"Strategic goods records: {len(strategic_df) if not strategic_df.empty else 0}")

        return {
            'trade_data': trade_df,
            'strategic_goods': strategic_df
        }

if __name__ == "__main__":
    collector = UNComtradeCollector()
    results = collector.run_collection()
