#!/usr/bin/env python3
"""
detect_chinese_vc_form_d.py - Chinese VC Detection in Form D Filings

SECURITY POLICY: NO DIRECT .CN ACCESS
- Uses only US/EU data sources
- Reference database built from SEC, CFIUS, academic sources
- No web scraping of Chinese domains

Detection Methodology:
1. Direct name matching with known Chinese VC firms
2. Address-based detection (mainland China, Hong Kong)
3. Network analysis (board member patterns)
4. Cross-reference with USPTO patent ownership

Last Updated: 2025-10-22
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import re

class ChineseVCDetector:
    """Detect Chinese VC involvement in Form D filings"""

    def __init__(self, db_path='F:/OSINT_WAREHOUSE/osint_master.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        # Load reference database
        ref_db_path = Path('data/chinese_vc_reference_database.json')
        with open(ref_db_path, 'r', encoding='utf-8') as f:
            self.ref_db = json.load(f)

        self.known_vcs = self.ref_db['known_chinese_vc_firms']
        self.detection_patterns = self.ref_db['detection_patterns']
        self.state_backed = self.ref_db['state_backed_entities']

        print("="*70)
        print("CHINESE VC DETECTION IN FORM D FILINGS")
        print("="*70)
        print(f"Database: {db_path}")
        print(f"Reference VCs: {len(self.known_vcs)} firms")
        print(f"State-backed entities: {len(self.state_backed)} entities")
        print(f"Detection layers: {len(self.ref_db['detection_methodology'])}")
        print("="*70)

    def tier1_direct_name_match(self):
        """Tier 1: Direct name matching with known Chinese VCs"""
        print("\n" + "="*70)
        print("TIER 1: DIRECT NAME MATCHING")
        print("="*70)

        matches = []

        # Build name search patterns
        search_names = []
        for vc in self.known_vcs + self.state_backed:
            search_names.append(vc['name'])
            if 'aliases' in vc:
                search_names.extend(vc['aliases'])

        print(f"\n-> Searching {len(search_names)} entity names...")

        # Search in persons table (directors, executives)
        for name in search_names:
            # Skip Chinese characters (can't reliably search without .cn access for verification)
            if any(ord(char) > 127 for char in name):
                continue

            # Search for name in person_name
            self.cursor.execute("""
                SELECT DISTINCT
                    p.accession_number,
                    o.issuer_name,
                    o.issuer_cik,
                    p.person_name,
                    p.relationship,
                    p.person_address_city,
                    p.person_address_state,
                    o.total_offering_amount,
                    o.industry_group_type,
                    o.filing_date
                FROM sec_form_d_persons p
                JOIN sec_form_d_offerings o ON p.accession_number = o.accession_number
                WHERE p.person_name LIKE ?
                AND o.collected_quarter = '2025q2'
            """, (f'%{name}%',))

            results = self.cursor.fetchall()

            for row in results:
                matches.append({
                    'tier': 1,
                    'detection_method': 'Direct name match',
                    'confidence': 'HIGH',
                    'matched_entity': name,
                    'accession_number': row[0],
                    'issuer_name': row[1],
                    'issuer_cik': row[2],
                    'person_name': row[3],
                    'relationship': row[4],
                    'person_city': row[5],
                    'person_state': row[6],
                    'offering_amount': row[7],
                    'industry': row[8],
                    'filing_date': row[9]
                })

        print(f"[FOUND] {len(matches)} direct name matches")
        return matches

    def tier2_address_detection(self):
        """Tier 2: Address-based detection (mainland China, Hong Kong)"""
        print("\n" + "="*70)
        print("TIER 2: ADDRESS-BASED DETECTION")
        print("="*70)

        matches = []

        # Mainland China cities
        china_cities = self.detection_patterns['mainland_china_cities']
        hk_indicators = self.detection_patterns['hong_kong_indicators']

        all_locations = china_cities + hk_indicators

        print(f"\n-> Searching for addresses in {len(all_locations)} Chinese locations...")

        for location in all_locations:
            self.cursor.execute("""
                SELECT DISTINCT
                    p.accession_number,
                    o.issuer_name,
                    o.issuer_cik,
                    p.person_name,
                    p.relationship,
                    p.person_address_city,
                    p.person_address_state,
                    o.total_offering_amount,
                    o.industry_group_type,
                    o.filing_date
                FROM sec_form_d_persons p
                JOIN sec_form_d_offerings o ON p.accession_number = o.accession_number
                WHERE (
                    p.person_address_city LIKE ?
                    OR p.person_address_state LIKE ?
                )
                AND o.collected_quarter = '2025q2'
            """, (f'%{location}%', f'%{location}%'))

            results = self.cursor.fetchall()

            for row in results:
                matches.append({
                    'tier': 2,
                    'detection_method': 'Address-based',
                    'confidence': 'MEDIUM',
                    'matched_location': location,
                    'accession_number': row[0],
                    'issuer_name': row[1],
                    'issuer_cik': row[2],
                    'person_name': row[3],
                    'relationship': row[4],
                    'person_city': row[5],
                    'person_state': row[6],
                    'offering_amount': row[7],
                    'industry': row[8],
                    'filing_date': row[9]
                })

        print(f"[FOUND] {len(matches)} address-based matches")
        return matches

    def tier3_company_name_patterns(self):
        """Tier 3: Company name pattern detection"""
        print("\n" + "="*70)
        print("TIER 3: COMPANY NAME PATTERN DETECTION")
        print("="*70)

        matches = []

        patterns = self.detection_patterns['chinese_company_names']

        print(f"\n-> Searching for {len(patterns)} company name patterns...")

        for pattern in patterns:
            self.cursor.execute("""
                SELECT DISTINCT
                    o.accession_number,
                    o.issuer_name,
                    o.issuer_cik,
                    o.total_offering_amount,
                    o.industry_group_type,
                    o.filing_date,
                    o.issuer_address_city,
                    o.issuer_address_state
                FROM sec_form_d_offerings o
                WHERE o.issuer_name LIKE ?
                AND o.collected_quarter = '2025q2'
            """, (f'%{pattern}%',))

            results = self.cursor.fetchall()

            for row in results:
                matches.append({
                    'tier': 3,
                    'detection_method': 'Company name pattern',
                    'confidence': 'MEDIUM',
                    'matched_pattern': pattern,
                    'accession_number': row[0],
                    'issuer_name': row[1],
                    'issuer_cik': row[2],
                    'offering_amount': row[3],
                    'industry': row[4],
                    'filing_date': row[5],
                    'issuer_city': row[6],
                    'issuer_state': row[7]
                })

        print(f"[FOUND] {len(matches)} company name pattern matches")
        return matches

    def tier4_dual_use_technology_focus(self):
        """Tier 4: Find China-linked deals in dual-use tech sectors"""
        print("\n" + "="*70)
        print("TIER 4: DUAL-USE TECHNOLOGY + CHINA LINKS")
        print("="*70)

        matches = []

        # Get all China-linked offerings from Tier 1-3
        china_linked_accessions = set()

        # Quick scan for China-linked persons
        self.cursor.execute("""
            SELECT DISTINCT p.accession_number
            FROM sec_form_d_persons p
            WHERE p.person_address_state LIKE '%Hong Kong%'
               OR p.person_address_state LIKE '%China%'
               OR p.person_address_city IN ('Beijing', 'Shanghai', 'Shenzhen', 'Hong Kong')
        """)

        for row in self.cursor.fetchall():
            china_linked_accessions.add(row[0])

        print(f"\n-> Found {len(china_linked_accessions)} China-linked offerings")

        # Check which are in high-risk dual-use sectors
        high_risk_sectors = self.detection_patterns['high_risk_sectors_dual_use']

        for accession in china_linked_accessions:
            self.cursor.execute("""
                SELECT
                    o.accession_number,
                    o.issuer_name,
                    o.issuer_cik,
                    o.industry_group_type,
                    o.total_offering_amount,
                    o.filing_date
                FROM sec_form_d_offerings o
                WHERE o.accession_number = ?
            """, (accession,))

            row = self.cursor.fetchone()
            if row:
                industry = row[3] or ""

                # Check if industry matches dual-use sectors
                for sector in high_risk_sectors:
                    if sector.lower() in industry.lower():
                        matches.append({
                            'tier': 4,
                            'detection_method': 'Dual-use tech + China link',
                            'confidence': 'HIGH',
                            'risk_sector': sector,
                            'accession_number': row[0],
                            'issuer_name': row[1],
                            'issuer_cik': row[2],
                            'industry': row[3],
                            'offering_amount': row[4],
                            'filing_date': row[5]
                        })
                        break

        print(f"[FOUND] {len(matches)} dual-use tech matches with China links")
        return matches

    def cross_reference_with_patents(self, matches):
        """Cross-reference detected companies with USPTO patent database"""
        print("\n" + "="*70)
        print("CROSS-REFERENCE WITH USPTO PATENTS")
        print("="*70)

        enriched_matches = []

        # Get unique CIKs from matches
        unique_ciks = set()
        for match in matches:
            cik = match.get('issuer_cik')
            if cik:
                unique_ciks.add(cik)

        print(f"\n-> Cross-referencing {len(unique_ciks)} companies with patent database...")

        for match in matches:
            issuer_name = match.get('issuer_name', '')
            issuer_cik = match.get('issuer_cik', '')

            # Search patents by company name
            # (Simplified - in production would use fuzzy matching)
            try:
                self.cursor.execute("""
                    SELECT COUNT(*) as patent_count
                    FROM patents
                    WHERE assignee_name LIKE ?
                    LIMIT 1
                """, (f'%{issuer_name}%',))
            except:
                # Try alternate table if patents table doesn't exist
                try:
                    self.cursor.execute("""
                        SELECT COUNT(*) as patent_count
                        FROM intelligence_patents
                        WHERE assignee_name LIKE ?
                        LIMIT 1
                    """, (f'%{issuer_name}%',))
                except:
                    match['patent_count'] = 0
                    match['has_patents'] = False
                    enriched_matches.append(match)
                    continue

            try:
                patent_count = self.cursor.fetchone()[0]
                match['patent_count'] = patent_count
                match['has_patents'] = patent_count > 0
            except:
                match['patent_count'] = 0
                match['has_patents'] = False

            enriched_matches.append(match)

        with_patents = sum(1 for m in enriched_matches if m['has_patents'])
        print(f"[FOUND] {with_patents} matches have USPTO patents")

        return enriched_matches

    def generate_report(self, all_matches):
        """Generate intelligence report"""
        print("\n" + "="*70)
        print("GENERATING INTELLIGENCE REPORT")
        print("="*70)

        # Deduplicate by accession number
        unique_matches = {}
        for match in all_matches:
            acc = match['accession_number']
            if acc not in unique_matches:
                unique_matches[acc] = match
            elif match['tier'] < unique_matches[acc]['tier']:
                # Keep higher tier (lower number = higher priority)
                unique_matches[acc] = match

        final_matches = list(unique_matches.values())

        # Sort by tier, then offering amount
        final_matches.sort(key=lambda x: (x['tier'], -(x.get('offering_amount') or 0)))

        # Statistics
        total_capital = sum(m.get('offering_amount', 0) or 0 for m in final_matches)
        by_tier = {}
        for match in final_matches:
            tier = match['tier']
            by_tier[tier] = by_tier.get(tier, 0) + 1

        report = {
            'timestamp': datetime.now().isoformat(),
            'quarter': '2025q2',
            'summary': {
                'total_matches': len(final_matches),
                'total_capital_flagged': total_capital,
                'by_tier': by_tier,
                'high_confidence': by_tier.get(1, 0) + by_tier.get(4, 0),
                'medium_confidence': by_tier.get(2, 0) + by_tier.get(3, 0)
            },
            'matches': final_matches,
            'methodology': self.ref_db['detection_methodology'],
            'data_sources': self.ref_db['metadata']['sources'],
            'compliance': self.ref_db['compliance_notes']
        }

        # Save report
        output_path = Path('analysis/chinese_vc_form_d_detection_q2_2025.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\n[OK] Report saved: {output_path}")

        # Print summary
        print("\n" + "="*70)
        print("DETECTION SUMMARY")
        print("="*70)
        print(f"Total matches:          {len(final_matches):,}")
        print(f"Total capital flagged:  ${total_capital:,.0f}")
        print(f"\nBy Detection Tier:")
        for tier in sorted(by_tier.keys()):
            print(f"  Tier {tier}: {by_tier[tier]:,} matches")
        print(f"\nConfidence Levels:")
        print(f"  HIGH confidence:   {report['summary']['high_confidence']:,}")
        print(f"  MEDIUM confidence: {report['summary']['medium_confidence']:,}")
        print("="*70)

        return report

    def run_full_detection(self):
        """Run all detection tiers"""
        print(f"\nStarting detection run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        all_matches = []

        # Run all detection tiers
        all_matches.extend(self.tier1_direct_name_match())
        all_matches.extend(self.tier2_address_detection())
        all_matches.extend(self.tier3_company_name_patterns())
        all_matches.extend(self.tier4_dual_use_technology_focus())

        # Cross-reference with patents
        enriched_matches = self.cross_reference_with_patents(all_matches)

        # Generate report
        report = self.generate_report(enriched_matches)

        return report


def main():
    """Run Chinese VC detection"""
    detector = ChineseVCDetector()
    report = detector.run_full_detection()

    print("\n" + "="*70)
    print("DETECTION COMPLETE")
    print("="*70)
    print(f"Matches: {report['summary']['total_matches']:,}")
    print(f"Report: analysis/chinese_vc_form_d_detection_q2_2025.json")
    print("="*70)


if __name__ == '__main__':
    main()
