#!/usr/bin/env python3
"""
Terminal B: Real Data Analyzer for Eastern EU Countries
Analyzes actual TED procurement data for Chinese vendors
Countries: CZ, HU, PL, RO, SK
"""

import tarfile
import xml.etree.ElementTree as ET
import sqlite3
from pathlib import Path
from datetime import datetime
import hashlib
import json
import re

class TerminalBRealAnalyzer:
    def __init__(self):
        self.warehouse_path = Path("F:/OSINT_WAREHOUSE/osint_research.db")
        self.ted_path = Path("F:/TED_Data/monthly")
        self.countries = ['CZ', 'HU', 'PL', 'RO', 'SK']

        # China detection patterns
        self.china_patterns = [
            # Chinese company names
            r'\bhuawei\b', r'\bzte\b', r'\bhikvision\b', r'\bdahua\b',
            r'\blenovo\b', r'\bxiaomi\b', r'\btcl\b', r'\bhaier\b',
            r'\bbyd\b', r'\bcrrc\b', r'\bcrbc\b', r'\bcrcc\b',
            r'\bcosco\b', r'\bsinopec\b', r'\bcnooc\b', r'\bcnpc\b',
            r'\bicbc\b', r'\bbank of china\b', r'\bchina construction bank\b',
            r'\bchina railway\b', r'\bchina communications\b',
            r'\bnuctech\b', r'\bzijin\b', r'\bhesteel\b',
            # Geographic indicators
            r'\bchina\b', r'\bchinese\b', r'\bbeijing\b', r'\bshanghai\b',
            r'\bshenzhen\b', r'\bguangzhou\b', r'\bhangzhou\b',
            # Special Eastern EU related
            r'\bfudan\b', r'\bcefc\b', r'\bcgn\b', r'\bcgnpc\b',
            r'\bbelt and road\b', r'\bbri\b', r'\bminth\b'
        ]

        self.results = {
            'total_contracts': 0,
            'china_contracts': 0,
            'by_country': {c: {'total': 0, 'china': 0, 'value': 0} for c in self.countries},
            'chinese_vendors': set(),
            'major_contracts': []
        }

    def extract_country_from_xml(self, root):
        """Extract country code from TED XML"""
        # Try different paths where country might be stored
        country_paths = [
            ".//ISO_COUNTRY",
            ".//COUNTRY",
            ".//ADDRESS_CONTRACTING_BODY//COUNTRY",
            ".//CONTRACTING_BODY//ADDRESS_CONTRACTING_BODY//COUNTRY"
        ]

        for path in country_paths:
            elem = root.find(path)
            if elem is not None:
                country_code = elem.get('VALUE', elem.text)
                if country_code and country_code.upper() in self.countries:
                    return country_code.upper()

        return None

    def detect_chinese_vendor(self, text):
        """Detect if text contains Chinese vendor indicators"""
        if not text:
            return False, 0.0

        text_lower = text.lower()

        for pattern in self.china_patterns:
            if re.search(pattern, text_lower):
                # Strong match for company names
                if any(company in pattern for company in ['huawei', 'zte', 'hikvision', 'tcl', 'byd']):
                    return True, 0.95
                # Medium match for general China references
                elif 'china' in pattern or 'chinese' in pattern:
                    return True, 0.8
                # Other matches
                else:
                    return True, 0.7

        return False, 0.0

    def parse_ted_file(self, file_path):
        """Parse a single TED XML file"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Get country
            country = self.extract_country_from_xml(root)
            if not country or country not in self.countries:
                return None

            # Get contract details
            contract_data = {
                'country': country,
                'file': file_path.name,
                'chinese_vendor': False,
                'china_score': 0.0
            }

            # Get notice ID
            notice_id = root.find(".//DOC_ID")
            if notice_id is not None:
                contract_data['doc_id'] = notice_id.text
            else:
                contract_data['doc_id'] = file_path.stem

            # Get title
            title_elem = root.find(".//TITLE")
            if title_elem is not None:
                contract_data['title'] = title_elem.text
                is_chinese, score = self.detect_chinese_vendor(title_elem.text)
                if is_chinese:
                    contract_data['chinese_vendor'] = True
                    contract_data['china_score'] = max(contract_data['china_score'], score)

            # Check contractor/winner info
            contractor_paths = [
                ".//CONTRACTOR",
                ".//AWARDED_TO_GROUP",
                ".//CONTRACTOR_NAME",
                ".//ORGANISATION"
            ]

            for path in contractor_paths:
                for elem in root.findall(path):
                    text = ET.tostring(elem, encoding='unicode', method='text')
                    is_chinese, score = self.detect_chinese_vendor(text)
                    if is_chinese:
                        contract_data['chinese_vendor'] = True
                        contract_data['china_score'] = max(contract_data['china_score'], score)
                        contract_data['vendor_text'] = text[:200]

            # Get contract value
            value_elem = root.find(".//VAL_TOTAL")
            if value_elem is not None:
                currency = value_elem.get('CURRENCY', 'EUR')
                try:
                    value = float(value_elem.text.replace(',', '').replace(' ', ''))
                    contract_data['value'] = value
                    contract_data['currency'] = currency
                except:
                    pass

            return contract_data

        except Exception as e:
            return None

    def analyze_ted_year(self, year):
        """Analyze TED data for a specific year"""
        year_path = self.ted_path / str(year)
        if not year_path.exists():
            return

        print(f"\nAnalyzing {year} TED data for Eastern EU...")

        # Process each month's tar.gz file
        for tar_file in year_path.glob("*.tar.gz"):
            print(f"  Processing {tar_file.name}...")

            try:
                with tarfile.open(tar_file, 'r:gz') as tar:
                    # Extract and process XML files
                    for member in tar.getmembers():
                        if member.name.endswith('.xml'):
                            # Extract file
                            f = tar.extractfile(member)
                            if f:
                                # Write to temp file for parsing
                                temp_path = Path(f"temp_{member.name}")
                                temp_path.write_bytes(f.read())

                                # Parse
                                contract = self.parse_ted_file(temp_path)

                                if contract:
                                    self.results['total_contracts'] += 1
                                    self.results['by_country'][contract['country']]['total'] += 1

                                    if contract['chinese_vendor']:
                                        self.results['china_contracts'] += 1
                                        self.results['by_country'][contract['country']]['china'] += 1

                                        if 'vendor_text' in contract:
                                            self.chinese_vendors.add(contract['vendor_text'][:50])

                                        if 'value' in contract and contract['value'] > 1000000:
                                            self.results['major_contracts'].append({
                                                'country': contract['country'],
                                                'doc_id': contract['doc_id'],
                                                'title': contract.get('title', 'N/A')[:100],
                                                'value': contract['value'],
                                                'year': year
                                            })

                                # Clean up temp file
                                temp_path.unlink(missing_ok=True)

            except Exception as e:
                print(f"    Error processing {tar_file.name}: {e}")

    def insert_to_warehouse(self):
        """Insert findings into warehouse"""
        conn = sqlite3.connect(self.warehouse_path)
        cursor = conn.cursor()

        inserted = 0

        # Insert major contracts as procurement records
        for contract in self.results['major_contracts']:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO core_f_procurement (
                        award_id, vendor_name, has_chinese_vendor,
                        supply_chain_risk, contract_value, currency,
                        award_date, source_system, retrieved_at,
                        confidence_score, buyer_country
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    contract['doc_id'],
                    'Chinese Vendor (TED detected)',
                    True,
                    'MEDIUM',
                    contract['value'],
                    'EUR',
                    f"{contract['year']}-01-01",
                    'TED_Terminal_B_Real',
                    datetime.now().isoformat(),
                    0.85,
                    contract['country']
                ))
                inserted += 1
            except Exception as e:
                print(f"Error inserting {contract['doc_id']}: {e}")

        conn.commit()
        conn.close()

        return inserted

    def generate_report(self):
        """Generate analysis report"""
        print("\n" + "="*60)
        print("TERMINAL B: REAL TED DATA ANALYSIS")
        print("="*60)

        print(f"\nTotal contracts analyzed: {self.results['total_contracts']}")
        print(f"Contracts with Chinese vendors: {self.results['china_contracts']}")

        if self.results['total_contracts'] > 0:
            china_rate = (self.results['china_contracts'] / self.results['total_contracts']) * 100
            print(f"China involvement rate: {china_rate:.2f}%")

        print("\nBy Country:")
        for country in self.countries:
            data = self.results['by_country'][country]
            if data['total'] > 0:
                rate = (data['china'] / data['total']) * 100
                print(f"  {country}: {data['total']} contracts, {data['china']} Chinese ({rate:.1f}%)")

        print(f"\nMajor contracts (>€1M): {len(self.results['major_contracts'])}")
        for contract in sorted(self.results['major_contracts'], key=lambda x: x['value'], reverse=True)[:5]:
            print(f"  {contract['country']}: €{contract['value']/1e6:.1f}M - {contract['title'][:60]}")

        print(f"\nUnique Chinese vendors detected: {len(self.results['chinese_vendors'])}")

    def run(self, years=[2023, 2022, 2021]):
        """Run analysis for specified years"""
        print(f"\nTerminal B Real Data Analysis")
        print(f"Analyzing TED procurement data for: {', '.join(self.countries)}")
        print(f"Years: {', '.join(map(str, years))}")

        for year in years:
            self.analyze_ted_year(year)

        # Insert to warehouse
        inserted = self.insert_to_warehouse()
        print(f"\nInserted {inserted} records to warehouse")

        # Generate report
        self.generate_report()

if __name__ == "__main__":
    analyzer = TerminalBRealAnalyzer()
    # Start with just 2023 to test
    analyzer.run(years=[2023])
