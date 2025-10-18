"""
USAspending.gov China Analysis Script
Analyzes US federal contracts and grants for China-related entities
Uses USAspending API v2
"""

import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict, Counter
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class USAspendingChinaAnalyzer:
    """Analyzes USAspending data for China connections"""

    def __init__(self):
        self.base_url = "https://api.usaspending.gov/api/v2"
        self.output_path = Path("C:/Projects/OSINT - Foresight/data/processed/usaspending_china")
        self.output_path.mkdir(parents=True, exist_ok=True)

        # China-related patterns for vendor/recipient names
        self.china_patterns = [
            # Chinese companies
            'huawei', 'zte', 'lenovo', 'xiaomi', 'alibaba', 'tencent',
            'baidu', 'dji', 'hikvision', 'dahua', 'bgi', 'bytedance',
            'smic', 'byd', 'geely', 'haier', 'tcl', 'oppo', 'vivo',
            'china telecom', 'china mobile', 'china unicom',
            'sinopec', 'petrochina', 'cnooc', 'sinochem',
            'cosco', 'china shipping', 'china merchants',
            'bank of china', 'icbc', 'ccb', 'agricultural bank',
            # Geographic indicators
            'beijing', 'shanghai', 'shenzhen', 'guangzhou', 'hong kong',
            'china', 'chinese', 'prc', 'peoples republic'
        ]

        # Critical technology keywords
        self.tech_keywords = {
            'ai_ml': ['artificial intelligence', 'machine learning', 'neural network', 'deep learning'],
            'quantum': ['quantum computing', 'quantum', 'qubit'],
            'semiconductors': ['semiconductor', 'chip', 'microprocessor', 'integrated circuit'],
            '5g_6g': ['5g', '6g', 'wireless', 'telecommunications'],
            'hypersonics': ['hypersonic', 'scramjet', 'high speed'],
            'biotechnology': ['biotechnology', 'genomics', 'synthetic biology', 'crispr'],
            'autonomous': ['autonomous', 'unmanned', 'drone', 'uav'],
            'cyber': ['cybersecurity', 'encryption', 'cryptography'],
            'space': ['satellite', 'spacecraft', 'launch vehicle'],
            'energy': ['battery', 'solar', 'renewable energy', 'nuclear']
        }

        self.stats = defaultdict(int)
        self.china_contracts = []
        self.china_grants = []

    def search_contracts(self, start_date: str, end_date: str, keywords: List[str] = None):
        """Search for contracts using the Advanced Search API"""

        endpoint = f"{self.base_url}/search/spending_by_award/"

        # Build filters
        filters = {
            "time_period": [{
                "start_date": start_date,
                "end_date": end_date
            }]
        }

        if keywords:
            filters["keywords"] = keywords

        payload = {
            "filters": filters,
            "fields": [
                "Award ID", "Recipient Name", "Award Amount",
                "Awarding Agency", "Awarding Sub Agency",
                "Contract Award Type", "Description",
                "Place of Performance City",
                "Place of Performance State",
                "Action Date", "Period of Performance Start Date",
                "Period of Performance Current End Date",
                "NAICS Code", "NAICS Description"
            ],
            "page": 1,
            "limit": 100,
            "sort": "Award Amount",
            "order": "desc"
        }

        all_results = []

        while True:
            try:
                response = requests.post(endpoint, json=payload)
                response.raise_for_status()
                data = response.json()

                results = data.get('results', [])
                if not results:
                    break

                all_results.extend(results)

                # Check if more pages
                if not data.get('hasNext', False):
                    break

                payload['page'] += 1
                time.sleep(0.5)  # Rate limiting

            except Exception as e:
                logger.error(f"Error searching contracts: {e}")
                break

        return all_results

    def analyze_vendor(self, vendor_name: str) -> bool:
        """Check if vendor name matches China patterns"""
        if not vendor_name:
            return False

        vendor_lower = vendor_name.lower()
        return any(pattern in vendor_lower for pattern in self.china_patterns)

    def analyze_description(self, description: str) -> List[str]:
        """Extract technology categories from description"""
        if not description:
            return []

        desc_lower = description.lower()
        categories = []

        for category, keywords in self.tech_keywords.items():
            if any(keyword in desc_lower for keyword in keywords):
                categories.append(category)

        return categories

    def get_vendor_details(self, vendor_duns: str) -> Optional[Dict]:
        """Get detailed vendor information using DUNS number"""

        endpoint = f"{self.base_url}/recipient/duns/{vendor_duns}/"

        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.debug(f"Error getting vendor details for DUNS {vendor_duns}: {e}")
            return None

    def analyze_contracts_by_year(self, year: int):
        """Analyze all contracts for a specific year"""

        logger.info(f"Analyzing contracts for {year}")

        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"

        # Search for contracts with potential China connections
        contracts = self.search_contracts(start_date, end_date)

        year_stats = {
            'total_contracts': len(contracts),
            'china_related': 0,
            'by_agency': defaultdict(int),
            'by_technology': defaultdict(int),
            'by_vendor': defaultdict(float),
            'total_value': 0
        }

        for contract in contracts:
            vendor_name = contract.get('Recipient Name', '')
            description = contract.get('Description', '')
            amount = float(contract.get('Award Amount', 0))
            agency = contract.get('Awarding Agency', '')

            # Check for China connection
            if self.analyze_vendor(vendor_name):
                year_stats['china_related'] += 1
                year_stats['by_agency'][agency] += 1
                year_stats['by_vendor'][vendor_name] += amount
                year_stats['total_value'] += amount

                # Analyze technology categories
                categories = self.analyze_description(description)
                for category in categories:
                    year_stats['by_technology'][category] += 1

                # Store contract details
                self.china_contracts.append({
                    'award_id': contract.get('Award ID'),
                    'vendor': vendor_name,
                    'amount': amount,
                    'agency': agency,
                    'description': description[:500],
                    'date': contract.get('Action Date'),
                    'categories': categories,
                    'place': f"{contract.get('Place of Performance City', '')}, {contract.get('Place of Performance State', '')}"
                })

        return year_stats

    def search_specific_vendors(self, vendor_list: List[str]):
        """Search for specific Chinese vendors"""

        logger.info(f"Searching for specific vendors: {vendor_list}")

        all_results = []

        for vendor in vendor_list:
            logger.info(f"  Searching for: {vendor}")

            # Search using vendor name as keyword
            endpoint = f"{self.base_url}/search/spending_by_award/"

            payload = {
                "filters": {
                    "keywords": [vendor],
                    "time_period": [{
                        "start_date": "2015-01-01",
                        "end_date": "2025-12-31"
                    }]
                },
                "fields": ["Award ID", "Recipient Name", "Award Amount",
                          "Awarding Agency", "Description", "Action Date"],
                "limit": 100,
                "page": 1
            }

            try:
                response = requests.post(endpoint, json=payload)
                response.raise_for_status()
                data = response.json()

                results = data.get('results', [])
                if results:
                    logger.info(f"    Found {len(results)} contracts for {vendor}")
                    all_results.extend(results)

            except Exception as e:
                logger.error(f"    Error searching for {vendor}: {e}")

            time.sleep(1)  # Rate limiting

        return all_results

    def analyze_agency_spending(self, agency_name: str = None):
        """Analyze spending by specific agency"""

        endpoint = f"{self.base_url}/agency/{agency_name}/awards/" if agency_name else f"{self.base_url}/agencies/awards/"

        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error analyzing agency spending: {e}")
            return None

    def generate_comprehensive_report(self, start_year: int = 2020, end_year: int = 2024):
        """Generate comprehensive analysis report"""

        logger.info(f"Generating USAspending China analysis for {start_year}-{end_year}")

        all_stats = {}

        # Analyze each year
        for year in range(start_year, end_year + 1):
            year_stats = self.analyze_contracts_by_year(year)
            all_stats[year] = year_stats

            # Save intermediate results
            self.save_year_results(year, year_stats)

        # Search for specific known Chinese companies
        chinese_vendors = [
            'huawei', 'zte', 'dji', 'hikvision', 'dahua',
            'lenovo', 'bgi', 'sensetime', 'megvii'
        ]

        specific_results = self.search_specific_vendors(chinese_vendors)

        # Generate report
        self.create_final_report(all_stats, specific_results)

        return all_stats

    def save_year_results(self, year: int, stats: Dict):
        """Save results for specific year"""

        output_file = self.output_path / f"usaspending_{year}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'year': year,
                'statistics': stats,
                'china_contracts': [c for c in self.china_contracts if str(year) in c.get('date', '')]
            }, f, indent=2, default=str)

        logger.info(f"Saved {year} results to {output_file}")

    def create_final_report(self, all_stats: Dict, specific_vendors: List):
        """Create final analysis report"""

        report = []
        report.append("# USAspending China Analysis Report")
        report.append(f"\n**Generated:** {datetime.now().isoformat()}")
        report.append(f"**Data Source:** USAspending.gov API v2")
        report.append(f"**Analysis Period:** {min(all_stats.keys())}-{max(all_stats.keys())}")

        # Executive Summary
        total_china = sum(s['china_related'] for s in all_stats.values())
        total_value = sum(s['total_value'] for s in all_stats.values())

        report.append("\n## Executive Summary")
        report.append(f"- **Total China-Related Contracts:** {total_china:,}")
        report.append(f"- **Total Contract Value:** ${total_value:,.2f}")
        report.append(f"- **Years Analyzed:** {len(all_stats)}")

        # Temporal Trends
        report.append("\n## Temporal Trends")
        report.append("\n| Year | China Contracts | Total Value | Top Agency |")
        report.append("|------|----------------|-------------|------------|")

        for year, stats in sorted(all_stats.items()):
            top_agency = max(stats['by_agency'].items(), key=lambda x: x[1])[0] if stats['by_agency'] else 'N/A'
            report.append(f"| {year} | {stats['china_related']:,} | ${stats['total_value']:,.0f} | {top_agency} |")

        # Technology Categories
        all_tech = defaultdict(int)
        for stats in all_stats.values():
            for tech, count in stats['by_technology'].items():
                all_tech[tech] += count

        report.append("\n## Technology Categories")
        for tech, count in sorted(all_tech.items(), key=lambda x: x[1], reverse=True):
            report.append(f"- **{tech.replace('_', ' ').title()}:** {count} contracts")

        # Top Vendors
        all_vendors = defaultdict(float)
        for stats in all_stats.values():
            for vendor, amount in stats['by_vendor'].items():
                all_vendors[vendor] += amount

        report.append("\n## Top China-Related Vendors")
        for vendor, amount in sorted(all_vendors.items(), key=lambda x: x[1], reverse=True)[:20]:
            report.append(f"- {vendor}: ${amount:,.2f}")

        # Specific Vendor Search Results
        if specific_vendors:
            report.append("\n## Targeted Vendor Search Results")
            vendor_summary = defaultdict(lambda: {'count': 0, 'value': 0})

            for contract in specific_vendors:
                vendor = contract.get('Recipient Name', 'Unknown')
                vendor_summary[vendor]['count'] += 1
                vendor_summary[vendor]['value'] += float(contract.get('Award Amount', 0))

            for vendor, data in sorted(vendor_summary.items(), key=lambda x: x[1]['value'], reverse=True):
                report.append(f"- {vendor}: {data['count']} contracts, ${data['value']:,.2f}")

        # Risk Assessment
        report.append("\n## Risk Assessment")
        report.append("\n### High-Risk Technology Areas")
        high_risk_tech = ['quantum', 'ai_ml', 'semiconductors', 'hypersonics', '5g_6g']
        for tech in high_risk_tech:
            if tech in all_tech:
                report.append(f"- **{tech.replace('_', ' ').title()}:** {all_tech[tech]} contracts identified")

        # Save report
        report_file = self.output_path / "USASPENDING_CHINA_ANALYSIS.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))

        # Save detailed data
        data_file = self.output_path / "usaspending_china_comprehensive.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total_contracts': total_china,
                    'total_value': total_value,
                    'years_analyzed': len(all_stats)
                },
                'yearly_statistics': all_stats,
                'china_contracts': self.china_contracts[:500],  # Top 500
                'specific_vendor_results': specific_vendors[:100]  # Top 100
            }, f, indent=2, default=str)

        logger.info(f"\n{'='*60}")
        logger.info("ANALYSIS COMPLETE")
        logger.info(f"Report saved to: {report_file}")
        logger.info(f"Data saved to: {data_file}")
        logger.info(f"Total China-related contracts: {total_china:,}")
        logger.info(f"Total value: ${total_value:,.2f}")
        logger.info(f"{'='*60}")

if __name__ == "__main__":
    analyzer = USAspendingChinaAnalyzer()

    # Run comprehensive analysis
    stats = analyzer.generate_comprehensive_report(start_year=2020, end_year=2024)

    # Display summary
    print(f"\n{'='*60}")
    print("USASPENDING CHINA ANALYSIS SUMMARY")
    print(f"{'='*60}")

    total_contracts = sum(s['china_related'] for s in stats.values())
    total_value = sum(s['total_value'] for s in stats.values())

    print(f"Total China-related contracts (2020-2024): {total_contracts:,}")
    print(f"Total contract value: ${total_value:,.2f}")
    print(f"\nTop agencies by China contracts:")

    all_agencies = defaultdict(int)
    for year_stats in stats.values():
        for agency, count in year_stats['by_agency'].items():
            all_agencies[agency] += count

    for agency, count in sorted(all_agencies.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {agency}: {count} contracts")
