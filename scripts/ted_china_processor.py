#!/usr/bin/env python3
"""
TED Procurement China Analysis Processor
Processes EU TED (Tenders Electronic Daily) data for China-related procurement
"""

import os
import json
import sqlite3
import tarfile
import gzip
from datetime import datetime
from typing import Dict, List, Set
from pathlib import Path
import xml.etree.ElementTree as ET

class TEDChinaProcessor:
    def __init__(self):
        self.base_path = Path("F:/TED_Data/monthly")
        self.db_path = Path("F:/OSINT_WAREHOUSE/ted_china_analysis.db")
        self.output_path = Path("C:/Projects/OSINT - Foresight/analysis")

        # China-related keywords
        self.china_keywords = {
            'companies': [
                'huawei', 'zte', 'hikvision', 'dahua', 'alibaba', 'tencent',
                'xiaomi', 'lenovo', 'dji', 'byd', 'smic', 'baidu', 'bytedance',
                'china mobile', 'china telecom', 'china unicom', 'sinopec',
                'china national', 'sinochem', 'cofco', 'geely', 'haier'
            ],
            'technology': [
                '5g', 'artificial intelligence', 'ai', 'surveillance', 'facial recognition',
                'smart city', 'iot', 'quantum', 'semiconductor', 'microchip',
                'telecommunication', 'cyber', 'drone', 'autonomous', 'robotics'
            ],
            'countries': [
                'china', 'chinese', 'prc', 'beijing', 'shanghai', 'shenzhen',
                'hong kong', 'macau'
            ]
        }

        self.setup_database()

    def setup_database(self):
        """Create SQLite database for TED China analysis"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('''
            CREATE TABLE IF NOT EXISTS ted_china_contracts (
                id TEXT PRIMARY KEY,
                publication_date DATE,
                country TEXT,
                contracting_authority TEXT,
                contractor TEXT,
                contract_title TEXT,
                contract_value REAL,
                currency TEXT,
                cpv_codes TEXT,
                china_relevance_score INTEGER,
                matched_keywords TEXT,
                technology_categories TEXT,
                risk_level TEXT,
                processed_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS processing_stats (
                year INTEGER,
                month INTEGER,
                total_contracts INTEGER,
                china_related INTEGER,
                total_value REAL,
                china_value REAL,
                processed_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (year, month)
            )
        ''')

        conn.commit()
        conn.close()

    def process_year(self, year: int):
        """Process one year of TED data"""
        year_path = self.base_path / str(year)
        if not year_path.exists():
            print(f"Year {year} not found")
            return

        results = {
            'year': year,
            'total_files': 0,
            'china_contracts': [],
            'stats': {}
        }

        # Process each monthly tar.gz file
        for tar_file in year_path.glob("*.tar.gz"):
            print(f"Processing {tar_file.name}...")
            month_results = self.process_monthly_archive(tar_file)
            results['china_contracts'].extend(month_results)
            results['total_files'] += 1

        # Save results
        self.save_results(year, results)
        return results

    def process_monthly_archive(self, tar_path: Path) -> List[Dict]:
        """Process a monthly tar.gz archive"""
        china_contracts = []

        try:
            with tarfile.open(tar_path, 'r:gz') as tar:
                for member in tar.getmembers():
                    if member.name.endswith('.xml'):
                        try:
                            f = tar.extractfile(member)
                            if f:
                                content = f.read()
                                contract_data = self.parse_ted_xml(content)
                                if contract_data and self.is_china_related(contract_data):
                                    china_contracts.append(contract_data)
                        except Exception as e:
                            continue
        except Exception as e:
            print(f"Error processing {tar_path}: {e}")

        return china_contracts

    def parse_ted_xml(self, xml_content: bytes) -> Dict:
        """Parse TED XML notice"""
        try:
            root = ET.fromstring(xml_content)

            # Extract key fields (simplified for demo)
            contract = {
                'id': self.get_xml_text(root, ".//NOTICE_ID"),
                'date': self.get_xml_text(root, ".//DATE_PUB"),
                'country': self.get_xml_text(root, ".//ISO_COUNTRY"),
                'authority': self.get_xml_text(root, ".//CA_NAME"),
                'contractor': self.get_xml_text(root, ".//CONTRACTOR_NAME"),
                'title': self.get_xml_text(root, ".//TITLE"),
                'description': self.get_xml_text(root, ".//SHORT_DESCR"),
                'value': self.get_xml_value(root, ".//VAL_TOTAL"),
                'currency': self.get_xml_text(root, ".//CURRENCY"),
                'cpv': self.get_xml_text(root, ".//CPV_CODE")
            }

            return contract if contract['id'] else None

        except Exception as e:
            return None

    def get_xml_text(self, root, xpath: str) -> str:
        """Safely extract text from XML"""
        elem = root.find(xpath)
        return elem.text if elem is not None and elem.text else ""

    def get_xml_value(self, root, xpath: str) -> float:
        """Extract numeric value from XML"""
        text = self.get_xml_text(root, xpath)
        try:
            return float(text.replace(',', '').replace(' ', ''))
        except:
            return 0.0

    def is_china_related(self, contract: Dict) -> bool:
        """Check if contract is China-related"""
        relevance_score = 0
        matched_keywords = []

        # Check all text fields
        text_to_check = ' '.join([
            contract.get('contractor', ''),
            contract.get('title', ''),
            contract.get('description', ''),
            contract.get('authority', '')
        ]).lower()

        # Check for Chinese companies
        for company in self.china_keywords['companies']:
            if company in text_to_check:
                relevance_score += 10
                matched_keywords.append(f"company:{company}")

        # Check for technology keywords
        for tech in self.china_keywords['technology']:
            if tech in text_to_check:
                relevance_score += 5
                matched_keywords.append(f"tech:{tech}")

        # Check for China references
        for country in self.china_keywords['countries']:
            if country in text_to_check:
                relevance_score += 8
                matched_keywords.append(f"country:{country}")

        if relevance_score > 0:
            contract['relevance_score'] = relevance_score
            contract['matched_keywords'] = matched_keywords
            contract['risk_level'] = self.assess_risk_level(relevance_score, contract)
            return True

        return False

    def assess_risk_level(self, score: int, contract: Dict) -> str:
        """Assess risk level based on relevance and value"""
        value = contract.get('value', 0)

        if score >= 20 or value > 10_000_000:
            return "HIGH"
        elif score >= 10 or value > 1_000_000:
            return "MEDIUM"
        else:
            return "LOW"

    def save_results(self, year: int, results: Dict):
        """Save results to database and generate report"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Insert contracts
        for contract in results['china_contracts']:
            cur.execute('''
                INSERT OR REPLACE INTO ted_china_contracts
                (id, publication_date, country, contracting_authority, contractor,
                 contract_title, contract_value, currency, cpv_codes,
                 china_relevance_score, matched_keywords, risk_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                contract.get('id'),
                contract.get('date'),
                contract.get('country'),
                contract.get('authority'),
                contract.get('contractor'),
                contract.get('title'),
                contract.get('value', 0),
                contract.get('currency', 'EUR'),
                contract.get('cpv'),
                contract.get('relevance_score', 0),
                json.dumps(contract.get('matched_keywords', [])),
                contract.get('risk_level', 'LOW')
            ))

        conn.commit()
        conn.close()

        print(f"Year {year}: Found {len(results['china_contracts'])} China-related contracts")

    def generate_intelligence_brief(self):
        """Generate intelligence brief from processed data"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Get summary statistics
        cur.execute('''
            SELECT
                COUNT(*) as total_contracts,
                SUM(contract_value) as total_value,
                COUNT(DISTINCT contracting_authority) as unique_authorities,
                COUNT(DISTINCT contractor) as unique_contractors
            FROM ted_china_contracts
        ''')
        stats = cur.fetchone()

        # Get top contractors
        cur.execute('''
            SELECT contractor, COUNT(*) as contract_count, SUM(contract_value) as total_value
            FROM ted_china_contracts
            WHERE contractor != ''
            GROUP BY contractor
            ORDER BY total_value DESC
            LIMIT 10
        ''')
        top_contractors = cur.fetchall()

        # Get high-risk contracts
        cur.execute('''
            SELECT * FROM ted_china_contracts
            WHERE risk_level = 'HIGH'
            ORDER BY contract_value DESC
            LIMIT 20
        ''')
        high_risk = cur.fetchall()

        conn.close()

        # Generate report
        report = f"""# TED CHINA PROCUREMENT INTELLIGENCE BRIEF
Generated: {datetime.now().isoformat()}

## EXECUTIVE SUMMARY
- **Total China-Related Contracts**: {stats[0]:,}
- **Total Contract Value**: €{stats[1]:,.2f} if stats[1] else 0
- **Unique Contracting Authorities**: {stats[2]:,}
- **Unique Chinese Contractors**: {stats[3]:,}

## TOP CHINESE CONTRACTORS IN EU PROCUREMENT

"""
        for contractor, count, value in top_contractors:
            report += f"- **{contractor}**: {count} contracts, €{value:,.2f}\n"

        report += f"""
## HIGH-RISK CONTRACTS REQUIRING REVIEW

"""
        for contract in high_risk[:10]:
            report += f"""### {contract[4]} ({contract[2]})
- **Authority**: {contract[3]}
- **Value**: €{contract[6]:,.2f}
- **Risk Level**: {contract[12]}
- **Keywords**: {contract[10]}

"""

        # Save report
        report_path = self.output_path / "TED_CHINA_INTELLIGENCE_BRIEF.md"
        report_path.write_text(report)
        print(f"Intelligence brief saved to {report_path}")

        return report

def main():
    processor = TEDChinaProcessor()

    # Process recent years first (they're most relevant)
    years_to_process = [2024, 2023, 2022, 2021, 2020]

    print("TED China Procurement Processor")
    print("=" * 50)

    for year in years_to_process:
        print(f"\nProcessing year {year}...")
        processor.process_year(year)

    # Generate intelligence brief
    print("\nGenerating intelligence brief...")
    processor.generate_intelligence_brief()

    print("\nProcessing complete!")
    print(f"Database: F:/OSINT_WAREHOUSE/ted_china_analysis.db")
    print(f"Report: C:/Projects/OSINT - Foresight/analysis/TED_CHINA_INTELLIGENCE_BRIEF.md")

if __name__ == "__main__":
    main()
