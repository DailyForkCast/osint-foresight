#!/usr/bin/env python3
"""
Report Metadata Enrichment Tool
================================

Backfill and enrich existing thinktank_reports metadata:
- Add missing URLs (canonical and download)
- Normalize publisher names
- Fill missing publication dates
- Add missing page counts
- Validate and flag incomplete records

Usage:
  python enrich_report_metadata.py --auto     # Automatic enrichment
  python enrich_report_metadata.py --manual   # Manual review mode
  python enrich_report_metadata.py --report   # Generate quality report only
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
import argparse
import re
from typing import Dict, List, Optional

class ReportEnricher:
    """Enrich thinktank_reports metadata."""

    def __init__(self, db_path: str = "F:/OSINT_WAREHOUSE/osint_master.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

        # Known publisher name mappings (for normalization)
        self.publisher_mappings = {
            'CSET': 'Center for Security and Emerging Technology',
            'DoD': 'U.S. Department of Defense',
            'DOD': 'U.S. Department of Defense',
            'Department of Defense': 'U.S. Department of Defense',
        }

        # Known URL patterns by publisher
        self.url_patterns = {
            'Center for Security and Emerging Technology': 'https://cset.georgetown.edu/publication/{slug}/',
            'U.S. Department of Defense': 'https://www.defense.gov/News/Releases/',
        }

    def connect(self):
        """Connect to database."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def generate_quality_report(self) -> Dict:
        """Generate comprehensive quality report."""
        self.connect()

        report = {
            'generated_at': datetime.now().isoformat(),
            'total_reports': 0,
            'missing_metadata': {},
            'publisher_distribution': {},
            'date_coverage': {},
            'recommendations': []
        }

        # Total reports
        self.cursor.execute('SELECT COUNT(*) FROM thinktank_reports')
        report['total_reports'] = self.cursor.fetchone()[0]

        # Missing metadata counts
        fields = ['url_canonical', 'url_download', 'publication_date_iso', 'pages', 'publisher_org']
        for field in fields:
            self.cursor.execute(f'''
                SELECT COUNT(*)
                FROM thinktank_reports
                WHERE {field} IS NULL OR {field} = '' OR {field} = 'None'
            ''')
            missing = self.cursor.fetchone()[0]
            report['missing_metadata'][field] = {
                'missing_count': missing,
                'percentage': (missing / report['total_reports'] * 100) if report['total_reports'] > 0 else 0
            }

        # Publisher distribution
        self.cursor.execute('''
            SELECT publisher_org, COUNT(*) as count
            FROM thinktank_reports
            GROUP BY publisher_org
            ORDER BY count DESC
        ''')
        for pub, count in self.cursor.fetchall():
            report['publisher_distribution'][pub or 'None'] = count

        # Date coverage
        self.cursor.execute('''
            SELECT strftime('%Y', publication_date_iso) as year, COUNT(*) as count
            FROM thinktank_reports
            WHERE publication_date_iso IS NOT NULL
            GROUP BY year
            ORDER BY year DESC
        ''')
        for year, count in self.cursor.fetchall():
            report['date_coverage'][year] = count

        # Generate recommendations
        if report['missing_metadata']['url_canonical']['missing_count'] > 0:
            report['recommendations'].append({
                'priority': 'CRITICAL',
                'issue': 'Missing canonical URLs',
                'count': report['missing_metadata']['url_canonical']['missing_count'],
                'action': 'Add source URLs for citation tracking'
            })

        if report['missing_metadata']['publication_date_iso']['missing_count'] > 0:
            report['recommendations'].append({
                'priority': 'HIGH',
                'issue': 'Missing publication dates',
                'count': report['missing_metadata']['publication_date_iso']['missing_count'],
                'action': 'Extract dates from PDF metadata or filenames'
            })

        if 'None' in report['publisher_distribution']:
            report['recommendations'].append({
                'priority': 'HIGH',
                'issue': 'Reports with null publishers',
                'count': report['publisher_distribution']['None'],
                'action': 'Identify publishers from file metadata or content'
            })

        self.close()
        return report

    def normalize_publishers(self, dry_run: bool = True) -> List[Dict]:
        """Normalize publisher names."""
        self.connect()

        updates = []

        for old_name, new_name in self.publisher_mappings.items():
            self.cursor.execute('''
                SELECT report_id, title, publisher_org
                FROM thinktank_reports
                WHERE publisher_org LIKE ?
            ''', (f'%{old_name}%',))

            for report_id, title, current_pub in self.cursor.fetchall():
                updates.append({
                    'report_id': report_id,
                    'title': title[:60],
                    'old_publisher': current_pub,
                    'new_publisher': new_name
                })

                if not dry_run:
                    self.cursor.execute('''
                        UPDATE thinktank_reports
                        SET publisher_org = ?,
                            updated_at = ?
                        WHERE report_id = ?
                    ''', (new_name, datetime.now().isoformat(), report_id))

        if not dry_run:
            self.conn.commit()

        self.close()
        return updates

    def add_missing_urls(self, url_mappings: Dict[int, Dict], dry_run: bool = True) -> int:
        """Add missing URLs based on provided mappings."""
        self.connect()

        count = 0
        for report_id, urls in url_mappings.items():
            canonical = urls.get('canonical')
            download = urls.get('download')

            if canonical or download:
                if not dry_run:
                    update_parts = []
                    params = []

                    if canonical:
                        update_parts.append('url_canonical = ?')
                        params.append(canonical)
                    if download:
                        update_parts.append('url_download = ?')
                        params.append(download)

                    update_parts.append('updated_at = ?')
                    params.append(datetime.now().isoformat())
                    params.append(report_id)

                    self.cursor.execute(f'''
                        UPDATE thinktank_reports
                        SET {', '.join(update_parts)}
                        WHERE report_id = ?
                    ''', params)

                count += 1

        if not dry_run:
            self.conn.commit()

        self.close()
        return count

    def infer_metadata_from_titles(self, dry_run: bool = True) -> List[Dict]:
        """Infer publisher and topic from abbreviated titles."""
        self.connect()

        inferences = []

        # Get reports with abbreviated titles and null publishers
        self.cursor.execute('''
            SELECT report_id, title, hash_sha256
            FROM thinktank_reports
            WHERE (publisher_org IS NULL OR publisher_org = 'None')
              AND title IS NOT NULL
        ''')

        for report_id, title, hash_val in self.cursor.fetchall():
            # Pattern: "AuthorName TopicKeyword"
            parts = title.split()

            if len(parts) >= 2:
                author_name = parts[0]
                topic_keywords = ' '.join(parts[1:])

                # Infer publisher based on common patterns
                inferred_publisher = None

                # Check if it looks like a CSET report (common author names)
                if any(name in author_name for name in ['Swope', 'Shivakumar', 'Allen', 'Jensen']):
                    inferred_publisher = 'Center for Security and Emerging Technology'

                if inferred_publisher:
                    inferences.append({
                        'report_id': report_id,
                        'title': title,
                        'hash': hash_val[:16],
                        'inferred_publisher': inferred_publisher,
                        'confidence': 'medium'
                    })

                    if not dry_run:
                        self.cursor.execute('''
                            UPDATE thinktank_reports
                            SET source_organization = ?,
                                publisher_org = ?,
                                updated_at = ?
                            WHERE report_id = ?
                        ''', (inferred_publisher, inferred_publisher, datetime.now().isoformat(), report_id))

        if not dry_run:
            self.conn.commit()

        self.close()
        return inferences

    def extract_dates_from_filenames(self, dry_run: bool = True) -> int:
        """Extract publication dates from title patterns if present."""
        self.connect()

        count = 0

        # Get reports missing dates
        self.cursor.execute('''
            SELECT report_id, title, created_at
            FROM thinktank_reports
            WHERE publication_date_iso IS NULL
        ''')

        for report_id, title, created_at in self.cursor.fetchall():
            # Try to extract year from title or created_at
            year_match = re.search(r'\b(20\d{2})\b', title or '')

            if year_match:
                year = int(year_match.group(1))
                pub_date = f"{year}-01-01"  # Default to January 1st

                if not dry_run:
                    self.cursor.execute('''
                        UPDATE thinktank_reports
                        SET publication_date_iso = ?,
                            updated_at = ?
                        WHERE report_id = ?
                    ''', (pub_date, datetime.now().isoformat(), report_id))

                count += 1

            elif created_at:
                # Use created_at as fallback
                pub_date = created_at.split('T')[0]  # Extract date part

                if not dry_run:
                    self.cursor.execute('''
                        UPDATE thinktank_reports
                        SET publication_date_iso = ?,
                            updated_at = ?
                        WHERE report_id = ?
                    ''', (pub_date, datetime.now().isoformat(), report_id))

                count += 1

        if not dry_run:
            self.conn.commit()

        self.close()
        return count

    def run_automatic_enrichment(self) -> Dict:
        """Run all automatic enrichment steps."""
        results = {
            'started_at': datetime.now().isoformat(),
            'steps': []
        }

        # Step 1: Normalize publishers
        print("\n[1/3] Normalizing publisher names...")
        publisher_updates = self.normalize_publishers(dry_run=False)
        results['steps'].append({
            'step': 'normalize_publishers',
            'updates': len(publisher_updates),
            'details': publisher_updates
        })
        print(f"  [OK] Updated {len(publisher_updates)} publisher names")

        # Step 2: Infer metadata from titles
        print("\n[2/3] Inferring metadata from titles...")
        inferences = self.infer_metadata_from_titles(dry_run=False)
        results['steps'].append({
            'step': 'infer_from_titles',
            'updates': len(inferences),
            'details': inferences
        })
        print(f"  [OK] Inferred metadata for {len(inferences)} reports")

        # Step 3: Extract dates
        print("\n[3/3] Extracting publication dates...")
        date_updates = self.extract_dates_from_filenames(dry_run=False)
        results['steps'].append({
            'step': 'extract_dates',
            'updates': date_updates
        })
        print(f"  [OK] Added {date_updates} publication dates")

        results['completed_at'] = datetime.now().isoformat()
        return results


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(description='Enrich thinktank_reports metadata')
    parser.add_argument('--auto', action='store_true', help='Run automatic enrichment')
    parser.add_argument('--report', action='store_true', help='Generate quality report only')
    parser.add_argument('--output', default='analysis/report_enrichment_results.json', help='Output file path')

    args = parser.parse_args()

    enricher = ReportEnricher()

    if args.report or (not args.auto):
        # Generate quality report
        print("="*80)
        print("REPORT METADATA QUALITY REPORT")
        print("="*80)

        report = enricher.generate_quality_report()

        print(f"\nTotal reports: {report['total_reports']}")
        print("\nMissing Metadata:")
        for field, stats in report['missing_metadata'].items():
            status = "[CRITICAL]" if stats['percentage'] > 50 else "[WARN]" if stats['percentage'] > 20 else "[OK]"
            print(f"  {status} {field:25s}: {stats['missing_count']:2d}/{report['total_reports']} ({stats['percentage']:5.1f}%)")

        print("\nPublisher Distribution:")
        for pub, count in report['publisher_distribution'].items():
            print(f"  {pub:40s}: {count:2d}")

        print("\nRecommendations:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"\n  [{i}] {rec['priority']} - {rec['issue']}")
            print(f"      Count: {rec['count']}")
            print(f"      Action: {rec['action']}")

        # Save report
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n[OK] Quality report saved to: {output_path}")

    if args.auto:
        # Run automatic enrichment
        print("\n" + "="*80)
        print("AUTOMATIC METADATA ENRICHMENT")
        print("="*80)

        results = enricher.run_automatic_enrichment()

        print("\n" + "="*80)
        print("ENRICHMENT COMPLETE")
        print("="*80)

        total_updates = sum(step.get('updates', 0) for step in results['steps'])
        print(f"\nTotal updates: {total_updates}")

        for step in results['steps']:
            print(f"\n{step['step']}:")
            print(f"  Updates: {step.get('updates', 0)}")

        # Save results
        results_path = Path(args.output).parent / "enrichment_execution_log.json"
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n[OK] Enrichment log saved to: {results_path}")


if __name__ == "__main__":
    main()
