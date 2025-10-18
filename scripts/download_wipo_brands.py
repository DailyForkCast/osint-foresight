#!/usr/bin/env python3
"""
WIPO Global Brand Database Downloader
Downloads trademark and brand data with China focus
Uses WIPO Global Brand Database API
"""

import requests
import pandas as pd
import sqlite3
from pathlib import Path
import time
from datetime import datetime
import json

class WIPOBrandDownloader:
    def __init__(self):
        self.base_path = Path("F:/OSINT_Data/WIPO_Brands")
        self.base_path.mkdir(parents=True, exist_ok=True)

        self.db_path = self.base_path / f"wipo_brands_{datetime.now().strftime('%Y%m%d')}.db"

        # WIPO Global Brand Database API
        self.api_base = "https://www3.wipo.int/branddb/api"

        # Strategic technology areas for trademark search
        self.search_terms = {
            'semiconductors': [
                'semiconductor', 'microchip', 'processor', 'integrated circuit',
                'silicon', 'wafer', 'chipset', 'SoC', 'ASIC', 'FPGA'
            ],
            'telecommunications': [
                '5G', '6G', 'telecom', 'wireless', 'broadband',
                'network', 'router', 'antenna', 'base station', 'fiber optic'
            ],
            'artificial_intelligence': [
                'AI', 'artificial intelligence', 'machine learning', 'deep learning',
                'neural network', 'computer vision', 'NLP', 'chatbot', 'algorithm'
            ],
            'quantum': [
                'quantum', 'quantum computing', 'quantum communication',
                'quantum encryption', 'qubit', 'quantum sensor'
            ],
            'batteries': [
                'battery', 'lithium', 'energy storage', 'power bank',
                'electric vehicle', 'EV', 'charging', 'solid state'
            ],
            'biotechnology': [
                'biotech', 'vaccine', 'pharma', 'medicine', 'therapeutic',
                'diagnostic', 'genetic', 'CRISPR', 'antibody', 'biosensor'
            ],
            'aerospace': [
                'aerospace', 'aircraft', 'satellite', 'spacecraft', 'drone',
                'UAV', 'aviation', 'rocket', 'propulsion', 'navigation'
            ],
            'robotics': [
                'robot', 'robotics', 'automation', 'autonomous', 'AGV',
                'industrial automation', 'collaborative robot', 'cobot'
            ]
        }

        # China-related owner patterns
        self.china_entities = [
            'huawei', 'xiaomi', 'oppo', 'vivo', 'zte', 'lenovo',
            'alibaba', 'tencent', 'baidu', 'bytedance', 'dji',
            'boe', 'tcl', 'haier', 'midea', 'gree', 'byd',
            'geely', 'nio', 'xpeng', 'li auto', 'saic',
            'china', 'chinese', 'beijing', 'shanghai', 'shenzhen',
            'guangzhou', 'hangzhou', 'wuhan', 'chengdu', 'xi\'an'
        ]

    def create_database(self):
        """Create SQL database schema for trademark data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('PRAGMA journal_mode=WAL')

        # Main trademarks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trademarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                registration_number TEXT,
                mark_name TEXT,
                owner_name TEXT,
                owner_country TEXT,
                filing_date TEXT,
                registration_date TEXT,
                expiry_date TEXT,
                nice_classes TEXT,
                goods_services TEXT,
                technology_category TEXT,
                china_related BOOLEAN,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Owner analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS owners (
                owner_id TEXT PRIMARY KEY,
                owner_name TEXT,
                owner_country TEXT,
                total_marks INTEGER,
                technology_focus TEXT,
                first_filing TEXT,
                last_filing TEXT,
                china_entity BOOLEAN,
                parent_company TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Technology trends table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tech_trends (
                technology_category TEXT,
                year INTEGER,
                total_filings INTEGER,
                china_filings INTEGER,
                us_filings INTEGER,
                eu_filings INTEGER,
                china_percentage REAL,
                growth_rate REAL,
                PRIMARY KEY (technology_category, year)
            )
        ''')

        # Nice class analysis (trademark classification)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nice_class_analysis (
                nice_class INTEGER PRIMARY KEY,
                description TEXT,
                total_marks INTEGER,
                china_marks INTEGER,
                china_percentage REAL,
                top_owners TEXT
            )
        ''')

        # Competition tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS competition_matrix (
                technology_area TEXT,
                company1 TEXT,
                country1 TEXT,
                company2 TEXT,
                country2 TEXT,
                overlap_marks INTEGER,
                competition_score REAL,
                PRIMARY KEY (technology_area, company1, company2)
            )
        ''')

        conn.commit()
        conn.close()

    def search_brands(self, search_term, technology_category):
        """Search for brands using WIPO API"""

        # Build search query
        params = {
            'q': search_term,
            'rows': 100,
            'start': 0,
            'sort': 'filing_date desc',
            'fq': [
                'status:active',
                'filing_date:[2019-01-01 TO 2024-12-31]'
            ]
        }

        # Add China filter for initial search
        china_filter = ' OR '.join([f'owner:*{entity}*' for entity in self.china_entities[:5]])
        params['fq'].append(f'({china_filter})')

        url = f"{self.api_base}/search"

        all_results = []
        total_found = 0

        try:
            # First request to get total count
            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                total_found = data.get('response', {}).get('numFound', 0)
                docs = data.get('response', {}).get('docs', [])
                all_results.extend(docs)

                # Get additional pages if needed (limit to 500 total)
                pages_to_fetch = min(5, (total_found // 100))

                for page in range(1, pages_to_fetch):
                    params['start'] = page * 100
                    response = requests.get(url, params=params, timeout=30)

                    if response.status_code == 200:
                        data = response.json()
                        docs = data.get('response', {}).get('docs', [])
                        all_results.extend(docs)

                    time.sleep(0.5)  # Rate limiting

                return all_results

        except Exception as e:
            print(f"Error searching for {search_term}: {e}")

        return []

    def analyze_trademark(self, tm_data):
        """Analyze individual trademark for China connections"""

        china_related = False

        # Check owner name
        owner = str(tm_data.get('owner', '')).lower()
        for pattern in self.china_entities:
            if pattern in owner:
                china_related = True
                break

        # Check owner country
        if tm_data.get('owner_country') in ['CN', 'CHN', 'China']:
            china_related = True

        return china_related

    def store_trademarks(self, trademarks, technology_category):
        """Store trademark data in database"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for tm in trademarks:
            china_related = self.analyze_trademark(tm)

            cursor.execute('''
                INSERT OR IGNORE INTO trademarks
                (registration_number, mark_name, owner_name, owner_country,
                 filing_date, registration_date, expiry_date, nice_classes,
                 goods_services, technology_category, china_related, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                tm.get('registration_number', ''),
                tm.get('mark_name', ''),
                tm.get('owner', ''),
                tm.get('owner_country', ''),
                tm.get('filing_date', ''),
                tm.get('registration_date', ''),
                tm.get('expiry_date', ''),
                str(tm.get('nice_classes', [])),
                tm.get('goods_services', ''),
                technology_category,
                china_related,
                tm.get('status', 'active')
            ))

        conn.commit()
        conn.close()

    def analyze_trends(self):
        """Analyze trademark trends by technology and year"""

        conn = sqlite3.connect(self.db_path)

        # Technology trends by year
        query = '''
            SELECT
                technology_category,
                substr(filing_date, 1, 4) as year,
                COUNT(*) as total_filings,
                SUM(china_related) as china_filings,
                ROUND(100.0 * SUM(china_related) / COUNT(*), 2) as china_percentage
            FROM trademarks
            WHERE filing_date IS NOT NULL
            GROUP BY technology_category, year
            ORDER BY year DESC, china_percentage DESC
        '''

        df = pd.read_sql_query(query, conn)

        # Store trends
        for _, row in df.iterrows():
            conn.execute('''
                INSERT OR REPLACE INTO tech_trends
                (technology_category, year, total_filings,
                 china_filings, china_percentage)
                VALUES (?, ?, ?, ?, ?)
            ''', (row['technology_category'], row['year'],
                  row['total_filings'], row['china_filings'],
                  row['china_percentage']))

        # Nice class analysis
        query = '''
            SELECT
                nice_classes,
                COUNT(*) as total_marks,
                SUM(china_related) as china_marks
            FROM trademarks
            GROUP BY nice_classes
        '''

        nice_df = pd.read_sql_query(query, conn)

        conn.commit()
        conn.close()

        return df

    def find_competitions(self):
        """Identify competitive overlaps in trademark filings"""

        conn = sqlite3.connect(self.db_path)

        query = '''
            SELECT technology_category, owner_name, owner_country, COUNT(*) as marks
            FROM trademarks
            GROUP BY technology_category, owner_name, owner_country
            HAVING marks > 5
            ORDER BY marks DESC
        '''

        companies = pd.read_sql_query(query, conn)

        competitions = []

        for tech in companies['technology_category'].unique():
            tech_companies = companies[companies['technology_category'] == tech]

            # Find companies with overlapping marks
            for i, company1 in tech_companies.iterrows():
                for j, company2 in tech_companies.iterrows():
                    if i < j:  # Avoid duplicates
                        overlap = min(company1['marks'], company2['marks'])

                        if overlap > 3:  # Significant overlap
                            competitions.append({
                                'technology': tech,
                                'company1': company1['owner_name'],
                                'country1': company1['owner_country'],
                                'company2': company2['owner_name'],
                                'country2': company2['owner_country'],
                                'overlap': overlap
                            })

        conn.close()

        return competitions

    def run_collection(self):
        """Execute trademark data collection"""

        print("="*80)
        print("WIPO GLOBAL BRAND DATABASE COLLECTION")
        print("="*80)

        self.create_database()

        total_marks = 0
        china_marks = 0

        for category, terms in self.search_terms.items():
            print(f"\n[{category.upper()}] Searching {len(terms)} terms:")

            for term in terms:
                print(f"  {term}: ", end='')

                # Search for trademarks
                results = self.search_brands(term, category)

                if results:
                    self.store_trademarks(results, category)

                    china_count = sum(1 for r in results if self.analyze_trademark(r))
                    total_marks += len(results)
                    china_marks += china_count

                    print(f"{len(results)} marks ({china_count} China-related)")
                else:
                    print("No results")

                time.sleep(1)  # Rate limiting

        print(f"\n\nTotal trademarks collected: {total_marks}")
        print(f"China-related marks: {china_marks} ({100*china_marks/max(total_marks,1):.1f}%)")

        # Analyze trends
        print("\nAnalyzing trends...")
        trends = self.analyze_trends()

        # Find competitions
        print("Identifying competitions...")
        competitions = self.find_competitions()

        # Generate summary report
        self.generate_report(trends, competitions)

        print(f"\n[COMPLETE] Database saved to: {self.db_path}")

        return {
            'database': str(self.db_path),
            'total_marks': total_marks,
            'china_marks': china_marks,
            'competitions': len(competitions)
        }

    def generate_report(self, trends, competitions):
        """Generate analysis report"""

        print("\n" + "="*80)
        print("WIPO TRADEMARK ANALYSIS SUMMARY")
        print("="*80)

        # Top China-dominated technologies
        if not trends.empty:
            top_china = trends.nlargest(5, 'china_percentage')

            print("\nTOP CHINA-DOMINATED TECHNOLOGY AREAS:")
            for _, row in top_china.iterrows():
                print(f"  {row['technology_category']} ({row['year']}): {row['china_percentage']:.1f}%")
                print(f"    {row['china_filings']}/{row['total_filings']} filings")

        # Key competitions
        if competitions:
            print(f"\nKEY COMPETITIVE OVERLAPS: {len(competitions)}")

            # Focus on China vs others
            china_competitions = [c for c in competitions
                                 if ('china' in c['company1'].lower() or 'china' in c['company2'].lower())]

            for comp in china_competitions[:5]:
                print(f"  {comp['technology']}: {comp['company1']} vs {comp['company2']}")

if __name__ == "__main__":
    downloader = WIPOBrandDownloader()
    results = downloader.run_collection()
    print(f"\nResults: {json.dumps(results, indent=2, default=str)}")
