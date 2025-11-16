#!/usr/bin/env python3
import re

# ============================================================================
# SECURITY: SQL injection prevention through identifier validation
# ============================================================================

def validate_sql_identifier(identifier):
    """
    SECURITY: Validate SQL identifier (table or column name).
    Only allows alphanumeric characters and underscores.
    Prevents SQL injection from dynamic SQL construction.
    """
    if not identifier:
        raise ValueError("Identifier cannot be empty")

    # Check for valid characters only (alphanumeric + underscore)
    if not re.match(r'^[a-zA-Z0-9_]+$', identifier):
        raise ValueError(f"Invalid identifier: {identifier}. Contains illegal characters.")

    # Check length (SQLite limit is 1024, we use 100 for safety)
    if len(identifier) > 100:
        raise ValueError(f"Identifier too long: {identifier}")

    # Blacklist dangerous SQL keywords
    dangerous_keywords = {'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
                         'EXEC', 'EXECUTE', 'UNION', 'SELECT', '--', ';', '/*', '*/'}
    if identifier.upper() in dangerous_keywords:
        raise ValueError(f"Identifier contains SQL keyword: {identifier}")

    return identifier


"""
Investigate Chinese VC Presence and Activity in Europe
======================================================
Identify Chinese VC firms operating in Europe and analyze their activity.

Author: OSINT Foresight Analysis
Date: 2025-10-25
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3
import json
from datetime import datetime
from pathlib import Path

class ChineseVCEuropeInvestigator:
    def __init__(self):
        self.db_path = 'F:/OSINT_WAREHOUSE/osint_master.db'
        self.output_dir = Path('analysis/chinese_vc_europe')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Known major Chinese VC firms to search for
        self.known_chinese_vcs = [
            'Sequoia Capital China',
            'Sequoia China',
            'IDG Capital',
            'Hillhouse Capital',
            'HHCG',
            'GGV Capital',
            'ZhenFund',
            'Matrix Partners China',
            'Qiming Venture Partners',
            'Legend Capital',
            'CDH Investments',
            'Hony Capital',
            'CITIC Capital',
            'China Investment Corporation',
            'CIC Capital',
            'Tencent Investment',
            'Alibaba Capital',
            'Baidu Ventures',
            'ByteDance',
            'Xiaomi Ventures',
            'Huawei Investment',
            'WuXi Healthcare Ventures',
            'OrbiMed Asia',
            'Loyal Valley Capital',
            'Shunwei Capital',
            'Northern Light Venture Capital',
            '5Y Capital',
            'Source Code Capital',
            'Sinovation Ventures',
            'Innovation Works',
            'Vertex Ventures China',
            'DCM Ventures',
            'Morningside Venture Capital'
        ]

        # European countries
        self.european_countries = [
            'GB', 'DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'AT', 'SE', 'DK',
            'NO', 'FI', 'IE', 'PT', 'GR', 'PL', 'CZ', 'HU', 'RO', 'BG',
            'HR', 'SI', 'SK', 'LT', 'LV', 'EE', 'LU', 'MT', 'CY', 'CH'
        ]

    def analyze_gleif_chinese_entities_europe(self):
        """Analyze GLEIF Chinese entities in Europe to identify VC firms"""
        print("\n" + "="*70)
        print("GLEIF CHINESE ENTITIES IN EUROPE - VC FIRM IDENTIFICATION")
        print("="*70)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        results = {
            'by_jurisdiction': [],
            'by_hq_location': [],
            'potential_vc_firms': []
        }

        # Method 1: Chinese jurisdiction, registered in Europe
        print("\n[1] Chinese jurisdiction entities registered in Europe:")
        for country in self.european_countries:
            cursor.execute('''
                SELECT
                    lei,
                    legal_name,
                    legal_address_country,
                    legal_jurisdiction,
                    hq_address_country,
                    entity_category
                FROM gleif_entities
                WHERE legal_jurisdiction IN ('CN', 'HK')
                AND legal_address_country = ?
            ''', (country,))

            entities = cursor.fetchall()
            if entities:
                print(f"\n  {country}: {len(entities)} entities")
                for entity in entities:
                    lei, name, leg_country, jurisdiction, hq_country, category = entity
                    print(f"    - {name}")
                    print(f"      LEI: {lei}")
                    print(f"      Legal Country: {leg_country}, Jurisdiction: {jurisdiction}, HQ: {hq_country}")

                    # Check if might be VC/investment firm
                    is_potential_vc = self._is_potential_vc(name)
                    if is_potential_vc:
                        print(f"      ⭐ POTENTIAL VC/INVESTMENT FIRM")
                        results['potential_vc_firms'].append({
                            'lei': lei,
                            'name': name,
                            'country': leg_country,
                            'detection_method': 'chinese_jurisdiction'
                        })

                    results['by_jurisdiction'].append({
                        'lei': lei,
                        'name': name,
                        'country': leg_country,
                        'jurisdiction': jurisdiction,
                        'hq_country': hq_country,
                        'category': category,
                        'is_potential_vc': is_potential_vc
                    })

        # Method 2: China HQ, registered in Europe
        print("\n[2] China HQ entities registered in Europe:")
        for country in self.european_countries:
            cursor.execute('''
                SELECT
                    lei,
                    legal_name,
                    legal_address_country,
                    legal_jurisdiction,
                    hq_address_country,
                    entity_category
                FROM gleif_entities
                WHERE hq_address_country IN ('CN', 'HK')
                AND legal_address_country = ?
                AND legal_jurisdiction NOT IN ('CN', 'HK')
            ''', (country,))

            entities = cursor.fetchall()
            if entities:
                print(f"\n  {country}: {len(entities)} entities")
                for entity in entities:
                    lei, name, leg_country, jurisdiction, hq_country, category = entity
                    print(f"    - {name}")
                    print(f"      LEI: {lei}")
                    print(f"      Legal Country: {leg_country}, Jurisdiction: {jurisdiction}, HQ: {hq_country}")

                    # Check if might be VC/investment firm
                    is_potential_vc = self._is_potential_vc(name)
                    if is_potential_vc:
                        print(f"      ⭐ POTENTIAL VC/INVESTMENT FIRM")
                        results['potential_vc_firms'].append({
                            'lei': lei,
                            'name': name,
                            'country': leg_country,
                            'detection_method': 'china_hq'
                        })

                    results['by_hq_location'].append({
                        'lei': lei,
                        'name': name,
                        'country': leg_country,
                        'jurisdiction': jurisdiction,
                        'hq_country': hq_country,
                        'category': category,
                        'is_potential_vc': is_potential_vc
                    })

        conn.close()
        return results

    def search_known_chinese_vcs_in_gleif(self):
        """Search GLEIF for known Chinese VC firms' European entities"""
        print("\n" + "="*70)
        print("SEARCHING GLEIF FOR KNOWN CHINESE VC FIRMS")
        print("="*70)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        found_vcs = []

        for vc_firm in self.known_chinese_vcs:
            # Search for entities with this name in Europe
            for country in self.european_countries:
                cursor.execute('''
                    SELECT
                        lei,
                        legal_name,
                        legal_address_country,
                        legal_jurisdiction,
                        hq_address_country
                    FROM gleif_entities
                    WHERE legal_name LIKE ?
                    AND legal_address_country = ?
                ''', (f'%{vc_firm}%', country))

                entities = cursor.fetchall()
                if entities:
                    print(f"\n✅ FOUND: {vc_firm} in {country}")
                    for entity in entities:
                        lei, name, leg_country, jurisdiction, hq_country = entity
                        print(f"  LEI: {lei}")
                        print(f"  Legal Name: {name}")
                        print(f"  Country: {leg_country}, Jurisdiction: {jurisdiction}, HQ: {hq_country}")

                        found_vcs.append({
                            'vc_firm_searched': vc_firm,
                            'lei': lei,
                            'legal_name': name,
                            'country': leg_country,
                            'jurisdiction': jurisdiction,
                            'hq_country': hq_country
                        })

        if not found_vcs:
            print("\n❌ No known Chinese VC firms found with European GLEIF registrations")

        conn.close()
        return found_vcs

    def analyze_european_investment_data(self):
        """Analyze any European investment data we have"""
        print("\n" + "="*70)
        print("ANALYZING EUROPEAN INVESTMENT DATA")
        print("="*70)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check what European data sources we have
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND (
                name LIKE '%europe%' OR
                name LIKE '%eu_%' OR
                name LIKE '%cordis%' OR
                name LIKE '%ted%'
            )
        """)
        tables = cursor.fetchall()

        print(f"\nAvailable European data tables:")
        for table in tables:
            table_name = table[0]
            # SECURITY: Validate table name before use in SQL
            safe_table = validate_sql_identifier(table_name)
            cursor.execute(f'SELECT COUNT(*) FROM {safe_table}')
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count:,} records")

        # Analyze CORDIS for Chinese VC involvement
        print("\n" + "="*70)
        print("CORDIS: Chinese Organizations (Potential VC/Investment)")
        print("="*70)

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name LIKE '%cordis%'
        """)
        cordis_tables = cursor.fetchall()

        if cordis_tables:
            # Try to find investment-related organizations
            for table in cordis_tables:
                table_name = table[0]

                # Get schema
                # SECURITY: Validate table name before use in SQL
                safe_table = validate_sql_identifier(table_name)
                cursor.execute(f'PRAGMA table_info({safe_table})')
                columns = [col[1] for col in cursor.fetchall()]

                # Look for organization name field
                org_col = next((col for col in columns if 'organization' in col.lower() or 'name' in col.lower()), None)

                if org_col:
                    print(f"\n  Searching {table_name} for investment/VC keywords...")

                    # Search for investment-related keywords
                    keywords = ['Investment', 'Capital', 'Venture', 'Fund', 'Holdings']
                    for keyword in keywords:
                        try:
                            # SECURITY: Validate column name and use parameterized query for values
                            safe_org_col = validate_sql_identifier(org_col)
                            cursor.execute(f'''
                                SELECT DISTINCT {safe_org_col}
                                FROM {safe_table}
                                WHERE {safe_org_col} LIKE ?
                                AND {safe_org_col} LIKE '%Chin%'
                                LIMIT 10
                            ''', (f'%{keyword}%',))
                            results = cursor.fetchall()
                            if results:
                                print(f"    {keyword}: {len(results)} matches")
                                for result in results[:5]:
                                    print(f"      - {result[0]}")
                        except Exception as e:
                            pass

        conn.close()

    def _is_potential_vc(self, name):
        """Check if entity name suggests it's a VC/investment firm"""
        name_lower = name.lower()

        # VC/Investment keywords
        vc_keywords = [
            'capital', 'venture', 'investment', 'fund', 'partners',
            'holdings', 'asset management', 'private equity', 'vc'
        ]

        # Check if name contains VC keywords
        for keyword in vc_keywords:
            if keyword in name_lower:
                return True

        # Check if matches known Chinese VC firms
        for known_vc in self.known_chinese_vcs:
            if known_vc.lower() in name_lower:
                return True

        return False

    def generate_report(self, gleif_results, known_vcs_found):
        """Generate comprehensive report"""
        print("\n" + "="*70)
        print("GENERATING REPORT")
        print("="*70)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        report = {
            'analysis_metadata': {
                'generated_timestamp': timestamp,
                'database_path': str(self.db_path),
                'european_countries_searched': len(self.european_countries),
                'known_vc_firms_searched': len(self.known_chinese_vcs)
            },
            'summary': {
                'chinese_entities_europe_jurisdiction': len(gleif_results['by_jurisdiction']),
                'chinese_entities_europe_hq': len(gleif_results['by_hq_location']),
                'total_unique_chinese_entities': len(gleif_results['by_jurisdiction']) + len(gleif_results['by_hq_location']),
                'potential_vc_firms_identified': len(gleif_results['potential_vc_firms']),
                'known_vc_firms_found': len(known_vcs_found)
            },
            'gleif_analysis': gleif_results,
            'known_vcs_in_europe': known_vcs_found,
            'recommendations': [
                'Manual verification required for potential VC firms identified',
                'Web search for Chinese VC firms\' European offices not in GLEIF',
                'Cross-reference with European startup funding databases',
                'Monitor EU foreign investment screening notifications'
            ]
        }

        # Save to JSON
        output_file = self.output_dir / f'chinese_vc_europe_investigation_{timestamp}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n[OK] Report saved: {output_file}")

        # Generate summary
        print("\n" + "="*70)
        print("INVESTIGATION SUMMARY")
        print("="*70)
        print(f"\nChinese entities in Europe (GLEIF):")
        print(f"  By jurisdiction (CN/HK law): {report['summary']['chinese_entities_europe_jurisdiction']}")
        print(f"  By HQ location (China HQ): {report['summary']['chinese_entities_europe_hq']}")
        print(f"  Total: {report['summary']['total_unique_chinese_entities']}")
        print(f"\nPotential VC/investment firms: {report['summary']['potential_vc_firms_identified']}")
        print(f"Known Chinese VC firms found: {report['summary']['known_vc_firms_found']}")

        if gleif_results['potential_vc_firms']:
            print("\nPotential VC firms identified:")
            for vc in gleif_results['potential_vc_firms']:
                print(f"  - {vc['name']} ({vc['country']})")

        if known_vcs_found:
            print("\nKnown VC firms with European presence:")
            for vc in known_vcs_found:
                print(f"  - {vc['vc_firm_searched']}")
                print(f"    Legal Name: {vc['legal_name']}")
                print(f"    Country: {vc['country']}")

        return output_file

    def run(self):
        """Run complete investigation"""
        print("\n" + "="*70)
        print("CHINESE VC PRESENCE IN EUROPE - INVESTIGATION")
        print("="*70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Step 1: Analyze GLEIF Chinese entities in Europe
        gleif_results = self.analyze_gleif_chinese_entities_europe()

        # Step 2: Search for known Chinese VCs
        known_vcs_found = self.search_known_chinese_vcs_in_gleif()

        # Step 3: Analyze other European data sources
        self.analyze_european_investment_data()

        # Step 4: Generate report
        output_file = self.generate_report(gleif_results, known_vcs_found)

        print("\n" + "="*70)
        print("INVESTIGATION COMPLETE")
        print("="*70)
        print(f"\nReport: {output_file}")
        print("\nNext steps:")
        print("  1. Manually verify potential VC firms identified")
        print("  2. Web search for Chinese VC European offices")
        print("  3. Cross-reference with Crunchbase/PitchBook if available")
        print("  4. Search European startup funding news")
        print("="*70)

if __name__ == '__main__':
    investigator = ChineseVCEuropeInvestigator()
    investigator.run()
