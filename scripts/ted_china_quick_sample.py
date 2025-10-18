#!/usr/bin/env python3
"""
TED China Quick Sampler
Gets a representative sample from each year to show patterns quickly
Full analysis runs in background
"""

import tarfile
import xml.etree.ElementTree as ET
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class TEDQuickSampler:
    """Quick sampling of TED data for immediate insights"""

    def __init__(self):
        self.ted_path = Path("F:/TED_Data/monthly/")
        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        self.results = {
            "samples_analyzed": 0,
            "china_found": 0,
            "examples": [],
            "by_year": {}
        }

        # Quick PRC indicators
        self.china_indicators = {
            'country_codes': {'CN', 'CHN', '156'},
            'cities': {'beijing', 'shanghai', 'shenzhen', 'guangzhou', 'hong kong'},
            'companies': {'huawei', 'zte', 'alibaba', 'tencent', 'sinopec', 'china mobile',
                         'china telecom', 'china construction', 'china railway'}
        }

    def quick_check(self, xml_content: str) -> dict:
        """Quick check for Chinese entities"""
        try:
            root = ET.fromstring(xml_content)
            result = {
                'has_china': False,
                'buyer': None,
                'supplier': None,
                'value': None,
                'details': []
            }

            # Check buyer
            buyer = root.find('.//CONTRACTING_AUTHORITY')
            if buyer:
                name = buyer.find('.//OFFICIALNAME')
                country = buyer.find('.//COUNTRY')
                if name and name.text:
                    result['buyer'] = name.text
                    if country and country.get('VALUE', '').upper() in self.china_indicators['country_codes']:
                        result['has_china'] = True
                        result['details'].append(f"Chinese buyer: {name.text}")

            # Check supplier
            contractor = root.find('.//CONTRACTOR')
            if contractor:
                name = contractor.find('.//OFFICIALNAME')
                country = contractor.find('.//COUNTRY')
                if name and name.text:
                    result['supplier'] = name.text
                    name_lower = name.text.lower()
                    if country and country.get('VALUE', '').upper() in self.china_indicators['country_codes']:
                        result['has_china'] = True
                        result['details'].append(f"Chinese supplier: {name.text}")
                    elif any(company in name_lower for company in self.china_indicators['companies']):
                        result['has_china'] = True
                        result['details'].append(f"Known Chinese company: {name.text}")

            # Get value
            value = root.find('.//VALUE')
            if value:
                result['value'] = value.get('AMOUNT')

            return result

        except:
            return {'has_china': False}

    def sample_year(self, year: int, max_samples: int = 100):
        """Sample contracts from a specific year"""
        year_path = self.ted_path / str(year)
        if not year_path.exists():
            return

        tar_files = list(year_path.glob("*.tar.gz"))
        if not tar_files:
            return

        # Pick a random tar file
        tar_file = random.choice(tar_files)
        china_count = 0
        samples = 0

        logging.info(f"Sampling {year} from {tar_file.name}")

        try:
            with tarfile.open(tar_file, 'r:gz') as tar:
                members = [m for m in tar.getmembers() if m.name.endswith('.xml')]

                # Sample random subset
                sample_size = min(max_samples, len(members))
                sampled = random.sample(members, sample_size)

                for member in sampled:
                    f = tar.extractfile(member)
                    if f:
                        content = f.read().decode('utf-8', errors='ignore')
                        result = self.quick_check(content)
                        samples += 1

                        if result['has_china']:
                            china_count += 1
                            self.results['china_found'] += 1

                            # Store example
                            if len(self.results['examples']) < 20:
                                self.results['examples'].append({
                                    'year': year,
                                    'file': member.name,
                                    'buyer': result['buyer'],
                                    'supplier': result['supplier'],
                                    'value': result['value'],
                                    'details': result['details']
                                })

                self.results['samples_analyzed'] += samples
                self.results['by_year'][year] = {
                    'sampled': samples,
                    'china_found': china_count,
                    'percentage': (china_count / samples * 100) if samples > 0 else 0
                }

                logging.info(f"  {year}: {china_count}/{samples} contracts with China ({china_count/samples*100:.1f}%)")

        except Exception as e:
            logging.error(f"Error sampling {year}: {e}")

    def run_quick_analysis(self):
        """Run quick sampling across all years"""
        logging.info("Running quick TED China sampling...")

        # Sample each year
        for year in range(2006, 2026):
            self.sample_year(year, max_samples=200)

        # Generate quick report
        report = f"""
TED CHINA QUICK SAMPLING RESULTS
=================================
Time: {datetime.now().isoformat()}

Total Samples: {self.results['samples_analyzed']}
China Contracts Found: {self.results['china_found']}
Overall Percentage: {self.results['china_found'] / max(self.results['samples_analyzed'], 1) * 100:.2f}%

BY YEAR:
"""
        for year, data in sorted(self.results['by_year'].items()):
            report += f"  {year}: {data['china_found']:>3}/{data['sampled']:>3} = {data['percentage']:>5.1f}%\n"

        report += "\nSAMPLE CHINA CONTRACTS:\n"
        for i, example in enumerate(self.results['examples'][:10], 1):
            report += f"\n{i}. Year {example['year']}:\n"
            report += f"   Buyer: {example['buyer'] or 'N/A'}\n"
            report += f"   Supplier: {example['supplier'] or 'N/A'}\n"
            if example['value']:
                report += f"   Value: €{example['value']}\n"
            report += f"   Detection: {', '.join(example['details'])}\n"

        print(report)

        # Save results
        with open("ted_china_quick_sample_results.json", "w") as f:
            json.dump(self.results, f, indent=2)

        return report

if __name__ == "__main__":
    sampler = TEDQuickSampler()
    sampler.run_quick_analysis()
