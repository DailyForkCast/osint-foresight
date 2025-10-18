#!/usr/bin/env python3
"""
USPTO Patent Data Downloader
Downloads patent data for strategic technology areas with China focus
Uses PatentsView API v2
"""

import requests
import pandas as pd
import sqlite3
from pathlib import Path
import time
from datetime import datetime, timedelta
import json

class USPTOPatentDownloader:
    def __init__(self):
        self.base_path = Path("F:/OSINT_Data/USPTO")
        self.base_path.mkdir(parents=True, exist_ok=True)

        self.db_path = self.base_path / f"uspto_patents_{datetime.now().strftime('%Y%m%d')}.db"

        # PatentsView API v2 endpoints
        self.api_base = "https://api.patentsview.org"

        # Strategic CPC codes (Cooperative Patent Classification)
        self.strategic_cpcs = {
            'semiconductors': [
                'H01L',  # Semiconductor devices
                'H03K',  # Pulse technique (logic circuits)
                'G11C',  # Static memory (SRAM/DRAM)
            ],
            'telecommunications': [
                'H04W',  # Wireless networks
                'H04L',  # Digital data transmission
                'H04B',  # Transmission systems
            ],
            'artificial_intelligence': [
                'G06N',  # Computer systems based on computational models
                'G06F',  # Electric digital data processing
                'G10L',  # Speech analysis/synthesis
            ],
            'quantum': [
                'G06N10',  # Quantum computing
                'H04L9',   # Quantum cryptography
                'B82Y',    # Nanostructures for quantum
            ],
            'biotechnology': [
                'C12N',  # Microorganisms/enzymes
                'A61K',  # Medical preparations
                'C07K',  # Peptides
            ],
            'batteries': [
                'H01M',  # Batteries, fuel cells
                'H02J',  # Circuit arrangements for batteries
                'B60L',  # Electric vehicle propulsion
            ],
            'aerospace': [
                'B64C',  # Aeroplanes, helicopters
                'B64D',  # Aircraft equipment
                'B64G',  # Spacecraft
            ],
            'robotics': [
                'B25J',  # Manipulators, robots
                'B62D',  # Motor vehicles (autonomous)
                'G05D',  # Control systems
            ]
        }

        # China-related assignee patterns
        self.china_patterns = [
            'huawei', 'xiaomi', 'oppo', 'vivo', 'zte', 'lenovo',
            'alibaba', 'tencent', 'baidu', 'bytedance', 'dji',
            'boe', 'tcl', 'haier', 'midea', 'gree', 'byd',
            'smic', 'tsmc', 'foxconn', 'wuxi', 'shanghai',
            'beijing', 'shenzhen', 'hangzhou', 'guangzhou',
            'chinese academy', 'tsinghua', 'peking university',
            'zhejiang', 'fudan', 'nanjing', 'harbin'
        ]

    def create_database(self):
        """Create SQL database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('PRAGMA journal_mode=WAL')

        # Patents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patents (
                patent_number TEXT PRIMARY KEY,
                patent_title TEXT,
                patent_date TEXT,
                patent_type TEXT,
                assignee_organization TEXT,
                assignee_country TEXT,
                inventor_country TEXT,
                cpc_group TEXT,
                cpc_subclass TEXT,
                technology_category TEXT,
                abstract TEXT,
                claims_count INTEGER,
                cited_by_count INTEGER,
                china_related BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Assignees analysis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assignees (
                assignee_id TEXT PRIMARY KEY,
                assignee_name TEXT,
                assignee_country TEXT,
                total_patents INTEGER,
                first_patent_date TEXT,
                last_patent_date TEXT,
                main_technology TEXT,
                china_entity BOOLEAN,
                subsidiary_of TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Technology trends
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS technology_trends (
                year INTEGER,
                technology_category TEXT,
                cpc_code TEXT,
                total_patents INTEGER,
                china_patents INTEGER,
                us_patents INTEGER,
                eu_patents INTEGER,
                china_percentage REAL,
                growth_rate REAL,
                PRIMARY KEY (year, technology_category, cpc_code)
            )
        ''')

        # Cross-citations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS citations (
                citing_patent TEXT,
                cited_patent TEXT,
                citation_date TEXT,
                citing_assignee TEXT,
                cited_assignee TEXT,
                citing_country TEXT,
                cited_country TEXT,
                technology_transfer BOOLEAN,
                PRIMARY KEY (citing_patent, cited_patent)
            )
        ''')

        # Collaboration patterns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collaborations (
                patent_number TEXT,
                assignee1 TEXT,
                assignee2 TEXT,
                country1 TEXT,
                country2 TEXT,
                collaboration_type TEXT,
                technology_area TEXT,
                year INTEGER,
                PRIMARY KEY (patent_number, assignee1, assignee2)
            )
        ''')

        conn.commit()
        conn.close()

    def search_patents(self, cpc_code, start_date, end_date, china_focus=True):
        """Search patents using PatentsView API"""

        # Build query
        query = {
            "patent_date": f"[{start_date} TO {end_date}]",
            "_and": [
                {"cpc_subgroup_id": {"_begins": cpc_code}}
            ]
        }

        if china_focus:
            # Add China-related filters
            china_conditions = []
            for pattern in self.china_patterns[:10]:  # Top patterns
                china_conditions.append(
                    {"assignee_organization": {"_contains": pattern}}
                )

            query["_and"].append({"_or": china_conditions})

        # Fields to retrieve
        fields = [
            "patent_number",
            "patent_title",
            "patent_date",
            "patent_type",
            "patent_abstract",
            "assignee_organization",
            "assignee_country",
            "inventor_country",
            "cpc_subgroup_id",
            "cited_patent_count",
            "claims"
        ]

        # API request
        params = {
            'q': json.dumps(query),
            'f': json.dumps(fields),
            'o': json.dumps({
                'page': 1,
                'per_page': 100
            })
        }

        url = f"{self.api_base}/patents/query"

        all_patents = []
        page = 1
        max_pages = 10  # Limit for testing

        while page <= max_pages:
            params['o'] = json.dumps({
                'page': page,
                'per_page': 100
            })

            try:
                response = requests.get(url, params=params, timeout=30)

                if response.status_code == 200:
                    data = response.json()

                    if 'patents' in data and data['patents']:
                        all_patents.extend(data['patents'])

                        if len(data['patents']) < 100:
                            break  # No more results

                        page += 1
                        time.sleep(0.5)  # Rate limiting
                    else:
                        break
                else:
                    print(f"API error: {response.status_code}")
                    break

            except Exception as e:
                print(f"Error fetching patents: {e}")
                break

        return all_patents

    def analyze_patent(self, patent_data):
        """Analyze individual patent for China connections"""

        china_related = False

        # Check assignee
        assignee = patent_data.get('assignee_organization', '')
        if assignee:
            assignee_lower = assignee.lower()
            for pattern in self.china_patterns:
                if pattern in assignee_lower:
                    china_related = True
                    break

        # Check assignee country
        if patent_data.get('assignee_country') == 'CN':
            china_related = True

        # Check inventor country
        if patent_data.get('inventor_country') == 'CN':
            china_related = True

        return china_related

    def store_patents(self, patents, technology_category, cpc_code):
        """Store patents in database"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for patent in patents:
            china_related = self.analyze_patent(patent)

            cursor.execute('''
                INSERT OR REPLACE INTO patents
                (patent_number, patent_title, patent_date, patent_type,
                 assignee_organization, assignee_country, inventor_country,
                 cpc_group, cpc_subclass, technology_category, abstract,
                 claims_count, cited_by_count, china_related)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                patent.get('patent_number'),
                patent.get('patent_title'),
                patent.get('patent_date'),
                patent.get('patent_type'),
                patent.get('assignee_organization'),
                patent.get('assignee_country'),
                patent.get('inventor_country'),
                cpc_code,
                patent.get('cpc_subgroup_id', ''),
                technology_category,
                patent.get('patent_abstract', ''),
                len(patent.get('claims', [])) if patent.get('claims') else 0,
                patent.get('cited_patent_count', 0),
                china_related
            ))

        conn.commit()
        conn.close()

    def analyze_trends(self):
        """Analyze patent trends by year and technology"""

        conn = sqlite3.connect(self.db_path)

        # Yearly trends by technology
        query = '''
            SELECT
                substr(patent_date, 1, 4) as year,
                technology_category,
                cpc_group,
                COUNT(*) as total_patents,
                SUM(china_related) as china_patents,
                ROUND(100.0 * SUM(china_related) / COUNT(*), 2) as china_percentage
            FROM patents
            GROUP BY year, technology_category, cpc_group
            ORDER BY year DESC, china_percentage DESC
        '''

        df = pd.read_sql_query(query, conn)

        # Store trends
        for _, row in df.iterrows():
            conn.execute('''
                INSERT OR REPLACE INTO technology_trends
                (year, technology_category, cpc_code, total_patents,
                 china_patents, china_percentage)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (row['year'], row['technology_category'], row['cpc_group'],
                  row['total_patents'], row['china_patents'], row['china_percentage']))

        conn.commit()
        conn.close()

        return df

    def find_collaborations(self):
        """Identify US-China patent collaborations"""

        conn = sqlite3.connect(self.db_path)

        # Find patents with multiple assignees from different countries
        query = '''
            SELECT patent_number, assignee_organization, assignee_country
            FROM patents
            WHERE assignee_organization LIKE '%,%'
               OR assignee_organization LIKE '%;%'
        '''

        multi_assignee = pd.read_sql_query(query, conn)

        collaborations = []

        for patent_num in multi_assignee['patent_number'].unique():
            patent_data = multi_assignee[multi_assignee['patent_number'] == patent_num]

            # Parse multiple assignees
            assignees = str(patent_data.iloc[0]['assignee_organization']).split(';')

            if len(assignees) > 1:
                # Check for international collaboration
                countries = set()
                for assignee in assignees:
                    if any(pattern in assignee.lower() for pattern in self.china_patterns):
                        countries.add('CN')
                    else:
                        countries.add('US')  # Default assumption

                if 'CN' in countries and len(countries) > 1:
                    collaborations.append({
                        'patent_number': patent_num,
                        'assignees': assignees,
                        'collaboration_type': 'US-China',
                        'year': patent_data.iloc[0]['patent_date'][:4] if pd.notna(patent_data.iloc[0]['patent_date']) else None
                    })

        conn.close()

        return collaborations

    def run_collection(self):
        """Execute patent data collection"""

        print("="*80)
        print("USPTO PATENT DATA COLLECTION")
        print("="*80)

        self.create_database()

        # Define date range (last 5 years)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=5*365)).strftime('%Y-%m-%d')

        total_patents = 0
        china_patents = 0

        for category, cpc_codes in self.strategic_cpcs.items():
            print(f"\n[{category.upper()}] Processing {len(cpc_codes)} CPC codes:")

            for cpc_code in cpc_codes:
                print(f"  {cpc_code}: ", end='')

                # Search with China focus
                patents = self.search_patents(cpc_code, start_date, end_date, china_focus=True)

                if patents:
                    self.store_patents(patents, category, cpc_code)

                    china_count = sum(1 for p in patents if self.analyze_patent(p))
                    total_patents += len(patents)
                    china_patents += china_count

                    print(f"{len(patents)} patents ({china_count} China-related)")
                else:
                    print("No patents found")

                time.sleep(1)  # Rate limiting

        print(f"\n\nTotal patents collected: {total_patents}")
        print(f"China-related patents: {china_patents} ({100*china_patents/max(total_patents,1):.1f}%)")

        # Analyze trends
        print("\nAnalyzing trends...")
        trends = self.analyze_trends()

        # Find collaborations
        print("Finding collaborations...")
        collaborations = self.find_collaborations()

        # Generate summary report
        self.generate_report(trends, collaborations)

        print(f"\n[COMPLETE] Database saved to: {self.db_path}")

        return {
            'database': str(self.db_path),
            'total_patents': total_patents,
            'china_patents': china_patents,
            'collaborations': len(collaborations)
        }

    def generate_report(self, trends, collaborations):
        """Generate analysis report"""

        print("\n" + "="*80)
        print("USPTO PATENT ANALYSIS SUMMARY")
        print("="*80)

        # Top China-dominated technologies
        if not trends.empty:
            top_china = trends.nlargest(5, 'china_percentage')

            print("\nTOP CHINA-DOMINATED TECHNOLOGIES:")
            for _, row in top_china.iterrows():
                print(f"  {row['technology_category']} ({row['cpc_code']}): {row['china_percentage']:.1f}%")
                print(f"    {row['china_patents']}/{row['total_patents']} patents in {row['year']}")

        # Collaboration patterns
        if collaborations:
            print(f"\nUS-CHINA COLLABORATIONS: {len(collaborations)} patents")

            # Group by year
            collab_by_year = {}
            for collab in collaborations:
                year = collab.get('year')
                if year:
                    collab_by_year[year] = collab_by_year.get(year, 0) + 1

            for year in sorted(collab_by_year.keys(), reverse=True)[:5]:
                print(f"  {year}: {collab_by_year[year]} collaborative patents")

if __name__ == "__main__":
    downloader = USPTOPatentDownloader()
    results = downloader.run_collection()
    print(f"\nResults: {json.dumps(results, indent=2)}")
