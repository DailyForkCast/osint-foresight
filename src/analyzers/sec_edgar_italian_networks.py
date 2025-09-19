#!/usr/bin/env python3
"""
Comprehensive SEC EDGAR Analysis for Italian Company Networks
Maps all Italian companies in US markets and their relationships
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from collections import defaultdict
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class SECItalianNetworkAnalyzer:
    """Comprehensive analysis of Italian companies in US markets via SEC EDGAR"""

    def __init__(self):
        self.output_dir = Path("data/processed/sec_italian_networks")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # SEC EDGAR API settings
        self.base_url = "https://www.sec.gov/files/company_tickers.json"
        self.edgar_base = "https://data.sec.gov/submissions"

        # User agent required by SEC
        self.headers = {
            'User-Agent': 'OSINT-Research team@research.org'
        }

        # Italian companies and subsidiaries to track
        self.italian_targets = {
            # Defense & Aerospace
            'leonardo': ['leonardo', 'finmeccanica', 'alenia', 'agusta', 'oto melara', 'selex'],
            'fincantieri': ['fincantieri', 'marinette marine', 'viareggio superyachts'],

            # Energy & Utilities
            'enel': ['enel', 'endesa', '3sun', 'enel green power'],
            'eni': ['eni', 'saipem', 'snam', 'versalis', 'agip'],
            'terna': ['terna', 'terna plus'],

            # Finance
            'intesa': ['intesa sanpaolo', 'banca dei territori'],
            'unicredit': ['unicredit', 'hvb', 'bank austria'],
            'generali': ['assicurazioni generali', 'generali group'],

            # Technology & Telecom
            'stmicroelectronics': ['stmicroelectronics', 'st micro'],
            'prysmian': ['prysmian', 'draka'],
            'italtel': ['italtel'],

            # Industrial
            'stellantis': ['stellantis', 'fiat chrysler', 'fca', 'iveco', 'maserati'],
            'pirelli': ['pirelli', 'pirelli tire'],
            'cnh': ['cnh industrial', 'case new holland', 'iveco'],
            'ferrari': ['ferrari'],

            # Luxury & Consumer
            'luxottica': ['luxottica', 'essilor luxottica'],
            'prada': ['prada'],
            'armani': ['giorgio armani'],

            # Infrastructure
            'atlantia': ['atlantia', 'autostrade', 'aeroporti di roma'],
            'cdp': ['cassa depositi prestiti'],

            # Media & Tech
            'mediaset': ['mediaset', 'mfe'],
            'reply': ['reply'],
            'engineering': ['engineering group']
        }

        # Chinese company indicators to look for in filings
        self.china_indicators = [
            'china', 'chinese', 'beijing', 'shanghai', 'shenzhen', 'guangzhou',
            'huawei', 'zte', 'alibaba', 'tencent', 'baidu', 'byd',
            'catl', 'contemporary amperex', 'ningde', 'ganfeng',
            'tianqi lithium', 'jiangxi ganfeng', 'sichuan',
            'sinopec', 'petrochina', 'cnooc', 'sinochem',
            'icbc', 'bank of china', 'china construction bank',
            'state grid', 'china southern grid', 'sgcc'
        ]

        self.results = {
            'companies_found': [],
            'china_relationships': [],
            'subsidiary_networks': {},
            'financial_flows': [],
            'supply_chain_links': [],
            'board_connections': []
        }

    def get_company_ticker_data(self):
        """Get all company ticker mappings from SEC"""
        logger.info("Fetching company ticker data from SEC...")

        try:
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()

            ticker_data = response.json()
            logger.info(f"Retrieved {len(ticker_data)} company records")

            return ticker_data

        except Exception as e:
            logger.error(f"Error fetching ticker data: {e}")
            return {}

    def find_italian_companies(self, ticker_data):
        """Find Italian companies in SEC database"""
        logger.info("Identifying Italian companies...")

        italian_companies = []

        for cik, company_info in ticker_data.items():
            company_name = company_info.get('title', '').lower()
            ticker = company_info.get('ticker', '')

            # Check against our Italian targets
            for group, variants in self.italian_targets.items():
                for variant in variants:
                    if variant in company_name:
                        italian_companies.append({
                            'cik': cik,
                            'ticker': ticker,
                            'name': company_info.get('title'),
                            'group': group,
                            'matched_variant': variant
                        })
                        logger.info(f"Found: {company_info.get('title')} (CIK: {cik})")
                        break

            # Also look for obvious Italian indicators
            italian_indicators = ['spa', 's.p.a.', 'italy', 'italian', 'milano', 'rome', 'torino']
            if any(indicator in company_name for indicator in italian_indicators):
                italian_companies.append({
                    'cik': cik,
                    'ticker': ticker,
                    'name': company_info.get('title'),
                    'group': 'other_italian',
                    'matched_variant': 'italian_indicator'
                })
                logger.info(f"Found Italian indicator: {company_info.get('title')}")

        self.results['companies_found'] = italian_companies
        return italian_companies

    def analyze_company_filings(self, company):
        """Analyze SEC filings for a specific company"""
        logger.info(f"Analyzing filings for {company['name']}...")

        cik = company['cik'].zfill(10)  # SEC requires 10-digit CIK

        try:
            # Get company submission summary
            url = f"{self.edgar_base}/CIK{cik}.json"
            response = requests.get(url, headers=self.headers)

            if response.status_code != 200:
                logger.warning(f"Could not fetch data for {company['name']}: {response.status_code}")
                return

            data = response.json()

            # Analyze recent filings (last 2 years)
            recent_filings = self.get_recent_filings(data)

            for filing in recent_filings[:20]:  # Limit to most recent 20
                self.analyze_filing_content(company, filing)
                time.sleep(0.1)  # Rate limiting

        except Exception as e:
            logger.error(f"Error analyzing {company['name']}: {e}")

    def get_recent_filings(self, submission_data):
        """Get recent filings from submission data"""
        recent_filings = []

        if 'filings' not in submission_data:
            return recent_filings

        filings = submission_data['filings']['recent']

        # Look for key filing types
        target_forms = ['10-K', '10-Q', '8-K', 'DEF 14A', '20-F']

        for i, form in enumerate(filings.get('form', [])):
            if form in target_forms:
                filing_date = filings['filingDate'][i]

                # Only recent filings (last 2 years)
                if filing_date >= '2022-01-01':
                    recent_filings.append({
                        'form': form,
                        'filing_date': filing_date,
                        'accession_number': filings['accessionNumber'][i],
                        'primary_document': filings['primaryDocument'][i]
                    })

        return sorted(recent_filings, key=lambda x: x['filing_date'], reverse=True)

    def analyze_filing_content(self, company, filing):
        """Analyze content of a specific filing"""
        # Construct filing URL
        accession = filing['accession_number'].replace('-', '')
        cik = company['cik'].zfill(10)

        filing_url = f"https://www.sec.gov/Archives/edgar/data/{company['cik']}/{accession}/{filing['primary_document']}"

        try:
            response = requests.get(filing_url, headers=self.headers)
            if response.status_code != 200:
                return

            content = response.text.lower()

            # Search for China-related content
            china_mentions = []
            for indicator in self.china_indicators:
                if indicator in content:
                    china_mentions.append(indicator)

            if china_mentions:
                # Extract context around mentions
                china_context = self.extract_china_context(content, china_mentions)

                self.results['china_relationships'].append({
                    'company': company['name'],
                    'ticker': company['ticker'],
                    'filing_type': filing['form'],
                    'filing_date': filing['filing_date'],
                    'china_mentions': china_mentions,
                    'context': china_context,
                    'filing_url': filing_url
                })

                logger.info(f"China relationship found: {company['name']} - {', '.join(china_mentions)}")

            # Look for subsidiary information
            self.extract_subsidiary_info(company, content, filing)

            # Look for financial flows
            self.extract_financial_flows(company, content, filing)

        except Exception as e:
            logger.debug(f"Error analyzing filing content: {e}")

    def extract_china_context(self, content, mentions):
        """Extract context around China mentions"""
        contexts = []

        for mention in mentions[:5]:  # Limit contexts
            pattern = rf'.{{0,200}}{re.escape(mention)}.{{0,200}}'
            matches = re.findall(pattern, content, re.IGNORECASE)

            for match in matches[:3]:  # Max 3 contexts per mention
                contexts.append({
                    'mention': mention,
                    'context': match.strip()[:400]  # Limit length
                })

        return contexts

    def extract_subsidiary_info(self, company, content, filing):
        """Extract subsidiary and affiliate information"""
        # Look for subsidiary patterns
        subsidiary_patterns = [
            r'subsidiary.{0,100}china',
            r'affiliate.{0,100}china',
            r'joint venture.{0,100}china',
            r'partnership.{0,100}china'
        ]

        for pattern in subsidiary_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if company['name'] not in [s['company'] for s in self.results['subsidiary_networks'].get('china_subs', [])]:
                    if 'china_subs' not in self.results['subsidiary_networks']:
                        self.results['subsidiary_networks']['china_subs'] = []

                    self.results['subsidiary_networks']['china_subs'].append({
                        'company': company['name'],
                        'relationship_type': 'subsidiary/affiliate',
                        'description': match[:300],
                        'filing_date': filing['filing_date']
                    })

    def extract_financial_flows(self, company, content, filing):
        """Extract financial flow information"""
        # Look for revenue/sales patterns with China
        financial_patterns = [
            r'revenue.{0,50}china.{0,50}\$[\d,]+',
            r'sales.{0,50}china.{0,50}\$[\d,]+',
            r'china.{0,50}revenue.{0,50}\$[\d,]+',
            r'china.{0,50}sales.{0,50}\$[\d,]+'
        ]

        for pattern in financial_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                self.results['financial_flows'].append({
                    'company': company['name'],
                    'flow_type': 'revenue/sales',
                    'description': match[:200],
                    'filing_date': filing['filing_date'],
                    'filing_type': filing['form']
                })

    def analyze_supply_chain_links(self):
        """Analyze supply chain relationships from collected data"""
        logger.info("Analyzing supply chain connections...")

        # Group by company and analyze patterns
        company_china_links = defaultdict(list)

        for relationship in self.results['china_relationships']:
            company_china_links[relationship['company']].append(relationship)

        # Identify critical supply chain dependencies
        for company, links in company_china_links.items():
            # Look for supply chain keywords in contexts
            supply_indicators = ['supplier', 'procurement', 'sourcing', 'manufacturing', 'component']

            supply_links = []
            for link in links:
                for context in link.get('context', []):
                    if any(indicator in context['context'].lower() for indicator in supply_indicators):
                        supply_links.append(context)

            if supply_links:
                self.results['supply_chain_links'].append({
                    'company': company,
                    'china_supply_links': len(supply_links),
                    'critical_contexts': supply_links[:5]  # Top 5
                })

                logger.info(f"Supply chain links found: {company} - {len(supply_links)} connections")

    def generate_network_analysis(self):
        """Generate network analysis of Italian-China connections"""
        logger.info("Generating network analysis...")

        # Create adjacency data for network analysis
        network_data = {
            'nodes': [],
            'edges': []
        }

        # Add Italian company nodes
        for company in self.results['companies_found']:
            network_data['nodes'].append({
                'id': company['name'],
                'type': 'italian_company',
                'group': company['group'],
                'ticker': company.get('ticker', '')
            })

        # Add China relationship edges
        for relationship in self.results['china_relationships']:
            for mention in relationship['china_mentions']:
                network_data['edges'].append({
                    'source': relationship['company'],
                    'target': mention,
                    'type': 'china_mention',
                    'filing_date': relationship['filing_date'],
                    'filing_type': relationship['filing_type']
                })

        return network_data

    def run_complete_analysis(self):
        """Run complete Italian company network analysis"""
        logger.info("Starting comprehensive Italian company network analysis...")

        # Step 1: Get all company data
        ticker_data = self.get_company_ticker_data()
        if not ticker_data:
            logger.error("Could not retrieve ticker data")
            return

        # Step 2: Find Italian companies
        italian_companies = self.find_italian_companies(ticker_data)
        logger.info(f"Found {len(italian_companies)} Italian companies")

        # Step 3: Analyze each company's filings
        for i, company in enumerate(italian_companies):
            logger.info(f"Processing {i+1}/{len(italian_companies)}: {company['name']}")
            self.analyze_company_filings(company)
            time.sleep(0.5)  # SEC rate limiting

        # Step 4: Analyze patterns
        self.analyze_supply_chain_links()

        # Step 5: Generate network analysis
        network_data = self.generate_network_analysis()

        # Step 6: Save results
        self.save_results(network_data)

        return self.results

    def save_results(self, network_data):
        """Save all analysis results"""
        # Save main results
        with open(self.output_dir / 'italian_company_networks.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        # Save network data
        with open(self.output_dir / 'network_data.json', 'w') as f:
            json.dump(network_data, f, indent=2)

        # Create summary CSV
        if self.results['china_relationships']:
            df = pd.DataFrame(self.results['china_relationships'])
            df.to_csv(self.output_dir / 'china_relationships.csv', index=False)

        # Generate markdown report
        self.write_markdown_report()

        logger.info(f"Results saved to {self.output_dir}")

    def write_markdown_report(self):
        """Write comprehensive markdown report"""
        report_path = self.output_dir / 'ITALIAN_COMPANY_NETWORKS_REPORT.md'

        with open(report_path, 'w') as f:
            f.write(f"""# Italian Company Networks in US Markets - China Connections
**Generated:** {datetime.now().isoformat()}
**Source:** SEC EDGAR Filings Analysis

## Executive Summary

Analysis of {len(self.results['companies_found'])} Italian companies in US markets reveals {len(self.results['china_relationships'])} instances of China-related business relationships documented in SEC filings.

## Key Findings

### Italian Companies Identified
""")

            # Group companies by category
            by_group = defaultdict(list)
            for company in self.results['companies_found']:
                by_group[company['group']].append(company)

            for group, companies in by_group.items():
                f.write(f"\n**{group.title()}:**\n")
                for company in companies:
                    f.write(f"- {company['name']} ({company.get('ticker', 'No ticker')})\n")

            f.write(f"""
### China Relationships by Company
""")

            # Group China relationships by company
            by_company = defaultdict(list)
            for rel in self.results['china_relationships']:
                by_company[rel['company']].append(rel)

            for company, relationships in by_company.items():
                f.write(f"\n**{company}:**\n")
                f.write(f"- {len(relationships)} China-related filings\n")

                # Show most recent mentions
                recent = sorted(relationships, key=lambda x: x['filing_date'], reverse=True)[:3]
                for rel in recent:
                    f.write(f"  - {rel['filing_date']}: {', '.join(rel['china_mentions'])} ({rel['filing_type']})\n")

            if self.results['supply_chain_links']:
                f.write(f"""
### Supply Chain Dependencies
""")
                for link in self.results['supply_chain_links']:
                    f.write(f"\n**{link['company']}:**\n")
                    f.write(f"- {link['china_supply_links']} supply chain connections identified\n")

            f.write(f"""
## Risk Assessment

### High-Risk Companies
Companies with multiple China connections in supply chain contexts:
""")

            # Identify high-risk companies
            high_risk = []
            for company in by_company.keys():
                china_count = len(by_company[company])
                supply_links = [s for s in self.results['supply_chain_links'] if s['company'] == company]

                if china_count >= 3 or supply_links:
                    high_risk.append((company, china_count, len(supply_links)))

            for company, china_count, supply_count in sorted(high_risk, key=lambda x: x[1], reverse=True):
                f.write(f"- **{company}:** {china_count} China mentions, {supply_count} supply chain links\n")

            f.write(f"""
## Network Analysis

### Connection Patterns
- Total Italian companies analyzed: {len(self.results['companies_found'])}
- Companies with China relationships: {len(by_company)}
- Average connections per company: {len(self.results['china_relationships'])/max(len(by_company), 1):.1f}

### Sector Distribution
""")

            sector_counts = defaultdict(int)
            for company in self.results['companies_found']:
                if company['name'] in by_company:
                    sector_counts[company['group']] += 1

            for sector, count in sorted(sector_counts.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- {sector}: {count} companies\n")

            f.write(f"""
## Implications for Italy's China Dependencies

This SEC EDGAR analysis reveals documented business relationships between major Italian companies and Chinese entities, providing concrete evidence of:

1. **Corporate-level China exposure** across multiple sectors
2. **Supply chain dependencies** in critical industries
3. **Financial flows** between Italian and Chinese entities
4. **Subsidiary networks** that may create hidden vulnerabilities

### Recommendations

1. **Enhanced Due Diligence:** Italian companies with multiple China connections need deeper analysis
2. **Supply Chain Mapping:** Companies showing supply chain keywords need Tier-2/3 mapping
3. **Financial Flow Analysis:** Track revenue dependencies and critical supplier relationships
4. **Regulatory Oversight:** Consider enhanced reporting requirements for China relationships

This analysis complements the TED procurement data by showing the private sector dimension of Italy-China economic integration.
""")

        logger.info(f"Report written to {report_path}")


def main():
    analyzer = SECItalianNetworkAnalyzer()

    print("Starting comprehensive Italian company network analysis...")
    print("This will analyze SEC EDGAR filings for China connections...")

    results = analyzer.run_complete_analysis()

    print(f"\n=== Analysis Complete ===")
    print(f"Italian companies found: {len(results['companies_found'])}")
    print(f"China relationships: {len(results['china_relationships'])}")
    print(f"Supply chain links: {len(results['supply_chain_links'])}")

    if results['china_relationships']:
        print(f"\nTop companies with China connections:")
        by_company = defaultdict(int)
        for rel in results['china_relationships']:
            by_company[rel['company']] += 1

        for company, count in sorted(by_company.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"- {company}: {count} connections")


if __name__ == "__main__":
    main()
