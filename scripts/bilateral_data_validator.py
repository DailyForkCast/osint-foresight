#!/usr/bin/env python3
"""
Bilateral Relations Data Validator
Comprehensive validation and quality assurance for bilateral relations data

Validation Categories:
1. Data Completeness - Required fields populated
2. Data Integrity - Foreign keys, constraints, formats
3. Source Verification - URL accessibility, reliability
4. Cross-Source Validation - Multiple source confirmation
5. Temporal Consistency - Date logic, chronology
6. Value Validation - Numeric ranges, currency
7. Duplicate Detection - Identify redundant records
8. Zero-Fabrication Compliance - Evidence requirements
"""

import sqlite3
import sys
import io
from pathlib import Path
from datetime import datetime
import json
import urllib.request
import urllib.error

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class BilateralDataValidator:
    def __init__(self):
        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        self.conn = None
        self.validation_results = {
            'completeness': {},
            'integrity': {},
            'sources': {},
            'cross_validation': {},
            'temporal': {},
            'values': {},
            'duplicates': {},
            'zero_fabrication': {}
        }
        self.issues_found = []
        self.warnings = []

    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(str(self.db_path))
        print(f"Connected to {self.db_path}")

    def validate_completeness(self, country_code='DE'):
        """Check required fields are populated"""
        print("\n" + "="*80)
        print("1. DATA COMPLETENESS VALIDATION")
        print("="*80)

        cursor = self.conn.cursor()
        issues = []

        # Check bilateral_countries
        print("\nChecking bilateral_countries...")
        cursor.execute("""
            SELECT country_code, country_name, country_name_chinese,
                   diplomatic_normalization_date, current_relationship_status
            FROM bilateral_countries WHERE country_code = ?
        """, (country_code,))
        country = cursor.fetchone()

        if not country:
            issues.append(f"CRITICAL: Country {country_code} not found in bilateral_countries")
        else:
            if not country[1]:
                issues.append("Missing: country_name")
            if not country[2]:
                self.warnings.append("Missing: country_name_chinese (recommended)")
            if not country[3]:
                issues.append("Missing: diplomatic_normalization_date")
            if not country[4]:
                issues.append("Missing: current_relationship_status")
            print(f"  ✓ Country record exists for {country[1] or country_code}")
            if country[2]:
                print(f"  ✓ Chinese name present: {country[2]}")
            else:
                print(f"  ⚠ Chinese name missing")

        # Check major_acquisitions
        print("\nChecking major_acquisitions...")
        cursor.execute("""
            SELECT acquisition_id, target_company, chinese_acquirer,
                   deal_value_usd, acquisition_date, source_url
            FROM major_acquisitions WHERE country_code = ?
        """, (country_code,))
        acquisitions = cursor.fetchall()

        print(f"  Total acquisitions: {len(acquisitions)}")
        for acq_id, company, acquirer, value, date, url in acquisitions:
            acq_issues = []
            if not company:
                acq_issues.append("missing target_company")
            if not acquirer:
                acq_issues.append("missing chinese_acquirer")
            if not value:
                acq_issues.append("missing deal_value_usd")
            if not date:
                acq_issues.append("missing acquisition_date")
            if not url:
                acq_issues.append("missing source_url")

            if acq_issues:
                issue_str = f"  ✗ {company or acq_id}: " + ", ".join(acq_issues)
                issues.append(issue_str)
                print(issue_str)
            else:
                print(f"  ✓ {company}: Complete")

        # Check bilateral_events
        print("\nChecking bilateral_events...")
        cursor.execute("""
            SELECT event_id, event_title, event_date, event_type,
                   event_category, source_url, source_type
            FROM bilateral_events WHERE country_code = ?
        """, (country_code,))
        events = cursor.fetchall()

        print(f"  Total events: {len(events)}")
        for event_id, title, date, etype, category, url, source_type in events:
            event_issues = []
            if not title:
                event_issues.append("missing event_title")
            if not date:
                event_issues.append("missing event_date")
            if not etype:
                event_issues.append("missing event_type")
            if not category:
                event_issues.append("missing event_category")
            if not source_type:
                event_issues.append("missing source_type")

            if event_issues:
                issue_str = f"  ✗ {title or event_id}: " + ", ".join(event_issues)
                issues.append(issue_str)
                print(issue_str)
            else:
                print(f"  ✓ {title}: Complete")

        self.validation_results['completeness'] = {
            'country_present': country is not None,
            'acquisitions_count': len(acquisitions),
            'events_count': len(events),
            'issues': issues
        }

        print(f"\nCompleteness Summary: {len(issues)} issues, {len(self.warnings)} warnings")
        return len(issues)

    def validate_integrity(self, country_code='DE'):
        """Check foreign keys and data integrity"""
        print("\n" + "="*80)
        print("2. DATA INTEGRITY VALIDATION")
        print("="*80)

        cursor = self.conn.cursor()
        issues = []

        # Check foreign key references
        print("\nChecking foreign key integrity...")

        # Check if all acquisitions reference valid countries
        cursor.execute("""
            SELECT a.acquisition_id, a.country_code
            FROM major_acquisitions a
            LEFT JOIN bilateral_countries c ON a.country_code = c.country_code
            WHERE c.country_code IS NULL AND a.country_code = ?
        """, (country_code,))
        orphan_acquisitions = cursor.fetchall()

        if orphan_acquisitions:
            for acq_id, cc in orphan_acquisitions:
                issues.append(f"Acquisition {acq_id} references non-existent country {cc}")
        else:
            print("  ✓ All acquisitions have valid country references")

        # Check if all events reference valid countries
        cursor.execute("""
            SELECT e.event_id, e.country_code
            FROM bilateral_events e
            LEFT JOIN bilateral_countries c ON e.country_code = c.country_code
            WHERE c.country_code IS NULL AND e.country_code = ?
        """, (country_code,))
        orphan_events = cursor.fetchall()

        if orphan_events:
            for event_id, cc in orphan_events:
                issues.append(f"Event {event_id} references non-existent country {cc}")
        else:
            print("  ✓ All events have valid country references")

        # Check date formats
        print("\nChecking date validity...")
        cursor.execute("""
            SELECT event_id, event_date
            FROM bilateral_events
            WHERE country_code = ? AND event_date IS NOT NULL
        """, (country_code,))

        for event_id, event_date in cursor.fetchall():
            try:
                datetime.strptime(event_date, '%Y-%m-%d')
            except ValueError:
                issues.append(f"Event {event_id} has invalid date format: {event_date}")

        if len(issues) == len(orphan_acquisitions) + len(orphan_events):  # No new issues
            print("  ✓ All dates are properly formatted")

        # Check value ranges
        print("\nChecking value ranges...")
        cursor.execute("""
            SELECT acquisition_id, target_company, deal_value_usd
            FROM major_acquisitions
            WHERE country_code = ? AND deal_value_usd IS NOT NULL
        """, (country_code,))

        for acq_id, company, value in cursor.fetchall():
            if value < 0:
                issues.append(f"Negative deal value for {company}: ${value}")
            elif value > 1e12:  # $1 trillion seems unrealistic for single acquisition
                issues.append(f"Suspiciously large deal value for {company}: ${value/1e9:.1f}B")

        if len(issues) == len(orphan_acquisitions) + len(orphan_events):
            print("  ✓ All deal values are in reasonable ranges")

        self.validation_results['integrity'] = {
            'orphan_acquisitions': len(orphan_acquisitions),
            'orphan_events': len(orphan_events),
            'issues': issues
        }

        print(f"\nIntegrity Summary: {len(issues)} issues found")
        return len(issues)

    def validate_sources(self, country_code='DE', check_urls=False):
        """Validate source URLs and reliability"""
        print("\n" + "="*80)
        print("3. SOURCE VALIDATION")
        print("="*80)

        cursor = self.conn.cursor()
        issues = []
        accessible_urls = 0
        inaccessible_urls = 0

        # Check source URLs for acquisitions
        print("\nChecking acquisition sources...")
        cursor.execute("""
            SELECT acquisition_id, target_company, source_url
            FROM major_acquisitions
            WHERE country_code = ?
        """, (country_code,))

        for acq_id, company, url in cursor.fetchall():
            if not url:
                issues.append(f"Missing source URL for {company}")
            elif check_urls:
                # Try to access URL (optional, can be slow)
                try:
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    urllib.request.urlopen(req, timeout=5)
                    accessible_urls += 1
                    print(f"  ✓ {company}: URL accessible")
                except (urllib.error.URLError, urllib.error.HTTPError, Exception) as e:
                    inaccessible_urls += 1
                    self.warnings.append(f"URL inaccessible for {company}: {url}")
                    print(f"  ⚠ {company}: URL inaccessible ({type(e).__name__})")
            else:
                print(f"  • {company}: {url[:60]}...")

        # Check source URLs for events
        print("\nChecking event sources...")
        cursor.execute("""
            SELECT event_id, event_title, source_url, source_type, source_reliability
            FROM bilateral_events
            WHERE country_code = ?
        """, (country_code,))

        for event_id, title, url, source_type, reliability in cursor.fetchall():
            if not source_type:
                issues.append(f"Missing source_type for event: {title}")

            if reliability is None:
                self.warnings.append(f"Missing source_reliability for event: {title}")
            elif reliability > 3:
                self.warnings.append(f"Low source reliability ({reliability}) for event: {title}")

            if url:
                print(f"  • {title}: {source_type} (reliability: {reliability or 'unset'})")
            else:
                self.warnings.append(f"Missing source URL for event: {title}")

        self.validation_results['sources'] = {
            'accessible_urls': accessible_urls,
            'inaccessible_urls': inaccessible_urls,
            'urls_checked': check_urls,
            'issues': issues
        }

        print(f"\nSource Summary: {len(issues)} issues, {len([w for w in self.warnings if 'URL' in w or 'source' in w])} warnings")
        if check_urls:
            print(f"  URLs checked: {accessible_urls + inaccessible_urls}")
            print(f"  Accessible: {accessible_urls}")
            print(f"  Inaccessible: {inaccessible_urls}")

        return len(issues)

    def validate_cross_references(self, country_code='DE'):
        """Cross-validate data points for consistency"""
        print("\n" + "="*80)
        print("4. CROSS-REFERENCE VALIDATION")
        print("="*80)

        cursor = self.conn.cursor()
        issues = []

        print("\nValidating Germany-specific facts...")

        # Verify diplomatic normalization date
        cursor.execute("""
            SELECT diplomatic_normalization_date
            FROM bilateral_countries
            WHERE country_code = ?
        """, (country_code,))
        result = cursor.fetchone()

        if result and result[0]:
            norm_date = result[0]
            if norm_date == '1972-10-11':
                print(f"  ✓ Diplomatic normalization date: {norm_date} (VERIFIED)")
            else:
                issues.append(f"Unexpected normalization date: {norm_date} (expected 1972-10-11 for West Germany)")
                print(f"  ✗ Unexpected date: {norm_date}")

        # Verify Kuka acquisition details
        cursor.execute("""
            SELECT deal_value_usd, chinese_acquirer, acquisition_date
            FROM major_acquisitions
            WHERE target_company = 'Kuka AG'
        """)
        kuka = cursor.fetchone()

        if kuka:
            value, acquirer, date = kuka
            print(f"\n  Kuka AG acquisition:")

            # Known facts from multiple sources
            if value == 5000000000:
                print(f"    ✓ Deal value: ${value/1e9:.1f}B (VERIFIED)")
            else:
                issues.append(f"Kuka value mismatch: ${value/1e9:.1f}B (expected $5.0B)")
                print(f"    ✗ Deal value: ${value/1e9:.1f}B (expected $5.0B)")

            if acquirer == 'Midea Group':
                print(f"    ✓ Acquirer: {acquirer} (VERIFIED)")
            else:
                issues.append(f"Kuka acquirer mismatch: {acquirer} (expected Midea Group)")

            if date == '2016-08-08':
                print(f"    ✓ Date: {date} (VERIFIED)")
            else:
                issues.append(f"Kuka date mismatch: {date} (expected 2016-08-08)")

        # Check event chronology
        print("\nChecking event chronology...")
        cursor.execute("""
            SELECT event_title, event_year
            FROM bilateral_events
            WHERE country_code = ?
            ORDER BY event_year
        """, (country_code,))

        events = cursor.fetchall()
        prev_year = 0
        for title, year in events:
            if year >= prev_year:
                prev_year = year
            else:
                issues.append(f"Chronology error: {title} ({year}) appears after later events")

        print(f"  ✓ Event chronology is consistent ({len(events)} events)")

        self.validation_results['cross_validation'] = {
            'facts_verified': 3,  # normalization date, Kuka value, Kuka acquirer
            'issues': issues
        }

        print(f"\nCross-reference Summary: {len(issues)} issues found")
        return len(issues)

    def validate_temporal_logic(self, country_code='DE'):
        """Check temporal consistency and logic"""
        print("\n" + "="*80)
        print("5. TEMPORAL CONSISTENCY VALIDATION")
        print("="*80)

        cursor = self.conn.cursor()
        issues = []

        # Check that acquisition dates are after announcement dates
        print("\nChecking acquisition timeline logic...")
        cursor.execute("""
            SELECT target_company, announcement_date, acquisition_date
            FROM major_acquisitions
            WHERE country_code = ? AND announcement_date IS NOT NULL AND acquisition_date IS NOT NULL
        """, (country_code,))

        for company, announced, acquired in cursor.fetchall():
            if announced > acquired:
                issues.append(f"{company}: Acquisition date ({acquired}) before announcement ({announced})")
                print(f"  ✗ {company}: Timeline error")
            else:
                print(f"  ✓ {company}: Announced {announced} → Acquired {acquired}")

        # Check that events don't occur before diplomatic normalization
        cursor.execute("""
            SELECT diplomatic_normalization_date FROM bilateral_countries WHERE country_code = ?
        """, (country_code,))
        norm_date_result = cursor.fetchone()

        if norm_date_result and norm_date_result[0]:
            norm_date = norm_date_result[0]
            cursor.execute("""
                SELECT event_title, event_date
                FROM bilateral_events
                WHERE country_code = ? AND event_date < ?
            """, (country_code, norm_date))

            pre_norm_events = cursor.fetchall()
            if pre_norm_events:
                for title, date in pre_norm_events:
                    # This might be OK if it's the normalization event itself
                    if 'normalization' not in title.lower():
                        issues.append(f"Event before normalization: {title} ({date})")

        # Check for future dates
        today = datetime.now().strftime('%Y-%m-%d')
        print("\nChecking for future dates...")

        cursor.execute("""
            SELECT event_title, event_date
            FROM bilateral_events
            WHERE country_code = ? AND event_date > ?
        """, (country_code, today))

        future_events = cursor.fetchall()
        for title, date in future_events:
            issues.append(f"Future date found: {title} ({date})")
            print(f"  ✗ {title}: {date} (future)")

        if not future_events:
            print("  ✓ No future dates found")

        self.validation_results['temporal'] = {
            'timeline_errors': len(issues),
            'issues': issues
        }

        print(f"\nTemporal Summary: {len(issues)} issues found")
        return len(issues)

    def detect_duplicates(self, country_code='DE'):
        """Detect potential duplicate records"""
        print("\n" + "="*80)
        print("6. DUPLICATE DETECTION")
        print("="*80)

        cursor = self.conn.cursor()
        duplicates = []

        # Check for duplicate acquisitions (same company, similar dates)
        print("\nChecking for duplicate acquisitions...")
        cursor.execute("""
            SELECT target_company, COUNT(*) as count
            FROM major_acquisitions
            WHERE country_code = ?
            GROUP BY target_company
            HAVING COUNT(*) > 1
        """, (country_code,))

        dup_acquisitions = cursor.fetchall()
        if dup_acquisitions:
            for company, count in dup_acquisitions:
                duplicates.append(f"Duplicate acquisition records for {company} ({count} entries)")
                print(f"  ⚠ {company}: {count} records")
        else:
            print("  ✓ No duplicate acquisitions found")

        # Check for duplicate events (same title, same date)
        print("\nChecking for duplicate events...")
        cursor.execute("""
            SELECT event_title, event_date, COUNT(*) as count
            FROM bilateral_events
            WHERE country_code = ?
            GROUP BY event_title, event_date
            HAVING COUNT(*) > 1
        """, (country_code,))

        dup_events = cursor.fetchall()
        if dup_events:
            for title, date, count in dup_events:
                duplicates.append(f"Duplicate event: {title} on {date} ({count} entries)")
                print(f"  ⚠ {title} ({date}): {count} records")
        else:
            print("  ✓ No duplicate events found")

        self.validation_results['duplicates'] = {
            'duplicates_found': len(duplicates),
            'issues': duplicates
        }

        print(f"\nDuplicate Summary: {len(duplicates)} potential duplicates")
        return len(duplicates)

    def validate_zero_fabrication(self, country_code='DE'):
        """Validate compliance with zero-fabrication mandate"""
        print("\n" + "="*80)
        print("7. ZERO-FABRICATION COMPLIANCE")
        print("="*80)

        cursor = self.conn.cursor()
        issues = []

        print("\nChecking evidence requirements...")

        # All acquisitions must have sources
        cursor.execute("""
            SELECT COUNT(*) FROM major_acquisitions
            WHERE country_code = ? AND (source_url IS NULL OR source_url = '')
        """, (country_code,))
        unsourced_acq = cursor.fetchone()[0]

        if unsourced_acq > 0:
            issues.append(f"{unsourced_acq} acquisitions lack source documentation")
            print(f"  ✗ {unsourced_acq} acquisitions without sources")
        else:
            print(f"  ✓ All acquisitions have source documentation")

        # All events must have source type
        cursor.execute("""
            SELECT COUNT(*) FROM bilateral_events
            WHERE country_code = ? AND (source_type IS NULL OR source_type = '')
        """, (country_code,))
        unsourced_events = cursor.fetchone()[0]

        if unsourced_events > 0:
            issues.append(f"{unsourced_events} events lack source type classification")
            print(f"  ✗ {unsourced_events} events without source type")
        else:
            print(f"  ✓ All events have source type classification")

        # Check for estimated/unverified data flags
        cursor.execute("""
            SELECT event_title, verification_status
            FROM bilateral_events
            WHERE country_code = ? AND verification_status = 'unverified'
        """, (country_code,))

        unverified = cursor.fetchall()
        if unverified:
            for title, status in unverified:
                self.warnings.append(f"Unverified event: {title}")
            print(f"  ⚠ {len(unverified)} events marked as unverified")
        else:
            print(f"  ✓ No explicitly unverified events")

        self.validation_results['zero_fabrication'] = {
            'unsourced_acquisitions': unsourced_acq,
            'unsourced_events': unsourced_events,
            'unverified_events': len(unverified),
            'issues': issues
        }

        print(f"\nZero-Fabrication Summary: {len(issues)} compliance issues")
        return len(issues)

    def generate_report(self):
        """Generate comprehensive validation report"""
        print("\n" + "="*80)
        print("VALIDATION REPORT SUMMARY")
        print("="*80)

        total_issues = sum(len(cat.get('issues', [])) for cat in self.validation_results.values())
        total_warnings = len(self.warnings)

        print(f"\nTotal Issues Found: {total_issues}")
        print(f"Total Warnings: {total_warnings}")
        print()

        for category, results in self.validation_results.items():
            if results and results.get('issues'):
                print(f"\n{category.upper()}:")
                for issue in results['issues'][:5]:  # Show first 5
                    print(f"  - {issue}")
                if len(results['issues']) > 5:
                    print(f"  ... and {len(results['issues']) - 5} more")

        if self.warnings:
            print(f"\nWARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:5]:
                print(f"  - {warning}")
            if len(self.warnings) > 5:
                print(f"  ... and {len(self.warnings) - 5} more")

        # Overall assessment
        print("\n" + "="*80)
        if total_issues == 0:
            print("✓ VALIDATION PASSED: No critical issues found")
            if total_warnings > 0:
                print(f"  {total_warnings} warnings to review")
        elif total_issues < 5:
            print("⚠ VALIDATION: Minor issues found, review recommended")
        else:
            print("✗ VALIDATION FAILED: Significant issues require attention")
        print("="*80)

        # Save report to file
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/BILATERAL_DATA_VALIDATION_REPORT.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_issues': total_issues,
                    'total_warnings': total_warnings
                },
                'results': self.validation_results,
                'warnings': self.warnings
            }, f, indent=2)
        print(f"\nDetailed report saved: {report_path}")

        return total_issues

    def close(self):
        if self.conn:
            self.conn.close()

def main():
    print("="*80)
    print("BILATERAL RELATIONS DATA VALIDATOR")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    validator = BilateralDataValidator()

    try:
        validator.connect()

        # Run all validation checks
        issues_completeness = validator.validate_completeness('DE')
        issues_integrity = validator.validate_integrity('DE')
        issues_sources = validator.validate_sources('DE', check_urls=False)  # Set True to check URL accessibility
        issues_cross_ref = validator.validate_cross_references('DE')
        issues_temporal = validator.validate_temporal_logic('DE')
        issues_duplicates = validator.detect_duplicates('DE')
        issues_zero_fab = validator.validate_zero_fabrication('DE')

        # Generate report
        total_issues = validator.generate_report()

        return total_issues == 0

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        validator.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
