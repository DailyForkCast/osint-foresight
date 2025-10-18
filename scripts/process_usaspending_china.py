"""
USAspending China Contractor Processor
Analyzes US government spending for China-linked contractors and technology
"""

import os
import json
import sqlite3
import csv
from datetime import datetime
from typing import Dict, List

class USAspendingChinaProcessor:
    def __init__(self):
        self.db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.raw_path = "F:/OSINT_Data/USASPENDING"
        self.output_path = "data/processed/usaspending_china_deep"

        # China-linked entity patterns
        self.china_patterns = {
            'direct_chinese': [
                'huawei', 'zte', 'hikvision', 'dahua', 'hytera',
                'china telecom', 'china mobile', 'china unicom',
                'lenovo', 'tcl', 'xiaomi', 'dji', 'bytedance', 'tiktok'
            ],
            'ownership_keywords': [
                'china', 'chinese', 'beijing', 'shanghai', 'shenzhen',
                'hong kong', 'prc', 'people\'s republic'
            ],
            'technology_categories': [
                'telecommunications', '5g', 'artificial intelligence',
                'semiconductors', 'quantum', 'aerospace', 'biotechnology',
                'surveillance', 'cybersecurity', 'cloud computing'
            ],
            'risk_agencies': [
                'DOD', 'DOE', 'NASA', 'NSF', 'NIST', 'DARPA'
            ]
        }

        os.makedirs(self.output_path, exist_ok=True)

    def process(self):
        print(f"[{datetime.now()}] Starting USAspending China analysis...")

        all_contracts = []
        suspicious_contractors = {}
        technology_exposure = {}
        agency_exposure = {}

        # Process all USAspending files
        files = [f for f in os.listdir(self.raw_path) if f.endswith(('.csv', '.json'))]
        print(f"Found {len(files)} USAspending files")

        for file in files:
            file_path = os.path.join(self.raw_path, file)
            print(f"Processing {file}...")

            try:
                if file.endswith('.csv'):
                    contracts = self.process_csv(file_path)
                else:
                    contracts = self.process_json(file_path)

                # Analyze each contract
                for contract in contracts:
                    if self.is_china_relevant(contract):
                        all_contracts.append(contract)

                        # Track contractor
                        vendor = contract.get('vendor_name', 'Unknown')
                        if vendor in suspicious_contractors:
                            suspicious_contractors[vendor]['count'] += 1
                            suspicious_contractors[vendor]['total_value'] += contract.get('award_amount', 0)
                        else:
                            suspicious_contractors[vendor] = {
                                'count': 1,
                                'total_value': contract.get('award_amount', 0),
                                'risk_indicators': self.identify_risks(contract)
                            }

                        # Track technology exposure
                        tech_area = self.classify_technology(contract)
                        if tech_area:
                            technology_exposure[tech_area] = technology_exposure.get(tech_area, 0) + 1

                        # Track agency exposure
                        agency = contract.get('awarding_agency', 'Unknown')
                        agency_exposure[agency] = agency_exposure.get(agency, 0) + 1

            except Exception as e:
                print(f"Error processing {file}: {e}")

        # Save results
        self.save_results(all_contracts, suspicious_contractors, technology_exposure, agency_exposure)
        return len(all_contracts)

    def process_csv(self, file_path):
        contracts = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                contract = {
                    'contract_id': row.get('award_id_piid', ''),
                    'vendor_name': row.get('recipient_name', ''),
                    'vendor_country': row.get('recipient_country_name', ''),
                    'vendor_address': row.get('recipient_address_line_1', ''),
                    'award_amount': float(row.get('total_obligation', 0) or 0),
                    'awarding_agency': row.get('awarding_agency_name', ''),
                    'description': row.get('award_description', ''),
                    'naics_code': row.get('naics_code', ''),
                    'award_date': row.get('action_date', ''),
                    'place_of_performance': row.get('primary_place_of_performance_country_name', '')
                }
                contracts.append(contract)
        return contracts

    def process_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif 'results' in data:
                return data['results']
            else:
                return [data]

    def is_china_relevant(self, contract):
        # Check vendor name
        vendor = contract.get('vendor_name', '').lower()
        for pattern in self.china_patterns['direct_chinese']:
            if pattern in vendor:
                return True

        # Check vendor country
        if contract.get('vendor_country', '').lower() in ['china', 'hong kong', 'prc']:
            return True

        # Check description for China keywords
        description = contract.get('description', '').lower()
        for keyword in self.china_patterns['ownership_keywords']:
            if keyword in description:
                return True

        # Check if it's sensitive technology from risk agency
        if contract.get('awarding_agency', '') in self.china_patterns['risk_agencies']:
            tech = self.classify_technology(contract)
            if tech in self.china_patterns['technology_categories']:
                return True

        return False

    def identify_risks(self, contract):
        risks = []

        # Direct Chinese company
        vendor = contract.get('vendor_name', '').lower()
        for company in self.china_patterns['direct_chinese']:
            if company in vendor:
                risks.append(f"Direct Chinese entity: {company}")

        # Foreign vendor in sensitive sector
        if contract.get('vendor_country') != 'USA':
            tech = self.classify_technology(contract)
            if tech in self.china_patterns['technology_categories']:
                risks.append(f"Foreign vendor in {tech}")

        # High-value contract
        if contract.get('award_amount', 0) > 10000000:  # $10M
            risks.append(f"High value: ${contract['award_amount']:,.0f}")

        # Sensitive agency
        if contract.get('awarding_agency') in self.china_patterns['risk_agencies']:
            risks.append(f"Sensitive agency: {contract['awarding_agency']}")

        return risks

    def classify_technology(self, contract):
        description = (contract.get('description', '') + ' ' +
                      contract.get('naics_code', '')).lower()

        for tech in self.china_patterns['technology_categories']:
            if tech in description:
                return tech

        # Check NAICS codes
        naics = contract.get('naics_code', '')
        if naics.startswith('334'):  # Computer and Electronic Product Manufacturing
            return 'semiconductors'
        elif naics.startswith('336'):  # Transportation Equipment Manufacturing
            return 'aerospace'
        elif naics.startswith('541'):  # Professional, Scientific, and Technical Services
            return 'artificial intelligence'

        return None

    def save_results(self, contracts, contractors, technologies, agencies):
        # Save detailed analysis
        output_file = os.path.join(self.output_path, f'usaspending_china_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')

        # Sort contractors by risk
        top_contractors = sorted(contractors.items(),
                                key=lambda x: x[1]['total_value'],
                                reverse=True)[:100]

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'extraction_date': datetime.now().isoformat(),
                'total_contracts': len(contracts),
                'total_value': sum(c.get('award_amount', 0) for c in contracts),
                'suspicious_contractors': len(contractors),
                'top_risk_contractors': top_contractors,
                'technology_exposure': sorted(technologies.items(), key=lambda x: x[1], reverse=True),
                'agency_exposure': sorted(agencies.items(), key=lambda x: x[1], reverse=True),
                'sample_contracts': contracts[:100]  # First 100
            }, f, indent=2)

        print(f"Saved {len(contracts)} USAspending contracts to {output_file}")

        # Save to database
        self.save_to_database(contracts, contractors)

    def save_to_database(self, contracts, contractors):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Save contracts
        cur.execute('''CREATE TABLE IF NOT EXISTS usaspending_china_deep
                       (contract_id TEXT PRIMARY KEY, vendor_name TEXT,
                        vendor_country TEXT, award_amount REAL,
                        awarding_agency TEXT, description TEXT,
                        technology_category TEXT, risk_indicators TEXT,
                        processed_date TEXT)''')

        for contract in contracts:
            tech = self.classify_technology(contract)
            risks = self.identify_risks(contract)

            cur.execute('''INSERT OR REPLACE INTO usaspending_china_deep VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (contract['contract_id'], contract['vendor_name'],
                        contract.get('vendor_country', ''), contract.get('award_amount', 0),
                        contract.get('awarding_agency', ''), contract.get('description', ''),
                        tech, json.dumps(risks), datetime.now().isoformat()))

        # Save contractor analysis
        cur.execute('''CREATE TABLE IF NOT EXISTS usaspending_contractors
                       (vendor_name TEXT PRIMARY KEY, contract_count INTEGER,
                        total_value REAL, risk_indicators TEXT, processed_date TEXT)''')

        for vendor, data in contractors.items():
            cur.execute('''INSERT OR REPLACE INTO usaspending_contractors VALUES (?, ?, ?, ?, ?)''',
                       (vendor, data['count'], data['total_value'],
                        json.dumps(data['risk_indicators']), datetime.now().isoformat()))

        conn.commit()
        conn.close()

if __name__ == "__main__":
    processor = USAspendingChinaProcessor()
    count = processor.process()
    print(f"Completed USAspending processing: {count} China-relevant contracts found")