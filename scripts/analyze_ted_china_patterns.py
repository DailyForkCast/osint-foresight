#!/usr/bin/env python3
"""
Analyze TED (Tenders Electronic Daily) XML files for China patterns
Search for Chinese companies, products, and relationships in EU procurement
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import json
import re
from datetime import datetime
from collections import defaultdict, Counter

class TEDChinaAnalyzer:
    def __init__(self):
        self.ted_path = Path("F:/DECOMPRESSED_DATA/ted_xml")

        self.china_patterns = {
            'countries': ['china', 'chinese', 'prc', "people's republic", 'cn'],
            'cities': ['beijing', 'shanghai', 'shenzhen', 'guangzhou', 'hangzhou',
                      'tianjin', 'chengdu', 'wuhan', 'nanjing', 'xiamen'],
            'companies': ['huawei', 'zte', 'alibaba', 'tencent', 'baidu', 'xiaomi',
                         'lenovo', 'dji', 'bytedance', 'tiktok', 'haier', 'hisense',
                         'byd', 'geely', 'great wall', 'saic', 'sinopec', 'petrochina',
                         'bank of china', 'icbc', 'hikvision', 'dahua'],
            'products': ['5g', 'telecom equipment', 'surveillance', 'solar panels',
                        'batteries', 'electric vehicles', 'wind turbines'],
            'indicators': ['manufactured in china', 'made in china', 'chinese supplier',
                          'chinese manufacturer', 'chinese bidder']
        }

        self.findings = {
            'total_files': 0,
            'files_with_china': 0,
            'contracts': [],
            'by_country': defaultdict(int),
            'by_year': defaultdict(int),
            'by_category': defaultdict(int),
            'chinese_companies': [],
            'high_value': [],
            'critical_sectors': []
        }

    def find_xml_files(self):
        """Locate all XML files in the TED extraction directory"""
        print("\n[SEARCHING FOR XML FILES]")
        print("-" * 40)

        xml_files = []

        # Search recursively for XML files
        for path in self.ted_path.rglob("*.xml"):
            xml_files.append(path)

        # Also check for nested tar/gz that might contain XML
        for tar_path in self.ted_path.rglob("*.tar"):
            print(f"  Found nested tar: {tar_path.name}")

        for gz_path in self.ted_path.rglob("*.gz"):
            if not gz_path.name.endswith('.tar.gz'):
                print(f"  Found nested gz: {gz_path.name}")

        print(f"\nTotal XML files found: {len(xml_files)}")

        if len(xml_files) == 0:
            print("\nNo XML files found. Checking directory structure...")
            self.explore_directory_structure()

        return xml_files

    def explore_directory_structure(self):
        """Explore the directory structure to understand what we have"""
        print("\n[DIRECTORY STRUCTURE]")

        for item in self.ted_path.iterdir():
            if item.is_dir():
                file_count = len(list(item.glob("*")))
                print(f"  {item.name}/: {file_count} items")

                # Check subdirectories
                for subitem in item.iterdir():
                    if subitem.is_dir():
                        subfile_count = len(list(subitem.glob("*")))
                        print(f"    {subitem.name}/: {subfile_count} items")
                    else:
                        print(f"    {subitem.name}: {subitem.stat().st_size / 1024:.1f} KB")

                    # Only show first 5 items
                    if list(item.iterdir()).index(subitem) >= 4:
                        print(f"    ... and {file_count - 5} more items")
                        break

    def analyze_xml_file(self, xml_path):
        """Analyze a single XML file for China patterns"""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # Convert entire XML to string for pattern searching
            xml_text = ET.tostring(root, encoding='unicode', method='text').lower()

            china_found = False
            matches = []

            # Search for China patterns
            for category, patterns in self.china_patterns.items():
                for pattern in patterns:
                    if pattern.lower() in xml_text:
                        china_found = True
                        matches.append({
                            'category': category,
                            'pattern': pattern,
                            'context': self.extract_context(xml_text, pattern)
                        })
                        self.findings['by_category'][category] += 1

            if china_found:
                self.findings['files_with_china'] += 1

                # Extract contract details
                contract = self.extract_contract_details(root, xml_path, matches)
                self.findings['contracts'].append(contract)

                # Check if high value
                if contract.get('value', 0) > 1000000:
                    self.findings['high_value'].append(contract)

                # Check for critical sectors
                if self.is_critical_sector(xml_text):
                    self.findings['critical_sectors'].append(contract)

                return True

        except Exception as e:
            print(f"  Error parsing {xml_path.name}: {str(e)[:50]}")

        return False

    def extract_context(self, text, pattern, context_size=100):
        """Extract context around a pattern match"""
        pattern_lower = pattern.lower()
        idx = text.find(pattern_lower)

        if idx != -1:
            start = max(0, idx - context_size)
            end = min(len(text), idx + len(pattern_lower) + context_size)
            return text[start:end].strip()

        return ""

    def extract_contract_details(self, root, xml_path, matches):
        """Extract contract details from XML"""
        contract = {
            'file': xml_path.name,
            'matches': matches,
            'value': 0,
            'date': '',
            'authority': '',
            'description': '',
            'country': ''
        }

        # Try to extract common TED fields (namespace-aware)
        namespaces = {'ted': 'http://ted.europa.eu'}

        # Value
        value_elem = root.find('.//VALUE', namespaces)
        if value_elem is None:
            value_elem = root.find('.//VAL_TOTAL', namespaces)
        if value_elem is not None and value_elem.text:
            try:
                contract['value'] = float(value_elem.text.replace(',', ''))
            except:
                pass

        # Date
        date_elem = root.find('.//DT_DISPATCH', namespaces)
        if date_elem is None:
            date_elem = root.find('.//DATE_PUB', namespaces)
        if date_elem is not None and date_elem.text:
            contract['date'] = date_elem.text
            try:
                year = date_elem.text[:4]
                self.findings['by_year'][year] += 1
            except:
                pass

        # Authority
        auth_elem = root.find('.//OFFICIALNAME', namespaces)
        if auth_elem is None:
            auth_elem = root.find('.//NAME_ADDRESSES_CONTACT_CONTRACT', namespaces)
        if auth_elem is not None and auth_elem.text:
            contract['authority'] = auth_elem.text[:100]

        # Country
        country_elem = root.find('.//COUNTRY', namespaces)
        if country_elem is None:
            country_elem = root.find('.//ISO_COUNTRY', namespaces)
        if country_elem is not None:
            country_code = country_elem.get('VALUE', country_elem.text)
            if country_code:
                contract['country'] = country_code
                self.findings['by_country'][country_code] += 1

        # Description
        desc_elem = root.find('.//SHORT_DESCR', namespaces)
        if desc_elem is None:
            desc_elem = root.find('.//DESCRIPTION', namespaces)
        if desc_elem is not None and desc_elem.text:
            contract['description'] = desc_elem.text[:200]

        return contract

    def is_critical_sector(self, text):
        """Check if contract involves critical sectors"""
        critical_keywords = [
            'telecom', '5g', 'network infrastructure', 'energy', 'power grid',
            'water supply', 'transportation', 'railway', 'airport', 'port',
            'defense', 'military', 'security', 'surveillance', 'critical infrastructure',
            'health', 'hospital', 'pharmaceutical', 'vaccine'
        ]

        for keyword in critical_keywords:
            if keyword in text:
                return True

        return False

    def generate_report(self):
        """Generate analysis report"""
        report = "# TED China Pattern Analysis Report\n\n"
        report += f"Generated: {datetime.now().isoformat()}\n\n"

        report += "## Summary\n\n"
        report += f"- **Total XML files analyzed**: {self.findings['total_files']}\n"
        report += f"- **Files with China patterns**: {self.findings['files_with_china']}\n"
        report += f"- **Contracts identified**: {len(self.findings['contracts'])}\n"
        report += f"- **High-value contracts (>€1M)**: {len(self.findings['high_value'])}\n"
        report += f"- **Critical sector contracts**: {len(self.findings['critical_sectors'])}\n\n"

        if self.findings['files_with_china'] > 0:
            percentage = (self.findings['files_with_china'] / self.findings['total_files'] * 100)
            report += f"- **China presence rate**: {percentage:.1f}%\n\n"

        report += "## Pattern Distribution\n\n"
        for category, count in sorted(self.findings['by_category'].items(),
                                     key=lambda x: x[1], reverse=True):
            report += f"- {category.capitalize()}: {count}\n"

        report += "\n## Geographic Distribution\n\n"
        for country, count in sorted(self.findings['by_country'].items(),
                                    key=lambda x: x[1], reverse=True)[:10]:
            report += f"- {country}: {count} contracts\n"

        report += "\n## Temporal Distribution\n\n"
        for year, count in sorted(self.findings['by_year'].items()):
            report += f"- {year}: {count} contracts\n"

        if self.findings['high_value']:
            report += "\n## High-Value Contracts\n\n"
            for contract in self.findings['high_value'][:5]:
                report += f"- {contract['file']}: €{contract['value']:,.0f}\n"
                report += f"  Authority: {contract.get('authority', 'Unknown')}\n"
                report += f"  Description: {contract.get('description', 'N/A')[:100]}\n\n"

        if self.findings['critical_sectors']:
            report += "\n## Critical Sector Contracts\n\n"
            for contract in self.findings['critical_sectors'][:5]:
                report += f"- {contract['file']}\n"
                report += f"  Sector indicators: {contract.get('description', '')[:100]}\n\n"

        return report

    def run(self):
        """Execute the analysis"""
        print("\n" + "="*70)
        print("TED CHINA PATTERN ANALYSIS")
        print("="*70)

        # Find XML files
        xml_files = self.find_xml_files()

        if not xml_files:
            print("\n[WARNING] No XML files found to analyze")
            print("TED files may still be compressed or in different format")
            return

        self.findings['total_files'] = len(xml_files)

        # Analyze each file
        print(f"\n[ANALYZING {len(xml_files)} XML FILES]")
        print("-" * 40)

        for i, xml_path in enumerate(xml_files, 1):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(xml_files)} files...")

            self.analyze_xml_file(xml_path)

        # Generate and save report
        report = self.generate_report()

        report_path = Path("C:/Projects/OSINT - Foresight/TED_CHINA_ANALYSIS_REPORT.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        # Save detailed findings
        findings_path = Path("C:/Projects/OSINT - Foresight/ted_china_findings.json")
        with open(findings_path, 'w', encoding='utf-8') as f:
            # Convert defaultdicts to regular dicts for JSON serialization
            findings_copy = {
                'total_files': self.findings['total_files'],
                'files_with_china': self.findings['files_with_china'],
                'contracts': self.findings['contracts'],
                'by_country': dict(self.findings['by_country']),
                'by_year': dict(self.findings['by_year']),
                'by_category': dict(self.findings['by_category']),
                'high_value': self.findings['high_value'],
                'critical_sectors': self.findings['critical_sectors']
            }
            json.dump(findings_copy, f, indent=2, default=str)

        print(f"\n[Report saved to {report_path}]")
        print(f"[Findings saved to {findings_path}]")

        # Print summary
        print("\n" + "="*70)
        print("ANALYSIS COMPLETE")
        print("="*70)
        print(f"\nFiles analyzed: {self.findings['total_files']}")
        print(f"China patterns found: {self.findings['files_with_china']}")
        print(f"Contracts identified: {len(self.findings['contracts'])}")

        if self.findings['critical_sectors']:
            print(f"\n[ALERT] {len(self.findings['critical_sectors'])} critical sector contracts found!")


if __name__ == "__main__":
    analyzer = TEDChinaAnalyzer()
    analyzer.run()
