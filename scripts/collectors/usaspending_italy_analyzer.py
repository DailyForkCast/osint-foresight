#!/usr/bin/env python3
"""
USAspending.gov Analyzer for Italy
Analyzes US government contracts and spending related to Italian entities
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class USAspendingItalyAnalyzer:
    """Analyze USAspending.gov data for Italian entities"""

    def __init__(self, data_path: str = "F:/OSINT_Data/USASPENDING"):
        self.data_path = Path(data_path)
        self.output_dir = Path("artifacts/ITA/usaspending_analysis")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Key Italian defense and technology companies
        self.italian_companies = [
            'Leonardo', 'Leonardo DRS', 'Leonardo S.p.A',
            'Fincantieri', 'Fincantieri Marine',
            'Iveco Defence', 'Oto Melara', 'Beretta',
            'Telespazio', 'Thales Alenia Space Italia',
            'STMicroelectronics', 'Ansaldo', 'Piaggio Aerospace'
        ]

        # Contract categories of interest
        self.contract_categories = {
            'defense': ['Defense', 'Military', 'Navy', 'Army', 'Air Force'],
            'aerospace': ['Space', 'Satellite', 'NASA', 'Aerospace'],
            'technology': ['Computer', 'Software', 'IT', 'Cyber', 'Data'],
            'research': ['Research', 'Development', 'R&D', 'Laboratory'],
            'manufacturing': ['Manufacturing', 'Production', 'Assembly']
        }

        self.results = {
            'summary': {},
            'contracts_by_company': defaultdict(list),
            'contracts_by_year': defaultdict(lambda: defaultdict(float)),
            'contracts_by_category': defaultdict(lambda: defaultdict(float)),
            'defense_contracts': [],
            'technology_contracts': [],
            'total_value_by_company': defaultdict(float),
            'china_related': [],
            'dual_use_concerns': []
        }

    def analyze_contract_file(self, filepath: Path) -> List[Dict]:
        """Analyze a single contract data file"""

        contracts = []
        try:
            if filepath.suffix == '.csv':
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        contract = self._process_contract_row(row)
                        if contract:
                            contracts.append(contract)
            elif filepath.suffix == '.json':
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            contract = self._process_contract_data(item)
                            if contract:
                                contracts.append(contract)
        except Exception as e:
            logger.error(f"Error processing {filepath}: {e}")

        return contracts

    def _process_contract_row(self, row: Dict) -> Dict:
        """Process a contract row from CSV"""

        vendor_name = row.get('recipient_name', '').upper()

        # Check if it's an Italian company
        is_italian = any(company.upper() in vendor_name for company in self.italian_companies)

        if not is_italian:
            # Also check country code
            if row.get('recipient_country_code', '') != 'IT':
                return None

        contract = {
            'contract_id': row.get('award_id_piid', ''),
            'vendor': row.get('recipient_name', ''),
            'vendor_country': row.get('recipient_country_code', ''),
            'agency': row.get('awarding_agency_name', ''),
            'sub_agency': row.get('awarding_sub_agency_name', ''),
            'amount': float(row.get('total_obligation', 0) or 0),
            'date': row.get('action_date', ''),
            'description': row.get('award_description', ''),
            'naics_code': row.get('naics_code', ''),
            'product_code': row.get('product_or_service_code', ''),
            'place_of_performance': row.get('primary_place_of_performance_country_name', ''),
            'contract_type': row.get('type_of_contract_pricing', ''),
            'set_aside': row.get('type_of_set_aside', ''),
            'category': self._categorize_contract(row)
        }

        return contract

    def _process_contract_data(self, data: Dict) -> Dict:
        """Process contract data from JSON"""

        vendor_name = data.get('vendor', {}).get('name', '').upper()

        # Check if it's an Italian company
        is_italian = any(company.upper() in vendor_name for company in self.italian_companies)

        if not is_italian:
            if data.get('vendor', {}).get('country', '') != 'Italy':
                return None

        contract = {
            'contract_id': data.get('id', ''),
            'vendor': data.get('vendor', {}).get('name', ''),
            'vendor_country': data.get('vendor', {}).get('country', ''),
            'agency': data.get('agency', ''),
            'sub_agency': data.get('sub_agency', ''),
            'amount': float(data.get('amount', 0)),
            'date': data.get('date', ''),
            'description': data.get('description', ''),
            'naics_code': data.get('naics', ''),
            'product_code': data.get('psc', ''),
            'place_of_performance': data.get('pop_country', ''),
            'contract_type': data.get('contract_type', ''),
            'category': self._categorize_contract(data)
        }

        return contract

    def _categorize_contract(self, contract_data: Dict) -> str:
        """Categorize contract based on description and codes"""

        description = str(contract_data.get('description', '') or
                         contract_data.get('award_description', '')).upper()

        for category, keywords in self.contract_categories.items():
            if any(keyword.upper() in description for keyword in keywords):
                return category

        # Check NAICS codes
        naics = str(contract_data.get('naics_code', '') or contract_data.get('naics', ''))
        if naics.startswith('336'):  # Aerospace
            return 'aerospace'
        elif naics.startswith('334'):  # Computer/Electronics
            return 'technology'
        elif naics.startswith('541'):  # Professional/Scientific
            return 'research'

        return 'other'

    def analyze_all_contracts(self):
        """Analyze all contract files"""

        logger.info(f"Analyzing contracts in {self.data_path}")

        contract_files = list(self.data_path.glob("**/*.csv")) + \
                        list(self.data_path.glob("**/*.json"))

        logger.info(f"Found {len(contract_files)} contract files")

        all_contracts = []
        for filepath in contract_files:
            contracts = self.analyze_contract_file(filepath)
            all_contracts.extend(contracts)

        # Process all contracts
        for contract in all_contracts:
            self._process_contract(contract)

    def _process_contract(self, contract: Dict):
        """Process individual contract"""

        vendor = contract['vendor']
        amount = contract['amount']
        year = contract['date'][:4] if contract['date'] else 'unknown'
        category = contract['category']

        # Track by company
        self.results['contracts_by_company'][vendor].append(contract)
        self.results['total_value_by_company'][vendor] += amount

        # Track by year
        self.results['contracts_by_year'][year]['total'] += amount
        self.results['contracts_by_year'][year]['count'] += 1

        # Track by category
        self.results['contracts_by_category'][category]['total'] += amount
        self.results['contracts_by_category'][category]['count'] += 1

        # Special categories
        if category == 'defense':
            self.results['defense_contracts'].append(contract)
        elif category == 'technology':
            self.results['technology_contracts'].append(contract)

        # Check for China-related concerns
        if self._check_china_related(contract):
            self.results['china_related'].append(contract)

        # Check for dual-use concerns
        if self._check_dual_use(contract):
            self.results['dual_use_concerns'].append(contract)

    def _check_china_related(self, contract: Dict) -> bool:
        """Check if contract might have China-related concerns"""

        description = contract['description'].upper()
        china_keywords = ['CHINA', 'CHINESE', 'PRC', 'INDO-PACIFIC', 'TAIWAN']

        return any(keyword in description for keyword in china_keywords)

    def _check_dual_use(self, contract: Dict) -> bool:
        """Check for potential dual-use technology concerns"""

        dual_use_keywords = [
            'SEMICONDUCTOR', 'MICROCHIP', 'QUANTUM', 'AI', 'ARTIFICIAL INTELLIGENCE',
            'CRYPTOGRAPH', 'SATELLITE', 'MISSILE', 'RADAR', 'SENSOR', 'NAVIGATION'
        ]

        description = contract['description'].upper()
        return any(keyword in description for keyword in dual_use_keywords)

    def analyze_trends(self):
        """Analyze contracting trends"""

        logger.info("Analyzing contracting trends")

        # Calculate year-over-year growth
        years = sorted(self.results['contracts_by_year'].keys())
        if len(years) > 1:
            for i in range(1, len(years)):
                prev_year = years[i-1]
                curr_year = years[i]
                prev_total = self.results['contracts_by_year'][prev_year]['total']
                curr_total = self.results['contracts_by_year'][curr_year]['total']

                if prev_total > 0:
                    growth = ((curr_total - prev_total) / prev_total) * 100
                    self.results['contracts_by_year'][curr_year]['growth'] = growth

    def generate_summary(self):
        """Generate summary statistics"""

        total_contracts = sum(data['count'] for data in self.results['contracts_by_year'].values())
        total_value = sum(data['total'] for data in self.results['contracts_by_year'].values())

        self.results['summary'] = {
            'total_contracts': total_contracts,
            'total_value': total_value,
            'companies_identified': len(self.results['contracts_by_company']),
            'defense_contracts': len(self.results['defense_contracts']),
            'technology_contracts': len(self.results['technology_contracts']),
            'china_related_contracts': len(self.results['china_related']),
            'dual_use_concerns': len(self.results['dual_use_concerns']),
            'top_vendor': max(self.results['total_value_by_company'].items(),
                            key=lambda x: x[1])[0] if self.results['total_value_by_company'] else 'N/A',
            'top_category': max(self.results['contracts_by_category'].items(),
                              key=lambda x: x[1]['total'])[0] if self.results['contracts_by_category'] else 'N/A'
        }

    def save_results(self):
        """Save analysis results"""

        output_file = self.output_dir / "usaspending_italy_analysis.json"

        # Convert defaultdicts to regular dicts for JSON serialization
        results_to_save = {
            'summary': self.results['summary'],
            'top_companies': sorted(
                [(company, value) for company, value in self.results['total_value_by_company'].items()],
                key=lambda x: x[1],
                reverse=True
            )[:20],
            'category_breakdown': dict(self.results['contracts_by_category']),
            'yearly_trends': dict(self.results['contracts_by_year']),
            'china_related_count': len(self.results['china_related']),
            'dual_use_count': len(self.results['dual_use_concerns'])
        }

        with open(output_file, 'w') as f:
            json.dump(results_to_save, f, indent=2, default=str)

        logger.info(f"Results saved to {output_file}")
        self.generate_markdown_report()

    def generate_markdown_report(self):
        """Generate markdown report"""

        report = f"""# USAspending.gov Analysis - Italian Contractors

**Generated:** {datetime.now().strftime('%Y-%m-%d')}
**Data Source:** USAspending.gov
**Focus:** US government contracts to Italian entities

## Executive Summary

- **Total Contracts:** {self.results['summary'].get('total_contracts', 0):,}
- **Total Value:** ${self.results['summary'].get('total_value', 0):,.2f}
- **Italian Companies:** {self.results['summary'].get('companies_identified', 0)}
- **Defense Contracts:** {self.results['summary'].get('defense_contracts', 0)}
- **Technology Contracts:** {self.results['summary'].get('technology_contracts', 0)}
- **China-Related:** {self.results['summary'].get('china_related_contracts', 0)}
- **Dual-Use Concerns:** {self.results['summary'].get('dual_use_concerns', 0)}

## Top Italian Contractors

"""
        # Add top companies
        for company, value in sorted(
            self.results['total_value_by_company'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]:
            contract_count = len(self.results['contracts_by_company'][company])
            report += f"- **{company}**: ${value:,.2f} ({contract_count} contracts)\n"

        # Add category breakdown
        report += "\n## Contract Categories\n\n"
        for category, data in sorted(
            self.results['contracts_by_category'].items(),
            key=lambda x: x[1]['total'],
            reverse=True
        ):
            report += f"- **{category.title()}**: ${data['total']:,.2f} ({data['count']} contracts)\n"

        # Add yearly trends
        report += "\n## Yearly Trends\n\n"
        for year in sorted(self.results['contracts_by_year'].keys())[-5:]:
            data = self.results['contracts_by_year'][year]
            growth = data.get('growth', 0)
            report += f"- **{year}**: ${data['total']:,.2f} ({data['count']} contracts"
            if growth:
                report += f", {growth:+.1f}% growth"
            report += ")\n"

        # Add risk assessment
        report += "\n## Risk Assessment\n\n"
        if self.results['china_related']:
            report += f"### China-Related Contracts: {len(self.results['china_related'])}\n\n"
            for contract in self.results['china_related'][:5]:
                report += f"- {contract['vendor']}: {contract['description'][:100]}...\n"

        if self.results['dual_use_concerns']:
            report += f"\n### Dual-Use Technology Concerns: {len(self.results['dual_use_concerns'])}\n\n"
            for contract in self.results['dual_use_concerns'][:5]:
                report += f"- {contract['vendor']}: {contract['description'][:100]}...\n"

        report_file = self.output_dir / "usaspending_italy_report.md"
        with open(report_file, 'w') as f:
            f.write(report)

        logger.info(f"Report saved to {report_file}")

def main():
    """Run USAspending analysis for Italian contractors"""

    analyzer = USAspendingItalyAnalyzer()

    print("\n" + "="*60)
    print("USASPENDING.GOV ANALYSIS - ITALIAN CONTRACTORS")
    print("="*60 + "\n")

    analyzer.analyze_all_contracts()
    analyzer.analyze_trends()
    analyzer.generate_summary()
    analyzer.save_results()

    print("\nSummary:")
    for key, value in analyzer.results['summary'].items():
        print(f"  {key}: {value}")

    print(f"\nResults saved to: artifacts/ITA/usaspending_analysis/")

if __name__ == "__main__":
    main()
