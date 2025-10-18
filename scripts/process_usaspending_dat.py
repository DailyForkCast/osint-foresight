"""
USAspending DAT.GZ PostgreSQL Dump Processor
Processes compressed PostgreSQL dumps from USAspending
"""

import os
import gzip
import json
import sqlite3
import re
from datetime import datetime
from typing import Dict, List, Generator

class USAspendingDATProcessor:
    def __init__(self):
        self.db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.raw_path = "F:/OSINT_Data/USASPENDING/extracted_data"
        self.output_path = "data/processed/usaspending_dat_analysis"

        # China detection patterns
        self.china_patterns = {
            'companies': [
                'huawei', 'zte', 'hikvision', 'dahua', 'hytera',
                'lenovo', 'dji', 'tiktok', 'bytedance', 'alibaba',
                'tencent', 'baidu', 'xiaomi', 'tcl', 'byd'
            ],
            'keywords': [
                'china', 'chinese', 'beijing', 'shanghai', 'hong kong',
                'prc', 'people\'s republic', 'sino-'
            ],
            'sensitive_tech': [
                '5g', 'artificial intelligence', 'quantum', 'semiconductor',
                'aerospace', 'nuclear', 'biotechnology', 'surveillance',
                'cryptograph', 'cyber', 'satellite', 'missile', 'radar'
            ]
        }

        os.makedirs(self.output_path, exist_ok=True)
        self.stats = {
            'files_processed': 0,
            'records_extracted': 0,
            'china_relevant': 0,
            'total_value': 0
        }

    def process(self):
        print(f"[{datetime.now()}] Starting USAspending DAT processing...")

        # Find all .dat.gz files
        dat_files = []
        if os.path.exists(self.raw_path):
            dat_files = [f for f in os.listdir(self.raw_path) if f.endswith('.dat.gz')]
        else:
            # Check if files are directly in USASPENDING folder
            alt_path = "F:/OSINT_Data/USASPENDING"
            if os.path.exists(alt_path):
                dat_files = [f for f in os.listdir(alt_path) if f.endswith('.dat.gz')]
                self.raw_path = alt_path

        print(f"Found {len(dat_files)} .dat.gz files")

        all_contracts = []
        contractor_analysis = {}
        agency_exposure = {}

        # Process each DAT file
        for i, dat_file in enumerate(dat_files, 1):
            print(f"Processing {i}/{len(dat_files)}: {dat_file}")
            self.stats['files_processed'] += 1

            file_path = os.path.join(self.raw_path, dat_file)
            contracts = self.parse_dat_file(file_path)

            for contract in contracts:
                self.stats['records_extracted'] += 1

                if self.is_china_relevant(contract):
                    self.stats['china_relevant'] += 1
                    all_contracts.append(contract)

                    # Track contractor
                    vendor = contract.get('vendor_name', 'Unknown')
                    if vendor not in contractor_analysis:
                        contractor_analysis[vendor] = {
                            'count': 0,
                            'total_value': 0,
                            'contracts': [],
                            'risk_flags': []
                        }

                    contractor_analysis[vendor]['count'] += 1
                    contractor_analysis[vendor]['total_value'] += contract.get('amount', 0)
                    contractor_analysis[vendor]['contracts'].append(contract['id'])

                    # Add risk flags
                    risk_flags = self.assess_risks(contract)
                    contractor_analysis[vendor]['risk_flags'].extend(risk_flags)

                    # Track agency
                    agency = contract.get('agency', 'Unknown')
                    agency_exposure[agency] = agency_exposure.get(agency, 0) + 1

                    self.stats['total_value'] += contract.get('amount', 0)

        # Save results
        self.save_results(all_contracts, contractor_analysis, agency_exposure)

        print(f"\n=== USAspending Processing Complete ===")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Records extracted: {self.stats['records_extracted']:,}")
        print(f"China-relevant contracts: {self.stats['china_relevant']:,}")
        print(f"Total contract value: ${self.stats['total_value']:,.2f}")

        return self.stats['china_relevant']

    def parse_dat_file(self, file_path: str) -> List[Dict]:
        """Parse PostgreSQL dump data from .dat.gz file"""
        contracts = []

        try:
            with gzip.open(file_path, 'rt', encoding='utf-8', errors='ignore') as f:
                content = f.read()

                # Look for COPY data sections (PostgreSQL format)
                copy_sections = re.findall(r'COPY.*?\n(.*?)\\\.', content, re.DOTALL)

                for section in copy_sections:
                    lines = section.strip().split('\n')
                    for line in lines[:1000]:  # Process first 1000 lines per section
                        if line and not line.startswith('--'):
                            # Parse tab-separated values
                            fields = line.split('\t')

                            if len(fields) >= 10:
                                contract = self.extract_contract_from_fields(fields)
                                if contract:
                                    contracts.append(contract)

                # Also try to find JSON data
                json_matches = re.findall(r'\{[^{}]*"vendor"[^{}]*\}', content)
                for match in json_matches[:100]:
                    try:
                        data = json.loads(match)
                        contracts.append(self.normalize_contract(data))
                    except:
                        pass

        except Exception as e:
            print(f"  Error parsing {file_path}: {e}")

        return contracts

    def extract_contract_from_fields(self, fields: List[str]) -> Dict:
        """Extract contract data from tab-separated fields"""
        try:
            # Basic contract structure (adjust based on actual schema)
            contract = {
                'id': fields[0] if len(fields) > 0 else '',
                'vendor_name': fields[1] if len(fields) > 1 else '',
                'amount': self.parse_amount(fields[2] if len(fields) > 2 else '0'),
                'agency': fields[3] if len(fields) > 3 else '',
                'description': fields[4] if len(fields) > 4 else '',
                'date': fields[5] if len(fields) > 5 else '',
                'naics': fields[6] if len(fields) > 6 else '',
                'country': fields[7] if len(fields) > 7 else ''
            }

            # Only return if it has meaningful data
            if contract['vendor_name'] or contract['description']:
                return contract
        except:
            pass

        return None

    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float"""
        try:
            # Remove currency symbols and commas
            clean = re.sub(r'[^\d.-]', '', amount_str)
            return float(clean) if clean else 0
        except:
            return 0

    def normalize_contract(self, data: Dict) -> Dict:
        """Normalize contract data from various formats"""
        return {
            'id': data.get('contract_id', data.get('award_id', '')),
            'vendor_name': data.get('vendor_name', data.get('recipient_name', '')),
            'amount': float(data.get('amount', data.get('total_obligation', 0))),
            'agency': data.get('agency', data.get('awarding_agency', '')),
            'description': data.get('description', data.get('award_description', '')),
            'date': data.get('date', data.get('action_date', '')),
            'naics': data.get('naics', data.get('naics_code', '')),
            'country': data.get('country', data.get('vendor_country', ''))
        }

    def is_china_relevant(self, contract: Dict) -> bool:
        """Check if contract is China-relevant"""
        text = (contract.get('vendor_name', '') + ' ' +
                contract.get('description', '')).lower()

        # Check for Chinese companies
        for company in self.china_patterns['companies']:
            if company in text:
                return True

        # Check for China keywords
        for keyword in self.china_patterns['keywords']:
            if keyword in text:
                return True

        # Check for sensitive technology
        for tech in self.china_patterns['sensitive_tech']:
            if tech in text:
                # Extra scrutiny for sensitive tech
                if contract.get('amount', 0) > 1000000:  # $1M+
                    return True

        # Check vendor country
        if contract.get('country', '').lower() in ['china', 'hong kong', 'prc']:
            return True

        return False

    def assess_risks(self, contract: Dict) -> List[str]:
        """Assess risk flags for contract"""
        risks = []

        vendor = contract.get('vendor_name', '').lower()
        description = contract.get('description', '').lower()

        # Direct Chinese company
        for company in self.china_patterns['companies']:
            if company in vendor:
                risks.append(f'Chinese entity: {company}')

        # Sensitive technology
        for tech in self.china_patterns['sensitive_tech']:
            if tech in description:
                risks.append(f'Sensitive tech: {tech}')

        # High value
        if contract.get('amount', 0) > 10000000:
            risks.append(f'High value: ${contract["amount"]:,.0f}')

        # Foreign vendor
        if contract.get('country') and contract['country'].lower() != 'usa':
            risks.append(f'Foreign vendor: {contract["country"]}')

        return risks

    def save_results(self, contracts: List, contractors: Dict, agencies: Dict):
        """Save analysis results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(self.output_path, f'usaspending_analysis_{timestamp}.json')

        # Get top risky contractors
        top_contractors = sorted(contractors.items(),
                               key=lambda x: x[1]['total_value'],
                               reverse=True)[:50]

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'extraction_date': datetime.now().isoformat(),
                'stats': self.stats,
                'top_contractors': [
                    {
                        'name': name,
                        'count': data['count'],
                        'total_value': data['total_value'],
                        'unique_risks': list(set(data['risk_flags']))
                    } for name, data in top_contractors
                ],
                'agency_exposure': sorted(agencies.items(),
                                         key=lambda x: x[1],
                                         reverse=True)[:20],
                'sample_contracts': contracts[:100]
            }, f, indent=2)

        print(f"Saved analysis to {output_file}")

        # Save to database
        self.save_to_database(contracts, contractors)

    def save_to_database(self, contracts: List, contractors: Dict):
        """Save to SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('''CREATE TABLE IF NOT EXISTS usaspending_dat_contracts
                       (id TEXT PRIMARY KEY, vendor_name TEXT, amount REAL,
                        agency TEXT, description TEXT, date TEXT,
                        risk_flags TEXT, processed_date TEXT)''')

        for contract in contracts[:10000]:  # Save first 10k
            risks = self.assess_risks(contract)
            cur.execute('''INSERT OR REPLACE INTO usaspending_dat_contracts
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (contract['id'], contract['vendor_name'],
                        contract['amount'], contract['agency'],
                        contract['description'], contract['date'],
                        json.dumps(risks), datetime.now().isoformat()))

        conn.commit()
        conn.close()

if __name__ == "__main__":
    processor = USAspendingDATProcessor()
    count = processor.process()
    print(f"\nTotal China-relevant contracts: {count}")