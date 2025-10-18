#!/usr/bin/env python3
"""
China Analysis on USASpending Data
Analyzes 9.4M financial records for China-related patterns
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import sys

class ChinaUSASpendingAnalyzer:
    def __init__(self):
        self.results_root = Path("C:/Projects/OSINT - Foresight")
        self.china_analysis = {
            'generated': datetime.now().isoformat(),
            'total_records_analyzed': 0,
            'china_related_findings': [],
            'patterns_detected': {},
            'temporal_analysis': {},
            'entity_analysis': {},
            'risk_indicators': []
        }

    def load_usaspending_data(self):
        """Load USASpending insights"""
        print("\nLoading USASpending data...")

        usa_file = self.results_root / "usaspending_insights.json"
        if usa_file.exists():
            with open(usa_file, 'r') as f:
                self.usaspending_data = json.load(f)
            print(f"  Loaded: {self.usaspending_data.get('total_rows', 0):,} rows")
            self.china_analysis['total_records_analyzed'] = self.usaspending_data.get('total_rows', 0)

            # Also load the parsed data summary
            postgres_file = self.results_root / "postgres_dat_parse_summary.json"
            if postgres_file.exists():
                with open(postgres_file, 'r') as f:
                    self.postgres_data = json.load(f)
                print(f"  Tables: {len(self.postgres_data.get('table_schemas', {}))}")

    def analyze_china_patterns(self):
        """Search for China-related patterns in the data"""
        print("\nSearching for China patterns...")

        china_keywords = [
            'china', 'chinese', 'beijing', 'shanghai', 'shenzhen',
            'huawei', 'zte', 'alibaba', 'tencent', 'baidu',
            'prc', 'ccp', 'sino-'
        ]

        # Check data patterns from insights
        if 'data_patterns' in self.usaspending_data:
            patterns = self.usaspending_data['data_patterns']

            # Check possible organizations
            if 'possible_orgs' in patterns:
                for org in patterns['possible_orgs']:
                    org_lower = org.lower() if org else ''
                    for keyword in china_keywords:
                        if keyword in org_lower:
                            self.china_analysis['china_related_findings'].append({
                                'type': 'organization',
                                'value': org,
                                'keyword_matched': keyword,
                                'source': 'usaspending'
                            })

            # Analyze dates for temporal patterns
            if 'dates' in patterns:
                date_years = defaultdict(int)
                for date in patterns['dates']:
                    if date and '-' in date:
                        year = date.split('-')[0]
                        date_years[year] += 1

                self.china_analysis['temporal_analysis'] = dict(date_years)
                print(f"  Temporal range: {min(date_years.keys())} - {max(date_years.keys())}")

            # Check financial values
            if 'financial_values' in patterns:
                self.china_analysis['patterns_detected']['financial_records'] = len(patterns['financial_values'])
                print(f"  Financial records found: {len(patterns['financial_values'])}")

    def analyze_table_structures(self):
        """Analyze database table structures for relevant data"""
        print("\nAnalyzing table structures...")

        if not hasattr(self, 'postgres_data'):
            return

        relevant_tables = []
        vendor_tables = []
        contract_tables = []
        award_tables = []

        for table_name, schema in self.postgres_data.get('table_schemas', {}).items():
            table_lower = table_name.lower()

            # Identify relevant tables
            if any(term in table_lower for term in ['vendor', 'recipient', 'contractor']):
                vendor_tables.append(table_name)
            elif any(term in table_lower for term in ['contract', 'procurement']):
                contract_tables.append(table_name)
            elif any(term in table_lower for term in ['award', 'grant', 'assistance']):
                award_tables.append(table_name)

            # Check for specific columns that might contain China data
            for col in schema.get('columns', []):
                col_name = col['name'].lower()
                if any(term in col_name for term in ['country', 'nation', 'foreign', 'international']):
                    relevant_tables.append({
                        'table': table_name,
                        'column': col['name'],
                        'type': col['type'],
                        'relevance': 'geographic'
                    })

        self.china_analysis['entity_analysis'] = {
            'vendor_tables': vendor_tables,
            'contract_tables': contract_tables,
            'award_tables': award_tables,
            'geographic_columns': relevant_tables
        }

        print(f"  Found {len(vendor_tables)} vendor tables")
        print(f"  Found {len(contract_tables)} contract tables")
        print(f"  Found {len(award_tables)} award tables")

    def identify_risk_indicators(self):
        """Identify potential risk indicators"""
        print("\nIdentifying risk indicators...")

        # Based on the data we have
        risks = []

        # Check for foreign entities
        if self.china_analysis['china_related_findings']:
            risks.append({
                'type': 'foreign_entity_presence',
                'severity': 'medium',
                'description': f"Found {len(self.china_analysis['china_related_findings'])} potential China-related entities",
                'recommendation': 'Deep dive into specific vendors and contracts'
            })

        # Check temporal patterns
        if self.china_analysis['temporal_analysis']:
            recent_years = [y for y in self.china_analysis['temporal_analysis'].keys() if int(y) >= 2020]
            if recent_years:
                risks.append({
                    'type': 'recent_activity',
                    'severity': 'low',
                    'description': f"Activity detected in recent years: {', '.join(recent_years)}",
                    'recommendation': 'Analyze trend over time'
                })

        # Check data volume
        if self.china_analysis['total_records_analyzed'] > 1000000:
            risks.append({
                'type': 'large_dataset',
                'severity': 'info',
                'description': f"Dataset contains {self.china_analysis['total_records_analyzed']:,} records",
                'recommendation': 'Consider sampling or distributed processing for detailed analysis'
            })

        self.china_analysis['risk_indicators'] = risks
        print(f"  Identified {len(risks)} risk indicators")

    def generate_recommendations(self):
        """Generate specific recommendations for further analysis"""
        recommendations = []

        # Based on what we found
        if self.china_analysis['entity_analysis'].get('vendor_tables'):
            recommendations.append({
                'priority': 'high',
                'action': 'Extract and analyze vendor tables',
                'reason': 'Vendor data can reveal foreign entity participation',
                'tables': self.china_analysis['entity_analysis']['vendor_tables'][:5]
            })

        if self.china_analysis['entity_analysis'].get('contract_tables'):
            recommendations.append({
                'priority': 'high',
                'action': 'Analyze contract data for China-related terms',
                'reason': 'Contracts may reference Chinese entities or technology',
                'tables': self.china_analysis['entity_analysis']['contract_tables'][:5]
            })

        if self.china_analysis['china_related_findings']:
            recommendations.append({
                'priority': 'critical',
                'action': 'Deep dive on identified China-related entities',
                'reason': f"Found {len(self.china_analysis['china_related_findings'])} potential matches",
                'entities': [f['value'] for f in self.china_analysis['china_related_findings'][:10]]
            })

        recommendations.append({
            'priority': 'medium',
            'action': 'Set up PostgreSQL and restore full database',
            'reason': 'Enable SQL queries for comprehensive analysis',
            'benefit': 'Access to all 9.4M records with full query capability'
        })

        recommendations.append({
            'priority': 'low',
            'action': 'Process large compressed files',
            'reason': 'May contain additional procurement or financial data',
            'size': '229 GB compressed'
        })

        self.china_analysis['recommendations'] = recommendations
        return recommendations

    def save_results(self):
        """Save analysis results"""
        print("\nSaving results...")

        # Add recommendations
        self.generate_recommendations()

        # Save main analysis
        with open(self.results_root / "china_usaspending_analysis.json", 'w') as f:
            json.dump(self.china_analysis, f, indent=2)

        # Generate report
        self.generate_report()

        print("Results saved")

    def generate_report(self):
        """Generate analysis report"""
        report = "# China Analysis: USASpending Data\n\n"
        report += f"Generated: {datetime.now().isoformat()}\n\n"

        report += "## Executive Summary\n\n"
        report += f"- **Records Analyzed**: {self.china_analysis['total_records_analyzed']:,}\n"
        report += f"- **China-Related Findings**: {len(self.china_analysis['china_related_findings'])}\n"
        report += f"- **Risk Indicators**: {len(self.china_analysis['risk_indicators'])}\n\n"

        if self.china_analysis['temporal_analysis']:
            report += "## Temporal Analysis\n\n"
            report += "| Year | Records |\n"
            report += "|------|--------|\n"
            for year in sorted(self.china_analysis['temporal_analysis'].keys()):
                report += f"| {year} | {self.china_analysis['temporal_analysis'][year]} |\n"
            report += "\n"

        report += "## Database Structure Analysis\n\n"
        entity = self.china_analysis['entity_analysis']
        report += f"- **Vendor Tables**: {len(entity.get('vendor_tables', []))}\n"
        report += f"- **Contract Tables**: {len(entity.get('contract_tables', []))}\n"
        report += f"- **Award Tables**: {len(entity.get('award_tables', []))}\n"
        report += f"- **Geographic Columns**: {len(entity.get('geographic_columns', []))}\n\n"

        if self.china_analysis['china_related_findings']:
            report += "## China-Related Entities Found\n\n"
            for finding in self.china_analysis['china_related_findings'][:10]:
                report += f"- {finding['value'][:100]} (matched: {finding['keyword_matched']})\n"
            report += "\n"

        if self.china_analysis['risk_indicators']:
            report += "## Risk Indicators\n\n"
            for risk in self.china_analysis['risk_indicators']:
                report += f"### {risk['type'].replace('_', ' ').title()}\n"
                report += f"- **Severity**: {risk['severity'].upper()}\n"
                report += f"- **Description**: {risk['description']}\n"
                report += f"- **Recommendation**: {risk['recommendation']}\n\n"

        report += "## Recommendations\n\n"
        for rec in self.china_analysis.get('recommendations', []):
            report += f"### Priority: {rec['priority'].upper()}\n"
            report += f"**Action**: {rec['action']}\n\n"
            report += f"**Reason**: {rec['reason']}\n\n"
            if 'tables' in rec:
                report += "**Tables to analyze**:\n"
                for table in rec['tables']:
                    report += f"- {table}\n"
                report += "\n"
            if 'entities' in rec:
                report += "**Entities to investigate**:\n"
                for entity in rec['entities']:
                    report += f"- {entity[:100]}\n"
                report += "\n"

        report += "## Next Steps\n\n"
        report += "1. **Immediate**: Review identified China-related entities\n"
        report += "2. **Short-term**: Set up PostgreSQL for full database access\n"
        report += "3. **Medium-term**: Implement automated scanning for China patterns\n"
        report += "4. **Long-term**: Build comprehensive foreign entity tracking system\n"

        with open(self.results_root / "china_usaspending_analysis_report.md", 'w', encoding='utf-8') as f:
            f.write(report)

        print("Report saved: china_usaspending_analysis_report.md")

    def run(self):
        """Execute China analysis on USASpending data"""
        print("\n" + "="*70)
        print("CHINA ANALYSIS: USASPENDING DATA")
        print("="*70)

        # Load data
        self.load_usaspending_data()

        # Analyze for China patterns
        self.analyze_china_patterns()

        # Analyze table structures
        self.analyze_table_structures()

        # Identify risks
        self.identify_risk_indicators()

        # Save results
        self.save_results()

        print("\n" + "="*70)
        print("ANALYSIS COMPLETE")
        print("="*70)
        print(f"\nFindings: {len(self.china_analysis['china_related_findings'])} China-related patterns")
        print(f"Risks: {len(self.china_analysis['risk_indicators'])} indicators identified")

        return 0


if __name__ == "__main__":
    analyzer = ChinaUSASpendingAnalyzer()
    sys.exit(analyzer.run())
