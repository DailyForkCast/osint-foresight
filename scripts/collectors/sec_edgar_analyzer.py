#!/usr/bin/env python3
"""
SEC EDGAR Analyzer for Italian Companies
Analyzes SEC filings for Italian companies listed in US markets or with US operations
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SECEdgarAnalyzer:
    """Analyze SEC EDGAR filings for Italian companies"""

    def __init__(self, data_path: str = "F:/OSINT_Data/SEC_EDGAR"):
        self.data_path = Path(data_path)
        self.output_dir = Path("artifacts/ITA/sec_edgar_analysis")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Italian companies that might have SEC filings
        self.italian_companies = [
            'ENI', 'Enel', 'Leonardo', 'Stellantis', 'Ferrari', 'Luxottica',
            'Telecom Italia', 'Mediaset', 'Prysmian', 'Campari', 'Moncler',
            'STMicroelectronics', 'Tenaris', 'CNH Industrial'
        ]

        # Risk keywords to search for
        self.risk_keywords = {
            'china_exposure': ['China', 'Chinese', 'PRC', 'Hong Kong', 'supply chain'],
            'technology_risk': ['intellectual property', 'technology transfer', 'R&D', 'innovation'],
            'cyber_risk': ['cybersecurity', 'data breach', 'cyber attack', 'information security'],
            'geopolitical': ['sanctions', 'trade war', 'tariff', 'export control', 'CFIUS']
        }

        self.results = {
            'summary': {},
            'companies_analyzed': [],
            'china_exposures': [],
            'technology_risks': [],
            'supply_chain_disclosures': [],
            'rd_investments': {},
            'risk_factors': {},
            'financial_metrics': {}
        }

    def analyze_filing(self, filepath: Path) -> Dict:
        """Analyze a single SEC filing"""

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            filing_data = {
                'file': filepath.name,
                'company': self._extract_company_name(content),
                'filing_type': self._extract_filing_type(content),
                'date': self._extract_filing_date(content),
                'china_mentions': 0,
                'china_revenue_exposure': None,
                'supply_chain_risks': [],
                'technology_disclosures': [],
                'rd_spending': None,
                'risk_factors': []
            }

            # Check if it's an Italian company
            if not any(company.lower() in filing_data['company'].lower() for company in self.italian_companies):
                return None

            # Analyze China exposure
            china_sections = self._find_china_mentions(content)
            filing_data['china_mentions'] = len(china_sections)

            if china_sections:
                # Extract revenue exposure if mentioned
                revenue_pattern = r'China.*?(\d+\.?\d*)\s*%.*?revenue'
                for section in china_sections:
                    match = re.search(revenue_pattern, section, re.IGNORECASE)
                    if match:
                        filing_data['china_revenue_exposure'] = float(match.group(1))
                        break

                self.results['china_exposures'].append({
                    'company': filing_data['company'],
                    'mentions': filing_data['china_mentions'],
                    'revenue_exposure': filing_data['china_revenue_exposure'],
                    'context': china_sections[:3]  # First 3 mentions
                })

            # Analyze supply chain disclosures
            supply_chain_sections = self._find_supply_chain_mentions(content)
            if supply_chain_sections:
                filing_data['supply_chain_risks'] = self._extract_supply_chain_risks(supply_chain_sections)
                self.results['supply_chain_disclosures'].append({
                    'company': filing_data['company'],
                    'risks': filing_data['supply_chain_risks']
                })

            # Extract R&D spending
            rd_spending = self._extract_rd_spending(content)
            if rd_spending:
                filing_data['rd_spending'] = rd_spending
                self.results['rd_investments'][filing_data['company']] = rd_spending

            # Extract risk factors
            risk_factors = self._extract_risk_factors(content)
            filing_data['risk_factors'] = risk_factors

            for risk_type, keywords in self.risk_keywords.items():
                risk_count = sum(1 for risk in risk_factors if any(kw.lower() in risk.lower() for kw in keywords))
                if risk_count > 0:
                    if risk_type not in self.results['risk_factors']:
                        self.results['risk_factors'][risk_type] = []
                    self.results['risk_factors'][risk_type].append({
                        'company': filing_data['company'],
                        'count': risk_count
                    })

            return filing_data

        except Exception as e:
            logger.error(f"Error processing {filepath}: {e}")
            return None

    def _extract_company_name(self, content: str) -> str:
        """Extract company name from filing"""

        pattern = r'COMPANY CONFORMED NAME:\s*([^\n]+)'
        match = re.search(pattern, content)
        if match:
            return match.group(1).strip()

        # Fallback pattern
        pattern = r'<COMPANY-NAME>([^<]+)'
        match = re.search(pattern, content)
        if match:
            return match.group(1).strip()

        return "Unknown"

    def _extract_filing_type(self, content: str) -> str:
        """Extract filing type (10-K, 20-F, etc.)"""

        pattern = r'FORM TYPE:\s*([^\n]+)'
        match = re.search(pattern, content)
        if match:
            return match.group(1).strip()

        return "Unknown"

    def _extract_filing_date(self, content: str) -> str:
        """Extract filing date"""

        pattern = r'FILED AS OF DATE:\s*(\d{8})'
        match = re.search(pattern, content)
        if match:
            date_str = match.group(1)
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"

        return "Unknown"

    def _find_china_mentions(self, content: str) -> List[str]:
        """Find all mentions of China in the filing"""

        china_patterns = ['China', 'Chinese', 'PRC', 'People\'s Republic of China']
        mentions = []

        for pattern in china_patterns:
            # Find context around mentions (200 chars before and after)
            regex = rf'.{{0,200}}{re.escape(pattern)}.{{0,200}}'
            matches = re.findall(regex, content, re.IGNORECASE)
            mentions.extend(matches)

        return mentions

    def _find_supply_chain_mentions(self, content: str) -> List[str]:
        """Find supply chain related sections"""

        supply_patterns = ['supply chain', 'supplier', 'procurement', 'sourcing', 'vendor']
        sections = []

        for pattern in supply_patterns:
            regex = rf'.{{0,300}}{re.escape(pattern)}.{{0,300}}'
            matches = re.findall(regex, content, re.IGNORECASE)
            sections.extend(matches)

        return sections

    def _extract_supply_chain_risks(self, sections: List[str]) -> List[str]:
        """Extract specific supply chain risks"""

        risks = []
        risk_patterns = [
            'single source', 'concentration', 'dependency', 'disruption',
            'shortage', 'constraint', 'availability'
        ]

        for section in sections:
            for pattern in risk_patterns:
                if pattern.lower() in section.lower():
                    risks.append(f"{pattern}: {section[:100]}...")
                    break

        return list(set(risks))[:5]  # Top 5 unique risks

    def _extract_rd_spending(self, content: str) -> float:
        """Extract R&D spending amount"""

        # Pattern for R&D spending in millions or billions
        patterns = [
            r'research and development.*?\$\s*(\d+\.?\d*)\s*(million|billion)',
            r'R&D.*?\$\s*(\d+\.?\d*)\s*(million|billion)',
            r'research.*?expenses.*?\$\s*(\d+\.?\d*)\s*(million|billion)'
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                amount = float(match.group(1))
                unit = match.group(2).lower()
                if unit == 'billion':
                    amount *= 1000  # Convert to millions
                return amount

        return None

    def _extract_risk_factors(self, content: str) -> List[str]:
        """Extract risk factors section"""

        # Find risk factors section
        pattern = r'RISK FACTORS(.*?)(?:ITEM|PART)'
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)

        if match:
            risk_section = match.group(1)
            # Extract individual risks (simplified)
            risks = re.split(r'\n\s*\n', risk_section)
            return [risk[:200] for risk in risks if len(risk) > 50][:20]  # Top 20 risks

        return []

    def analyze_all_filings(self):
        """Analyze all SEC filings in the data directory"""

        logger.info(f"Analyzing SEC filings in {self.data_path}")

        filing_files = list(self.data_path.glob("**/*.txt")) + list(self.data_path.glob("**/*.html"))
        logger.info(f"Found {len(filing_files)} filing files")

        for filepath in filing_files:
            result = self.analyze_filing(filepath)
            if result:
                self.results['companies_analyzed'].append(result)

    def generate_summary(self):
        """Generate summary statistics"""

        total_companies = len(set(c['company'] for c in self.results['companies_analyzed']))
        total_filings = len(self.results['companies_analyzed'])

        china_exposed = len([c for c in self.results['china_exposures'] if c['mentions'] > 0])
        avg_china_revenue = sum(c['revenue_exposure'] for c in self.results['china_exposures']
                               if c['revenue_exposure']) / max(1, len([c for c in self.results['china_exposures']
                                                                       if c['revenue_exposure']]))

        self.results['summary'] = {
            'total_italian_companies': total_companies,
            'total_filings_analyzed': total_filings,
            'companies_with_china_exposure': china_exposed,
            'average_china_revenue_exposure': avg_china_revenue if avg_china_revenue else 0,
            'companies_with_rd_disclosure': len(self.results['rd_investments']),
            'total_rd_spending_millions': sum(self.results['rd_investments'].values())
        }

    def save_results(self):
        """Save analysis results"""

        output_file = self.output_dir / "sec_edgar_italy_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        logger.info(f"Results saved to {output_file}")
        self.generate_markdown_report()

    def generate_markdown_report(self):
        """Generate markdown report"""

        report = f"""# SEC EDGAR Analysis - Italian Companies

**Generated:** {datetime.now().strftime('%Y-%m-%d')}
**Data Source:** SEC EDGAR Database
**Focus:** Italian companies with US listings/operations

## Executive Summary

- **Italian Companies Analyzed:** {self.results['summary'].get('total_italian_companies', 0)}
- **Total Filings Reviewed:** {self.results['summary'].get('total_filings_analyzed', 0)}
- **Companies with China Exposure:** {self.results['summary'].get('companies_with_china_exposure', 0)}
- **Average China Revenue Exposure:** {self.results['summary'].get('average_china_revenue_exposure', 0):.1f}%
- **Total R&D Spending:** ${self.results['summary'].get('total_rd_spending_millions', 0):,.0f}M

## China Exposure Analysis

"""

        # Add China exposure details
        for exposure in self.results['china_exposures'][:10]:
            report += f"### {exposure['company']}\n"
            report += f"- Mentions: {exposure['mentions']}\n"
            if exposure['revenue_exposure']:
                report += f"- Revenue Exposure: {exposure['revenue_exposure']}%\n"

        # Add R&D investments
        report += "\n## R&D Investment Disclosure\n\n"
        for company, spending in sorted(self.results['rd_investments'].items(), key=lambda x: x[1], reverse=True):
            report += f"- {company}: ${spending:,.0f}M\n"

        # Add risk factors
        report += "\n## Risk Factor Analysis\n\n"
        for risk_type, companies in self.results['risk_factors'].items():
            report += f"### {risk_type.replace('_', ' ').title()}\n"
            report += f"- Companies affected: {len(companies)}\n"

        report_file = self.output_dir / "sec_edgar_italy_report.md"
        with open(report_file, 'w') as f:
            f.write(report)

        logger.info(f"Report saved to {report_file}")

def main():
    """Run SEC EDGAR analysis for Italian companies"""

    analyzer = SECEdgarAnalyzer()

    print("\n" + "="*60)
    print("SEC EDGAR ANALYSIS - ITALIAN COMPANIES")
    print("="*60 + "\n")

    analyzer.analyze_all_filings()
    analyzer.generate_summary()
    analyzer.save_results()

    print("\nSummary:")
    for key, value in analyzer.results['summary'].items():
        print(f"  {key}: {value}")

    print(f"\nResults saved to: artifacts/ITA/sec_edgar_analysis/")

if __name__ == "__main__":
    main()
