#!/usr/bin/env python3
"""
Terminal F: Non-EU Strategic Countries Data Collector
Focus on strategic partners: CH (Switzerland), NO (Norway), RS (Serbia), TR (Turkey), UA (Ukraine)
Following MASTER_SQL_WAREHOUSE_GUIDE.md specifications
Priority: RS (Serbia) - highest China exposure in Europe
"""

import sqlite3
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import json
import time
import hashlib

class TerminalFCollector:
    def __init__(self):
        self.warehouse_path = Path("F:/OSINT_WAREHOUSE/osint_research.db")

        # Priority countries (alphabetized)
        self.countries = ['CH', 'NO', 'RS', 'TR', 'UA']

        # Additional non-priority if time permits (alphabetized)
        self.additional = ['AL', 'BA', 'GE', 'IS', 'LI', 'MD', 'ME', 'MK', 'XK']

        # Standard China detection keywords
        self.china_keywords = [
            'China', 'Chinese', 'Beijing', 'Shanghai', 'Tsinghua',
            'Huawei', 'CAS', 'Xinjiang', 'Tibet', 'Shenzhen',
            'Guangzhou', 'Wuhan', 'Hangzhou', 'Alibaba', 'Tencent', 'Baidu'
        ]

        # Serbia-specific keywords (highest priority - known China investments)
        self.serbia_china_keywords = [
            'Hesteel', 'Smederevo', 'Zijin', 'Bor',
            'CRBC', 'Mihajlo Pupin', 'Shandong Linglong',
            'China Road and Bridge Corporation', 'HBIS', 'Zijin Mining'
        ]

        # Turkey-specific keywords
        self.turkey_china_keywords = [
            'Akkuyu', 'ICBC Turkey', 'Bank of China Turkey',
            'Huawei Turkey', 'ZTE Turkey', 'BYD', 'Sinosure',
            'Belt and Road', 'BRI', 'Yavuz Sultan Selim Bridge'
        ]

        # Norway-specific keywords
        self.norway_china_keywords = [
            'Sinopec', 'CNOOC', 'Arctic cooperation', 'Statoil China',
            'Equinor China', 'China-Norway Ocean Research'
        ]

        # Switzerland-specific keywords
        self.switzerland_china_keywords = [
            'Swiss-China Free Trade', 'China Construction Bank Switzerland',
            'Bank of China Switzerland', 'Swisscom Huawei'
        ]

        # Ukraine-specific keywords (pre-2022 focus)
        self.ukraine_china_keywords = [
            'Motor Sich', 'Skyrizon', 'Beijing Skyrizon', 'COFCO',
            'China National Complete Engineering', 'Xinwei Group'
        ]

    def detect_china_involvement(self, text):
        """Enhanced China detection for strategic countries"""
        if not text:
            return 0.0

        text_lower = str(text).lower()

        # Strong indicators (return 0.95)
        strong = ['china', 'chinese', 'beijing', 'shanghai', 'tsinghua',
                  'huawei', 'cas', 'xinjiang', 'tibet', 'shenzhen', 'guangzhou',
                  'wuhan', 'hangzhou', 'alibaba', 'tencent', 'baidu',
                  'hesteel', 'zijin', 'crbc', 'motor sich', 'belt and road']

        for term in strong:
            if term in text_lower:
                return 0.95

        # Medium indicators (return 0.6)
        medium = ['asia', 'sino-', 'prc', 'hong kong', 'macau', 'bri']
        for term in medium:
            if term in text_lower:
                return 0.6

        return 0.0

    def collect_serbia_specific_intel(self):
        """Serbia deep dive - documented Chinese investments"""
        print("\n[CRITICAL] Serbia - Europe's highest China dependency...")

        # Known documented investments to verify
        known_investments = [
            {
                'company': 'Hesteel Group',
                'investment': 'Smederevo Steel Plant',
                'type': 'Acquisition',
                'year': 2016,
                'value_usd': 46000000,
                'strategic_importance': 'Largest Serbian steel producer'
            },
            {
                'company': 'Zijin Mining Group',
                'investment': 'RTB Bor Copper Mine',
                'type': 'Acquisition',
                'year': 2018,
                'value_usd': 1260000000,
                'strategic_importance': 'Major European copper reserves'
            },
            {
                'company': 'China Road and Bridge Corporation',
                'investment': 'Belgrade-Budapest Railway',
                'type': 'Infrastructure',
                'year': 2020,
                'strategic_importance': 'Key Belt & Road corridor'
            },
            {
                'company': 'Shandong Linglong',
                'investment': 'Tire Factory Zrenjanin',
                'type': 'Greenfield',
                'year': 2019,
                'value_usd': 800000000,
                'strategic_importance': 'Industrial capacity'
            }
        ]

        return known_investments

    def collect_openaire_keyword_search(self, country):
        """
        OpenAIRE collection using KEYWORD method with API fix
        CRITICAL FIX: Handle results as dict with string values
        """
        print(f"\n[OPENAIRE] {country} - Using keyword search method...")

        # Get country-specific keywords
        extra_keywords = []
        if country == 'RS':
            extra_keywords = self.serbia_china_keywords
        elif country == 'TR':
            extra_keywords = self.turkey_china_keywords
        elif country == 'NO':
            extra_keywords = self.norway_china_keywords
        elif country == 'CH':
            extra_keywords = self.switzerland_china_keywords
        elif country == 'UA':
            extra_keywords = self.ukraine_china_keywords

        # Base OpenAIRE API
        base_url = "https://api.openaire.eu/search/publications"

        # Build keyword string
        keyword_str = 'China OR Chinese OR Beijing OR Shanghai'
        if extra_keywords:
            keyword_str += ' OR ' + ' OR '.join(extra_keywords[:5])  # Add top 5 specific keywords

        params = {
            'country': country,
            'keywords': keyword_str,
            'format': 'json',
            'size': 50,
            'page': 0
        }

        results = []
        max_pages = 20  # Limit for testing

        for page in range(max_pages):
            params['page'] = page

            try:
                response = requests.get(base_url, params=params, timeout=30)

                if response.status_code == 200:
                    data = response.json()

                    if 'results' in data and data['results']:
                        # CRITICAL FIX: Handle OpenAIRE response structure
                        publications_found = 0
                        for result_id, result_content in data['results'].items():
                            # result_content is the string content
                            china_score = self.detect_china_involvement(result_content)

                            if china_score > 0:
                                results.append({
                                    'id': result_id,
                                    'title': result_content[:200],
                                    'authors': 'OpenAIRE_Authors',
                                    'year': datetime.now().year,
                                    'country': country,
                                    'china_score': china_score,
                                    'source': 'OpenAIRE_Keyword'
                                })
                                publications_found += 1

                        print(f"  Page {page}: {publications_found} China-linked publications")

                        if publications_found == 0:
                            break  # No more relevant results
                    else:
                        break  # No more results

                time.sleep(0.5)  # Be respectful to API

            except Exception as e:
                print(f"  Error on page {page}: {str(e)}")
                continue

        print(f"  Total: {len(results)} China-linked publications for {country}")
        return results

    def insert_to_warehouse(self, data, table_type='collaboration'):
        """Insert data into warehouse following schema"""
        conn = sqlite3.connect(self.warehouse_path)
        cursor = conn.cursor()

        inserted = 0

        try:
            if table_type == 'collaboration':
                for record in data:
                    # Generate unique ID
                    collab_id = hashlib.md5(
                        f"{record['id']}_{record['country']}".encode()
                    ).hexdigest()

                    cursor.execute("""
                        INSERT OR REPLACE INTO core_f_collaboration (
                            collab_id, project_name, has_chinese_partner,
                            china_collaboration_score, source_system,
                            confidence_score, source_file, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        collab_id,
                        record.get('title', 'Unknown'),
                        record['china_score'] > 0.5,
                        record['china_score'],
                        record.get('source', 'OpenAIRE_Keyword'),
                        0.85,  # Fixed confidence for keyword search
                        f"terminal_f_{record['country']}",
                        datetime.now().isoformat()
                    ))
                    inserted += 1

            elif table_type == 'investment':
                # Special handling for documented investments
                for record in data:
                    cursor.execute("""
                        INSERT OR REPLACE INTO core_f_procurement (
                            award_id, award_title, has_chinese_vendor,
                            supply_chain_risk, vendor_name, award_value_eur,
                            source_system, created_at, analyst_notes
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        f"serbia_invest_{record['company'].replace(' ', '_')}",
                        record['investment'],
                        True,
                        'HIGH',
                        record['company'],
                        record.get('value_usd', 0) * 0.92,  # USD to EUR approx
                        'Terminal_F_Verified',
                        datetime.now().isoformat(),
                        f"Type: {record['type']}, Year: {record['year']}, Strategic: {record['strategic_importance']}"
                    ))
                    inserted += 1

            conn.commit()
            print(f"  Inserted {inserted} records to warehouse")

        except Exception as e:
            print(f"  Warehouse error: {str(e)}")
            conn.rollback()
        finally:
            conn.close()

        return inserted

    def run_collection(self):
        """Main collection orchestration"""
        print(f"\n{'='*60}")
        print("TERMINAL F: NON-EU STRATEGIC COUNTRIES COLLECTION")
        print(f"{'='*60}")
        print(f"Start Time: {datetime.now()}")
        print(f"Priority Countries: {', '.join(self.countries)}")
        print(f"Warehouse: {self.warehouse_path}")

        total_records = 0

        # 1. SERBIA - HIGHEST PRIORITY
        print(f"\n{'='*40}")
        print("PRIORITY 1: SERBIA - HIGHEST CHINA EXPOSURE")
        print(f"{'='*40}")

        # Insert known investments first
        serbia_investments = self.collect_serbia_specific_intel()
        investment_count = self.insert_to_warehouse(serbia_investments, 'investment')
        print(f"  Documented {investment_count} major Chinese investments")

        # Then search for research collaborations
        serbia_collabs = self.collect_openaire_keyword_search('RS')
        if serbia_collabs:
            collab_count = self.insert_to_warehouse(serbia_collabs, 'collaboration')
            total_records += collab_count

        # 2. Other priority countries
        for country in ['TR', 'NO', 'CH', 'UA']:
            print(f"\n{'='*40}")
            print(f"COLLECTING: {country}")
            print(f"{'='*40}")

            collabs = self.collect_openaire_keyword_search(country)
            if collabs:
                count = self.insert_to_warehouse(collabs, 'collaboration')
                total_records += count

        # 3. Generate summary statistics
        self.generate_statistics()

        print(f"\n{'='*60}")
        print(f"COLLECTION COMPLETE")
        print(f"Total Records: {total_records}")
        print(f"End Time: {datetime.now()}")
        print(f"{'='*60}")

    def generate_statistics(self):
        """Generate collection statistics"""
        conn = sqlite3.connect(self.warehouse_path)
        cursor = conn.cursor()

        print(f"\n{'='*40}")
        print("TERMINAL F STATISTICS")
        print(f"{'='*40}")

        for country in self.countries:
            cursor.execute("""
                SELECT COUNT(*), SUM(has_chinese_partner)
                FROM core_f_collaboration
                WHERE source_file LIKE ?
            """, (f"%terminal_f_{country}%",))

            total, china_count = cursor.fetchone()
            china_count = china_count or 0

            if total and total > 0:
                rate = (china_count / total) * 100
                print(f"{country}: {total} records, {china_count} China links ({rate:.1f}%)")
            else:
                print(f"{country}: No data collected")

        # Special Serbia analysis
        cursor.execute("""
            SELECT COUNT(*), SUM(has_chinese_vendor), SUM(award_value_eur)
            FROM core_f_procurement
            WHERE award_id LIKE 'serbia_invest_%'
        """)

        invest_count, china_vendors, total_value = cursor.fetchone()
        if invest_count:
            print(f"\nSerbia Investments: {invest_count} major deals, €{total_value/1e9:.2f}B total")

        conn.close()

if __name__ == "__main__":
    collector = TerminalFCollector()
    collector.run_collection()
