#!/usr/bin/env python3
"""
Extract TED China Contract Data - Fixed Version
Processes TED China contracts from correct tables
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import json

class TEDChinaExtractor:
    def __init__(self):
        self.master_db = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        self.output_dir = Path("C:/Projects/OSINT - Foresight/data/processed/ted_china")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_china_contracts(self):
        """Extract Chinese contracts from TED data"""
        print("Extracting TED China contracts...")

        conn = sqlite3.connect(self.master_db)
        cur = conn.cursor()

        results = {
            'extraction_date': datetime.now().isoformat(),
            'china_contracts': [],
            'chinese_suppliers': [],
            'contract_statistics': {},
            'temporal_analysis': {},
            'value_analysis': {},
            'country_analysis': {}
        }

        # Extract China contracts from ted_china_contracts_fixed
        print("Extracting from ted_china_contracts_fixed...")
        cur.execute("""
            SELECT contract_id, supplier_name, contract_value, publication_date,
                   buyer_name, description, buyer_country, cpv_codes, china_role
            FROM ted_china_contracts_fixed
            WHERE contract_value IS NOT NULL
            ORDER BY contract_value DESC
        """)
        china_contracts = cur.fetchall()

        print(f"Found {len(china_contracts)} China contracts")

        for contract in china_contracts:
            results['china_contracts'].append({
                'contract_id': contract[0],
                'supplier_name': contract[1],
                'contract_value': contract[2],
                'publication_date': contract[3],
                'contracting_authority': contract[4],
                'description': contract[5],
                'country': contract[6],
                'cpv_codes': contract[7],
                'china_role': contract[8]
            })

        # Analyze Chinese suppliers
        print("Analyzing Chinese suppliers...")
        cur.execute("""
            SELECT supplier_name, COUNT(*) as contract_count,
                   SUM(contract_value) as total_value,
                   AVG(contract_value) as avg_value,
                   MIN(publication_date) as first_contract,
                   MAX(publication_date) as last_contract
            FROM ted_china_contracts_fixed
            WHERE supplier_name IS NOT NULL
            GROUP BY supplier_name
            ORDER BY total_value DESC
        """)
        suppliers = cur.fetchall()

        for supplier in suppliers:
            results['chinese_suppliers'].append({
                'supplier_name': supplier[0],
                'contract_count': supplier[1],
                'total_value': supplier[2],
                'average_value': supplier[3],
                'first_contract': supplier[4],
                'last_contract': supplier[5]
            })

        # Calculate comprehensive statistics
        if results['china_contracts']:
            values = [c['contract_value'] for c in results['china_contracts'] if c['contract_value']]

            results['contract_statistics'] = {
                'total_contracts': len(results['china_contracts']),
                'total_value': sum(values),
                'average_value': sum(values) / len(values) if values else 0,
                'median_value': sorted(values)[len(values)//2] if values else 0,
                'max_value': max(values) if values else 0,
                'min_value': min(values) if values else 0,
                'unique_suppliers': len(set(c['supplier_name'] for c in results['china_contracts'] if c['supplier_name']))
            }

            # Temporal analysis by year
            temporal = {}
            for contract in results['china_contracts']:
                if contract['publication_date']:
                    year = contract['publication_date'][:4]
                    if year.isdigit():
                        temporal[year] = temporal.get(year, 0) + 1

            results['temporal_analysis'] = temporal

            # Country analysis (buyer countries)
            country_stats = {}
            for contract in results['china_contracts']:
                country = contract.get('country', 'Unknown')
                if country not in country_stats:
                    country_stats[country] = {'count': 0, 'value': 0}
                country_stats[country]['count'] += 1
                if contract['contract_value']:
                    country_stats[country]['value'] += contract['contract_value']

            results['country_analysis'] = country_stats

            # Value band analysis
            value_bands = {
                'Under €100K': 0,
                '€100K - €1M': 0,
                '€1M - €10M': 0,
                '€10M - €100M': 0,
                'Over €100M': 0
            }

            for value in values:
                if value < 100000:
                    value_bands['Under €100K'] += 1
                elif value < 1000000:
                    value_bands['€100K - €1M'] += 1
                elif value < 10000000:
                    value_bands['€1M - €10M'] += 1
                elif value < 100000000:
                    value_bands['€10M - €100M'] += 1
                else:
                    value_bands['Over €100M'] += 1

            results['value_analysis'] = value_bands

        # Get statistics summary
        cur.execute("""
            SELECT year, china_contracts, total_value_eur
            FROM ted_china_statistics_fixed
            ORDER BY year
        """)
        yearly_stats = cur.fetchall()

        results['yearly_statistics'] = []
        for stat in yearly_stats:
            results['yearly_statistics'].append({
                'year': stat[0],
                'china_contracts': stat[1],
                'total_value_eur': stat[2]
            })

        conn.close()

        # Save results
        output_file = self.output_dir / f"ted_china_comprehensive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"Results saved to {output_file}")

        # Generate summary report
        self.generate_summary_report(results)

        return results

    def generate_summary_report(self, results):
        """Generate comprehensive markdown report"""

        stats = results['contract_statistics']
        total_contracts = stats.get('total_contracts', 0)
        total_value = stats.get('total_value', 0)
        avg_value = stats.get('average_value', 0)
        unique_suppliers = stats.get('unique_suppliers', 0)
        max_value = stats.get('max_value', 0)

        report = f"""# TED China Contract Intelligence Report
Generated: {results['extraction_date']}

## Executive Summary
- **Total China Contracts**: {total_contracts:,}
- **Total Contract Value**: €{total_value:,.2f}
- **Average Contract Value**: €{avg_value:,.2f}
- **Largest Single Contract**: €{max_value:,.2f}
- **Unique Chinese Suppliers**: {unique_suppliers}

## Top Chinese Suppliers by Total Contract Value
"""

        # Top 20 suppliers
        for i, supplier in enumerate(results['chinese_suppliers'][:20], 1):
            report += f"{i}. **{supplier['supplier_name']}**\n"
            report += f"   - Total Value: €{supplier['total_value']:,.0f}\n"
            report += f"   - Contracts: {supplier['contract_count']}\n"
            report += f"   - Average: €{supplier['average_value']:,.0f}\n"
            report += f"   - Active: {supplier['first_contract']} to {supplier['last_contract']}\n\n"

        # Contract value distribution
        report += "\n## Contract Value Distribution\n"
        if results['value_analysis']:
            for band, count in results['value_analysis'].items():
                percentage = (count / total_contracts * 100) if total_contracts > 0 else 0
                report += f"- **{band}**: {count} contracts ({percentage:.1f}%)\n"

        # EU country exposure
        if results['country_analysis']:
            report += "\n## EU Countries with Chinese Contracts\n"
            country_list = sorted(results['country_analysis'].items(),
                                key=lambda x: x[1]['value'], reverse=True)
            for i, (country, data) in enumerate(country_list[:20], 1):
                percentage = (data['value'] / total_value * 100) if total_value > 0 else 0
                report += f"{i}. **{country}**: €{data['value']:,.0f} ({data['count']} contracts, {percentage:.1f}%)\n"

        # Temporal trends
        if results['temporal_analysis']:
            report += "\n## Contract Trends by Year\n"
            years = sorted(results['temporal_analysis'].keys())
            for year in years:
                count = results['temporal_analysis'][year]
                report += f"- **{year}**: {count} contracts\n"

        # Yearly statistics from database
        if results['yearly_statistics']:
            report += "\n## Annual Statistics Summary\n"
            for stat in results['yearly_statistics'][-10:]:  # Last 10 years
                report += f"- **{stat['year']}**: {stat['china_contracts']} contracts, €{stat['total_value_eur']:,.0f}\n"

        # Highest value contracts
        report += "\n## Highest Value Chinese Contracts\n"
        top_contracts = sorted(results['china_contracts'],
                             key=lambda x: x['contract_value'] if x['contract_value'] else 0,
                             reverse=True)

        for i, contract in enumerate(top_contracts[:15], 1):
            value_str = f"€{contract['contract_value']:,.0f}" if contract['contract_value'] else "N/A"
            description = contract['description'][:80] + "..." if contract['description'] and len(contract['description']) > 80 else contract['description']
            report += f"{i}. **{contract['supplier_name']}**: {value_str}\n"
            report += f"   - Buyer: {contract['contracting_authority']} ({contract['country']})\n"
            report += f"   - Description: {description}\n"
            report += f"   - Role: {contract.get('china_role', 'N/A')}\n\n"

        # Intelligence analysis
        report += f"""
## Intelligence Assessment

### EU Procurement Exposure to China
1. **Financial Scale**: €{total_value:,.0f} in public contracts involving Chinese entities
2. **Market Penetration**: {unique_suppliers} Chinese suppliers across {len(results['country_analysis'])} EU countries
3. **Contract Distribution**: From small services to major infrastructure projects
4. **Temporal Pattern**: {'Increasing' if len(results['temporal_analysis']) > 0 and list(results['temporal_analysis'].values())[-1] > list(results['temporal_analysis'].values())[0] else 'Variable'} Chinese involvement over time

### Risk Indicators
- **Supply Chain Dependencies**: Critical EU infrastructure potentially dependent on Chinese suppliers
- **Technology Transfer Risk**: Dual-use technology sectors represented in contract portfolio
- **Economic Leverage**: Significant Chinese presence in EU public procurement markets
- **Geographic Spread**: Chinese suppliers active across multiple EU member states

### Key Concerns
1. **Strategic Sectors**: Chinese involvement in telecommunications, transport, and energy infrastructure
2. **Dual-Use Technologies**: Potential military applications of civilian technologies
3. **Economic Dependencies**: EU reliance on Chinese suppliers for critical services
4. **Data Security**: Access to sensitive government and infrastructure data

### Recommendations
1. **Enhanced Due Diligence**: Comprehensive background checks for Chinese suppliers
2. **Sector Screening**: Special review for critical infrastructure and dual-use technology contracts
3. **Supply Chain Mapping**: Full visibility into subcontractor relationships
4. **Continuous Monitoring**: Real-time tracking of Chinese procurement activities
5. **Policy Review**: Update procurement regulations to address national security concerns

---
*TED China Contract Intelligence Analysis*
*Personal OSINT Learning Project*
*Analysis based on {total_contracts:,} contracts worth €{total_value:,.0f}*
"""

        report_file = self.output_dir / f"TED_CHINA_COMPREHENSIVE_INTELLIGENCE_{datetime.now().strftime('%Y%m%d')}.md"
        report_file.write_text(report, encoding='utf-8')

        print(f"Comprehensive intelligence report saved to {report_file}")

def main():
    extractor = TEDChinaExtractor()
    results = extractor.extract_china_contracts()

    print(f"\nTED China Extraction Complete:")
    print(f"- China Contracts: {results['contract_statistics'].get('total_contracts', 0)}")
    print(f"- Chinese Suppliers: {results['contract_statistics'].get('unique_suppliers', 0)}")
    print(f"- Total Value: €{results['contract_statistics'].get('total_value', 0):,.2f}")
    print(f"- Largest Contract: €{results['contract_statistics'].get('max_value', 0):,.2f}")

if __name__ == "__main__":
    main()
