#!/usr/bin/env python3
"""
Extract TED China Contract Data
Processes existing TED procurement data for Chinese suppliers
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

    def check_ted_schema(self):
        """Check TED table schema"""
        conn = sqlite3.connect(self.master_db)
        cur = conn.cursor()

        # Find TED tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%ted%'")
        ted_tables = cur.fetchall()

        print("TED Tables found:")
        for table in ted_tables:
            print(f"- {table[0]}")
            # Show schema
            cur.execute(f"PRAGMA table_info({table[0]})")
            columns = cur.fetchall()
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            print()

        conn.close()

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

        # Check for ted_china_contracts table first
        try:
            cur.execute("SELECT COUNT(*) FROM ted_china_contracts")
            china_contract_count = cur.fetchone()[0]
            print(f"Found {china_contract_count} China contracts in ted_china_contracts table")

            # Extract China contracts
            cur.execute("""
                SELECT contract_id, supplier_name, contract_value, award_date,
                       contracting_authority, contract_title, country
                FROM ted_china_contracts
                ORDER BY contract_value DESC
            """)
            china_contracts = cur.fetchall()

            for contract in china_contracts:
                results['china_contracts'].append({
                    'contract_id': contract[0],
                    'supplier_name': contract[1],
                    'contract_value': contract[2],
                    'award_date': contract[3],
                    'contracting_authority': contract[4],
                    'contract_title': contract[5],
                    'country': contract[6]
                })

        except sqlite3.OperationalError:
            print("ted_china_contracts table not found, checking other TED tables...")

        # Check for ted_contracts table
        try:
            cur.execute("""
                SELECT contract_id, supplier_name, contract_value, award_date,
                       contracting_authority, contract_title, country
                FROM ted_china_contracts
                WHERE LOWER(supplier_name) LIKE '%china%'
                   OR LOWER(supplier_name) LIKE '%chinese%'
                   OR LOWER(supplier_name) LIKE '%beijing%'
                   OR LOWER(supplier_name) LIKE '%shanghai%'
                ORDER BY contract_value DESC
                LIMIT 5000
            """)
            ted_china_contracts = cur.fetchall()

            if ted_china_contracts:
                print(f"Found {len(ted_china_contracts)} China-related contracts in ted_contracts")
                for contract in ted_china_contracts:
                    results['china_contracts'].append({
                        'contract_id': contract[0],
                        'supplier_name': contract[1],
                        'contract_value': contract[2],
                        'award_date': contract[3],
                        'contracting_authority': contract[4],
                        'contract_title': contract[5],
                        'country': contract[6]
                    })

        except sqlite3.OperationalError:
            print("ted_contracts table not found")

        # Try ted_analysis table
        try:
            cur.execute("""
                SELECT supplier_name, COUNT(*) as contract_count,
                       SUM(contract_value) as total_value
                FROM ted_analysis
                WHERE LOWER(supplier_name) LIKE '%china%'
                   OR LOWER(supplier_name) LIKE '%chinese%'
                   OR supplier_country = 'CN'
                GROUP BY supplier_name
                ORDER BY total_value DESC
            """)
            china_suppliers = cur.fetchall()

            if china_suppliers:
                print(f"Found {len(china_suppliers)} Chinese suppliers in ted_analysis")
                for supplier in china_suppliers:
                    results['chinese_suppliers'].append({
                        'supplier_name': supplier[0],
                        'contract_count': supplier[1],
                        'total_value': supplier[2]
                    })

        except sqlite3.OperationalError:
            print("ted_analysis table not found")

        # Calculate statistics
        if results['china_contracts']:
            total_value = sum(c['contract_value'] for c in results['china_contracts'] if c['contract_value'])
            results['contract_statistics'] = {
                'total_contracts': len(results['china_contracts']),
                'total_value': total_value,
                'average_value': total_value / len(results['china_contracts']) if results['china_contracts'] else 0,
                'unique_suppliers': len(set(c['supplier_name'] for c in results['china_contracts'] if c['supplier_name']))
            }

            # Temporal analysis by year
            temporal = {}
            for contract in results['china_contracts']:
                if contract['award_date']:
                    year = contract['award_date'][:4]
                    if year.isdigit():
                        temporal[year] = temporal.get(year, 0) + 1

            results['temporal_analysis'] = temporal

            # Country analysis
            country_stats = {}
            for contract in results['china_contracts']:
                country = contract.get('country', 'Unknown')
                if country not in country_stats:
                    country_stats[country] = {'count': 0, 'value': 0}
                country_stats[country]['count'] += 1
                if contract['contract_value']:
                    country_stats[country]['value'] += contract['contract_value']

            results['country_analysis'] = country_stats

        conn.close()

        # Save results
        output_file = self.output_dir / f"ted_china_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"Results saved to {output_file}")

        # Generate summary report
        self.generate_summary_report(results)

        return results

    def generate_summary_report(self, results):
        """Generate markdown summary report"""

        stats = results['contract_statistics']
        total_contracts = stats.get('total_contracts', 0)
        total_value = stats.get('total_value', 0)
        avg_value = stats.get('average_value', 0)
        unique_suppliers = stats.get('unique_suppliers', 0)

        report = f"""# TED China Contract Intelligence Report
Generated: {results['extraction_date']}

## Executive Summary
- **Total China Contracts**: {total_contracts:,}
- **Total Contract Value**: €{total_value:,.2f}
- **Average Contract Value**: €{avg_value:,.2f}
- **Unique Chinese Suppliers**: {unique_suppliers}

## Top Chinese Suppliers by Contract Value
"""

        # Top suppliers from china_contracts
        supplier_totals = {}
        for contract in results['china_contracts']:
            supplier = contract['supplier_name']
            if supplier:
                if supplier not in supplier_totals:
                    supplier_totals[supplier] = {'count': 0, 'value': 0}
                supplier_totals[supplier]['count'] += 1
                if contract['contract_value']:
                    supplier_totals[supplier]['value'] += contract['contract_value']

        top_suppliers = sorted(supplier_totals.items(), key=lambda x: x[1]['value'], reverse=True)

        for i, (supplier, data) in enumerate(top_suppliers[:15], 1):
            report += f"{i}. **{supplier}**: €{data['value']:,.0f} ({data['count']} contracts)\n"

        # Add suppliers from chinese_suppliers if available
        if results['chinese_suppliers']:
            report += "\n## Additional Chinese Suppliers (from TED Analysis)\n"
            for i, supplier in enumerate(results['chinese_suppliers'][:10], 1):
                report += f"{i}. **{supplier['supplier_name']}**: €{supplier['total_value']:,.0f} ({supplier['contract_count']} contracts)\n"

        # Country analysis
        if results['country_analysis']:
            report += "\n## Contracts by EU Country\n"
            country_list = sorted(results['country_analysis'].items(),
                                key=lambda x: x[1]['value'], reverse=True)
            for i, (country, data) in enumerate(country_list[:15], 1):
                report += f"{i}. **{country}**: €{data['value']:,.0f} ({data['count']} contracts)\n"

        # Temporal analysis
        if results['temporal_analysis']:
            report += "\n## China Contracts by Year\n"
            years = sorted(results['temporal_analysis'].keys())
            for year in years[-10:]:  # Last 10 years
                count = results['temporal_analysis'][year]
                report += f"- **{year}**: {count} contracts\n"

        # Top contracts by value
        report += "\n## Highest Value China Contracts\n"
        top_contracts = sorted(results['china_contracts'],
                             key=lambda x: x['contract_value'] if x['contract_value'] else 0,
                             reverse=True)

        for i, contract in enumerate(top_contracts[:10], 1):
            value_str = f"€{contract['contract_value']:,.0f}" if contract['contract_value'] else "N/A"
            title = contract['contract_title'][:60] + "..." if contract['contract_title'] and len(contract['contract_title']) > 60 else contract['contract_title']
            report += f"{i}. **{contract['supplier_name']}**: {value_str}\n"
            report += f"   {title}\n"
            report += f"   Authority: {contract['contracting_authority']}\n\n"

        # Intelligence insights
        report += f"""
## Key Intelligence Insights

1. **EU Procurement Exposure**: €{total_value:,.0f} in public contracts awarded to Chinese suppliers
2. **Market Penetration**: {unique_suppliers} distinct Chinese suppliers active in EU procurement
3. **Contract Scale**: Average contract value of €{avg_value:,.0f} indicates significant procurement activity
4. **Geographic Spread**: Chinese suppliers winning contracts across multiple EU member states

## Risk Assessment

### Procurement Security Concerns:
- Large-scale Chinese supplier involvement in EU public procurement
- Potential supply chain dependencies on Chinese entities
- Critical infrastructure contracts requiring enhanced due diligence

### Recommendations:
1. **Enhanced Screening**: Implement comprehensive due diligence for Chinese suppliers
2. **Supply Chain Security**: Assess critical infrastructure contracts for security implications
3. **Monitoring**: Track procurement patterns and dependencies on Chinese suppliers
4. **Policy Review**: Evaluate procurement rules for national security considerations

---
*TED China Contract Intelligence Analysis*
*Personal OSINT Learning Project*
"""

        report_file = self.output_dir / f"TED_CHINA_INTELLIGENCE_{datetime.now().strftime('%Y%m%d')}.md"
        report_file.write_text(report, encoding='utf-8')

        print(f"Intelligence report saved to {report_file}")

def main():
    extractor = TEDChinaExtractor()

    # First check the schema
    print("Checking TED database schema...")
    extractor.check_ted_schema()

    # Then extract contracts
    results = extractor.extract_china_contracts()

    print(f"\nTED China Extraction Complete:")
    print(f"- China Contracts: {results['contract_statistics'].get('total_contracts', 0)}")
    print(f"- Chinese Suppliers: {results['contract_statistics'].get('unique_suppliers', 0)}")
    print(f"- Total Value: €{results['contract_statistics'].get('total_value', 0):,.2f}")

if __name__ == "__main__":
    main()
