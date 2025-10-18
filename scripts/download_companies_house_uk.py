#!/usr/bin/env python3
"""
Companies House UK Data Downloader
Downloads UK company data with China ownership/director analysis
Uses Companies House API
"""

import requests
import pandas as pd
import sqlite3
from pathlib import Path
import time
from datetime import datetime
import json

class CompaniesHouseDownloader:
    def __init__(self):
        self.base_path = Path("F:/OSINT_Data/CompaniesHouse_UK")
        self.base_path.mkdir(parents=True, exist_ok=True)

        self.db_path = self.base_path / f"uk_companies_{datetime.now().strftime('%Y%m%d')}.db"

        # Companies House API
        self.api_base = "https://api.company-information.service.gov.uk"

        # Note: Requires API key from https://developer.company-information.service.gov.uk/
        # For now using public endpoints that don't require auth

        # Strategic sectors to search
        self.search_terms = {
            'technology': [
                'semiconductor', 'artificial intelligence', 'quantum',
                'robotics', '5G', 'telecommunications', 'software'
            ],
            'energy': [
                'nuclear', 'renewable', 'battery', 'lithium',
                'solar', 'wind', 'hydrogen', 'electric vehicle'
            ],
            'infrastructure': [
                'port', 'airport', 'railway', 'utilities',
                'water', 'electricity', 'gas', 'telecoms'
            ],
            'defense': [
                'aerospace', 'defence', 'military', 'security',
                'surveillance', 'cyber', 'satellite'
            ],
            'biotech': [
                'pharmaceutical', 'vaccine', 'biotechnology',
                'medical device', 'diagnostic', 'therapeutic'
            ],
            'finance': [
                'investment', 'fund', 'capital', 'venture',
                'private equity', 'acquisition', 'holdings'
            ]
        }

        # China-related patterns for directors/owners
        self.china_indicators = [
            # Company name patterns
            'china', 'chinese', 'sino-', 'beijing', 'shanghai',
            'shenzhen', 'guangzhou', 'hangzhou', 'hong kong',
            'huawei', 'tencent', 'alibaba', 'baidu', 'bytedance',

            # Common Chinese surnames in directors
            'wang', 'li', 'zhang', 'liu', 'chen', 'yang',
            'huang', 'zhao', 'wu', 'zhou', 'xu', 'sun',

            # Investment entities
            'cic', 'safe', 'silk road', 'belt and road',
            'state-owned', 'sovereign wealth'
        ]

    def create_database(self):
        """Create SQL database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('PRAGMA journal_mode=WAL')

        # Companies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                company_number TEXT PRIMARY KEY,
                company_name TEXT,
                company_type TEXT,
                company_status TEXT,
                incorporation_date TEXT,
                sic_codes TEXT,
                registered_address TEXT,
                sector TEXT,
                china_connected BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Directors/Officers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS officers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_number TEXT,
                officer_name TEXT,
                officer_role TEXT,
                appointed_date TEXT,
                resigned_date TEXT,
                nationality TEXT,
                country_of_residence TEXT,
                occupation TEXT,
                china_national BOOLEAN,
                FOREIGN KEY (company_number) REFERENCES companies(company_number)
            )
        ''')

        # Ownership/PSC (Persons with Significant Control) table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ownership (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_number TEXT,
                psc_name TEXT,
                psc_type TEXT,
                nature_of_control TEXT,
                notified_date TEXT,
                nationality TEXT,
                country_of_residence TEXT,
                china_entity BOOLEAN,
                ownership_percentage TEXT,
                FOREIGN KEY (company_number) REFERENCES companies(company_number)
            )
        ''')

        # Filing history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS filings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_number TEXT,
                filing_date TEXT,
                filing_type TEXT,
                filing_description TEXT,
                FOREIGN KEY (company_number) REFERENCES companies(company_number)
            )
        ''')

        # China connections summary
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS china_connections (
                company_number TEXT PRIMARY KEY,
                company_name TEXT,
                connection_type TEXT,
                connection_details TEXT,
                risk_level TEXT,
                sector TEXT,
                first_identified TEXT
            )
        ''')

        # Sector analysis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sector_analysis (
                sector TEXT PRIMARY KEY,
                total_companies INTEGER,
                china_connected INTEGER,
                china_percentage REAL,
                key_companies TEXT,
                risk_assessment TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def search_companies(self, search_term, sector):
        """Search for companies using Companies House API"""

        # Using the search endpoint (limited without API key)
        url = f"{self.api_base}/search/companies"

        params = {
            'q': search_term,
            'items_per_page': 20
        }

        try:
            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                return data.get('items', [])
            elif response.status_code == 429:
                print("Rate limit reached, waiting...")
                time.sleep(60)  # Wait 1 minute
                return []
            else:
                return []

        except Exception as e:
            print(f"Error searching {search_term}: {e}")
            return []

    def get_company_details(self, company_number):
        """Get detailed company information"""

        url = f"{self.api_base}/company/{company_number}"

        try:
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                return response.json()

        except Exception:
            pass

        return None

    def get_officers(self, company_number):
        """Get company officers/directors"""

        url = f"{self.api_base}/company/{company_number}/officers"

        try:
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                data = response.json()
                return data.get('items', [])

        except Exception:
            pass

        return []

    def get_psc(self, company_number):
        """Get persons with significant control"""

        url = f"{self.api_base}/company/{company_number}/persons-with-significant-control"

        try:
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                data = response.json()
                return data.get('items', [])

        except Exception:
            pass

        return []

    def analyze_china_connections(self, company, officers, pscs):
        """Analyze company for China connections"""

        china_connected = False
        connection_details = []

        # Check company name
        company_name = company.get('company_name', '').lower()
        for indicator in self.china_indicators:
            if indicator in company_name:
                china_connected = True
                connection_details.append(f"Company name contains '{indicator}'")
                break

        # Check officers
        for officer in officers:
            name = officer.get('name', '').lower()
            nationality = officer.get('nationality', '').lower()
            residence = officer.get('country_of_residence', '').lower()

            # Check nationality/residence
            if 'china' in nationality or 'chinese' in nationality:
                china_connected = True
                connection_details.append(f"Officer {name} is Chinese national")
            elif 'china' in residence:
                china_connected = True
                connection_details.append(f"Officer {name} resides in China")

            # Check name patterns
            for indicator in self.china_indicators[10:22]:  # Chinese surnames
                if indicator in name.split():
                    china_connected = True
                    connection_details.append(f"Officer {name} has Chinese surname")
                    break

        # Check PSCs
        for psc in pscs:
            name = psc.get('name', '').lower()
            nationality = psc.get('nationality', '').lower()

            if 'china' in nationality or 'chinese' in nationality:
                china_connected = True
                connection_details.append(f"PSC {name} is Chinese entity")

            for indicator in self.china_indicators:
                if indicator in name:
                    china_connected = True
                    connection_details.append(f"PSC {name} contains '{indicator}'")
                    break

        return china_connected, connection_details

    def store_company_data(self, company, officers, pscs, sector):
        """Store company data in database"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        company_number = company.get('company_number')

        # Analyze China connections
        china_connected, connection_details = self.analyze_china_connections(
            company, officers, pscs
        )

        # Store company
        cursor.execute('''
            INSERT OR REPLACE INTO companies
            (company_number, company_name, company_type, company_status,
             incorporation_date, sic_codes, registered_address, sector, china_connected)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            company_number,
            company.get('company_name'),
            company.get('company_type'),
            company.get('company_status'),
            company.get('date_of_creation'),
            str(company.get('sic_codes', [])),
            str(company.get('registered_office_address', {})),
            sector,
            china_connected
        ))

        # Store officers
        for officer in officers:
            china_national = False
            nationality = officer.get('nationality', '').lower()
            if 'china' in nationality or 'chinese' in nationality:
                china_national = True

            cursor.execute('''
                INSERT OR IGNORE INTO officers
                (company_number, officer_name, officer_role, appointed_date,
                 resigned_date, nationality, country_of_residence, occupation, china_national)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company_number,
                officer.get('name'),
                officer.get('officer_role'),
                officer.get('appointed_on'),
                officer.get('resigned_on'),
                officer.get('nationality'),
                officer.get('country_of_residence'),
                officer.get('occupation'),
                china_national
            ))

        # Store PSCs
        for psc in pscs:
            china_entity = False
            nationality = psc.get('nationality', '').lower()
            name = psc.get('name', '').lower()

            if 'china' in nationality or any(ind in name for ind in self.china_indicators):
                china_entity = True

            cursor.execute('''
                INSERT OR IGNORE INTO ownership
                (company_number, psc_name, psc_type, nature_of_control,
                 notified_date, nationality, country_of_residence, china_entity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company_number,
                psc.get('name'),
                psc.get('kind'),
                str(psc.get('natures_of_control', [])),
                psc.get('notified_on'),
                psc.get('nationality'),
                psc.get('country_of_residence'),
                china_entity
            ))

        # Store China connections if found
        if china_connected:
            risk_level = 'HIGH' if len(connection_details) > 2 else 'MEDIUM'

            cursor.execute('''
                INSERT OR REPLACE INTO china_connections
                (company_number, company_name, connection_type, connection_details,
                 risk_level, sector, first_identified)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                company_number,
                company.get('company_name'),
                'Multiple' if len(connection_details) > 1 else 'Single',
                '; '.join(connection_details),
                risk_level,
                sector,
                datetime.now().isoformat()
            ))

        conn.commit()
        conn.close()

    def generate_report(self):
        """Generate analysis report"""

        conn = sqlite3.connect(self.db_path)

        print("\n" + "="*80)
        print("UK COMPANIES CHINA CONNECTION ANALYSIS")
        print("="*80)

        # Overall statistics
        cursor = conn.execute('''
            SELECT COUNT(*), SUM(china_connected)
            FROM companies
        ''')
        total, china_connected = cursor.fetchone()

        if total:
            print(f"\nTotal companies analyzed: {total}")
            print(f"China-connected companies: {china_connected or 0}")
            print(f"Percentage: {100*(china_connected or 0)/total:.1f}%")

        # By sector
        cursor = conn.execute('''
            SELECT sector, COUNT(*) as total, SUM(china_connected) as china_count
            FROM companies
            GROUP BY sector
            ORDER BY china_count DESC
        ''')

        print("\nCHINA CONNECTIONS BY SECTOR:")
        for row in cursor:
            if row[2]:
                print(f"  {row[0]}: {row[2]}/{row[1]} companies ({100*row[2]/row[1]:.1f}%)")

        # High-risk connections
        cursor = conn.execute('''
            SELECT company_name, sector, connection_details
            FROM china_connections
            WHERE risk_level = 'HIGH'
            LIMIT 10
        ''')

        high_risk = cursor.fetchall()
        if high_risk:
            print("\nHIGH-RISK CHINA CONNECTIONS:")
            for company in high_risk:
                print(f"\n  {company[0]} ({company[1]})")
                print(f"    {company[2]}")

        conn.close()

    def run_collection(self):
        """Execute data collection"""

        print("="*80)
        print("COMPANIES HOUSE UK DATA COLLECTION")
        print("="*80)

        self.create_database()

        total_companies = 0
        china_companies = 0

        for sector, terms in self.search_terms.items():
            print(f"\n[{sector.upper()}] Searching {len(terms)} terms:")

            for term in terms[:3]:  # Limit to 3 per sector for testing
                print(f"  {term}: ", end='')

                companies = self.search_companies(term, sector)

                if companies:
                    for company in companies[:5]:  # Limit to 5 companies per term
                        company_number = company.get('company_number')

                        # Get details
                        details = self.get_company_details(company_number)
                        if details:
                            officers = self.get_officers(company_number)
                            pscs = self.get_psc(company_number)

                            self.store_company_data(details, officers, pscs, sector)

                            china_connected, _ = self.analyze_china_connections(
                                details, officers, pscs
                            )

                            total_companies += 1
                            if china_connected:
                                china_companies += 1

                        time.sleep(0.5)  # Rate limiting

                    print(f"{len(companies)} found")
                else:
                    print("No results")

                time.sleep(1)  # Rate limiting between searches

        self.generate_report()

        print(f"\n[COMPLETE] Database saved to: {self.db_path}")

        return {
            'database': str(self.db_path),
            'total_companies': total_companies,
            'china_connected': china_companies
        }

if __name__ == "__main__":
    downloader = CompaniesHouseDownloader()
    results = downloader.run_collection()
    print(f"\nResults: {json.dumps(results, indent=2, default=str)}")
