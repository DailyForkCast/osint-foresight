#!/usr/bin/env python3
"""
detect_chinese_investment_global.py - Global Chinese Investment Analysis

Analyzes Chinese investment/influence across multiple data sources:
- GLEIF: Global company ownership (3.1M companies)
- CORDIS: EU research funding (5K+ Chinese orgs)
- TED: European public procurement (3K+ contracts)
- EPO: European patents (80K+)
- OpenAIRE: EU research collaborations

Compares US (Form D) vs Europe vs Global patterns

SECURITY: NO .CN ACCESS

Last Updated: 2025-10-22
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class GlobalChineseInvestmentAnalyzer:
    """Analyze Chinese investment patterns globally"""

    def __init__(self, db_path='F:/OSINT_WAREHOUSE/osint_master.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        print("="*70)
        print("GLOBAL CHINESE INVESTMENT ANALYSIS")
        print("="*70)
        print(f"Database: {db_path}")
        print("="*70)

    def analyze_gleif_global(self):
        """Analyze GLEIF for Chinese companies worldwide"""
        print("\n" + "="*70)
        print("1. GLEIF: CHINESE COMPANIES BY COUNTRY")
        print("="*70)

        # Find Chinese companies registered globally
        self.cursor.execute("""
            SELECT
                legal_address_country as country,
                COUNT(*) as count
            FROM gleif_entities
            WHERE (
                legal_name LIKE '%China%'
                OR legal_name LIKE '%Chinese%'
                OR legal_name LIKE '%Beijing%'
                OR legal_name LIKE '%Shanghai%'
                OR legal_name LIKE '%Shenzhen%'
                OR legal_name LIKE '%Hong Kong%'
                OR hq_address_country = 'CN'
                OR legal_address_country = 'CN'
            )
            AND legal_address_country IS NOT NULL
            AND legal_address_country != 'CN'
            GROUP BY country
            ORDER BY count DESC
            LIMIT 30
        """)

        results = self.cursor.fetchall()

        print(f"\nChinese companies registered outside mainland China:")
        print(f"{'Country':<30} {'Count':>10}")
        print("-"*70)

        by_region = {
            'Europe': 0,
            'Asia': 0,
            'Americas': 0,
            'Other': 0
        }

        european_countries = ['GB', 'DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'LU', 'IE', 'CH',
                            'AT', 'SE', 'DK', 'NO', 'FI', 'PL', 'CZ', 'PT', 'GR', 'HU']
        asian_countries = ['SG', 'HK', 'JP', 'KR', 'MY', 'TH', 'ID', 'PH', 'VN', 'IN']
        americas = ['US', 'CA', 'BR', 'MX', 'AR', 'CL']

        for country, count in results:
            print(f"{country:<30} {count:>10,}")

            if country in european_countries:
                by_region['Europe'] += count
            elif country in asian_countries:
                by_region['Asia'] += count
            elif country in americas:
                by_region['Americas'] += count
            else:
                by_region['Other'] += count

        print("\n" + "-"*70)
        print("Regional Distribution:")
        for region, count in sorted(by_region.items(), key=lambda x: x[1], reverse=True):
            print(f"  {region}: {count:,} companies")

        return results

    def analyze_cordis_research(self):
        """Analyze EU research funding with Chinese participation"""
        print("\n" + "="*70)
        print("2. CORDIS: CHINESE ORGANIZATIONS IN EU RESEARCH")
        print("="*70)

        # Get Chinese org participation
        self.cursor.execute("SELECT COUNT(*) FROM cordis_chinese_orgs")
        chinese_orgs = self.cursor.fetchone()[0]

        print(f"\nChinese organizations in EU research: {chinese_orgs:,}")

        if chinese_orgs > 0:
            self.cursor.execute("""
                SELECT org_name, technology_focus, project_count, total_funding
                FROM cordis_chinese_orgs
                ORDER BY project_count DESC
                LIMIT 15
            """)

            print("\nTop Chinese Organizations:")
            print(f"{'Organization':<50} {'Projects':>8} {'Tech Focus':<20}")
            print("-"*70)

            for name, tech, projects, funding in self.cursor.fetchall():
                tech_display = (tech or 'General')[:18]
                print(f"{name[:48]:<50} {projects:>8} {tech_display:<20}")

        # Get country distribution
        self.cursor.execute("""
            SELECT primary_country, COUNT(*) as count
            FROM cordis_chinese_orgs
            WHERE primary_country IS NOT NULL
            GROUP BY primary_country
            ORDER BY count DESC
        """)

        country_dist = self.cursor.fetchall()
        if country_dist:
            print("\nChinese Org Distribution in EU Projects:")
            for country, count in country_dist[:10]:
                print(f"  {country}: {count:,} organizations")

        return chinese_orgs

    def analyze_ted_contracts(self):
        """Analyze European public procurement with Chinese involvement"""
        print("\n" + "="*70)
        print("3. TED: CHINESE COMPANIES IN EU PUBLIC PROCUREMENT")
        print("="*70)

        self.cursor.execute("SELECT COUNT(*) FROM ted_china_contracts_fixed")
        total_contracts = self.cursor.fetchone()[0]

        print(f"\nContracts with Chinese involvement: {total_contracts:,}")

        if total_contracts > 0:
            # Get top EU countries with Chinese contractors
            self.cursor.execute("""
                SELECT buyer_country, COUNT(*) as count, SUM(contract_value) as total_value
                FROM ted_china_contracts_fixed
                WHERE buyer_country IS NOT NULL
                GROUP BY buyer_country
                ORDER BY count DESC
                LIMIT 15
            """)

            print("\nTop EU Countries by Chinese Contract Count:")
            print(f"{'Country':<20} {'Contracts':>10} {'Total Value':>20}")
            print("-"*70)

            for country, count, value in self.cursor.fetchall():
                value_str = f"€{value/1e6:,.1f}M" if value else "N/A"
                print(f"{country:<20} {count:>10,} {value_str:>20}")

        return total_contracts

    def analyze_epo_patents(self):
        """Analyze European patents with Chinese involvement"""
        print("\n" + "="*70)
        print("4. EPO: CHINESE PATENTS IN EUROPE")
        print("="*70)

        self.cursor.execute("SELECT COUNT(*) FROM epo_patents")
        total_patents = self.cursor.fetchone()[0]

        print(f"\nTotal EPO patents in database: {total_patents:,}")

        # Check Chinese patent flag
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM epo_patents
            WHERE is_chinese_entity = 1
        """)

        chinese_patents = self.cursor.fetchone()[0]
        print(f"Patents with Chinese entities: {chinese_patents:,} ({chinese_patents/total_patents*100:.2f}%)")

        # Check dual-use technology
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM epo_patents
            WHERE is_chinese_entity = 1 AND has_dual_use = 1
        """)

        chinese_dual_use = self.cursor.fetchone()[0]
        print(f"Chinese dual-use tech patents: {chinese_dual_use:,}")

        return chinese_patents

    def analyze_openaire_collaborations(self):
        """Analyze OpenAIRE research collaborations"""
        print("\n" + "="*70)
        print("5. OPENAIRE: EU-CHINA RESEARCH COLLABORATIONS")
        print("="*70)

        self.cursor.execute("SELECT COUNT(*) FROM openaire_china_collaborations")
        collabs = self.cursor.fetchone()[0]

        print(f"\nEU-China research collaborations: {collabs:,}")

        if collabs > 0:
            # Get sample data
            self.cursor.execute("""
                SELECT * FROM openaire_china_collaborations LIMIT 5
            """)
            print("\nSample collaborations found in database")

        return collabs

    def compare_us_vs_europe(self):
        """Compare US (Form D) vs Europe patterns"""
        print("\n" + "="*70)
        print("6. COMPARATIVE ANALYSIS: US vs EUROPE")
        print("="*70)

        # Get US Form D stats
        self.cursor.execute("""
            SELECT COUNT(*) as total_filings,
                   SUM(CASE WHEN collected_quarter LIKE '2024%' THEN 1 ELSE 0 END) as filings_2024
            FROM sec_form_d_offerings
        """)

        us_total, us_2024 = self.cursor.fetchone()

        self.cursor.execute("""
            SELECT COUNT(DISTINCT p.accession_number)
            FROM sec_form_d_persons p
            WHERE p.person_address_state LIKE '%Hong Kong%'
               OR p.person_address_state LIKE '%China%'
               OR p.person_address_city IN ('Beijing', 'Shanghai', 'Shenzhen', 'Hong Kong')
        """)

        us_china_linked = self.cursor.fetchone()[0]

        # Get Europe stats
        europe_contracts = 0
        self.cursor.execute("SELECT COUNT(*) FROM ted_china_contracts_fixed")
        europe_contracts = self.cursor.fetchone()[0]

        europe_research = 0
        self.cursor.execute("SELECT COUNT(*) FROM cordis_chinese_orgs")
        europe_research = self.cursor.fetchone()[0]

        print("\nUS Private Capital (Form D):")
        print(f"  Total filings (10 years):    {us_total:,}")
        print(f"  China-linked filings:         {us_china_linked:,} ({us_china_linked/us_total*100:.2f}%)")
        print(f"  2024 filings:                 {us_2024:,}")

        print("\nEurope:")
        print(f"  Public procurement (TED):     {europe_contracts:,} contracts")
        print(f"  Research funding (CORDIS):    {europe_research:,} Chinese orgs")

        comparison = {
            'us': {
                'total_filings': us_total,
                'china_linked': us_china_linked,
                'percentage': us_china_linked/us_total*100 if us_total else 0
            },
            'europe': {
                'contracts': europe_contracts,
                'research_orgs': europe_research
            }
        }

        return comparison

    def generate_report(self, gleif_results, cordis_count, ted_count, epo_count, openaire_count, comparison):
        """Generate comprehensive global report"""
        print("\n" + "="*70)
        print("GENERATING GLOBAL REPORT")
        print("="*70)

        report = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'scope': 'Global Chinese Investment Analysis',
                'data_sources': ['GLEIF', 'CORDIS', 'TED', 'EPO', 'OpenAIRE', 'Form D']
            },
            'summary': {
                'gleif_chinese_companies_global': len(gleif_results),
                'cordis_chinese_research_orgs': cordis_count,
                'ted_european_contracts': ted_count,
                'epo_chinese_patents': epo_count,
                'openaire_collaborations': openaire_count
            },
            'us_vs_europe': comparison,
            'gleif_country_distribution': [{'country': r[0], 'count': r[1]} for r in gleif_results],
        }

        # Save report
        output_path = Path('analysis/chinese_investment_global_analysis.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\n[OK] Report saved: {output_path}")

        print("\n" + "="*70)
        print("GLOBAL SUMMARY")
        print("="*70)
        print(f"GLEIF Chinese Companies (outside CN):  {len(gleif_results)} countries")
        print(f"CORDIS EU Research Orgs:                {cordis_count:,}")
        print(f"TED European Contracts:                 {ted_count:,}")
        print(f"EPO Patents:                            {epo_count:,}")
        print(f"OpenAIRE Collaborations:                {openaire_count:,}")
        print("="*70)

        return report

    def run_full_analysis(self):
        """Run complete global analysis"""
        print(f"\nStarting global analysis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Run all analyses
        gleif_results = self.analyze_gleif_global()
        cordis_count = self.analyze_cordis_research()
        ted_count = self.analyze_ted_contracts()
        epo_count = self.analyze_epo_patents()
        openaire_count = self.analyze_openaire_collaborations()
        comparison = self.compare_us_vs_europe()

        # Generate report
        report = self.generate_report(gleif_results, cordis_count, ted_count,
                                     epo_count, openaire_count, comparison)

        return report


def main():
    """Run global analysis"""
    analyzer = GlobalChineseInvestmentAnalyzer()
    report = analyzer.run_full_analysis()

    print("\n" + "="*70)
    print("GLOBAL ANALYSIS COMPLETE")
    print("="*70)
    print("Report: analysis/chinese_investment_global_analysis.json")
    print("="*70)


if __name__ == '__main__':
    main()
