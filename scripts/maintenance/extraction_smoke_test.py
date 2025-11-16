#!/usr/bin/env python3
"""
Entity & Technology Extraction Smoke Test
==========================================
Validate extraction quality for 3 representative reports (AI, space, semiconductors).
Check deduplication, risk levels, and data quality.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

class ExtractionSmokeTest:
    def __init__(self, db_path="F:/OSINT_WAREHOUSE/osint_master.db"):
        self.db_path = db_path
        self.results = {
            'test_date': datetime.now().isoformat(),
            'reports_tested': [],
            'overall_status': 'PENDING',
            'issues': [],
            'recommendations': []
        }

    def run_test(self):
        """Run comprehensive smoke test."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        print("="*80)
        print("ENTITY & TECHNOLOGY EXTRACTION SMOKE TEST")
        print("="*80)

        # Get sample reports with actual extractions
        # Use reports known to have entity/technology extractions
        target_reports = [
            (15, 'ai_ml'),      # CSET - AI on the Edge of Space
            (21, 'semiconductors'),  # CSET - EUV in China's Semiconductor Ecosystem
            (23, 'space')       # 2024 DoD Arctic Strategy
        ]

        for report_id, topic in target_reports:
            cursor.execute('''
                SELECT title FROM thinktank_reports WHERE report_id = ?
            ''', (report_id,))

            result = cursor.fetchone()
            if result:
                title = result[0]
                print(f"\n[{report_id}] Testing {topic.upper()}: {title}")
                print("-"*80)

                report_result = self.test_report(cursor, report_id, title, topic)
                self.results['reports_tested'].append(report_result)

        # Run deduplication checks
        print("\n" + "="*80)
        print("DEDUPLICATION CHECK")
        print("="*80)
        self.test_deduplication(cursor)

        # Risk assessment
        print("\n" + "="*80)
        print("RISK ASSESSMENT")
        print("="*80)
        self.test_risk_levels(cursor)

        conn.close()

        # Overall assessment
        self.assess_overall_status()

        return self.results

    def test_report(self, cursor, report_id, title, topic):
        """Test extraction for a single report."""
        result = {
            'report_id': report_id,
            'title': title,
            'topic': topic,
            'stats': {},
            'samples': {},
            'issues': []
        }

        # Count entities
        cursor.execute('''
            SELECT COUNT(*), COUNT(DISTINCT entity_name)
            FROM report_entities
            WHERE report_id = ?
        ''', (report_id,))
        entity_count, unique_entities = cursor.fetchone()
        result['stats']['entities'] = {
            'total': entity_count,
            'unique': unique_entities
        }

        # Count technologies
        cursor.execute('''
            SELECT COUNT(*), COUNT(DISTINCT specific_technology)
            FROM report_technologies
            WHERE report_id = ?
        ''', (report_id,))
        tech_count, unique_techs = cursor.fetchone()
        result['stats']['technologies'] = {
            'total': tech_count,
            'unique': unique_techs
        }

        # Count risk indicators
        cursor.execute('''
            SELECT COUNT(*)
            FROM report_risk_indicators
            WHERE report_id = ?
        ''', (report_id,))
        risk_count = cursor.fetchone()[0]
        result['stats']['risk_indicators'] = risk_count

        print(f"  Entities: {entity_count} total, {unique_entities} unique")
        print(f"  Technologies: {tech_count} total, {unique_techs} unique")
        print(f"  Risk Indicators: {risk_count}")

        # Quality checks
        if entity_count == 0:
            issue = f"No entities extracted from {title}"
            result['issues'].append(issue)
            self.results['issues'].append(issue)
            print(f"  [WARN] No entities extracted")

        if tech_count == 0:
            issue = f"No technologies extracted from {title}"
            result['issues'].append(issue)
            self.results['issues'].append(issue)
            print(f"  [WARN] No technologies extracted")

        if risk_count == 0:
            print(f"  [INFO] No risk indicators")

        # Sample entities
        cursor.execute('''
            SELECT entity_name, entity_type, confidence
            FROM report_entities
            WHERE report_id = ?
            ORDER BY confidence DESC
            LIMIT 3
        ''', (report_id,))

        result['samples']['entities'] = []
        for ent_name, ent_type, conf in cursor.fetchall():
            result['samples']['entities'].append({
                'name': ent_name,
                'type': ent_type,
                'confidence': conf
            })
            print(f"    Entity: {ent_name[:40]} ({ent_type}) conf={conf:.2f}")

        # Sample technologies
        cursor.execute('''
            SELECT technology_category, specific_technology, dual_use_flag
            FROM report_technologies
            WHERE report_id = ?
            LIMIT 3
        ''', (report_id,))

        result['samples']['technologies'] = []
        for tech_cat, tech_spec, dual_use in cursor.fetchall():
            result['samples']['technologies'].append({
                'category': tech_cat,
                'specific': tech_spec,
                'dual_use': bool(dual_use)
            })
            dual_str = '[DUAL-USE]' if dual_use else ''
            print(f"    Tech: {tech_cat} - {tech_spec[:35]} {dual_str}")

        return result

    def test_deduplication(self, cursor):
        """Test entity deduplication across reports."""
        # Check for duplicate entities
        cursor.execute('''
            SELECT entity_name, COUNT(DISTINCT report_id) as report_count
            FROM report_entities
            GROUP BY entity_name
            HAVING report_count > 1
            ORDER BY report_count DESC
            LIMIT 10
        ''')

        dupes = cursor.fetchall()
        if dupes:
            print(f"\nEntities appearing in multiple reports: {len(dupes)}")
            for entity, count in dupes[:5]:
                print(f"  - {entity}: {count} reports")
            self.results['deduplication'] = {
                'cross_report_entities': len(dupes),
                'top_shared': [(e, c) for e, c in dupes[:5]]
            }
        else:
            print("\n[OK] No cross-report entity duplication")
            self.results['deduplication'] = {'cross_report_entities': 0}

    def test_risk_levels(self, cursor):
        """Test risk indicator distribution."""
        cursor.execute('''
            SELECT severity, COUNT(*) as count
            FROM report_risk_indicators
            GROUP BY severity
        ''')

        risk_dist = cursor.fetchall()
        if risk_dist:
            print("\nRisk Severity Distribution:")
            self.results['risk_distribution'] = {}
            for severity, count in risk_dist:
                print(f"  {severity}: {count} indicators")
                self.results['risk_distribution'][severity] = count
        else:
            print("\n[INFO] No risk indicators in tested reports")
            self.results['risk_distribution'] = {}

    def assess_overall_status(self):
        """Assess overall test status."""
        total_issues = len(self.results['issues'])

        if total_issues == 0:
            self.results['overall_status'] = 'PASS'
            print("\n" + "="*80)
            print("[PASS] All smoke tests passed")
            print("="*80)
        elif total_issues <= 2:
            self.results['overall_status'] = 'PASS_WITH_WARNINGS'
            print("\n" + "="*80)
            print(f"[PASS] Tests passed with {total_issues} warnings")
            print("="*80)
        else:
            self.results['overall_status'] = 'FAIL'
            print("\n" + "="*80)
            print(f"[FAIL] Tests failed with {total_issues} issues")
            print("="*80)

        if self.results['issues']:
            print("\nIssues found:")
            for issue in self.results['issues']:
                print(f"  - {issue}")


def main():
    """Run smoke test."""
    tester = ExtractionSmokeTest()
    results = tester.run_test()

    # Save results
    output_path = Path("analysis/extraction_smoke_test_results.json")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n[OK] Results saved to: {output_path}")
    print(f"\nOverall Status: {results['overall_status']}")

if __name__ == "__main__":
    main()
