"""
Comprehensive TED (Tenders Electronic Daily) China Analysis
Analyzes 25GB of EU procurement data for China-related contracts and suppliers
"""

import xml.etree.ElementTree as ET
import json
import gzip
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TEDChinaAnalyzer:
    """Analyzes TED procurement data for China involvement"""

    def __init__(self):
        self.base_path = Path("F:/TED_Data/monthly")
        self.output_path = Path("C:/Projects/OSINT - Foresight/data/processed/ted_china_comprehensive")
        self.output_path.mkdir(parents=True, exist_ok=True)

        # China-related patterns
        self.china_patterns = [
            r'\bchina\b', r'\bchinese\b', r'\bprc\b',
            r'\bbeijing\b', r'\bshanghai\b', r'\bshenzhen\b', r'\bguangzhou\b',
            r'\bhuawei\b', r'\bzte\b', r'\bxiaomi\b', r'\blenovo\b', r'\balibaba\b',
            r'\btencent\b', r'\bbaidu\b', r'\bdji\b', r'\bhikvision\b', r'\bdahua\b',
            r'\bsmic\b', r'\bbyd\b', r'\bgeely\b', r'\bhaier\b'
        ]

        # EU countries
        self.eu_countries = {
            'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
            'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
            'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE', 'UK', 'GB'
        }

        # Technology categories
        self.tech_categories = {
            'telecommunications': ['5g', '6g', 'telecom', 'network', 'mobile', 'wireless'],
            'surveillance': ['camera', 'surveillance', 'security', 'monitoring', 'cctv'],
            'computing': ['server', 'computer', 'laptop', 'workstation', 'hardware'],
            'software': ['software', 'application', 'system', 'platform', 'solution'],
            'energy': ['solar', 'battery', 'renewable', 'energy', 'power'],
            'transport': ['rail', 'train', 'metro', 'bus', 'vehicle', 'transport'],
            'medical': ['medical', 'health', 'diagnostic', 'equipment', 'device'],
            'infrastructure': ['construction', 'building', 'bridge', 'road', 'infrastructure']
        }

        self.stats = {
            'total_contracts': 0,
            'china_related': 0,
            'by_year': defaultdict(int),
            'by_country': defaultdict(int),
            'by_category': defaultdict(int),
            'by_value': defaultdict(float),
            'chinese_companies': Counter(),
            'contract_types': Counter(),
            'temporal_trends': defaultdict(lambda: defaultdict(int))
        }

    def is_china_related(self, text: str) -> bool:
        """Check if text contains China-related terms"""
        if not text:
            return False
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in self.china_patterns)

    def categorize_contract(self, text: str) -> List[str]:
        """Categorize contract by technology area"""
        if not text:
            return []

        text_lower = text.lower()
        categories = []
        for category, keywords in self.tech_categories.items():
            if any(keyword in text_lower for keyword in keywords):
                categories.append(category)
        return categories

    def parse_ted_file(self, file_path: Path) -> Dict:
        """Parse individual TED XML file"""
        try:
            if file_path.suffix == '.gz':
                with gzip.open(file_path, 'rt', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

            root = ET.fromstring(content)

            # Extract key fields
            contract_data = {
                'file': file_path.name,
                'notice_type': root.findtext('.//TD_DOCUMENT_TYPE', ''),
                'country': root.findtext('.//ISO_COUNTRY', ''),
                'contracting_authority': root.findtext('.//OFFICIALNAME', ''),
                'title': root.findtext('.//TITLE_CONTRACT', ''),
                'description': root.findtext('.//SHORT_CONTRACT_DESCRIPTION', ''),
                'cpv_codes': [elem.text for elem in root.findall('.//CPV_CODE')],
                'value': root.findtext('.//VALUE_COST', ''),
                'currency': root.findtext('.//CURRENCY', ''),
                'award_date': root.findtext('.//DT_AWARD', ''),
                'contractors': []
            }

            # Extract contractor information
            for contractor in root.findall('.//CONTRACTOR'):
                contractor_info = {
                    'name': contractor.findtext('.//OFFICIALNAME', ''),
                    'country': contractor.findtext('.//COUNTRY', ''),
                    'address': contractor.findtext('.//ADDRESS', ''),
                    'city': contractor.findtext('.//TOWN', '')
                }
                contract_data['contractors'].append(contractor_info)

            return contract_data

        except Exception as e:
            logger.debug(f"Error parsing {file_path}: {e}")
            return None

    def analyze_contract(self, contract: Dict) -> bool:
        """Analyze individual contract for China connections"""
        if not contract:
            return False

        china_found = False

        # Check main fields
        for field in ['title', 'description', 'contracting_authority']:
            if self.is_china_related(contract.get(field, '')):
                china_found = True
                break

        # Check contractors
        for contractor in contract.get('contractors', []):
            if contractor.get('country', '').upper() == 'CN':
                china_found = True
                self.stats['chinese_companies'][contractor.get('name', 'Unknown')] += 1
            elif self.is_china_related(contractor.get('name', '')):
                china_found = True
                self.stats['chinese_companies'][contractor.get('name', 'Unknown')] += 1

        return china_found

    def process_year(self, year: int) -> Dict:
        """Process all TED files for a specific year"""
        year_path = self.base_path / str(year)
        if not year_path.exists():
            logger.warning(f"Year {year} directory not found")
            return {}

        year_stats = {
            'total': 0,
            'china_related': 0,
            'by_month': defaultdict(int),
            'by_country': defaultdict(int),
            'samples': []
        }

        # Process all month directories
        for month_dir in sorted(year_path.iterdir()):
            if not month_dir.is_dir():
                continue

            month = month_dir.name
            logger.info(f"Processing {year}/{month}")

            # Process all XML files in month
            xml_files = list(month_dir.glob("*.xml")) + list(month_dir.glob("*.xml.gz"))

            for xml_file in xml_files:
                year_stats['total'] += 1
                self.stats['total_contracts'] += 1

                contract = self.parse_ted_file(xml_file)
                if contract and self.analyze_contract(contract):
                    year_stats['china_related'] += 1
                    self.stats['china_related'] += 1
                    self.stats['by_year'][year] += 1

                    country = contract.get('country', 'Unknown')
                    if country in self.eu_countries:
                        year_stats['by_country'][country] += 1
                        self.stats['by_country'][country] += 1

                    # Categorize
                    categories = self.categorize_contract(
                        f"{contract.get('title', '')} {contract.get('description', '')}"
                    )
                    for category in categories:
                        self.stats['by_category'][category] += 1

                    # Sample for reporting
                    if len(year_stats['samples']) < 10:
                        year_stats['samples'].append({
                            'title': contract.get('title', '')[:100],
                            'country': country,
                            'contractors': contract.get('contractors', [])[:2],
                            'file': xml_file.name
                        })

                # Progress update
                if year_stats['total'] % 1000 == 0:
                    logger.info(f"  Processed {year_stats['total']} contracts, {year_stats['china_related']} China-related")

        return year_stats

    def analyze_all_years(self, start_year: int = 2015, end_year: int = 2025):
        """Analyze all available years of TED data"""
        logger.info(f"Starting TED China analysis from {start_year} to {end_year}")

        all_results = {}

        for year in range(start_year, end_year + 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing year {year}")
            logger.info(f"{'='*60}")

            year_results = self.process_year(year)
            all_results[year] = year_results

            # Save intermediate results
            self.save_year_results(year, year_results)

        # Generate final report
        self.generate_comprehensive_report(all_results)

        return all_results

    def save_year_results(self, year: int, results: Dict):
        """Save results for a specific year"""
        output_file = self.output_path / f"ted_china_{year}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {year} results to {output_file}")

    def generate_comprehensive_report(self, all_results: Dict):
        """Generate comprehensive analysis report"""
        report = []
        report.append("# TED China Procurement Analysis Report")
        report.append(f"\n**Generated:** {datetime.now().isoformat()}")
        report.append(f"**Data Source:** TED (Tenders Electronic Daily)")
        report.append(f"**Analysis Period:** {min(all_results.keys())}-{max(all_results.keys())}")

        report.append("\n## Executive Summary")
        report.append(f"- **Total Contracts Analyzed:** {self.stats['total_contracts']:,}")
        report.append(f"- **China-Related Contracts:** {self.stats['china_related']:,}")
        report.append(f"- **Percentage:** {self.stats['china_related']/max(self.stats['total_contracts'],1)*100:.2f}%")

        report.append("\n## Temporal Trends")
        report.append("\n| Year | Total | China-Related | Percentage |")
        report.append("|------|-------|---------------|------------|")
        for year in sorted(all_results.keys()):
            total = all_results[year]['total']
            china = all_results[year]['china_related']
            pct = china/max(total,1)*100
            report.append(f"| {year} | {total:,} | {china:,} | {pct:.2f}% |")

        report.append("\n## Top EU Countries (China Contracts)")
        for country, count in sorted(self.stats['by_country'].items(), key=lambda x: x[1], reverse=True)[:10]:
            report.append(f"- **{country}:** {count:,} contracts")

        report.append("\n## Technology Categories")
        for category, count in sorted(self.stats['by_category'].items(), key=lambda x: x[1], reverse=True):
            report.append(f"- **{category.title()}:** {count:,} contracts")

        report.append("\n## Top Chinese Companies")
        for company, count in self.stats['chinese_companies'].most_common(20):
            report.append(f"- {company}: {count} contracts")

        # Save report
        report_file = self.output_path / "TED_CHINA_COMPREHENSIVE_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))

        # Save statistics
        stats_file = self.output_path / "ted_china_statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total_contracts': self.stats['total_contracts'],
                    'china_related': self.stats['china_related'],
                    'percentage': self.stats['china_related']/max(self.stats['total_contracts'],1)*100
                },
                'by_year': dict(self.stats['by_year']),
                'by_country': dict(self.stats['by_country']),
                'by_category': dict(self.stats['by_category']),
                'top_companies': self.stats['chinese_companies'].most_common(50)
            }, f, indent=2)

        logger.info(f"\n{'='*60}")
        logger.info("ANALYSIS COMPLETE")
        logger.info(f"Report saved to: {report_file}")
        logger.info(f"Statistics saved to: {stats_file}")
        logger.info(f"{'='*60}")

if __name__ == "__main__":
    analyzer = TEDChinaAnalyzer()

    # Analyze recent years with most relevant data
    results = analyzer.analyze_all_years(start_year=2018, end_year=2024)

    print(f"\n{'='*60}")
    print("TED CHINA ANALYSIS SUMMARY")
    print(f"{'='*60}")
    print(f"Total contracts analyzed: {analyzer.stats['total_contracts']:,}")
    print(f"China-related contracts: {analyzer.stats['china_related']:,}")
    print(f"Percentage: {analyzer.stats['china_related']/max(analyzer.stats['total_contracts'],1)*100:.2f}%")
    print(f"\nTop 5 countries by China contracts:")
    for country, count in sorted(analyzer.stats['by_country'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {country}: {count:,}")
