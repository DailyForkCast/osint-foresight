"""
Process TED Europa procurement data from tar.gz archives
Extracts technology procurement and China connections for supply chain analysis
"""

import tarfile
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import logging
from collections import defaultdict
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TEDDataProcessor:
    def __init__(self):
        self.ted_path = Path("F:/TED_Data/monthly")
        self.output_dir = Path("data/processed/ted_analysis")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Technology CPV codes
        self.tech_cpv_prefixes = {
            "30": "Computer equipment",
            "32": "Telecom equipment",
            "38": "Laboratory equipment",
            "48": "Software systems",
            "72": "IT services",
            "73": "R&D services"
        }

        # China-related keywords
        self.china_keywords = ["china", "chinese", "huawei", "zte", "xiaomi", "lenovo", "alibaba", "tencent", "baidu"]

        self.stats = defaultdict(int)

    def process_tar_gz(self, tar_path: Path, country_code: str = "DE"):
        """Process a single tar.gz archive"""
        logging.info(f"Processing {tar_path.name}")

        contracts = []

        try:
            with tarfile.open(tar_path, 'r:gz') as tar:
                # Process each file in archive
                for member in tar.getmembers():
                    if member.isfile() and (member.name.endswith('.xml') or member.name.endswith('.json')):
                        try:
                            f = tar.extractfile(member)
                            if f:
                                content = f.read()

                                # Parse based on file type
                                if member.name.endswith('.xml'):
                                    contract = self.parse_xml_contract(content, country_code)
                                elif member.name.endswith('.json'):
                                    contract = self.parse_json_contract(content, country_code)

                                if contract:
                                    contracts.append(contract)
                                    self.stats['total_contracts'] += 1

                                    if contract.get('is_technology'):
                                        self.stats['tech_contracts'] += 1
                                    if contract.get('has_china_connection'):
                                        self.stats['china_contracts'] += 1

                        except Exception as e:
                            logging.debug(f"Error processing {member.name}: {e}")
                            self.stats['errors'] += 1

        except Exception as e:
            logging.error(f"Failed to open {tar_path}: {e}")

        return contracts

    def parse_xml_contract(self, content: bytes, country_code: str) -> Dict:
        """Parse XML contract data"""
        try:
            root = ET.fromstring(content)

            # Extract basic info (simplified - actual TED XML is complex)
            contract = {
                'type': 'contract_notice',
                'country': '',
                'cpv_codes': [],
                'value': 0,
                'description': '',
                'suppliers': [],
                'is_technology': False,
                'has_china_connection': False
            }

            # Look for country code
            country_elem = root.find('.//{*}ISO_COUNTRY')
            if country_elem is not None and country_elem.get('VALUE') == country_code:
                contract['country'] = country_code
            else:
                return None  # Skip if not target country

            # Extract CPV codes
            for cpv in root.findall('.//{*}CPV_MAIN'):
                code = cpv.find('./{*}CPV_CODE')
                if code is not None:
                    cpv_code = code.get('CODE', '')
                    contract['cpv_codes'].append(cpv_code)

                    # Check if technology-related
                    if any(cpv_code.startswith(prefix) for prefix in self.tech_cpv_prefixes):
                        contract['is_technology'] = True

            # Check for China connections in text
            text_content = ET.tostring(root, encoding='unicode').lower()
            if any(keyword in text_content for keyword in self.china_keywords):
                contract['has_china_connection'] = True

            return contract if contract['country'] else None

        except Exception as e:
            logging.debug(f"XML parsing error: {e}")
            return None

    def parse_json_contract(self, content: bytes, country_code: str) -> Dict:
        """Parse JSON contract data"""
        try:
            data = json.loads(content)

            # Handle different JSON structures
            if isinstance(data, dict):
                contracts = [data]
            elif isinstance(data, list):
                contracts = data
            else:
                return None

            for contract_data in contracts:
                if contract_data.get('buyer', {}).get('country') == country_code:
                    contract = {
                        'type': 'contract_notice',
                        'country': country_code,
                        'cpv_codes': contract_data.get('cpv_codes', []),
                        'value': contract_data.get('value', {}).get('amount', 0),
                        'description': contract_data.get('description', ''),
                        'suppliers': contract_data.get('suppliers', []),
                        'is_technology': False,
                        'has_china_connection': False
                    }

                    # Check technology
                    for cpv in contract['cpv_codes']:
                        if any(str(cpv).startswith(prefix) for prefix in self.tech_cpv_prefixes):
                            contract['is_technology'] = True
                            break

                    # Check China connections
                    full_text = json.dumps(contract_data).lower()
                    if any(keyword in full_text for keyword in self.china_keywords):
                        contract['has_china_connection'] = True

                    return contract

        except Exception as e:
            logging.debug(f"JSON parsing error: {e}")
            return None

    def analyze_contracts(self, contracts: List[Dict]) -> Dict:
        """Analyze contracts for patterns"""
        analysis = {
            'total_contracts': len(contracts),
            'technology_contracts': sum(1 for c in contracts if c.get('is_technology')),
            'china_connections': sum(1 for c in contracts if c.get('has_china_connection')),
            'tech_with_china': sum(1 for c in contracts if c.get('is_technology') and c.get('has_china_connection')),
            'cpv_distribution': defaultdict(int),
            'technology_categories': defaultdict(int)
        }

        for contract in contracts:
            if contract.get('is_technology'):
                for cpv in contract['cpv_codes']:
                    prefix = cpv[:2] if len(cpv) >= 2 else ''
                    if prefix in self.tech_cpv_prefixes:
                        analysis['technology_categories'][self.tech_cpv_prefixes[prefix]] += 1

        return analysis

    def process_year(self, year: int, country_code: str = "DE"):
        """Process all monthly data for a specific year"""
        year_dir = self.ted_path / str(year)

        if not year_dir.exists():
            logging.warning(f"Year directory {year_dir} does not exist")
            return

        all_contracts = []
        tar_files = list(year_dir.glob("*.tar.gz"))

        logging.info(f"Found {len(tar_files)} archives for year {year}")

        for tar_file in tar_files[:2]:  # Process first 2 months as demo
            contracts = self.process_tar_gz(tar_file, country_code)
            all_contracts.extend(contracts)

        # Analyze results
        analysis = self.analyze_contracts(all_contracts)

        # Save results
        output_file = self.output_dir / f"ted_{country_code}_{year}_analysis.json"
        with open(output_file, 'w') as f:
            json.dump({
                'year': year,
                'country': country_code,
                'analysis': analysis,
                'processing_stats': dict(self.stats),
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)

        logging.info(f"Saved analysis to {output_file}")

        # Print summary
        print(f"\n{'='*60}")
        print(f"TED DATA ANALYSIS - {country_code} {year}")
        print(f"{'='*60}")
        print(f"Total contracts processed: {self.stats['total_contracts']:,}")
        print(f"Technology contracts: {analysis['technology_contracts']:,}")
        print(f"Contracts with China connections: {analysis['china_connections']:,}")
        print(f"Tech contracts with China: {analysis['tech_with_china']:,}")

        if analysis['technology_categories']:
            print("\nTop Technology Categories:")
            for category, count in sorted(analysis['technology_categories'].items(),
                                         key=lambda x: x[1], reverse=True)[:5]:
                print(f"  - {category}: {count}")

def main():
    processor = TEDDataProcessor()

    # Process 2024 data for Germany
    processor.process_year(2024, "DE")

    print("\nProcessing complete!")
    print(f"Check output in: {processor.output_dir}")

if __name__ == "__main__":
    main()
