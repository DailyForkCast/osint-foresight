#!/usr/bin/env python3
"""
Analyze China patterns found in USASpending data
Extracts entities, contracts, and relationships from 1,644 matches
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import csv

class ChinaPatternAnalyzer:
    def __init__(self):
        self.china_patterns = {
            'countries': [r'\bchina\b', r'\bchinese\b', r'\bprc\b', r"people's republic"],
            'cities': [r'\bbeijing\b', r'\bshanghai\b', r'\bshenzhen\b', r'\bguangzhou\b',
                      r'\bhangzhou\b', r'\btianjin\b', r'\bchengdu\b', r'\bwuhan\b'],
            'companies': [r'\bhuawei\b', r'\bzte\b', r'\balibaba\b', r'\btencent\b',
                         r'\bbaidu\b', r'\bxiaomi\b', r'\blenovo\b', r'\bdji\b',
                         r'\bbytedance\b', r'\btiktok\b', r'\bhaier\b', r'\bhisense\b'],
            'universities': [r'\btsinghua\b', r'\bpeking university\b', r'\bfudan\b',
                           r'\bzhejiang university\b', r'\bbeihang\b'],
            'indicators': [r'\bsino-', r'\bcn\b', r'\b86\d{9,10}\b', r'\+86']
        }

        self.findings = {
            'total_matches': 0,
            'by_category': defaultdict(int),
            'entities': defaultdict(list),
            'contracts': [],
            'high_value': [],
            'timeline': defaultdict(int),
            'agencies': defaultdict(int),
            'suspicious': []
        }

    def load_and_analyze(self):
        """Load the China matches and perform deep analysis"""
        print("\n" + "="*70)
        print("CHINA PATTERN ANALYSIS - USASpending Data")
        print("="*70)

        # Load the expanded sample file with China examples
        sample_file = Path("C:/Projects/OSINT - Foresight/json_expanded_sample.json")

        if sample_file.exists():
            print("\nLoading China matches from expanded sample...")
            with open(sample_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Process the china_examples array
            if 'china_examples' in data:
                print(f"Found {len(data['china_examples'])} China match examples")
                self.process_china_examples(data['china_examples'])
            else:
                print("No china_examples found in file")
        else:
            print("Sample file not found!")

        self.analyze_patterns()
        self.extract_entities()
        self.identify_high_risk()
        self.generate_timeline()

    def process_china_examples(self, examples):
        """Process the China match examples from the JSON"""
        print(f"\nProcessing {len(examples)} China-related contracts...")

        for i, example in enumerate(examples):
            if i % 100 == 0 and i > 0:
                print(f"  Processed {i} contracts...")

            # Parse the tab-separated content
            try:
                fields = example['content'].split('\t')

                # Extract key fields based on USASpending format
                # The format appears to be tab-separated with specific columns
                contract = {
                    'line_num': example['line_num'],
                    'contract_id': fields[5] if len(fields) > 5 else '',
                    'amount': self.parse_amount(fields[11] if len(fields) > 11 else '0'),
                    'description': fields[13] if len(fields) > 13 else '',
                    'vendor': fields[20] if len(fields) > 20 else 'Unknown',
                    'date': fields[27] if len(fields) > 27 else '',
                    'year': fields[28] if len(fields) > 28 else '',
                    'agency': fields[36] if len(fields) > 36 else '',
                    'location': '',  # Add location field
                    'category': self.categorize_china_mention(example['content'])
                }

                # Update findings
                self.findings['total_matches'] += 1
                self.findings['by_category'][contract['category']] += 1
                self.findings['contracts'].append(contract)

                # Track high-value contracts
                if contract['amount'] > 1000000:
                    self.findings['high_value'].append(contract)

                # Track by agency
                if contract['agency'] and contract['agency'] not in ['\\N', '']:
                    self.findings['agencies'][contract['agency']] += 1

                # Track timeline
                if contract['year'] and contract['year'] not in ['\\N', '']:
                    self.findings['timeline'][contract['year']] += 1

                # Check for risk flags
                self.check_risk_flags(contract)

            except Exception as e:
                print(f"Error processing example {i}: {str(e)[:50]}")
                continue

        print(f"\nSuccessfully processed {len(self.findings['contracts'])} contracts")

    def parse_amount(self, amount_str):
        """Parse amount string to float"""
        try:
            # Remove any non-numeric characters except decimal point
            clean = amount_str.replace(',', '').replace('$', '').strip()
            return float(clean) if clean and clean != '\\N' else 0.0
        except:
            return 0.0

    def categorize_china_mention(self, content):
        """Categorize the type of China mention"""
        content_lower = content.lower()

        # Check for specific patterns
        if 'made in china' in content_lower:
            return 'manufactured'
        elif 'chinese' in content_lower:
            return 'chinese_entity'
        elif any(company in content_lower for company in ['huawei', 'zte', 'lenovo', 'alibaba']):
            return 'chinese_company'
        elif any(city in content_lower for city in ['beijing', 'shanghai', 'shenzhen']):
            return 'chinese_city'
        elif 'china' in content_lower:
            return 'china_general'
        else:
            return 'other'

    def check_risk_flags(self, contract):
        """Check contract for risk indicators"""
        risk_flags = []

        # High value
        if contract['amount'] > 10000000:
            risk_flags.append('HIGH_VALUE_>10M')
        elif contract['amount'] > 1000000:
            risk_flags.append('HIGH_VALUE_>1M')

        # Check description for sensitive items
        desc_lower = contract['description'].lower() if contract['description'] else ''

        if any(term in desc_lower for term in ['technology', 'software', 'computer', 'network']):
            risk_flags.append('TECHNOLOGY')
        if any(term in desc_lower for term in ['defense', 'military', 'weapon']):
            risk_flags.append('DEFENSE')
        if any(term in desc_lower for term in ['communication', 'telecom', '5g']):
            risk_flags.append('COMMUNICATIONS')
        if 'made in china' in desc_lower:
            risk_flags.append('CHINESE_MANUFACTURED')

        # Check agency
        agency_lower = contract['agency'].lower() if contract['agency'] else ''
        if any(term in agency_lower for term in ['defense', 'dod', 'army', 'navy', 'air force']):
            risk_flags.append('DEFENSE_AGENCY')
        if any(term in agency_lower for term in ['energy', 'doe', 'nuclear']):
            risk_flags.append('ENERGY_AGENCY')

        if risk_flags:
            contract['risk_flags'] = risk_flags
            self.findings['suspicious'].append(contract)

    def extract_from_sample(self, sample_file):
        """Legacy method - kept for compatibility"""
        pass

    def extract_contract_details(self, data, category, pattern):
        """Extract contract details from JSON data"""
        contract = {
            'category': category,
            'pattern': pattern,
            'vendor': data.get('recipient_name', data.get('vendor_name', 'Unknown')),
            'amount': data.get('total_obligation', data.get('award_amount', 0)),
            'date': data.get('action_date', data.get('award_date', '')),
            'agency': data.get('funding_agency', data.get('awarding_agency', '')),
            'description': data.get('award_description', data.get('product_or_service', '')),
            'location': data.get('vendor_country', data.get('recipient_country', '')),
            'naics': data.get('naics_code', ''),
            'contract_id': data.get('contract_award_unique_key', data.get('award_id', ''))
        }

        # Convert amount to float if string
        try:
            contract['amount'] = float(contract['amount'])
        except:
            contract['amount'] = 0

        self.findings['contracts'].append(contract)

        # Track high-value contracts (>$1M)
        if contract['amount'] > 1000000:
            self.findings['high_value'].append(contract)

        # Track by agency
        if contract['agency']:
            self.findings['agencies'][contract['agency']] += 1

        # Extract date for timeline
        if contract['date']:
            try:
                year = contract['date'][:4]
                self.findings['timeline'][year] += 1
            except:
                pass

    def analyze_patterns(self):
        """Analyze the distribution of patterns"""
        print("\n[PATTERN DISTRIBUTION]")
        print("-" * 40)

        total = self.findings['total_matches']
        print(f"Total China-related matches: {total:,}")

        print("\nBy Category:")
        for category, count in self.findings['by_category'].items():
            percentage = (count / total * 100) if total > 0 else 0
            print(f"  {category:15} {count:6,} ({percentage:.1f}%)")

    def extract_entities(self):
        """Extract unique entities from contracts"""
        print("\n[ENTITY EXTRACTION]")
        print("-" * 40)

        vendors = set()
        agencies = set()
        locations = set()

        for contract in self.findings['contracts']:
            if contract['vendor'] and contract['vendor'] != 'Unknown':
                vendors.add(contract['vendor'])
            if contract['agency']:
                agencies.add(contract['agency'])
            if contract.get('location') and contract['location']:
                locations.add(contract['location'])

        print(f"Unique vendors: {len(vendors)}")
        print(f"Unique agencies: {len(agencies)}")
        print(f"Unique locations: {len(locations)}")

        # Show top vendors by contract count
        vendor_counts = Counter(c['vendor'] for c in self.findings['contracts']
                               if c['vendor'] != 'Unknown')

        if vendor_counts:
            print("\nTop 10 China-Related Vendors:")
            for vendor, count in vendor_counts.most_common(10):
                print(f"  {vendor[:50]:50} {count:4} contracts")

    def identify_high_risk(self):
        """Identify high-risk or suspicious patterns"""
        print("\n[HIGH-RISK INDICATORS]")
        print("-" * 40)

        # Identify suspicious patterns
        for contract in self.findings['contracts']:
            risk_flags = []

            # High value
            if contract['amount'] > 10000000:
                risk_flags.append('HIGH_VALUE')

            # Defense/security agencies
            agency_lower = contract['agency'].lower() if contract['agency'] else ''
            if any(term in agency_lower for term in ['defense', 'dod', 'navy', 'army', 'air force']):
                risk_flags.append('DEFENSE_RELATED')

            # Technology sectors
            desc_lower = contract['description'].lower() if contract['description'] else ''
            if any(term in desc_lower for term in ['software', 'technology', 'communications',
                                                   'telecom', 'network', 'cyber']):
                risk_flags.append('TECHNOLOGY')

            # Known Chinese companies
            vendor_lower = contract['vendor'].lower() if contract['vendor'] else ''
            if any(company in vendor_lower for company in ['huawei', 'zte', 'lenovo', 'dji']):
                risk_flags.append('KNOWN_CHINESE_COMPANY')

            if risk_flags:
                contract['risk_flags'] = risk_flags
                self.findings['suspicious'].append(contract)

        print(f"High-value contracts (>$1M): {len(self.findings['high_value'])}")
        print(f"Suspicious contracts flagged: {len(self.findings['suspicious'])}")

        # Calculate total value
        total_value = sum(c['amount'] for c in self.findings['contracts'])
        high_value_total = sum(c['amount'] for c in self.findings['high_value'])

        print(f"\nTotal contract value: ${total_value:,.2f}")
        print(f"High-value total: ${high_value_total:,.2f}")

    def generate_timeline(self):
        """Generate timeline analysis"""
        print("\n[TIMELINE ANALYSIS]")
        print("-" * 40)

        if self.findings['timeline']:
            sorted_years = sorted(self.findings['timeline'].items())

            print("China-related contracts by year:")
            for year, count in sorted_years[-10:]:  # Last 10 years
                bar = '█' * min(count // 10, 50)
                print(f"  {year}: {count:4} {bar}")

    def save_results(self):
        """Save analysis results"""
        # Save detailed findings
        output_file = Path("C:/Projects/OSINT - Foresight/china_analysis_results.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.findings, f, indent=2, default=str)

        # Create executive summary
        summary = self.create_executive_summary()
        summary_file = Path("C:/Projects/OSINT - Foresight/CHINA_ANALYSIS_SUMMARY.md")
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)

        # Export high-risk contracts to CSV
        if self.findings['suspicious']:
            csv_file = Path("C:/Projects/OSINT - Foresight/china_high_risk_contracts.csv")
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                if self.findings['suspicious']:
                    fieldnames = ['vendor', 'amount', 'date', 'agency', 'description',
                                 'risk_flags', 'contract_id']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for contract in self.findings['suspicious']:
                        row = {k: contract.get(k, '') for k in fieldnames}
                        row['risk_flags'] = ', '.join(contract.get('risk_flags', []))
                        writer.writerow(row)

        print(f"\n[Results saved to {output_file}]")
        print(f"[Summary saved to {summary_file}]")

    def create_executive_summary(self):
        """Create executive summary of findings"""
        summary = "# China Pattern Analysis - USASpending Data\n\n"
        summary += f"Generated: {datetime.now().isoformat()}\n\n"

        summary += "## Executive Summary\n\n"
        summary += f"- **Total China-related patterns found**: {self.findings['total_matches']:,}\n"
        summary += f"- **Contracts identified**: {len(self.findings['contracts']):,}\n"
        summary += f"- **High-value contracts (>$1M)**: {len(self.findings['high_value']):,}\n"
        summary += f"- **Suspicious contracts flagged**: {len(self.findings['suspicious']):,}\n\n"

        # Calculate totals
        total_value = sum(c['amount'] for c in self.findings['contracts'])
        high_value_total = sum(c['amount'] for c in self.findings['high_value'])

        summary += "## Financial Impact\n\n"
        summary += f"- **Total contract value**: ${total_value:,.2f}\n"
        summary += f"- **High-value contracts total**: ${high_value_total:,.2f}\n"
        if total_value > 0:
            summary += f"- **High-value percentage**: {high_value_total/total_value*100:.1f}%\n\n"

        summary += "## Pattern Distribution\n\n"
        for category, count in sorted(self.findings['by_category'].items(),
                                     key=lambda x: x[1], reverse=True):
            summary += f"- {category.capitalize()}: {count:,}\n"

        summary += "\n## Top Agencies Involved\n\n"
        for agency, count in Counter(self.findings['agencies']).most_common(10):
            summary += f"- {agency}: {count} contracts\n"

        summary += "\n## Risk Indicators\n\n"

        # Count risk flags
        risk_flag_counts = defaultdict(int)
        for contract in self.findings['suspicious']:
            for flag in contract.get('risk_flags', []):
                risk_flag_counts[flag] += 1

        for flag, count in sorted(risk_flag_counts.items(), key=lambda x: x[1], reverse=True):
            summary += f"- {flag}: {count} contracts\n"

        summary += "\n## Recommendations\n\n"
        summary += "1. **Immediate Review**: All contracts flagged as DEFENSE_RELATED + KNOWN_CHINESE_COMPANY\n"
        summary += "2. **Supply Chain Audit**: Verify vendors in TECHNOLOGY category\n"
        summary += "3. **Timeline Analysis**: Investigate surge patterns in recent years\n"
        summary += "4. **Agency Briefing**: Alert agencies with highest China exposure\n"
        summary += "5. **Deep Dive**: Extract full contract details for HIGH_VALUE flags\n"

        return summary

    def run(self):
        """Execute the analysis"""
        self.load_and_analyze()
        self.save_results()

        print("\n" + "="*70)
        print("ANALYSIS COMPLETE")
        print("="*70)
        print(f"\nProcessed {self.findings['total_matches']:,} China patterns")
        print(f"Identified {len(self.findings['contracts']):,} contracts")
        print(f"Flagged {len(self.findings['suspicious']):,} suspicious contracts")

        if self.findings['suspicious']:
            print("\n[CRITICAL] High-risk contracts exported to china_high_risk_contracts.csv")
            print("[ACTION REQUIRED] Review flagged contracts immediately")

            # Show top 5 suspicious contracts
            print("\nTop 5 Suspicious Contracts:")
            for i, contract in enumerate(self.findings['suspicious'][:5], 1):
                print(f"\n  {i}. Contract {contract.get('contract_id', 'N/A')}")
                print(f"     Amount: ${contract.get('amount', 0):,.2f}")
                print(f"     Flags: {', '.join(contract.get('risk_flags', []))}")
                print(f"     Description: {contract.get('description', '')[:80]}...")


if __name__ == "__main__":
    analyzer = ChinaPatternAnalyzer()
    analyzer.run()
