#!/usr/bin/env python3
"""
BIS Entity List - Temporal Cross-Reference Analyzer
Properly flags violations vs. historical activity based on dates

Key Logic:
- Activity BEFORE BIS listing = Historical (flag for awareness, not violation)
- Activity AFTER BIS listing = Potential violation (flag for compliance review)
- Ongoing activity crossing sanction date = Mixed (flag for detailed review)

Zero Fabrication Protocol:
- Only flag as "violation" if dates confirm post-sanction activity
- Otherwise mark as "historical" or "temporal context required"
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import json

MASTER_DB = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_DIR = Path("F:/OSINT_Data/BIS_Cross_Reference")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class BISTemporalAnalyzer:
    def __init__(self):
        self.conn = sqlite3.connect(MASTER_DB, timeout=300)
        self.cur = self.conn.cursor()

    def analyze_ted_contracts(self):
        """Analyze TED contracts with temporal awareness"""
        print('=' * 80)
        print('TED CONTRACTS - BIS ENTITY LIST CROSS-REFERENCE')
        print('=' * 80)

        # Note: date_added is often NULL in parsed PDF data
        # For now, use known major sanction dates
        known_dates = {
            'HUAWEI': '2019-05-15',
            'ZTE': '2018-04-15',
            'HIKVISION': '2019-10-07',
            'DJI': '2020-12-18',
            'SMIC': '2020-12-18',
            'YMTC': '2022-12-15',
        }

        query = """
            SELECT
                t.document_id,
                t.contractor_name,
                t.award_date,
                t.value_total,
                t.iso_country,
                b.entity_name,
                b.reason_for_listing,
                b.date_added
            FROM ted_contracts_production t
            CROSS JOIN bis_entity_list b
            WHERE UPPER(t.contractor_name) LIKE '%' || UPPER(b.entity_name) || '%'
              AND b.country LIKE '%China%'
        """

        self.cur.execute(query)
        results = []

        for row in self.cur.fetchall():
            document_id, contractor, award_date, value, country, bis_entity, reason, date_added = row

            # Determine sanction date
            sanction_date = date_added
            if not sanction_date:
                # Try known dates
                for key, date in known_dates.items():
                    if key in bis_entity.upper():
                        sanction_date = date
                        break

            # Temporal analysis
            flag_type, description = self._classify_temporal_status(
                contract_date, sanction_date, bis_entity
            )

            result = {
                'contract_id': contract_id,
                'contractor': contractor,
                'contract_date': contract_date,
                'value': value,
                'country': country,
                'bis_entity': bis_entity,
                'reason': reason,
                'sanction_date': sanction_date,
                'flag_type': flag_type,
                'description': description
            }
            results.append(result)

        self._print_results('TED CONTRACTS', results)
        return results

    def analyze_openalex_collaborations(self):
        """Analyze research collaborations with temporal awareness"""
        print('=' * 80)
        print('OPENALEX RESEARCH - BIS ENTITY LIST CROSS-REFERENCE')
        print('=' * 80)

        query = """
            SELECT
                o.id,
                o.title,
                o.year,
                o.authors,
                o.institutions,
                b.entity_name,
                b.reason_for_listing,
                b.date_added
            FROM openalex_works o
            CROSS JOIN bis_entity_list b
            WHERE o.institutions LIKE '%' || b.entity_name || '%'
              AND b.country LIKE '%China%'
            LIMIT 100
        """

        self.cur.execute(query)
        results = []

        for row in self.cur.fetchall():
            work_id, title, year, authors, institutions, bis_entity, reason, date_added = row

            # Convert year to date string
            pub_date = f"{year}-01-01" if year else None

            flag_type, description = self._classify_temporal_status(
                pub_date, date_added, bis_entity
            )

            result = {
                'work_id': work_id,
                'title': title[:80] + '...' if title and len(title) > 80 else title,
                'year': year,
                'bis_entity': bis_entity,
                'reason': reason,
                'sanction_date': date_added,
                'flag_type': flag_type,
                'description': description
            }
            results.append(result)

        self._print_results('OPENALEX RESEARCH', results)
        return results

    def analyze_uspto_patents(self):
        """Analyze patents with temporal awareness"""
        print('=' * 80)
        print('USPTO PATENTS - BIS ENTITY LIST CROSS-REFERENCE')
        print('=' * 80)

        query = """
            SELECT
                p.patent_number,
                p.assignee_organization,
                p.grant_date,
                p.filing_date,
                b.entity_name,
                b.reason_for_listing,
                b.date_added
            FROM uspto_patents_chinese p
            CROSS JOIN bis_entity_list b
            WHERE p.assignee_organization LIKE '%' || b.entity_name || '%'
              AND b.country LIKE '%China%'
            LIMIT 100
        """

        try:
            self.cur.execute(query)
            results = []

            for row in self.cur.fetchall():
                patent_num, assignee, grant_date, filing_date, bis_entity, reason, date_added = row

                # Use filing date (when tech was developed)
                flag_type, description = self._classify_temporal_status(
                    filing_date, date_added, bis_entity
                )

                result = {
                    'patent_number': patent_num,
                    'assignee': assignee[:50] + '...' if assignee and len(assignee) > 50 else assignee,
                    'filing_date': filing_date,
                    'grant_date': grant_date,
                    'bis_entity': bis_entity,
                    'reason': reason,
                    'sanction_date': date_added,
                    'flag_type': flag_type,
                    'description': description
                }
                results.append(result)

            self._print_results('USPTO PATENTS', results)
            return results

        except Exception as e:
            print(f'[INFO] USPTO analysis skipped: {e}')
            return []

    def _classify_temporal_status(self, activity_date, sanction_date, entity_name):
        """
        Classify temporal relationship between activity and sanction

        Returns: (flag_type, description)
        """
        if not activity_date:
            return 'UNKNOWN_DATE', f'Activity date unknown - cannot determine if pre/post sanction'

        if not sanction_date:
            return 'SANCTION_DATE_UNKNOWN', f'BIS listing date for {entity_name} not available - manual verification required'

        try:
            act_dt = datetime.fromisoformat(activity_date.split('T')[0])
            sanc_dt = datetime.fromisoformat(sanction_date.split('T')[0])

            if act_dt < sanc_dt:
                years_before = (sanc_dt - act_dt).days / 365.25
                return 'HISTORICAL', f'Pre-sanction activity ({years_before:.1f} years before BIS listing) - Legitimate at time'

            elif act_dt > sanc_dt:
                years_after = (act_dt - sanc_dt).days / 365.25
                return 'POTENTIAL_VIOLATION', f'⚠️ Post-sanction activity ({years_after:.1f} years AFTER BIS listing) - Review required'

            else:
                return 'BOUNDARY', f'Activity on same date as BIS listing - Edge case requiring review'

        except Exception as e:
            return 'DATE_PARSE_ERROR', f'Could not parse dates: {e}'

    def _print_results(self, title, results):
        """Print analysis results"""
        print(f'\n{title}:')
        print(f'Total matches: {len(results)}')

        if not results:
            print('  (No matches found)')
            return

        # Breakdown by flag type
        flag_counts = {}
        for r in results:
            flag = r.get('flag_type', 'UNKNOWN')
            flag_counts[flag] = flag_counts.get(flag, 0) + 1

        print('\nBreakdown by temporal status:')
        for flag, count in sorted(flag_counts.items()):
            print(f'  {flag}: {count}')

        # Show sample violations (if any)
        violations = [r for r in results if r.get('flag_type') == 'POTENTIAL_VIOLATION']
        if violations:
            print(f'\n⚠️ POTENTIAL VIOLATIONS ({len(violations)}):')
            for v in violations[:5]:
                print(f"\n  Entity: {v.get('bis_entity')}")
                print(f"  Activity: {v.get('contract_id') or v.get('work_id') or v.get('patent_number')}")
                print(f"  Activity Date: {v.get('contract_date') or v.get('year') or v.get('filing_date')}")
                print(f"  Sanction Date: {v.get('sanction_date')}")
                print(f"  Status: {v.get('description')}")

        # Show sample historical (for context)
        historical = [r for r in results if r.get('flag_type') == 'HISTORICAL']
        if historical:
            print(f'\n✅ HISTORICAL (Pre-sanction) - Sample ({len(historical)} total):')
            for h in historical[:3]:
                print(f"\n  Entity: {h.get('bis_entity')}")
                print(f"  Activity: {h.get('contract_id') or h.get('work_id') or h.get('patent_number')}")
                print(f"  Status: {h.get('description')}")

    def generate_report(self):
        """Generate comprehensive cross-reference report"""
        print('=' * 80)
        print('BIS TEMPORAL CROSS-REFERENCE ANALYSIS')
        print('=' * 80)
        print()

        ted_results = self.analyze_ted_contracts()
        openalex_results = self.analyze_openalex_collaborations()
        uspto_results = self.analyze_uspto_patents()

        # Save to JSON
        report = {
            'generated_at': datetime.now().isoformat(),
            'ted_contracts': ted_results,
            'openalex_research': openalex_results,
            'uspto_patents': uspto_results,
            'summary': {
                'total_ted_matches': len(ted_results),
                'total_openalex_matches': len(openalex_results),
                'total_uspto_matches': len(uspto_results),
                'ted_violations': len([r for r in ted_results if r.get('flag_type') == 'POTENTIAL_VIOLATION']),
                'openalex_violations': len([r for r in openalex_results if r.get('flag_type') == 'POTENTIAL_VIOLATION']),
                'uspto_violations': len([r for r in uspto_results if r.get('flag_type') == 'POTENTIAL_VIOLATION']),
            }
        }

        output_file = OUTPUT_DIR / f"bis_cross_reference_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print('=' * 80)
        print('REPORT SUMMARY')
        print('=' * 80)
        for key, value in report['summary'].items():
            print(f'{key}: {value}')

        print(f'\n[OK] Full report saved: {output_file}')

    def close(self):
        self.conn.close()

def main():
    analyzer = BISTemporalAnalyzer()

    try:
        analyzer.generate_report()
    finally:
        analyzer.close()

if __name__ == '__main__':
    main()
