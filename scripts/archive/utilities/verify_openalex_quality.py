#!/usr/bin/env python3
"""
OpenAlex Data Quality Verification
==================================
Verifies the quality and completeness of OpenAlex collection.

NO FABRICATION - All checks based on actual database records.

Created: 2025-10-26
"""

import sqlite3
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

DB_PATH = Path('F:/OSINT_WAREHOUSE/osint_master.db')
CHECKPOINT_PATH = Path('data/openalex_v4_checkpoint.json')

def run_quality_checks():
    """Run comprehensive quality checks on OpenAlex data."""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    results = {
        'timestamp': datetime.now().isoformat(),
        'database': str(DB_PATH),
        'checks': {}
    }

    print("="*70)
    print("OPENALEX DATA QUALITY CHECKS")
    print("="*70)

    # Check 1: Verify domain counts (should be exactly 25,000 each)
    print("\n[Check 1] Technology Domain Counts")
    print("-" * 70)

    domain_query = """
        SELECT technology_domain, COUNT(*) as count
        FROM openalex_works
        GROUP BY technology_domain
        ORDER BY technology_domain
    """

    domain_counts = {}
    for row in cursor.execute(domain_query):
        domain, count = row
        domain_counts[domain] = count
        status = "[OK]" if count == 25000 else "[WARNING]"
        print(f"  {status} {domain}: {count:,}")

    results['checks']['domain_counts'] = domain_counts
    results['checks']['all_domains_25k'] = all(c == 25000 for c in domain_counts.values())

    # Check 2: Verify no NULL in critical fields
    print("\n[Check 2] NULL Field Analysis")
    print("-" * 70)

    critical_fields = ['work_id', 'title', 'publication_date', 'technology_domain']
    null_counts = {}

    for field in critical_fields:
        query = f"SELECT COUNT(*) FROM openalex_works WHERE {field} IS NULL"
        null_count = cursor.execute(query).fetchone()[0]
        null_counts[field] = null_count
        status = "[OK]" if null_count == 0 else "[ERROR]"
        print(f"  {status} {field}: {null_count} NULL records")

    results['checks']['null_fields'] = null_counts
    results['checks']['no_critical_nulls'] = all(c == 0 for c in null_counts.values())

    # Check 3: Date range analysis
    print("\n[Check 3] Publication Date Range")
    print("-" * 70)

    date_query = """
        SELECT
            MIN(publication_date) as earliest,
            MAX(publication_date) as latest,
            COUNT(DISTINCT publication_date) as distinct_dates
        FROM openalex_works
        WHERE publication_date IS NOT NULL
    """

    date_info = cursor.execute(date_query).fetchone()
    earliest, latest, distinct_dates = date_info

    print(f"  Earliest publication: {earliest}")
    print(f"  Latest publication: {latest}")
    print(f"  Distinct dates: {distinct_dates:,}")

    results['checks']['date_range'] = {
        'earliest': earliest,
        'latest': latest,
        'distinct_dates': distinct_dates
    }

    # Check 4: Chinese collaboration detection
    print("\n[Check 4] Chinese Collaboration Detection")
    print("-" * 70)

    # Query for works with Chinese authors (country_code = 'CN')
    chinese_query = """
        SELECT w.technology_domain, COUNT(DISTINCT w.work_id) as chinese_works
        FROM openalex_works w
        JOIN openalex_work_authors a ON w.work_id = a.work_id
        WHERE a.country_code = 'CN'
        GROUP BY w.technology_domain
        ORDER BY chinese_works DESC
    """

    chinese_counts = {}
    total_chinese = 0

    for row in cursor.execute(chinese_query):
        domain, count = row
        chinese_counts[domain] = count
        total_chinese += count

        # Get domain total for accurate percentage
        domain_total = cursor.execute(
            "SELECT COUNT(*) FROM openalex_works WHERE technology_domain = ?",
            (domain,)
        ).fetchone()[0]

        percentage = (count / domain_total) * 100 if domain_total > 0 else 0
        print(f"  {domain}: {count:,} / {domain_total:,} ({percentage:.1f}%)")

    # Get overall total works
    total_works = cursor.execute("SELECT COUNT(*) FROM openalex_works").fetchone()[0]

    print(f"\n  TOTAL Chinese collaborations: {total_chinese:,} / {total_works:,} ({(total_chinese/total_works)*100:.1f}%)")

    results['checks']['chinese_collaborations'] = {
        'by_domain': chinese_counts,
        'total': total_chinese,
        'total_works': total_works,
        'percentage': (total_chinese / total_works) * 100 if total_works > 0 else 0
    }

    # Check 5: Institutional affiliation data quality
    print("\n[Check 5] Institutional Data Quality")
    print("-" * 70)

    # Count works that have author affiliations
    total_works_query = "SELECT COUNT(*) FROM openalex_works"
    total_works = cursor.execute(total_works_query).fetchone()[0]

    works_with_authors_query = "SELECT COUNT(DISTINCT work_id) FROM openalex_work_authors"
    works_with_authors = cursor.execute(works_with_authors_query).fetchone()[0]

    works_with_institutions_query = """
        SELECT COUNT(DISTINCT work_id)
        FROM openalex_work_authors
        WHERE institution_id IS NOT NULL
    """
    works_with_institutions = cursor.execute(works_with_institutions_query).fetchone()[0]

    print(f"  Total works: {total_works:,}")
    print(f"  Works with authors: {works_with_authors:,} ({(works_with_authors/total_works)*100:.1f}%)")
    print(f"  Works with institutional affiliations: {works_with_institutions:,} ({(works_with_institutions/total_works)*100:.1f}%)")

    results['checks']['institutions'] = {
        'total_works': total_works,
        'with_authors': works_with_authors,
        'with_institutions': works_with_institutions,
        'author_coverage': (works_with_authors / total_works) * 100 if total_works > 0 else 0,
        'institution_coverage': (works_with_institutions / total_works) * 100 if total_works > 0 else 0
    }

    # Check 6: Duplicate detection
    print("\n[Check 6] Duplicate Detection")
    print("-" * 70)

    duplicate_query = """
        SELECT work_id, COUNT(*) as count
        FROM openalex_works
        GROUP BY work_id
        HAVING count > 1
    """

    duplicates = cursor.execute(duplicate_query).fetchall()
    print(f"  Duplicate work_ids: {len(duplicates)}")

    if duplicates:
        print(f"  [WARNING] Found duplicates:")
        for work_id, count in duplicates[:5]:
            print(f"    - {work_id}: {count} occurrences")
    else:
        print(f"  [OK] No duplicates found")

    results['checks']['duplicates'] = {
        'count': len(duplicates),
        'examples': duplicates[:5] if duplicates else []
    }

    # Check 7: Checkpoint verification
    print("\n[Check 7] Checkpoint File Verification")
    print("-" * 70)

    if CHECKPOINT_PATH.exists():
        with open(CHECKPOINT_PATH, 'r') as f:
            checkpoint = json.load(f)

        print(f"  [OK] Checkpoint file exists")
        print(f"  Last file processed: {checkpoint.get('last_file_processed', 'N/A')}")
        print(f"  Processing completed: {checkpoint.get('completed', False)}")

        results['checks']['checkpoint'] = checkpoint
    else:
        print(f"  [WARNING] Checkpoint file not found at {CHECKPOINT_PATH}")
        results['checks']['checkpoint'] = None

    # Summary
    print("\n" + "="*70)
    print("QUALITY CHECK SUMMARY")
    print("="*70)

    passed_checks = 0
    total_checks = 6

    # Note: Expecting ~225k works total (not exactly 25k per domain due to deduplication)
    total_collected = sum(results['checks']['domain_counts'].values())
    if total_collected >= 220000:
        print(f"  [PASS] Collected {total_collected:,} works (target: ~225,000)")
        passed_checks += 1
    else:
        print(f"  [WARN] Only {total_collected:,} works collected (target: ~225,000)")

    if results['checks']['no_critical_nulls']:
        print("  [PASS] No NULL values in critical fields")
        passed_checks += 1
    else:
        print("  [FAIL] NULL values found in critical fields")

    if results['checks']['date_range']['distinct_dates'] > 100:
        print("  [PASS] Good date range coverage")
        passed_checks += 1
    else:
        print("  [WARN] Limited date range")

    if results['checks']['chinese_collaborations']['total'] > 0:
        print("  [PASS] Chinese collaborations detected")
        passed_checks += 1
    else:
        print("  [FAIL] No Chinese collaborations found")

    if results['checks']['institutions']['author_coverage'] > 50:
        print(f"  [PASS] Good author coverage ({results['checks']['institutions']['author_coverage']:.1f}%)")
        passed_checks += 1
    else:
        print(f"  [WARN] Low author coverage ({results['checks']['institutions']['author_coverage']:.1f}%)")

    if results['checks']['duplicates']['count'] == 0:
        print("  [PASS] No duplicate work_ids")
        passed_checks += 1
    else:
        print("  [FAIL] Duplicate work_ids detected")

    print(f"\n  Overall: {passed_checks}/{total_checks} checks passed")
    results['summary'] = {
        'passed': passed_checks,
        'total': total_checks,
        'pass_rate': (passed_checks / total_checks) * 100
    }

    conn.close()

    # Save results
    output_path = Path('analysis/openalex_quality_check_20251026.json')
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n[OK] Quality check results saved to: {output_path}")
    print("="*70)

    return results

if __name__ == '__main__':
    run_quality_checks()
