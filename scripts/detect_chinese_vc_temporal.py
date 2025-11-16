#!/usr/bin/env python3
"""
detect_chinese_vc_temporal.py - Temporal Analysis of Chinese VC in Form D (2015-2025)

10-Year Trend Analysis:
- Chinese VC involvement patterns over 40 quarters
- Dual-use technology sector analysis
- Geographic distribution changes
- Investment volume trends

SECURITY: NO .CN ACCESS - US/EU sources only

Last Updated: 2025-10-22
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class ChineseVCTemporalAnalyzer:
    """Analyze 10 years of Chinese VC trends in Form D filings"""

    def __init__(self, db_path='F:/OSINT_WAREHOUSE/osint_master.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        # Load reference database
        ref_db_path = Path('data/chinese_vc_reference_database.json')
        with open(ref_db_path, 'r', encoding='utf-8') as f:
            self.ref_db = json.load(f)

        self.detection_patterns = self.ref_db['detection_patterns']

        print("="*70)
        print("CHINESE VC TEMPORAL ANALYSIS (2015 Q3 - 2025 Q2)")
        print("="*70)
        print(f"Database: {db_path}")
        print(f"Analysis period: 10 years (40 quarters)")
        print("="*70)

    def get_all_quarters(self):
        """Get list of all quarters in database"""
        self.cursor.execute("""
            SELECT DISTINCT collected_quarter
            FROM sec_form_d_offerings
            WHERE collected_quarter IS NOT NULL
            ORDER BY collected_quarter
        """)
        return [row[0] for row in self.cursor.fetchall()]

    def detect_china_links_by_quarter(self):
        """Detect China-linked offerings for each quarter"""
        print("\\n" + "="*70)
        print("RUNNING DETECTION ACROSS ALL QUARTERS")
        print("="*70)

        quarters = self.get_all_quarters()
        results_by_quarter = {}

        china_cities = self.detection_patterns['mainland_china_cities']
        hk_indicators = self.detection_patterns['hong_kong_indicators']
        all_locations = china_cities + hk_indicators

        for quarter in quarters:
            print(f"\\r-> Processing {quarter}...", end='', flush=True)

            # Count China-linked offerings by address
            china_linked = 0
            china_capital = 0

            for location in all_locations:
                self.cursor.execute("""
                    SELECT COUNT(DISTINCT o.accession_number),
                           SUM(o.total_offering_amount)
                    FROM sec_form_d_persons p
                    JOIN sec_form_d_offerings o ON p.accession_number = o.accession_number
                    WHERE (
                        p.person_address_city LIKE ?
                        OR p.person_address_state LIKE ?
                    )
                    AND o.collected_quarter = ?
                """, (f'%{location}%', f'%{location}%', quarter))

                row = self.cursor.fetchone()
                if row[0]:
                    china_linked += row[0]
                    china_capital += (row[1] or 0)

            # Get total offerings for this quarter
            self.cursor.execute("""
                SELECT COUNT(*), SUM(total_offering_amount)
                FROM sec_form_d_offerings
                WHERE collected_quarter = ?
            """, (quarter,))

            total_offerings, total_capital = self.cursor.fetchone()

            results_by_quarter[quarter] = {
                'china_linked_count': china_linked,
                'china_linked_capital': china_capital,
                'total_offerings': total_offerings,
                'total_capital': total_capital or 0,
                'percentage': (china_linked / total_offerings * 100) if total_offerings else 0
            }

        print(f"\\n[OK] Detection complete across {len(quarters)} quarters")
        return results_by_quarter

    def analyze_dual_use_sectors(self):
        """Analyze China-linked deals in dual-use technology sectors"""
        print("\\n" + "="*70)
        print("DUAL-USE TECHNOLOGY SECTOR ANALYSIS")
        print("="*70)

        high_risk_sectors = self.detection_patterns['high_risk_sectors_dual_use']

        sector_results = {}
        quarters = self.get_all_quarters()

        for sector in high_risk_sectors:
            print(f"\\r-> Analyzing {sector}...", end='', flush=True)

            sector_data = {}
            for quarter in quarters:
                # Count China-linked offerings in this sector
                self.cursor.execute("""
                    SELECT COUNT(DISTINCT o.accession_number), SUM(o.total_offering_amount)
                    FROM sec_form_d_offerings o
                    JOIN sec_form_d_persons p ON o.accession_number = p.accession_number
                    WHERE o.industry_group_type LIKE ?
                    AND (
                        p.person_address_state LIKE '%Hong Kong%'
                        OR p.person_address_state LIKE '%China%'
                        OR p.person_address_city IN ('Beijing', 'Shanghai', 'Shenzhen', 'Hong Kong')
                    )
                    AND o.collected_quarter = ?
                """, (f'%{sector}%', quarter))

                count, capital = self.cursor.fetchone()
                if count and count > 0:
                    sector_data[quarter] = {
                        'count': count,
                        'capital': capital or 0
                    }

            if sector_data:
                sector_results[sector] = sector_data

        print(f"\\n[OK] Found {len(sector_results)} dual-use sectors with China links")
        return sector_results

    def calculate_trends(self, results_by_quarter):
        """Calculate multi-year trends"""
        print("\\n" + "="*70)
        print("TREND ANALYSIS")
        print("="*70)

        # Group by year
        by_year = defaultdict(lambda: {'count': 0, 'capital': 0, 'total': 0})

        for quarter, data in results_by_quarter.items():
            year = quarter[:4]
            by_year[year]['count'] += data['china_linked_count']
            by_year[year]['capital'] += data['china_linked_capital']
            by_year[year]['total'] += data['total_offerings']

        # Calculate year-over-year growth
        years = sorted(by_year.keys())
        trends = {}

        for i, year in enumerate(years):
            yoy_growth = None
            if i > 0:
                prev_year = years[i-1]
                prev_count = by_year[prev_year]['count']
                curr_count = by_year[year]['count']
                if prev_count > 0:
                    yoy_growth = ((curr_count - prev_count) / prev_count) * 100

            trends[year] = {
                'count': by_year[year]['count'],
                'capital': by_year[year]['capital'],
                'total_offerings': by_year[year]['total'],
                'percentage': (by_year[year]['count'] / by_year[year]['total'] * 100) if by_year[year]['total'] else 0,
                'yoy_growth': yoy_growth
            }

        return trends

    def generate_report(self, quarterly_results, sector_results, trends):
        """Generate comprehensive temporal analysis report"""
        print("\\n" + "="*70)
        print("GENERATING TEMPORAL ANALYSIS REPORT")
        print("="*70)

        report = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'period': '2015 Q3 - 2025 Q2',
                'total_quarters': len(quarterly_results),
                'methodology': 'Address-based detection (mainland China + Hong Kong)',
                'data_sources': self.ref_db['metadata']['sources']
            },
            'summary': {
                'total_form_d_filings': sum(q['total_offerings'] for q in quarterly_results.values()),
                'total_china_linked': sum(q['china_linked_count'] for q in quarterly_results.values()),
                'total_capital_flagged': sum(q['china_linked_capital'] for q in quarterly_results.values()),
                'average_percentage': sum(q['percentage'] for q in quarterly_results.values()) / len(quarterly_results)
            },
            'quarterly_data': quarterly_results,
            'annual_trends': trends,
            'dual_use_sectors': sector_results
        }

        # Save report
        output_path = Path('analysis/chinese_vc_temporal_analysis_2015_2025.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\\n[OK] Report saved: {output_path}")

        # Print summary
        print("\\n" + "="*70)
        print("10-YEAR SUMMARY")
        print("="*70)
        print(f"Total Form D filings:     {report['summary']['total_form_d_filings']:,}")
        print(f"China-linked filings:     {report['summary']['total_china_linked']:,}")
        print(f"Average percentage:       {report['summary']['average_percentage']:.2f}%")
        print(f"Total capital flagged:    ${report['summary']['total_capital_flagged']:,.0f}")

        print("\\n" + "="*70)
        print("ANNUAL TRENDS")
        print("="*70)

        for year in sorted(trends.keys()):
            t = trends[year]
            yoy = f" ({t['yoy_growth']:+.1f}% YoY)" if t['yoy_growth'] is not None else ""
            print(f"{year}: {t['count']:>4,} matches | {t['percentage']:>5.2f}% of filings{yoy}")

        print("="*70)

        return report

    def run_full_analysis(self):
        """Run complete temporal analysis"""
        print(f"\\nStarting temporal analysis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Run detection across all quarters
        quarterly_results = self.detect_china_links_by_quarter()

        # Analyze dual-use sectors
        sector_results = self.analyze_dual_use_sectors()

        # Calculate trends
        trends = self.calculate_trends(quarterly_results)

        # Generate report
        report = self.generate_report(quarterly_results, sector_results, trends)

        return report


def main():
    """Run temporal analysis"""
    analyzer = ChineseVCTemporalAnalyzer()
    report = analyzer.run_full_analysis()

    print("\\n" + "="*70)
    print("TEMPORAL ANALYSIS COMPLETE")
    print("="*70)
    print(f"Quarters analyzed: {report['metadata']['total_quarters']}")
    print(f"Report: analysis/chinese_vc_temporal_analysis_2015_2025.json")
    print("="*70)


if __name__ == '__main__':
    main()
